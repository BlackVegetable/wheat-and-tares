#CS5490/6490
#Final Project
#Terminal Client

#imports
import sys
import os
import threading
import time
import getopt
from wt_core import wtCore

#Private variables
commandArgs = sys.argv[1:]
myIP = None
myPort = None
useFakeNetwork = 0


def usage():
    print("")
    print("usage: terminal.py -i <ipaddress> -p <port> [options]")
    print("-i, --ipAddress      Host machine IP Address, may also use 127.0.0.1")
    print("-p, --port           The port you use for incoming data")
    print("-f, --fakeNetwork    Use a fake network instead")
    print("-h, --help           Prints out proper usage of this program")
    sys.exit(2)

#make sure we have the required arguments
# if (len(commandArgs) < 3):
#     usage()

# #Setup some variabls
# myIP = commandArgs[1]
# myPort = commandArgs[2]
# useFakeNetwork = 0

# if (len(commandArgs) > 3) and (commandArgs[3] == "1"):
#     useFakeNetwork = 1

#use getOpt to neatly go through the command arguments passed into us.
try:
    opts, args = getopt.getopt(commandArgs, "i:p:fh", ["ipAddress", "port", "fakeNetwork", "help"])
except getopt.GetoptError:
    usage()
    sys.exit(2)

#Go through the command line arguments passed in and set appropriate variables
for opt, arg in opts:
    if opt in("-i", "--ipAddress"):
        myIP = arg
    elif opt in ("-p", "--port"):
        myPort = arg
    elif opt in ("-f", "--fakeNetwork"):
        useFakeNetwork = 1
    elif opt in ("-h", "--help"):
        usage()
        sys.exit(2)

#Check to make sure we have the required arguments.
if myIP is None:
    print("")
    print("You must provide the ip address for us to listen on")
    usage()

if myPort is None:
    print("")
    print("You must provide the port to listen on")
    usage()

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
                allMessages.append(myIP + ": " + message)

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

peerIP = raw_input("Enter the IP address of who you want to talk to: ")
peerPort = None
try:
    peerPort = int(raw_input("Enter the port that your peer is using: "))
except Exception as e:
    print("Port must be a number")

#initialize our core, if error is returned print the error and then exit.
try:
    core = wtCore(myIP, myPort, peerIP, peerPort, useFakeNetwork)
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
