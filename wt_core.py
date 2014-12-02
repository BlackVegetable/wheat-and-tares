#Wheat and Tare
#Core

#import sys
import threading
import wt_utils
from Crypto.Random import random


class wt_Exception:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class wtCore:

    def backgroundWorker(self):
        fragBits = None
        #we always want to see if there is more data.
        while(True):
            #get whatever we have from network.
            data = self.objNetwork.getData()
            #check to make sure network did not receive close and returning bad data.
            if(data is not None):
                #use utility to give us dictionary with message and remaining bits.
                message = wt_utils.unpack_bits_to_message(data, self.authKey, fragBits, self.customHash)
                fragBits = message["frag_bits"]
                message = message["msg"]
                self.messageList.append(message)

    def sendMessage(self, message, fakeMessage=""):
        #This key is to get us started
        #get all the data to send.
        quartets = wt_utils.package_message_to_bits(message, self.outSequence, self.authKey, fakeMessage, self.fakeKey, self.customHash, self.entropyFile)
        #find how much to increment the sequence and then update sequence
        numberOfQuartets = len(quartets)
        self.outSequence += numberOfQuartets
        data = ""
        for quartet in quartets:
            data += quartet[0]
            data += quartet[1]
            data += quartet[2]
            data += quartet[3]

        #send how much data
        dataSize = len(data)
        self.objNetwork.sendData(str(dataSize))

        #Now send the data iteself
        self.objNetwork.sendData(data)

    def getMessages(self):
        tmpMessageList = self.messageList
        self.messageList = []
        return tmpMessageList

    def connect(self):
        try:
            self.objNetwork.connect(self.peerIP, self.peerPort)
            return True
        except:
            return False

    def __init__(self, peerIP, authKey, fakeNetwork, peerPort, myIP=None, myPort=None, fakeAuthKey=None, customHash=None, entropyFile=None):
        self.myIP = myIP
        self.myPort = myPort
        self.peerIP = peerIP
        self.peerPort = peerPort
        self.outSequence = random.randint(0, 100000)
        self.authKey = authKey
        self.fakeKey = fakeAuthKey
        self.customHash = customHash
        self.entropyFile = entropyFile

        #determine which network file to load
        if(fakeNetwork == 1):
            from wt_fakeNetwork import fakeNetwork as network
        else:
            from wt_network import network

        #create a network object to use.
        try:
            self.objNetwork = network(self.myIP, self.myPort)
        except:
            raise wt_Exception("Unable to bind to " + self.myIP + " on port " +self.myPort)
            return None

        #initialize list of messages to be empty.
        self.messageList = []

        #Create background thread that is used to get data from network
        self.backgroundThread = threading.Thread(target=self.backgroundWorker)
        #make it so that when the main thread quits it stops the other threads.
        self.backgroundThread.daemon = True
        #start the background thread
        self.backgroundThread.start()
