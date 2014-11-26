#Wheat and Tare
#Fake Network

import socket


class fakeNetwork:

    def sendData(self, _data):
        self.peerSocket.sendall(_data)

    def getData(self):
        if(self.incomingSocket is None):
            _incomingSocket, peerAddress = self.serverSocket.accept()
            self.incomingSocket = _incomingSocket
        data = self.incomingSocket.recv(4096)
        return data

    def connect(self, _peerIp, _peerPort):
        try:
            self.peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.peerSocket.connect((_peerIp, _peerPort))
            return True
        except:
            return False

    def __init__(self, _listenIP, _listenPort):
        #create the default socket, which is TCP
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        listenIP = None
        if(_listenPort is None):
            #When this is used in bind, tell python to use any IP computer has.
            listenIP = ''
        else:
            listenIP = _listenIP

        listenPort = None
        if(_listenPort is None):
            listenPort = 10122
        else:
            listenPort = _listenPort

        self.peerPort = listenPort

        #tell the socket what IP and port to listen on
        self.serverSocket.bind((listenIP, listenPort))
        #listen for a single incoming connection.
        self.serverSocket.listen(1)
