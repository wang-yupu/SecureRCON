import socket
import threading
from .internal import *
from .clientConnection import ClientConnection
from .. import shared

maxConnections = 5
activeConnections = 0
connectionLock = threading.Lock()


def handleClient(clientSocket, clientAddress, chatSender, logger):
    global activeConnections

    try:
        connection = ClientConnection(clientSocket, AuthOptions(legacyPassword="test"),
                                      NetworkOptions(), activeConnections, chatSender, logger)
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


def startServer(logger, chatSender, host='0.0.0.0', port=8888):
    global activeConnections
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen()
    serverSocket.settimeout(1.0)
    logger.info("RCON Server started.")

    try:
        while not shared.stop:
            try:
                clientSocket, clientAddress = serverSocket.accept()
            except socket.timeout:
                continue
            with connectionLock:
                if activeConnections >= maxConnections:
                    logger.warn("RCON Server busy.")
                    clientSocket.sendall(b"Server busy, try later")
                    clientSocket.close()
                    continue
                activeConnections += 1

            clientThread = threading.Thread(
                target=handleClient,
                args=(clientSocket, clientAddress, chatSender, logger),
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
