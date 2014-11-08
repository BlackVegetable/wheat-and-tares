#CS5490/6490
#Final Project
#Fake Network


class fakeNetwork:

    def sendData(self, _data):
        self.receivedBuffer.append(_data)

    def getData(self):
        tmpBuffer = self.receivedBuffer
        self.receivedBuffer = []
        return tmpBuffer

    def connect(self, _peerIp, _peerPort):
        return True

    def __init__(self, _listenIP, _listenPort):
        self.host = _listenIP
        self.port = _listenPort
        self.receivedBuffer = []
