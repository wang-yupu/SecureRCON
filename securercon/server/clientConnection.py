#
from socket import socket
from .internal import *
from enum import Enum
from mcdreforged.api import rcon
from .. import shared


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
    def __init__(self, clientSocket: socket, authOptions: AuthOptions) -> None:
        self.socket = clientSocket
        self.authOptions = authOptions

        self.authSuccess = False
        self.encrypted = False

        self.authMethod: AuthMethod = AuthMethod.UNAUTHORIZATION

        self.RCONClient = rcon.RconConnection(shared.rcon.host, shared.rcon.port, shared.rcon.password)

    def doLegacyAuth(self, packet: RCONPacket) -> tuple[bool, str, AuthMethod]:
        try:
            pwd = packet.payload.decode('utf-8')
        except UnicodeDecodeError:
            return False, 'Failed to decode password.', AuthMethod.UNAUTHORIZATION

        if self.authOptions.allowLegacy and self.authOptions.legacyPassword:
            if self.authOptions.legacyPassword == pwd:
                return True, 'Success login', AuthMethod.FIXED_PASSWORD
            return False, 'Access with a fixed password and without encryption is not allowed.', AuthMethod.UNAUTHORIZATION
        elif self.authOptions.allowDynmaic and self.authOptions.dynmaicKey and self.authOptions.dynmaicLength:
            if getPasswordNow(self.authOptions.dynmaicKey, self.authOptions.dynmaicLength) == pwd:
                return True, 'Success login', AuthMethod.DYNMAIC_PASSWORD
            return False, 'Access with a dynmaic password and without encryption is not allowed.', AuthMethod.UNAUTHORIZATION
        return False, 'Access with a dynmaic or fixed password and without encryption is not allowed.', AuthMethod.UNAUTHORIZATION

    def executeCommand(self, packet: RCONPacket) -> str:
        result = self.RCONClient.send_command(packet.payload.decode(encoding='utf-8'))
        return result if result else ""

    def executeMCDRCommand(self, packet: RCONPacket):
        print(f"EXECUTE COMMAND: {packet.payload}")
        return "Result: MCDR command"

    def start(self):
        while True:
            data = self.socket.recv(2048)
            if not self.encrypted:
                packet = rawToPacketClass(data)
                match (packet.type):
                    case 3:  # AUTH
                        authResult, authMessage, method = self.doLegacyAuth(packet)
                        print(authMessage)
                        self.authMethod = method
                        if not authResult:
                            print("AUTH FAILED:", self.authMethod)
                            self.socket.send(packetClassToRaw(RCONPacket(
                                0, -1, 2, authMessage.encode(encoding='utf-8'))))
                            break
                        self.authSuccess = True
                        self.RCONClient.connect()
                        self.socket.send(packetClassToRaw(RCONPacket(
                            0, packet.id, 3, authMessage.encode(encoding='utf-8'))))
                    case 2:  # EXECUTE_COMMAND
                        if self.authSuccess and self.authMethod != AuthMethod.UNAUTHORIZATION:
                            result = self.executeCommand(packet)
                            self.socket.send(packetClassToRaw(RCONPacket(0, packet.id, 0, result.encode('utf-8'))))
                    case 8:  # MCDR Command
                        if self.authSuccess and self.authMethod != AuthMethod.UNAUTHORIZATION:
                            result = self.executeMCDRCommand(packet)
                            self.socket.send(packetClassToRaw(RCONPacket(0, packet.id, 0, result.encode('utf-8'))))
                    case 255:  # 开始加密流程
                        ...
                    case _:
                        self.socket.close()

        self.socket.close()
