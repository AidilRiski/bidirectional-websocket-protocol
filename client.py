import time
import socket

print('Sending...')
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.connect(('localhost', 65000))
for i in range(0, 10):
    dataToSend = 'Hello Jancuk!' + str(i)
    serverSocket.send(bytes(dataToSend, 'UTF-8'))
    time.sleep(0.5)
print('Done')