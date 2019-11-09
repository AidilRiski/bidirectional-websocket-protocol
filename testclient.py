# from constants import *
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

# from websocket import create_connection
# url = "ws://localhost:" + str(PORT)
# ws = create_connection(url)
# print("Sending 'Hello, World'...")
# ws.send("!echo HALO1...")
# ws.send("!echo HALO2...")
# ws.send("!echo HALO3...")
# ws.send("!echo HALO4...")
# ws.send("!echo HALO5...")
# ws.send("!echo HALO6...")
# ws.send("!echo HALO7...")
# ws.send("!echo HALO8...")
# ws.send("!echo HALO9...")
# ws.send("!echo HALO10...")
# ws.send("!echo HALO11...")
# ws.send("!echo HALO12...")
# ws.send("!echo HALO13...")
# ws.send("!echo HALO14...")

# print("Sent")
# print("Receiving...")
# result =  ws.recv()
# print("Received '%s'" % result)
# ws.close()

import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        strsend = ""
        for i in range(100):
            time.sleep(1)
            strsend = "!echo ABC" + str(i)
            ws.send(strsend)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    url = "ws://localhost:" + str(65000)
    ws = websocket.WebSocketApp(url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()