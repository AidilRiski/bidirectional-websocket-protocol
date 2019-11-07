import base64
import hashlib
import threading

class WebConnection(threading.Thread):

    def __init__(self, connection, sourceAddress):
        threading.Thread.__init__(self)
        self._connection = connection
        self._sourceAddress = sourceAddress

    def run(self):        
        data = self._connection.recv(2**32 - 1)
        handshakeRequest = self.parseHandshake(data)
        if handshakeRequest is None:
            self._connection.send(bytes(self.getDenyHandshakeResponse(), 'utf-8'))
            return
        
        self._connection.send(bytes(self.getHandshakeResponse(handshakeRequest), 'utf-8'))

        while True:
            data = self.parseFrame(self._connection.recv(2**32 - 1))
            if not data:
                break
            data['payload'] = self.unmaskPayload(data['mask'], data['payload'])
            print(data)

    def parseHandshake(self, data):
        data = data.decode('utf-8')
        httpHandshake = data.split('\r\n')
        if 'Connection: Upgrade' in httpHandshake and 'Upgrade: websocket' in httpHandshake:
            httpHandshake = httpHandshake[1:]
            headers = {}
            for headerString in httpHandshake:
                if headerString == '' or headerString == ' ':
                    continue
                header, value = headerString.split(' ', 1)
                header = header[:len(header) - 1]
                headers[header] = value
            return headers
        return None
    
    def getHandshakeResponse(self, headers):
        httpResponse =  'HTTP/1.1 101 Switching Protocol\r\n' + \
                        'Upgrade: websocket\r\n' + \
                        'Connection: Upgrade\r\n' + \
                        'Sec-WebSocket-Accept: %s\r\n\r\n' %((self.generateResponseKey(headers['Sec-WebSocket-Key'])).decode())
        
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
        key = key.encode()
        return base64.b64encode(hashlib.sha1(key).digest())
    
    def unmaskPayload(self, mask, payload):
        decodedPayload = bytearray()
        print('Mask ', mask)

        i = 0
        for byte in payload:
            maskkk = (mask >> ((3 - i) * 8)) & 0xff
            decodedPayload.append(byte ^ maskkk)
            i += 1
            if (i >= 4):
                i = 0
            
        return decodedPayload
    
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
                mask = (mask << 8) + int(data[bytePointer])
                bytePointer += 1

        payload = data[bytePointer:len(data)]

        return {
            'fin': fin,
            'opCode': opCode,
            'useMask': useMask,
            'length': length,
            'mask': mask,
            'payload': payload,
        }

    def buildFrame(self, frameDict):
        payloadData = bytearray(0)
        payloadData.append(frameDict['fin'])
        payloadData.append(frameDict['opCode'])
        payloadData.append(frameDict['useMask'])
        
        if frameDict['length'] < 126:
            payloadData.append(frameDict['length'])
        elif frameDict['length'] < 65536:
            payloadData.append(bytes(126))
            payloadData.append(frameDict['length'].to_bytes(2, 'little'))
        else:
            payloadData.append(bytes(127))
            payloadData.append(frameDict['length'].to_bytes(8, 'little'))

        payloadData.append(frameDict['payload'])
        return payloadData
        


