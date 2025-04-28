import socket
import threading
from .internal import *
from .clientConnection import ClientConnection
from .. import shared

maxConnections = 5
activeConnections = 0
connectionLock = threading.Lock()


def handleClient(clientSocket, clientAddress):
    global activeConnections
    print(f"连接来自 {clientAddress}")

    try:
        connection = ClientConnection(clientSocket, AuthOptions(legacyPassword="test"))
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


def startServer(host='0.0.0.0', port=8888):
    global activeConnections
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen()
    serverSocket.settimeout(1.0)  # ⭐ 设置1秒超时时间
    print(f"服务器监听在 {host}:{port}")

    try:
        while not shared.stop:
            try:
                clientSocket, clientAddress = serverSocket.accept()
            except socket.timeout:
                continue  # 超时了，继续循环，顺便可以检测Ctrl+C
            with connectionLock:
                if activeConnections >= maxConnections:
                    print(f"拒绝连接 {clientAddress}，已达到最大连接数")
                    clientSocket.sendall(b"Server busy, try later")
                    clientSocket.close()
                    continue
                activeConnections += 1

            clientThread = threading.Thread(
                target=handleClient,
                args=(clientSocket, clientAddress),
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
