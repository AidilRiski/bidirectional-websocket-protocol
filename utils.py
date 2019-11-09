import os
import shutil
import hashlib
from constants import *

def zipCurrentFiles():
    currentDirectory = os.getcwd()
    shutil.make_archive(FILE_NAME, 'zip', currentDirectory)

def generateChecksumFromFile():
    currentDirectory = os.getcwd()
    fileNamePath = currentDirectory + '/' + FILE_NAME + '.zip'
    hash_md5 = hashlib.md5()
    with open(fileNamePath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def generateChecksumFromData(data):
    hash_md5 = hashlib.md5()
    hash_md5.update(data)
    return hash_md5.hexdigest()

def compareHashes(hashClient, hashServer):
    return hashClient.lower() == hashServer.lower()

# print(generateChecksumFromData(data))