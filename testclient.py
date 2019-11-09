from constants import *
from websocket import create_connection
url = "ws://localhost:" + str(PORT)
ws = create_connection(url)
print("Sending 'Hello, World'...")
ws.send("!submission")
# print("Sent")
# print("Receiving...")
result =  ws.recv()
# print("Received '%s'" % result)
with open("Aingcupu", "wb") as file:
    file.write(result)

ws.close()