# Client Side for connecting to local server for chatroom
# Clients have a unique uuid which is communicated to the server to identify themself
# one thread for constantly receiving another for sending

# Packet form :  [uuid] + | + [command] + | + [extra args]

import uuid
import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 9999

def recvThread(socket):
    while True:
        print(socket.recv(1024).decode("utf-8"))

def sendThread(socket):
    while True:
        rawInput = input().replace(" ", "|")
        
    

def Connect():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    clientSocket.connect((HOST, PORT))
    clientSocket.setblocking(1)
    
    senThread = threading.Thread(target=sendThread, args=(clientSocket,))
    senThread.daemon = False
    senThread.start()

    recThread = threading.Thread(target=recvThread, args=(clientSocket,))
    recThread.daemon = False 
    recThread.start()

if __name__ == "__main__":
    Connect()