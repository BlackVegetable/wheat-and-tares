#Terminal Client

#imports
import sys
import os
import threading
import time
import getopt
from wt_core import wtCore

#Private variables
version = 1.0
commandArgs = sys.argv[1:]
myIP = None
peerIP = None
myPort = 10122
peerPort = 10122
useFakeNetwork = 0
authKey = None
fakeAuthKey = None
alternateHash = None
entropyFile = None


def usage():
    print("")
    print("usage: wt_terminal.py [options]")
    print("")
    print("Options:")
    print("--alternateHash     [path]      Specify a file with your custom hash method.")
    print("--entropyFile       [path]      Not yet implemented")
    print("-f, --fakeNetwork                Use a fake network instead")
    print("--fakeKeyFile      [path]      File that contains fake keys you want to use.")
    print("-h, --help                       Prints out proper usage of this program")
    print("--key-file           [path]      File that contains your authentication keys")
    print("-p, --port           [port]      Custom port you and peer will listen on")
    print("--version                        Prints the version")

#use getOpt to neatly go through the command arguments passed into us.
shortArgs = "fhp:"
longArgs = ["fakeNetwork", "help", "port=", "alternateHash=", "entropyFile=", "fakeKeyFile=", "keyFile=","version"]

try:
    opts, args = getopt.getopt(commandArgs, shortArgs, longArgs)
except getopt.GetoptError:
    usage()
    sys.exit(2)

#Go through the command line arguments passed in and set appropriate variables
for opt, arg in opts:
    if opt in ("-p", "--port"):
        try:
            myPort = int(arg)
        except:
            print("Port must be a number")
            sys.exit(2)
    elif opt in ("-f", "--fakeNetwork"):
        useFakeNetwork = 1
    elif opt in ("-h", "--help"):
        usage()
        sys.exit(0)
    elif opt == "--alternateHash":
        print("Alternate hash is not implemented yet.")
        sys.exit(0)
    elif opt == "--entropyFile":
        print("Entropy file functionality is not implemented yet.")
        sys.exit(0)
    elif opt == "--fakeKeyFile":
        print("Fake key file functionality is not implemented yet.")
        sys.exit(0)
    elif opt == "--keyFile":
        print("Key file functionality is not implemented yet.")
        sys.exit(0)
    elif opt == "--version":
        print(version)
        sys.exit(0)

#Declare the core vairable
core = None
allMessages = []

#Create an object that we use to send and receive data
# objNetwork = network(commandArgs[1], commandArgs[2])

lock = threading.Lock()


#Call to get data from the networking object, then print data to the screen.
def backgroundWorker():
    while True:
        newMessages = core.getMessages()
        if (len(newMessages) > 0):
            for message in newMessages:
                allMessages.append("Peer: " + message)

            with lock:
                os.system('cls' if os.name == 'nt' else 'clear')
                for message in allMessages:
                    print(message)

                print("")
                #We cleared the prompt, notify user to press enter.
                print("Press enter to start typing your message")

        #sleep so that we don't use all of the processor
        time.sleep(1)

#clear the screen
os.system('cls' if os.name == 'nt' else 'clear')

#print the welcom message
print("Welcome to the simple chat program that is Wheat and Tare")

#Get IP peer will be on.
peerIP = raw_input("Enter the IP address of who you want to talk to: ")

#USing default port for now.
# try:
#     peerPort = int(raw_input("Enter the port that your peer is using: "))
# except Exception as e:
#     print("Port must be a number")

#initialize our core, if error is returned print the error and then exit.
try:
    authKey = "12345678901234567890123456789012"
    core = wtCore(peerIP, authKey, useFakeNetwork, peerPort, myIP, myPort, fakeAuthKey, alternateHash, entropyFile)
except Exception as e:
    print(e)
    sys.exit(2)

#Try to connect to peer, and loop until we do.
while not core.connect():
    print("Unable to connect to " + myIP + " on port " + myPort)
    print("Will try again in 10 seconds")
    time.sleep(10)

#Give user status update
print("We are connected to " + peerIP + " on port " + str(peerPort))

#Create a background thread that is used to get data from networking object
backgroundThread = threading.Thread(target=backgroundWorker)
#make it so that when the main thread quits it stops the other threads.
backgroundThread.daemon = True

#start the background thread
backgroundThread.start()

#Give user status update
print("You can now type anything you want to send")

while (True):
    raw_input("Press enter to start typing your message")
    with lock:
        userMessage = raw_input("Type your message: ")
        allMessages.append("You: " + userMessage)
        core.sendMessage(userMessage)
