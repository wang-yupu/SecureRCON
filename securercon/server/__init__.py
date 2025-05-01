import socket
import threading
from .internal import *
from .clientConnection import ClientConnection
from .. import shared

activeConnections = 0
connectionLock = threading.Lock()


def handleClient(clientSocket, clientAddress, chatSender, logger, authConfig):
    global activeConnections

    network = NetworkOptions(shared.config.network.maxConnection,
                             shared.config.network.timeout, shared.config.network.bufsize)

    try:
        connection = ClientConnection(clientSocket, authConfig,
                                      network, activeConnections, chatSender, logger)
        connection.start()
    except ConnectionResetError:
        pass
    except:
        pass
    finally:
        clientSocket.close()
        with connectionLock:
            activeConnections -= 1
        logger.info(f"Disconnected from {clientAddress}")


def startServer(logger, chatSender):
    global activeConnections
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = shared.config.network.host
    port = shared.config.network.port
    serverSocket.bind((host, port))
    serverSocket.listen()
    serverSocket.settimeout(1.0)
    logger.info(f"RCON Server started on {host}:{port}.")
    authConfig = AuthOptions()
    authConfig.allowDynmaic = shared.config.authorization.dynmaic.enable and not shared.config.authorization.dynmaic.requireEncrypt
    authConfig.allowLegacy = shared.config.authorization.fixed.enable and not shared.config.authorization.fixed.requireEncrypt
    authConfig.allowEncrypt = shared.config.authorization.enableEncrypt
    authConfig.allowEncryptedDynmaic = shared.config.authorization.dynmaic.enable and authConfig.allowEncrypt
    authConfig.allowEncryptedLegacy = shared.config.authorization.fixed.enable and authConfig.allowEncrypt
    authConfig.dynmaicKey = shared.config.authorization.dynmaic.key
    authConfig.dynmaicLength = shared.config.authorization.dynmaic.length
    authConfig.legacyPassword = shared.config.authorization.fixed.password
    logger.info(f"Authorization options: {authConfig}")

    try:
        while not shared.stop:
            try:
                clientSocket, clientAddress = serverSocket.accept()
            except socket.timeout:
                continue
            with connectionLock:
                if activeConnections >= shared.config.network.maxConnection:
                    logger.warn("RCON Server busy.")
                    clientSocket.sendall(b"Server busy, try later")
                    clientSocket.close()
                    continue
                activeConnections += 1

            clientThread = threading.Thread(
                target=handleClient,
                args=(clientSocket, clientAddress, chatSender, logger, authConfig),
                daemon=True,
                name=f"RCONClientConnection-{activeConnections}"
            )
            clientThread.start()
            logger.info(f"New RCON connect from: {clientAddress}")

    except KeyboardInterrupt:
        logger.info("Stopping RCON Server...")
    finally:
        serverSocket.close()
        logger.info("RCON server stopped")
        shared.stopped = True
