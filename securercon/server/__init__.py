import socket
import threading
from .internal import *
from .clientConnection import ClientConnection
from .. import shared

maxConnections = 5
activeConnections = 0
connectionLock = threading.Lock()


def handleClient(clientSocket, clientAddress, logger):
    global activeConnections
    print(f"连接来自 {clientAddress}")

    try:
        connection = ClientConnection(clientSocket, AuthOptions(legacyPassword="test"), NetworkOptions(), logger)
        connection.start()
    except ConnectionResetError:
        pass
    except:
        pass
    finally:
        clientSocket.close()
        with connectionLock:
            activeConnections -= 1
        print(f"断开连接 {clientAddress}，当前连接数：{activeConnections}")


def startServer(logger, host='0.0.0.0', port=8888):
    global activeConnections
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen()
    serverSocket.settimeout(1.0)
    print(f"服务器监听在 {host}:{port}")

    try:
        while not shared.stop:
            try:
                clientSocket, clientAddress = serverSocket.accept()
            except socket.timeout:
                continue
            with connectionLock:
                if activeConnections >= maxConnections:
                    print(f"拒绝连接 {clientAddress}，已达到最大连接数")
                    clientSocket.sendall(b"Server busy, try later")
                    clientSocket.close()
                    continue
                activeConnections += 1

            clientThread = threading.Thread(
                target=handleClient,
                args=(clientSocket, clientAddress, logger),
                daemon=True,
                name=f"RCONClientConnection-{activeConnections}"
            )
            clientThread.start()
            print(f"新连接 {clientAddress}，当前连接数：{activeConnections}")

    except KeyboardInterrupt:
        print("\n服务器正在关闭...")
    finally:
        serverSocket.close()
        print("服务器已关闭。")
        shared.stopped = True
