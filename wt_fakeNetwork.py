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

    def connect(self):
        return True

    def __init__(self, _host, _port):
        self.host = _host
        self.port = _port
        self.receivedBuffer = []
