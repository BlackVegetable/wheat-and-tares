#CS5490/6490
#Final Project
#Core

#import sys
import threading
#import wt_utils


class wt_Exception:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class wtCore:

    def backgroundWorker(self):
        while(True):
            bits = []
            while(True):
                message = self.objNetwork.getData()
                message = message.split(',')
                bits.append(message[0])

    def getMessage(self):
        return self.messageList

    def __init__(self, myIP, myPort, peerIP, peerPort, fakeNetwork):
        self.myIP = myIP
        self.myPort = myPort
        self.peerIP = peerIP
        self.peerPort = peerPort

        #determine which network file to load
        if(fakeNetwork == 1):
            from wt_fakeNetwork import fakeNetwork as network
        else:
            from wt_network import network

        #create a network object to use.
        try:
            self.objNetwork = network(self.myIP, self.myPort)
        except Exception as e:
            raise wt_Exception(e)
            return None

        #initialize list of messages to be empty.
        self.messageList = []

        #Create background thread that is used to get data from network
        self.backgroundThread = threading.Thread(target=self.backgroundWorker)
        #make it so that when the main thread quits it stops the other threads.
        self.backgroundThread.daemon = True
        #start the background thread
        self.backgroundThread.start()
