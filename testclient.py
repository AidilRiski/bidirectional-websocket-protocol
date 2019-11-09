from constants import *
# from websocket import create_connection
# import os

# currentDirectory = os.getcwd()
# fileNamePath = currentDirectory + '/' + FILE_NAME + '.zip'
# payload = bytearray()

# with open(fileNamePath, 'rb') as binary_file:
#     while True:
#         byte = binary_file.read(1)
#         if byte == b"":
#             break
#         payload.extend(byte)

# url = "ws://localhost:" + str(PORT)
# ws = create_connection(url)
# print("Sending...")
# ws.send(payload)
# # print("Sent")
# print("Receiving...")
# result = ws.recv()
# print("Received '%s'" % result)
# # with open("Aingcupu", "wb") as file:
# #     file.write(result)
# ws.close()

from websocket import create_connection
url = "ws://localhost:" + str(PORT)
ws = create_connection(url)
print("Sending 'Hello, World'...")
ws.send("!echo HALO...")
print("Sent")
print("Receiving...")
result =  ws.recv()
print("Received '%s'" % result)
ws.close()