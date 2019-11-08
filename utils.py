import os
import shutil
from constants import *

def zipCurrentFiles():
    currentDirectory = os.getcwd()
    shutil.make_archive(FILE_NAME, 'zip', currentDirectory)

# Readfile reads the file and returns bytearray to be parsed
def readFile():
    payload = bytearray()
    currentDirectory = os.getcwd()
    fileNamePath = currentDirectory + '/' + FILE_NAME + '.zip'
    with open(fileNamePath, 'rb') as binary_file:
        while True:
            byte = binary_file.read(1)
            if byte == b"":
                break
            # print(byte)
            payload.extend(byte)
            # payload.append(byte.to_bytes(1, 'little'))
    # print(payload)
    print(os.path.getsize(fileNamePath))


    payload.append(126)
    print(payload[50876])
    # return data
def test():
    payload = bytearray()
    payload.append(50000 & 0xffff)

# zipCurrentFiles()
readFile()