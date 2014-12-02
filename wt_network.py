#Wheat and Tare
#Fake Network

import socket


class network:

    def sendData(self, _data):
        self.peerSocket.sendall(_data)

    def getData(self):
        #check if we already have a socket for receiving data.
        if(self.incomingSocket is None):
            _incomingSocket, peerAddress = self.serverSocket.accept()
            self.incomingSocket = _incomingSocket
        #get size of data we will receive.
        dataSize = int(self.incomingSocket.recv(4096))
        data = ""
        #loop until our data matches the size we should have.
        while(dataSize > len(data)):
            data += self.incomingSocket.recv(3000)
        return data

    def connect(self, _peerIp, _peerPort):
        #Throws error, calee is expected to catch this.
        self.peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peerSocket.connect((_peerIp, _peerPort))

    def __init__(self, _listenIP, _listenPort):
        self.incomingSocket = None
        self.peerSocket = None

        #create the default socket, which is TCP
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        listenIP = None
        if(_listenIP is None):
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
