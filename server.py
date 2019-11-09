import connection
import socket
import threading

def accepting(incomingConnection, incomingAddress):
    print('Entered')
    print(incomingConnection)
    print(incomingAddress)
    while True:
        data = incomingConnection.recv(1024)
        if (not data):
            break
        print(str(data))

print('Starting...')
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('localhost', 65000))
serverSocket.listen()
threadNum = 0
while True:
    # print("Trying")
    incomingConnection = None
    incomingAddress = None
    threadNum += 1 
    try:
        incomingConnection, incomingAddress = serverSocket.accept()
    except Exception:
        print("Closing Server...")
        break
    # print('Entering')
    # threading.Thread(target = accepting, args = (incomingConnection, incomingAddress)).start()
    connectionThread = connection.WebConnection(incomingConnection, incomingAddress, threadNum)
    connectionThread.start()