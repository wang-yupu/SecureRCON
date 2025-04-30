#
from socket import socket
from .internal import *
from enum import Enum
from mcdreforged.api import rcon
from .. import shared
from ..encrypt import exchange
import threading
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.exceptions import InvalidTag
from ..encrypt.encrypt import *
from queue import Queue, Empty, Full
import json
import time


class AuthMethod(Enum):
    # 第0位: 是否加密
    # 第1位: 是否固定密码
    # 第2位: 是否动态密码
    UNAUTHORIZATION = 0b000
    FIXED_PASSWORD = 0b010
    DYNMAIC_PASSWORD = 0b001
    ENCRYPTED_FIXED_PASSWORD = 0b110
    ENCRYPTED_DYNMAIC_PASSWORD = 0b111


class ClientConnection:
    def __init__(self, clientSocket: socket, authOptions: AuthOptions, networkOptions: NetworkOptions, id: int, chatSender, logger) -> None:
        self.socket = clientSocket
        self.authOptions = authOptions
        self.networkOptions = networkOptions
        self.logger = logger
        self.id = id

        self.socket.settimeout(self.networkOptions.timeout)
        self.sendLock = threading.Lock()
        self.progressLock = threading.Lock()

        self.authSuccess = False
        self.encrypted = False
        self.encryptKey = b""
        self.packedID = 0

        self.authMethod: AuthMethod = AuthMethod.UNAUTHORIZATION

        self.RCONClient = rcon.RconConnection(shared.rcon.host, shared.rcon.port, shared.rcon.password)

        self.inChat = False
        self.chatQueue = Queue(50)
        self.chatSender = chatSender

    def doAuth(self, packet: RCONPacket) -> tuple[bool, str, AuthMethod]:
        try:
            pwd = packet.payload.decode('utf-8')
        except UnicodeDecodeError:
            return False, 'Failed to decode password.', AuthMethod.UNAUTHORIZATION

        if not self.encrypted:
            if self.authOptions.allowLegacy and self.authOptions.legacyPassword:
                print("'", packet.payload, "'")
                if self.authOptions.legacyPassword == pwd:
                    return True, 'Success login', AuthMethod.FIXED_PASSWORD
                return False, 'Access with a fixed password and without encryption is not allowed.', AuthMethod.UNAUTHORIZATION
            elif self.authOptions.allowDynmaic and self.authOptions.dynmaicKey and self.authOptions.dynmaicLength:
                if getPasswordNow(self.authOptions.dynmaicKey, self.authOptions.dynmaicLength) == pwd:
                    return True, 'Success login', AuthMethod.DYNMAIC_PASSWORD
                return False, 'Access with a dynmaic password and without encryption is not allowed.', AuthMethod.UNAUTHORIZATION
            return False, 'Access with a dynmaic or fixed password and without encryption is not allowed.', AuthMethod.UNAUTHORIZATION
        elif self.encrypted:
            if self.authOptions.allowEncryptedLegeacy and self.authOptions.legacyPassword:
                print("'", packet.payload, "'")
                if self.authOptions.legacyPassword == pwd:
                    return True, 'Success login', AuthMethod.ENCRYPTED_FIXED_PASSWORD
                return False, 'Access with a fixed password is not allowed.', AuthMethod.UNAUTHORIZATION
            elif self.authOptions.allowEncryptedDynmaic and self.authOptions.dynmaicKey and self.authOptions.dynmaicLength:
                if getPasswordNow(self.authOptions.dynmaicKey, self.authOptions.dynmaicLength) == pwd:
                    return True, 'Success login', AuthMethod.ENCRYPTED_DYNMAIC_PASSWORD
                return False, 'Access with a dynmaic password is not allowed.', AuthMethod.UNAUTHORIZATION
            return False, 'Access with a dynmaic or fixed password is not allowed.', AuthMethod.UNAUTHORIZATION
        return False, 'Access is not allowed.', AuthMethod.UNAUTHORIZATION

    def executeCommand(self, packet: RCONPacket) -> str:
        result = self.RCONClient.send_command(packet.payload.decode(encoding='utf-8'))
        return result if result else ""

    def executeMCDRCommand(self, packet: RCONPacket):
        print(f"EXECUTE COMMAND: {packet.payload}")
        return "Result: MCDR command"

    def sendChat(self, packet: RCONPacket):
        self.chatSender(f'[RCON] {packet.payload.decode(encoding='utf-8', errors='ignore')}')
        self.logger.info(f"RCON Chat: {packet.payload.decode(encoding='utf-8', errors='ignore')}")

    def chatListener(self):
        # 添加listener
        shared.chatTriggers[f'Listener_{self.id}'] = self.chatCallback
        self.logger.info("Chat listener was register success.")
        while self.inChat and not shared.stop:
            try:
                content = self.chatQueue.get_nowait()
                if self.inChat:
                    # 编码聊天为json
                    data = {
                        "source": content[0],
                        "content": content[1],
                        "time": int(time.time())
                    }
                    with self.progressLock:
                        self.send(RCONPacket(0, -500, 20, json.dumps(data).encode(encoding='utf-8')))
                        self.logger.info(f"Chat to client: {content[1]}")
            except Empty:
                time.sleep(0.01)
                continue

        del shared.chatTriggers[f'Listener_{self.id}']

    def chatCallback(self, source, content):
        try:
            self.chatQueue.put([source, content])
        except Full:
            self.chatQueue = Queue(50)

    def send(self, packet: RCONPacket):
        packet.id = self.packedID
        d = packetClassToRaw(packet)
        if self.encrypted:
            encryptedData = ChaCha20Poly1305Encrypt(d, self.encryptKey, None, self.packedID)
            with self.sendLock:
                self.socket.send(encryptedData)
        else:
            with self.sendLock:
                self.socket.send(d)

    def recv(self, skipEncrypt: bool = False) -> tuple[bool, RCONPacket | None]:
        raw = b''
        while True:
            try:
                raw = self.socket.recv(self.networkOptions.bufsize)
                break
            except TimeoutError:
                if self.authMethod == AuthMethod.UNAUTHORIZATION:
                    self.logger.warn("Peer timeout.")
                    return False, None
                continue
        if self.encrypted and not skipEncrypt:
            try:
                r = ChaCha20Poly1305Decrypt(raw, self.encryptKey, None, self.packedID)
                p = rawToPacketClass(r)
            except InvalidTag:
                self.logger.info(f"Maybe client out of sync.")
                self.logger.info(f"ChaCha20Poly1305 Key: {self.encryptKey}")
                self.logger.info(f"Packet ID: {self.packedID}")
                return False, None
            self.packedID += 1
            return True, p
        elif not self.encrypted:
            try:
                p = rawToPacketClass(raw)
            except:
                return False, None
            self.packedID += 1
            return True, p
        return False, None

    def start(self):
        while True:
            res, packet = self.recv()
            if packet is None:
                self.logger.warn("Failed to decode RCON data. ")
                break
            with self.progressLock:
                match (packet.type):
                    case 3:  # AUTH
                        authResult, authMessage, method = self.doAuth(packet)
                        print(authMessage)
                        self.authMethod = method
                        if not authResult:
                            print("AUTH FAILED:", self.authMethod)
                            self.send(RCONPacket(
                                0, -1, 2, authMessage.encode(encoding='utf-8')))
                            break
                        self.authSuccess = True
                        self.RCONClient.connect()
                        self.send(RCONPacket(
                            0, packet.id, 3, authMessage.encode(encoding='utf-8')))
                    case 2:  # EXECUTE_COMMAND
                        if self.authSuccess and self.authMethod != AuthMethod.UNAUTHORIZATION and not self.inChat:
                            result = self.executeCommand(packet)
                            self.send(RCONPacket(0, packet.id, 0, result.encode('utf-8')))
                    case 8:  # MCDR Command
                        if self.authSuccess and self.authMethod != AuthMethod.UNAUTHORIZATION and not self.inChat:
                            result = self.executeMCDRCommand(packet)
                            self.send(RCONPacket(0, packet.id, 0, result.encode('utf-8')))
                    case 255:  # 开始加密流程
                        # 交换密钥，用X25519
                        if not (shared.public and shared.private):
                            break
                        self.socket.send(packetClassToRaw(RCONPacket(0, packet.id, 255,
                                                                     exchange.toBase85(shared.public).encode(encoding='utf-8'))))
                        # 等待
                        try:
                            result = rawToPacketClass(self.socket.recv(2048))
                        except TimeoutError:
                            break
                        self.encryptKey = exchange.exchange(shared.private, x25519.X25519PublicKey.from_public_bytes(
                            result.payload), None, b"INFO", 32)

                        self.encrypted = True
                        self.logger.info("Key exchange success.")
                        self.packedID = 0
                    case 16:  # Chat start
                        if not self.inChat:
                            threading.Thread(name=f"RCONChatListener-{self.id}",
                                             target=self.chatListener, daemon=True).start()
                            self.inChat = True
                            self.logger.info("Chat listen was registerd.")
                        else:
                            pass
                    case 17:  # Chat end
                        self.inChat = False
                        self.logger.info("Chat listen was unregisterd.")
                    case 20:  # chat content
                        if self.inChat:
                            self.sendChat(packet)
                    case 128:
                        self.send(RCONPacket(0, packet.id, 128, packet.payload))
                    case _:
                        self.logger.info("Client send a unknown packet. Maybe outdated server.")
                        self.socket.close()

        self.logger.info("Event loop was exited.")
        self.socket.close()
