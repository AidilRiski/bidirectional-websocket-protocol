import threading

class WebConnection(threading.Thread):

    def __init__(self, connection, sourceAddress):
        self._connection = connection
        self._sourceAddress = sourceAddress

    def run(self):
        while True:
            data = _connection.recv(1024)
            if not data:
                break
    
    def handleData(self, data):
        fin = data[0] >> 7
        opCode = data[0] & 15
        mask = data[1] >> 7
        length = int(data[1] & 127)
        
        return {
            'fin': fin,
            'opCode': opCode,
            'mask': mask,
            'length': length,
        }
    

