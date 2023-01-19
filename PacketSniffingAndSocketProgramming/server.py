# Server that runs a chatroom in the background
# By Joseph Fabrello - <Insert Finish Date Here>
# List of features:
#   - Login and logout 
#   - Blocking of users when failing logins
#   - multi user
#   - Online Prescence
#   - When was an individual Last on
#   - broadcasting
#   - Direct Messaging
#   - Blocking Messages

import threading
import socket
import time
import uuid
import datetime

HOST = "127.0.0.1"
PORT = 9999

blockAmount = 3
blockTime = 60
currUsers = {}
offlineUsers = {}
clientConnections = {}
blockedIndividuals = {}

def login(socket):
    attempts = 0
    while True:
        socket.sendall(f"Please enter: <username> <password>\n")
        data = socket.recv(1024).split("|")
        if (attempts < blockAmount):
            with open("users.txt", "r") as f:
                while f != None:
                    cred = f.readline().split()
                    if cred[0] == data[1] and cred[1] == data[2]:
                        socket.sendall(f"Successfully logged in as {cred[0]}")
                        currUsers.update(data[0], cred[0])
                        clientConnections.update(cred[0], socket)
                        offlineUsers.pop(cred[0])
                        return True
                    
            attempts += 1
            socket.sendall(f"Failed to login as user {data[1]}, Please try again: login <username> <password>.\n You have {blockAmount - attempts} attempts left before being blocked\n")
            
        else:
            socket.sendall(f"You have been blocked for {blockTime} seconds, the server will not respond to you\n")
            time.sleep(blockTime)
            # flush socket out
            while True:
                if socket.recv(8196) == None:
                    break
        
def logout(socket, uuid):
    offlineUsers.update(currUsers[uuid], datetime.datetime.now())
    clientConnections.pop(currUsers[uuid])
    currUsers.pop(uuid)
    socket.close()

def register(socket):
    while True:
        socket.sendall(f"Please enter new credentials: <username> <password>\n")
        data = socket.recv(1024).split("|")
        socket.sendall(f"Please enter password again:")
        verify = socket.recv(1024).split("|")

        if data[2] == verify[1]:
            with open("user.txt", "a") as f:
                f.write(f"{data[1]} {data[2]}\n")

            socket.sendall(f"Registration Successful, welcome: {data[1]}")
            return True

        else:
            socket.sendall(f"Password was not verified please try again\n")


def currentlyOnline(socket, uuid):
    for userShowname in currUsers.values:
        if (currUsers[uuid] == userShowname):
            msg = f"Me - ({userShowname})\n"
        else:
            msg = f"{userShowname}\n"
        
        socket.sendall(msg)


def lastOn(socket, targetName):
    try:
        time = offlineUsers(targetName)
        socket.send(f"User {targetName} was last online {time}\n")
    except:
        if targetName in currUsers.values():
            socket.send(f"User {targetName} is currently online\n")
        else:
            socket.send(f"User {targetName} was last online ""unavailable""\n")

def broadcast(msg, fromUUID):
    showName = currUsers[fromUUID]
    for s in clientConnections.values():
        clientUUID = {i for i in clientConnections if clientConnections[i] == s}
        if (clientUUID, s) in blockedIndividuals.items() or clientConnections[fromUUID] == s:
            continue

        s.sendall(f"{showName}: {msg}\n")

def dm(msg, fromUUID, toName):
    toUUID = {i for i in currUsers if currUsers[i] == toName}
    fromName = currUsers[fromUUID]
    if (toUUID, clientConnections[fromUUID]) not in blockedIndividuals.items():
        clientConnections[toUUID].sendall(f"{fromName}: {msg}\n")

def blockUser(blockerUUID, blockeeName):
    blockeeUUID = {i for i in currUsers if currUsers[i] == blockeeName}
    blockedIndividuals.update(blockerUUID, clientConnections[blockeeUUID])

def handleStandardCommands(socket):

    while True:
        socket.sendall("Waiting for Command, type help for details >>")
        msg = socket.recv(1024).split("|")

        if msg[1] == "whoelse":
            if len(msg) == 2:
                currentlyOnline(socket, msg[0])
            else:
                socket.sendall("Incorrect Arguments provided: <whoelse>\n")
        elif msg[1] == "laston":
            if len(msg) == 3:
                lastOn(socket,msg[2])
            else:
                socket.sendall("Incorrect Arguments provided: <laston> <targetname>\n")
        elif msg[1] == "broadcast":
            if len(msg) == 3:
                broadcast(msg[2], msg[0])
            else:
                socket.sendall("Incorrect Arguments provided: <broadcast> <message>\n")
        elif msg[1] == "dm":
            if len(msg) == 4:
                dm(msg[3], msg[0], msg[2])
            else:
                socket.sendall("Incorrect Arguments provided: <dm> <msg> <Person>\n")
        elif msg[1] == "block":
            if len(msg) == 3:
                blockUser(msg[0],msg[2])
            else:
                socket.sendall("Incorrect Arguments provided : <block> <Person>\n")
        elif msg[1] == "logout":
            if len(msg) == 2:
                logout(socket)
                break
            else:
                socket.sendall("No Arguments required for logout\n")
    




def HandleConnection(socket, addr):

    while True:
        socket.sendall(("Please Either use login or register").encode("utf-8"))
        time.sleep(1)
        splitD = socket.recv(1024).decode("utf-8").split("|")

        if splitD[1] == "login":
            attempt = login(socket)
        elif splitD[1] == "register":
            attempt = register(socket)

        if attempt == True:
            break

    handleStandardCommands(socket)



def FindConnections():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(3)
    print(f"Now Listening for Connections")
    while True: 
        connectionSocket, address = s.accept()
        print(f"Received Connection from {address}")
        thread = threading.Thread(target=HandleConnection, args=(connectionSocket, address))
        thread.daemon = True 
        thread.start()




if __name__ == "__main__":
    FindConnections()