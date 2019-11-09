import base64
import hashlib
import threading
from constants import *
from utils import *

class WebConnection(threading.Thread):
    # Array of frames
    data_array = []

    def __init__(self, connection, sourceAddress):
        threading.Thread.__init__(self)
        self._connection = connection
        self._sourceAddress = sourceAddress

    def run(self):        
        data = self._connection.recv(FRAME_SIZE)
        handshakeRequest = self.parseHandshake(data)
        if handshakeRequest is None:
            self._connection.send(bytes(self.getDenyHandshakeResponse(), 'utf-8'))
            return
        
        self._connection.send(bytes(self.getHandshakeResponse(handshakeRequest), 'utf-8'))

        while True:
            data = self.parseFrame(self._connection.recv(FRAME_SIZE))
            if not data:
                break
            data['payload'] = self.unmaskPayload(data['mask'], data['payload'])
            # Handle multiple frames.
            self.data_array.append(data)
            print('Received', data)
            if (data['opCode'] == PING):
                # Send PONG Frame
                self._connection.send(buildFrame(createPONGFrame(data)))
            elif (data['opCode'] == CLOSE):
                # Stop the connection
                self._connection.send(self.buildFrame(self.createCloseFrame(data)))
                self._connection.close()
                break
            else:
                self.handleRequest(data)

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

        # Bit-0: FIN
        fin = data[bytePointer] >> 7
        # Bit-1 until Bit-3: EMPTY
        # Bit-4 until Bit-7: OPCODE
        opCode = int(data[bytePointer] & 15)

        bytePointer += 1
        # Bit-8: MASK
        useMask = data[bytePointer] >> 7
        # Bit-9 until Bit-15: LENGTH
        length = int(data[bytePointer] & 127)
        
        bytePointer += 1

        if length == 126:
            #Bit-16 until Bit-23: EXTENDED LENGTH
            length = int(data[bytePointer]) << 8

            bytePointer += 1

            #Bit-24 until Bit-31: EXTENDED LENGTH
            length += int(data[bytePointer])

            bytePointer += 1
        #EVEN MORE EXTENDED LENGTH
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
            'payload': payload
        }

    def buildFrame(self, frameDict):
        payloadData = bytearray()

        finOpcodeByte = frameDict['fin'] << 7 | (frameDict['opCode'] & 0x0f)
        payloadData.append(finOpcodeByte)
        
        if frameDict['length'] < 126:
            maskLengthByte = frameDict['useMask'] << 7 | (frameDict['length'] & 0x7f)
            payloadData.append(maskLengthByte)
        elif frameDict['length'] < 65536:
            maskLengthByte = frameDict['useMask'] << 7 | (126 & 0x7f)
            payloadData.append(maskLengthByte)
            payloadData.extend(frameDict['length'].to_bytes(2, 'big'))
        else:
            maskLengthByte = frameDict['useMask'] << 7 | (127 & 0x7f)
            payloadData.append(maskLengthByte)
            payloadData.extend(frameDict['length'].to_bytes(8, 'big'))
    
        payloadData.extend(frameDict['payload'])
        return payloadData

    def combineData(self):
        combinedPayload = bytearray()
        for data in self.data_array:
            combinedPayload.append(data['payload'])
        return combinedPayload
    
    # These are control frame functions:
    # All control frames MUST have a payload length of 125 bytes or less and MUST NOT be fragmented
    def createPONGFrame(self, frameDict):
        # Send PONG
        pongFrameDict = frameDict
        pongFrameDict['opCode'] = PONG
        pongFrameDict['fin'] = 1
        pongFrameDict['useMask'] = 0
        pongFrameDict['mask'] = 0
        return pongFrameDict

    def createCloseFrame(self, frameDict):
        closeFrameDict = frameDict
        closeFrameDict['fin'] = 1
        closeFrameDict['useMask'] = 0
        closeFrameDict['mask'] = 0
        return closeFrameDict
    
    def isEchoRequest(self, payload):
        return payload[0] == 0x21 and payload[1] == 0x65 and payload[2] == 0x63 and payload[3] == 0x68 and payload[4] == 0x6f and payload[5] == 0x20 

    def isSubmissionRequest(self, payload):
        return payload[0] == 0x21 and payload[1] == 0x73 and payload[2] == 0x75 and payload[3] == 0x62 and payload[4] == 0x6d and payload[5] == 0x69 and payload[6] == 0x73 and payload[7] == 0x73 and payload[8] == 0x69 and payload[9] == 0x6f and payload[10] == 0x6e
    
    def isCheckRequest(self, payload):
        return payload[0] == 0x21 and payload[1] == 0x63 and payload[2] == 0x68 and payload[3] == 0x65 and payload[4] == 0x63 and payload[5] == 0x6b
 
    def handleRequest(self, data):
        
        if (self.isEchoRequest(data['payload'])):

            print('Respoding with frame', self.createEchoResponse(data))
            self._connection.send(self.buildFrame(self.createEchoResponse(data)))

        elif (self.isSubmissionRequest(data['payload'])):

            zipCurrentFiles()
            print('Respoding with frame', self.createSubmissionResponse())
            self._connection.send(self.buildFrame(self.createSubmissionResponse()))

        elif (self.isCheckRequest(data['payload'])):

            print('Respoding with frame', self.createCheckResponse(data))
            self._connection.send(self.buildFrame(self.createCheckResponse(data)))
    
    def createEchoResponse(self, data):
        
        bytePointer = 6
        payload = bytearray()
        for i in range(0, data['length'] - 6):
            payload.append(data['payload'][bytePointer])
            bytePointer += 1

        return {
            'fin': 1,
            'opCode': 1,
            'useMask': 0,
            'length': data['length'] - 6,
            'mask': 0,
            'payload': payload
        }
    
    def createSubmissionResponse(self):

        payload = bytearray()
        currentDirectory = os.getcwd()
        fileNamePath = currentDirectory + '/' + FILE_NAME + '.zip'
        with open(fileNamePath, 'rb') as binary_file:
            while True:
                byte = binary_file.read(1)
                if byte == b"":
                    break
                payload.extend(byte)
        
        # print(payload)
        return {
            'fin': 1,
            'opCode': 2,
            'useMask': 0,
            'length': os.path.getsize(fileNamePath),
            'mask': 0,
            'payload': payload
        }

    def createCheckResponse(self, data):

        bytePointer = 7

        payload = bytearray()
        hashPayload = ''

        for i in range(0, data['length'] - 7):
            hashPayload += str(chr(data['payload'][bytePointer]))
            bytePointer += 1
        
        print(hashPayload)
        if (compareHashes(hashPayload, generateChecksum())):
            payload.extend('1'.encode('utf-8'))
        else:
            payload.extend('0'.encode('utf-8'))

        return {
            'fin': 1,
            'opCode': 1,
            'useMask': 0,
            'length': 1,
            'mask': 0,
            'payload': payload
        }
