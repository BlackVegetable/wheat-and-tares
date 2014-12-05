#Wheat and Tare
#Terminal Client

#imports
import sys
import os
import signal
import threading
import time
import getopt
import socket
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
useFakeMessage = False
fakeAuthKey = None
alternateHash = None
entropyFile = None
core = None
backgroundThread = None
promptThread = None


def usage():
    print("")
    print("usage: wt_terminal.py [options]")
    print("")
    print("Options:")
    print("--alternateHash      [path]      Specify a file with your custom hash method.")
    print("--entropyFile        [path]      Not yet implemented")
    print("-f, --fakeNetwork                Use a fake network instead")
    print("--fakeKeyFile        [path]      File that contains fake keys you want to use.")
    print("-h, --help                       Prints out proper usage of this program")
    print("--key-file           [path]      File that contains your authentication keys")
    print("-p, --port           [port]      Custom port you and peer will listen on")
    print("--version                        Prints the version")


def updateMessages():
    os.system('cls' if os.name == 'nt' else 'clear')
    for message in allMessages:
        print(message)

    print("")
    #We cleared the prompt, notify user to press enter.
    print("Press enter to start typing your message or quitWT to exit program")


#Call to get data from the networking object, then print data to the screen.
def backgroundWorker(arg, stopEvent):
    try:
        while not stopEvent.is_set():
            if core.backgroundThreadAlive():
                newMessages = core.getMessages()
                if (len(newMessages) > 0):
                    for message in newMessages:
                        allMessages.append("Peer: " + message)

                    with lock:
                        updateMessages()

                #sleep so that we don't use all of the processor
                time.sleep(1)
            else:
                stopEvent.set()
        print("Stopping interface background thread")
    except:
        stopEvent.set()


def promptWorker(arg, stopEvent):
    while(not stopEvent.is_set()):
        if backgroundThread.is_alive() and core.backgroundThreadAlive():
            if(raw_input() == "quitWT"):
                stopEvent.set()
            else:
                with lock:
                    userMessage = raw_input("Type your message: ")
                    fakeMessage = ""
                    if(useFakeMessage):
                        loop = True
                        while (loop):
                            fakeMessage = raw_input("type your fake message")
                            if(len(userMessage) == len(fakeMessage)):
                                loop = False
                    try:
                        core.sendMessage(userMessage, fakeMessage)
                        allMessages.append("You: " + userMessage)
                        updateMessages()
                    except Exception as e:
                        print(e)
                        stopThread.set()
        else:
            print("Background threads have stopped, exiting program")
    print("Exiting Program")


#event handler for when ctrl+C is pushed
def safeCleanup():
    print("Exiting Program")
    stopThread.set()
    #Need to clean up all code.
    if core is not None:
        core.stop()
    if backgroundThread is not None:
        backgroundThread.join()
    if promptThread is not None:
        promptThread.join(1)
        sys.exit(0)


#event handler for when ctrl+C is pushed
def ctrlCHandler(signal, frame):
    print("You pressed CTRL+C, program now closing")
    stopThread.set()
    #Need to clean up all code.
    if core is not None:
        core.stop()
    if backgroundThread is not None:
        backgroundThread.join()
    if promptThread is not None:
        promptThread.join(1)
    sys.exit(0)


#Tell python to call our ctrlC hander method
signal.signal(signal.SIGINT, ctrlCHandler)

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
            print("")
            print("Port must be a number")
            usage()
            sys.exit(2)
    elif opt in ("-f", "--fakeNetwork"):
        useFakeNetwork = 1
    elif opt in ("-h", "--help"):
        usage()
        sys.exit(0)
    elif opt == "--alternateHash":
        try:
            customHash = __import__(arg)    #this is cool, allows you to import using string value.
            alternateHash = customHash.custom_hash_func
        except Exception as e:
            print("")
            print(e)
            usage()
            sys.exit(2)
    elif opt == "--entropyFile":
        try:
            tmp = open(arg, "r")
        except Exception as e:
            print(e)
            sys.exit(2)
        #If we are here, then no error with path.
        entropyFile = arg
    elif opt == "--fakeKeyFile":
        try:
            keyFile = open(arg, "r")
            fakeAuthKey = keyFile.read()
            keyFile.close()
            useFakeMessage = True
        except Exception as e:
            print("")
            print("Error opening fake key File")
            sys.exit(0)
    elif opt == "--keyFile":
        try:
            keyFile = open(arg, "r")
            authKey = keyFile.read()
            keyFile.close()
        except Exception as e:
            print("")
            print("Error opening key File")
            sys.exit(0)
    elif opt == "--version":
        print(version)
        sys.exit(0)

#make sure we have a authKey before continuing.
if (authKey is None):
    print("No key, or invalid key, provided.")
    usage()
    sys.exit(2)

#Declare a variable to hold all messages.
allMessages = []

#Create event that we can call, which will set the flag that background worker checks
stopThread = threading.Event()

#create a lock for control.
lock = threading.Lock()

#clear the screen
os.system('cls' if os.name == 'nt' else 'clear')

#print the welcom message
print("Welcome to the simple chat program that is Wheat and Tare")

#Show user a reachable IP.
print("")
print("This is your reachable IP Address:" + socket.gethostbyname(socket.gethostname()))

#Get IP peer will be on.
print("")
peerIP = raw_input("Enter the IP address of your peer: ")

#initialize our core, if error is returned print the error and then exit.
try:
    #authKey = "12345678901234567890123456789012"
    core = wtCore(peerIP, authKey, useFakeNetwork, peerPort, myIP, myPort, fakeAuthKey, alternateHash, entropyFile)
except Exception as e:
    print(e)
    sys.exit(2)

#Try to connect to peer, and loop until we do.
while not core.connect():
    print("Unable to connect to " + peerIP)
    print("Will try again in 5 seconds")
    time.sleep(5)

#Give user status update
print("You are connected to " + peerIP + " on port " + str(peerPort))

try:
    #Create a background thread that is used to get data from networking object
    backgroundThread = threading.Thread(name="UI_Background", target=backgroundWorker, args=(1, stopThread))
    #make it so that when the main thread quits it stops the other threads.
    backgroundThread.daemon = True
    #start the background thread
    backgroundThread.start()
except Exception as e:
    print(e)
    sys.exit(2)

#Give user status update
print("You can now type anything you want to send")
print("Press enter to start typing your message")

promptThread = threading.Thread(name="interfacePromptThread", target=promptWorker, args=(1, stopThread))
promptThread.daemon = True
promptThread.start()

while(True):
    if (not backgroundThread.is_alive()) or (not promptThread.is_alive()) or (not core.backgroundThreadAlive()):
        safeCleanup()
        time.sleep(0.2)
