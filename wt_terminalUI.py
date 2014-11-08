#CS5490/6490
#Final Project
#Terminal Client

#imports
import sys
import os
import threading
import time

#Private variables
commandArgs = sys.argv
host = None


def usage():
    print("You did not provide all the necessary arguments")
    print("Correct usage of this software:")
    print("terminal.py <HostIP> <hostPort> [useFakeNetwork]")
    sys.exit(2)

#make sure we have the required arguments
if (len(commandArgs) < 3):
    usage()

#If the third argument passed in is 1, then use the fake network object.
if (len(commandArgs) > 3):
    if (commandArgs[3] == "1"):
        from fakeNetwork import fakeNetwork as network
else:
    from network import network

#Setup some variabls
host = commandArgs[1]
port = commandArgs[2]
allMessages = []

#Create an object that we use to send and receive data
objNetwork = network(commandArgs[1], commandArgs[2])

lock = threading.Lock()


#Call to get data from the networking object, then print data to the screen.
def backgroundWorker():
    while True:
        newMessages = objNetwork.getData()
        if (len(newMessages) > 0):
            for message in newMessages:
                allMessages.append(host + ": " + message)

            with lock:
                os.system('cls' if os.name == 'nt' else 'clear')
                for message in allMessages:
                    print(message)

                #We cleared the prompt, notify user to press enter.
                print("Press enter to start typing your message")

        #sleep so that we don't use all of the processor
        time.sleep(1)

#clear the screen
os.system('cls' if os.name == 'nt' else 'clear')

#print the welcom message
print("Welcome to the simple chat program that uses ")

#Try to connect to peer, and loop until we do.
while not objNetwork.connect():
    print("Unable to connect to " + host + " on port " + port)
    print("Will try again in 10 seconds")
    time.sleep(10)

#Give user status update
print("We are connected to " + host + " on port " + port)

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
        objNetwork.sendData(userMessage)
