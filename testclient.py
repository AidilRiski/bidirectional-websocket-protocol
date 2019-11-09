from constants import *
from websocket import create_connection
import os

url = "ws://localhost:" + str(PORT)
ws = create_connection(url)
payload = bytearray()
currentDirectory = os.getcwd()
fileNamePath = currentDirectory + '/' + FILE_NAME + '.zip'
with open(fileNamePath, 'rb') as binary_file:
    while True:
        byte = binary_file.read(1)
        if byte == b"":
            break
        payload.extend(byte)

print("Sending...")
ws.send('!submission')
# print("Sent")
print("Receiving...")
result = ws.recv()
print("Received '%s'" % result)
# with open("Aingcupu", "wb") as file:
#     file.write(result)


ws.close()