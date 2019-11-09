from websocket import create_connection
import os

currentDirectory = os.getcwd()
fileNamePath = currentDirectory + '/' + 'Source' + '.zip'
payload = bytearray()

with open(fileNamePath, 'rb') as binary_file:
    while True:
        byte = binary_file.read(1)
        if byte == b"":
            break
        payload.extend(byte)

url = "ws://localhost:" + str(65001)
ws = create_connection(url)
print("Sending...")
ws.send(payload)
# print("Sent")
print("Receiving...")
result = ws.recv()
print("Received '%s'" % result)
# with open("Aingcupu", "wb") as file:
#     file.write(result)
ws.close()