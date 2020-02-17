import sqlite3
import socket
import json
import sys
import select




class message:
    #def __init__(self, username, messageText, seqNum):
    #    self.seq = seqNum
    #    self.user = username
    #    self.message = messageText
    def __init__(self, jsonStr):
        selfDict = json.loads(jsonStr)
        self.messageType = selfDict['messageType']
        
    def toJson(self):
        selfDict = {}
        selfDict['command'] = self.command
        selfDict['command'] = self.command
        return json.dumps(selfDict)
        
    def display(self):
        print(self.command)

#class operation:
#    def __init__(self, jsonStr):
#        selfDict = json.loads(jsonStr)
#        self.operation = selfDict['operation']
#        self.client = selfDict['client']

#returns an operation if the message is an operation, a message if its a message, or crashes if niether
def getPacketContents(theMessage):
    try:
        m = message(theMessage)
        return m
    except:
        print('Could not convert message')

def responseToMessage(theMessage):
    return ''
    

if __name__=="__main__":
    conn = sqlite3.connect('example.db')
    listenPortNumber = int(sys.argv[1])
    ownIP = socket.gethostbyname(socket.gethostname())
    clients = {}
    breakLoop = False
    seqNum = 0
    createConnectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    createConnectionSocket.bind((ownIP,listenPortNumber))
    createConnectionSocket.listen()
    readConnections = [createConnectionSocket]
    xconnections = []
    #Write messages is a dictionary from messages to their creators
    writeMessages = {}
    
    while not breakLoop:
        readyRead,readyWrite,xconnections = select.select(readConnections,clients.values(),[])
        for s in readyRead:
            
            if(s==createConnectionSocket):
                c,a = s.accept()
                readConnections.append(c)
            else:
                data = s.recv(2048).decode('utf-8')
                #print(data)
                i=0
                while True:
                    
                    try:
                        incomingMessage = getPacketContents(data[data.find('{'):data.find('}',i)+1])
                        if(isinstance(incomingMessage,operation)):
                            if(incomingMessage.operation == 'subscribe'):
                                clients[incomingMessage.client] = s
                            else:
                                del clients[incomingMessage.client]
                        else:
                            writeMessages[incomingMessage]=[incomingMessage.client]
                        break
                    except:
                        if len(data)==0:
                            break
#                       #This condition should deal with messages with } in them
#                        elif data.find('}',i)!=-1:
#                            i=data.find('}',i)+1
#                        
#                        else:
#                            stillReading, nothing,  nothing2 = select.select([s],[],[])
#                            if s in stillReading:
#                                data = data + s.recv(2048).decode('utf-8')
#                            elif(unfinishedMessage==""):
#                                unfinishedMessage = data
#                                break
#                            else:
#                                data = unfinishedMessage + data 
#                                unfinishedMessage = ""
                
        #s is a connection to a client ready to accept data, m is a connection to             
        for s in readyWrite:
            for m in writeMessages.keys():
                s.sendall(responseToMessage(m).toJson().encode('utf-8'))
#                if len(m)>0 and clients[writeMessages[m]]!=s:
#                    
#                    try:
#                        
#                    except:
#                        pass
        writeMessages = {}

