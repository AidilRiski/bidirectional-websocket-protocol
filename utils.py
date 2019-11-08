import os
import shutil
import hashlib
from constants import *

def zipCurrentFiles():
    currentDirectory = os.getcwd()
    shutil.make_archive(FILE_NAME, 'zip', currentDirectory)

def generateChecksum():
    currentDirectory = os.getcwd()
    fileNamePath = currentDirectory + '/' + FILE_NAME + '.zip'
    hash_md5 = hashlib.md5()
    with open(fileNamePath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def compareHashes(hashClient, hashServer):
    return hashClient.lower() == hashServer.lower()

def test():
    test = bytearray()
    test.extend('1'.encode('utf-8'))
    print(test)

# print(generateChecksum('A4A531314723D98E86945D683E703791', 'a4a531314723d98e86945d683e703791'))
# print(compareHashes())
test()