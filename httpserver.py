import http
import socket
import select
import sqlite3
import http.server

#Helper functions
def removeNonAlphanumeric(string):
    return ''.join([k for k in string if k.isalnum()])

def initializeDatabase():
    connection = sqlite3.connect("socialite.db")
    cursor = connection.cursor()
    
    sql_command = """
CREATE TABLE user_table (  
username VARCHAR(20), 
password VARCHAR(30),
age INTEGER,
bio VARCHAR(3000),
clientConnection VARCHAR(40),
UNIQUE(username)
);"""
    cursor.execute(sql_command)
    sql_command = """
CREATE TABLE message_table (  
user1 VARCHAR(20), 
user2 VARCHAR(30),
messageText VARCHAR(3000),
UNIQUE(user1,user2));"""
    cursor.execute(sql_command)
    connection.commit()

#Database commands
def addConnectionToClient(clientUserName, connectionStr):
    #print(connectionStr)
    command = '''UPDATE user_table
SET clientConnection = '{}'
WHERE username = '{}' '''.format(connectionStr,clientUserName)
    cursor.execute(command)
    connection.commit()

def getLoginInfo(username,password):
    command = '''SELECT * FROM user_table
WHERE username='{}' AND password = '{}' ;'''.format(username,password)
    cursor.execute(command)
    return cursor.fetchone()

def getSignupInfo(username,password):
    command = '''SELECT * FROM user_table
WHERE username='{}' '''.format(username)
    cursor.execute(command)
    commandReturn = cursor.fetchone()
    if commandReturn == '' or commandReturn == None:
        command = ''' INSERT INTO user_table (username, password)
VALUES ('{}', '{}') '''.format(username,password)
        cursor.execute(command)
        connection.commit()
    command = '''SELECT * FROM user_table WHERE username='{}' AND password = '{}';'''.format(username,password)
    cursor.execute(command)
    commandReturn = cursor.fetchone()
    #cursor.execute('''SELECT * FROM user_table''')
    return commandReturn

def sendMessage(message, toUser,fromUser):
    message = 'FROM:{}:{}'.format(fromUser,message)
    firstAlphabetical,secondAlphabetical = (toUser,fromUser) if toUser < fromUser else (fromUser,toUser)
    command = '''UPDATE message_table SET messageText=messageText || '{}' WHERE user1 = '{}'
                   AND user2 = '{}' '''.format(message,firstAlphabetical,secondAlphabetical)
    
    cursor.execute(command)
    connection.commit()
    #command = '''
   #IF NOT EXISTS (SELECT * FROM message_table 
   #                WHERE user1 = '{}'
   #                AND user2 = '{}' )
   #BEGIN
   #    INSERT INTO messages_table(user1, user2, messageText)
   #    VALUES ('{}','{}','{}')
   #END
#'''.format(firstAlphabetical,secondAlphabetical,firstAlphabetical,secondAlphabetical,message)
    #command = '''INSERT INTO message_table(user1,user2,messageText)
#SELECT '{}','{}','{}' 
#WHERE NOT EXISTS(SELECT 1 FROM message_table WHERE user1 = '{}' AND user2 = '{}');'''.format(user1,user2,message,user1,user2)
    command = '''INSERT OR IGNORE INTO message_table(user1, user2,messageText) VALUES('{}','{}','{}')'''.format(firstAlphabetical,secondAlphabetical,message)
    #print(command)
    cursor.execute(command)
    command =  '''SELECT clientConnection FROM user_table WHERE username = '{}' '''.format(toUser)
    cursor.execute(command)
    destinationAddress = cursor.fetchone()[0]
    #print(destinationAddress)
    command = ''' SELECT * FROM message_table'''
    cursor.execute(command)
    print(cursor.fetchone())
    print(destinationAddress)
    if destinationAddress != None:
        hostPort = (destinationAddress, 8001)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print('Attempting to connect to {}'.format(str((destinationAddress, 8001))))
            s.connect((destinationAddress, 8001))
            print('Connected to {}!'.format(str((destinationAddress, 8001))))
            s.sendall(message.encode('utf8'))
            print('Send message!')
        #createConnectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #createConnectionSocket.bind((host,port))
        #createConnectionSocket.listen()
        #readyRead,readyWrite,xconnections = select.select([],[createConnectionSocket],[])
        #for s in readyWrite:
        #    s.sendall(message.encode('utf-8'))
    

class serverHandler(http.server.BaseHTTPRequestHandler):
    def parseRequest(self):
        requestText = str(self.rfile.read1(100))
        print('RequestText: ',requestText)
        data = requestText.split(':')
        #print(data)
        self.commandType = removeNonAlphanumeric(data[0])
        if 'Login' in self.commandType or 'Signup' in self.commandType:
            self.clientUserName = removeNonAlphanumeric(data[1])
            self.clientPassword = removeNonAlphanumeric(data[2])
        elif 'Message' in self.commandType:
            self.clientUserName = removeNonAlphanumeric(data[1])
            self.destinationUser = removeNonAlphanumeric(data[2])
            self.messageText = removeNonAlphanumeric(data[3])
        
            
            
    def do_GET(self):
        #if (CONNECTION_NOT_YET_STORED):
        #print('Doing Get!')
        
        self.parseRequest()
        addConnectionToClient(self.clientUserName,self.address_string())
        if 'Login' in self.commandType:
            logData = getLoginInfo(self.clientUserName,self.clientPassword)
        elif 'Signup' in self.commandType:
            logData = getSignupInfo(self.clientUserName,self.clientPassword)
        self.send_response(200)
        self.end_headers()
        self.flush_headers()
        #print(str(logData))
        self.wfile.write(str(logData).encode('utf8'))
        
    def do_POST(self):
        #if (CONNECTION_NOT_YET_STORED):
        self.parseRequest()
        addConnectionToClient(self.clientUserName,self.address_string())
        if 'Message' in self.commandType:
            sendMessage(self.messageText, self.clientUserName,self.destinationUser)
        

        


if __name__=='__main__':
    #initializeDatabase()
    connection = sqlite3.connect("socialite.db")
    cursor = connection.cursor()
    server_address = ('127.0.0.1', 8000)
    theServer = http.server.HTTPServer(server_address,serverHandler)
    theServer.serve_forever()    
    
