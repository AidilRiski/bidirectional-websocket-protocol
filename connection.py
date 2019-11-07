import threading

class WebConnection(threading.Thread):

    def __init__(self, connection, sourceAddress):
        threading.Thread.__init__(self)
        self._connection = connection
        self._sourceAddress = sourceAddress

    def run(self):        
        data = self._connection.recv(2**32 - 1)
        handshakeRequest = self.parseHandshake(data)
        print(handshakeRequest)
        if handshakeRequest is None:
            self._connection.send(self.getDenyHandshakeResponse())
            return
        
        self._connection.send(self.getHandshakeResponse(handshakeRequest))

        while True:
            data = _connection.recv(2**32 - 1)
            if not data:
                break

    def parseHandshake(self, data):
        data = str(data)
        httpHandshake = data.split('\r\n')
        if 'Connection: Upgrade' in httpHandshake and 'Upgrade: Websocket' in httpHandshake:
            httpHandshake = httpHandshake[1:]
            headers = {}
            for headerString in httpHandshake:
                header, value = headerString.split(' ')
                header[:len(header) - 1]
                headers[header] = value
            
            return headers
        return None
    
    def getHandshakeResponse(self, headers):
        httpResponse =  'HTTP/1.1 101 Switching Protocol\r\n' + \
                        'Upgrade: websocket\r\n' + \
                        'Connection: Upgrade\r\n' + \
                        'Sec-WebSocket-Accept: %s\r\n\r\n' %(self.generateResponseKey(headers['Sec-WebSocket-Key']))
        
        return httpResponse
    
    def getDenyHandshakeResponse(self):
        httpResponse =  'HTTP/1.1 400 Bad Request\r\n' + \
                        'Content-Type: text/plain\r\n' + \
                        'Connection: close\r\n\r\n' + \
                        'Incorrect request'
        
        return httpResponse
                            
    
    def generateResponseKey(self, key):
        WS_MAGIC_KEY = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        key += WS_MAGIC_KEY
        return base64.standard_b64encode(hashlib.sha1(key).digest())
    
    def parseFrame(self, data):
        bytePointer = 0

        fin = data[bytePointer] >> 7
        opCode = data[bytePointer] & 15
        bytePointer += 1

        useMask = data[bytePointer] >> 7
        length = int(data[bytePointer] & 127)
        bytePointer += 1

        if length == 126:
            length = int(data[bytePointer]) << 8
            bytePointer += 1
            length += int(data[bytePointer])
            bytePointer += 1
        elif length == 127:
            for i in range(0, 8):
                if i == 7:
                    length = int(data[bytePointer])
                else:
                    length = length << 8 + int(data[bytePointer])
                bytePointer += 1
        
        mask = 0
        if useMask:
            for i in range(0, 4):
                if i == 3:
                    mask = int(data[bytePointer])
                else:
                    mask = mask << 8 + int(data[bytePointer])
                bytePointer += 1

        payload = data[bytePointer:len(data) - 1]

        return {
            'fin': fin,
            'opCode': opCode,
            'useMask': useMask,
            'length': length,
            'mask': mask,
            'payload': payload,
        }
    

