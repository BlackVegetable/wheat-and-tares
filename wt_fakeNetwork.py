#CS5490/6490
#Final Project
#Fake Network


class fakeNetwork:

    def sendData(self, _data):
        #print("sent:" + _data)
        self.receivedBuffer.append(_data)

    def getData(self):
        message = None
        if (len(self.receivedBuffer) > 0):
            message = self.receivedBuffer.pop()

        return message

    def connect(self, _peerIp, _peerPort):
        return True

    def __init__(self, _listenIP, _listenPort):
        self.host = _listenIP
        self.port = _listenPort
        self.receivedBuffer = []
