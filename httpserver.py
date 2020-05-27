import http
import socket
import select
import sqlite3
import http.server
import json

def getTableColumnNames(table = 'user_table'):
    command = """SELECT * FROM {} LIMIT 1""".format(table)
    cursor.execute(command)
    des = cursor.description
    return [c[0] for c in des]

def getFields(fields,restrictions,fetchOne = False,table = 'user_table'):
    if fields != '*':
        fieldsText = ', '.join([i for i in fields])
    else:
        fieldsText = '*'
        fields = getTableColumnNames(table)
    restrictionsText = ""
    numKeys = 0
    keys = restrictions.keys()
    for k in keys:
        numKeys +=1
        andOrNot = ' AND 'if numKeys!=len(keys) else ''
        if type(restrictions[k])==str:
            restrictionsText += "{} = '{}'{}".format(k,str(restrictions[k]),andOrNot)
        else:
            restrictionsText += "{} = {}{}".format(k,str(restrictions[k]),andOrNot)
    if len(restrictionsText) > 0:
        restrictionsText = 'WHERE ( ' + restrictionsText + ' );'
    command = '''SELECT {} FROM {} {}'''.format(fieldsText,table,restrictionsText)
    print(command)
    cursor.execute(command)
    if not fetchOne:
        output = cursor.fetchall()
        return [tupleToJson(fields,t) for t in output]
    else:
        output = cursor.fetchall()
        return tupleToJson(fields,output)
def tupleToJson(fields,theTuple):
    if theTuple ==None:
        return {}
    jsonOutput = {}
    for f,t in zip(fields,theTuple):
        jsonOutput[f] = t
    return jsonOutput
#Quest Format:

#{'name': 'QuestName','pictureFileName':'img1.jpg','description':'just do it',
#'progressFunction': 'aFunctionDefinedServersideOrOnClient','progress':5,
#'requiredFinish': 100, 'finished': False,'available':False,'prerequisites': ['quest1', 'quest2', 'quest3']}
def updateQuest(username, updateFieldsAndNewValues):
    command = '''SELECT (username,age,bio,gender) FROM user_table
WHERE username='{}';'''.format(username)
    cursor.execute(command)
    currentQuests =  cursor.fetchone()[0]
    
    for k in updateFieldsAndNewValues.keys():
        pass

#Helper functions
#def makeStringSQLSafe(string):
#    return ''.join([k for k in string if k.isalnum()])

def makeStringSQLSafe(string):
    if "'" in string:
        return string.replace("'","''")
    else:
        return string

def initializeDatabase():
    connection = sqlite3.connect("socialite.db")
    cursor = connection.cursor()
    
    sql_command = """
CREATE TABLE user_table (  
username VARCHAR(20), 
password VARCHAR(30),
age INTEGER,
radius INTEGER,
bio VARCHAR(3000),
gender VARCHAR(10),
clientConnection VARCHAR(40),
quests TEXT,
UNIQUE(username)
);"""
    cursor.execute(sql_command)
    sql_command = """
CREATE TABLE message_table (  
user1 VARCHAR(20), 
user2 VARCHAR(30),
messageText TEXT,
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

def getPublicInfo(username):
    #command = '''SELECT (username,age,bio,gender) FROM user_table
#WHERE username='{}';'''.format(username)
   # cursor.execute(command)
   # return cursor.fetchone()
   return getFields(fields = ['username','age','bio','gender'],restrictions = {'username':username},fetchOne = True)

def updateProfile(username,password, newName,newGender,newRadius, newAge, newBio):
    updateString = ''
    if newName != '':
        updateString = updateString + 'age = {}'.format(str(newName))
    if newGender != '':
        updateString = updateString + ''', gender = '{}' '''.format(str(newGender))
    if newRadius != 0 and newRadius!='':
        updateString = updateString + ''', radius = {} '''.format(str(newRadius))
    if newAge != 0 and newAge!='':
        updateString = updateString + ''', age = {} '''.format(str(newAge))
    if newBio != 0 and newBio!='':
        updateString = updateString + ''', bio ='{}' '''.format(str(newBio))
    command = '''UPDATE user_table
SET age = {}, bio = '{}'
WHERE username = '{}' AND password = '{}' '''.format(newAge, newBio,username,password)
    cursor.execute(command)
    connection.commit()

def getLoginInfo(username,password):
    #command = '''SELECT * FROM user_table
#WHERE username='{}' AND password = '{}' ;'''.format(username,password)
#    cursor.execute(command)
#    return cursor.fetchone()
    return getFields(fields = '*',restrictions = {'username':username},fetchOne = True)


def getSignupInfo(username,password):
#    command = '''SELECT * FROM user_table
#WHERE username='{}' '''.format(username)
#    cursor.execute(command)
#    commandReturn = cursor.fetchone()
    existingUsersWithName =  getFields(fields = ['username'], restrictions = {'username':username})
    if len(existingUsersWithName) == 0:
        command = ''' INSERT INTO user_table (username, password)
VALUES ('{}', '{}') '''.format(username,password)
        cursor.execute(command)
        connection.commit()
        return getFields(fields = '*',restrictions = {'username':username},fetchOne = True)
    else:
        return {}

def sendMessage(message, toUser,fromUser):
    message = {'FROM':fromUser,'MESSAGE':message}
    firstAlphabetical,secondAlphabetical = (toUser,fromUser) if toUser < fromUser else (fromUser,toUser)
    #print(getFields(['messageText'],{'user1':firstAlphabetical,'user2':secondAlphabetical},table = 'message_table',fetchOne = True))
    #print(type(getFields(['messageText'],{'user1':firstAlphabetical,'user2':secondAlphabetical},table = 'message_table')))
    messages = getFields(['messageText'],{'user1':firstAlphabetical,'user2':secondAlphabetical},table = 'message_table')
    if messages != None and len(messages)>0:
        messages = json.loads(messages)
        messages.append(message)
        command = '''UPDATE message_table SET messageText='{}' WHERE user1 = '{}'
                   AND user2 = '{}' '''.format(makeStringSQLSafe(str(messages)),firstAlphabetical,secondAlphabetical)
    
        cursor.execute(command)
        connection.commit()
    else:
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
        command = '''INSERT OR IGNORE INTO message_table(user1, user2,messageText) VALUES('{}','{}','{}')'''.format(firstAlphabetical,secondAlphabetical,makeStringSQLSafe(str([message])))
        print(command)
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
            s.sendall(makeStringSQLSafe(str(message)).encode('utf8'))
            print('Send message!')
            s.close()
        #createConnectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #createConnectionSocket.bind((host,port))
        #createConnectionSocket.listen()
        #readyRead,readyWrite,xconnections = select.select([],[createConnectionSocket],[])
        #for s in readyWrite:
        #    s.sendall(message.encode('utf-8'))
    

class serverHandler(http.server.BaseHTTPRequestHandler):
    def parseRequest(self):
        requestText = str(self.rfile.read1(100))
        if requestText[0:2] == "b'":
            requestText = requestText[2:]
        if requestText[-1] == "'":
            requestText = requestText[0:-1]
        print('RequestText: ',requestText)
        data = requestText.split(':')
        print(data)
        #print(data)
        self.commandType = makeStringSQLSafe(data[0])
        #FORMAT (Get): Login:Username:Password or Signup:Username:Password
        if 'Login' in self.commandType or 'Signup' in self.commandType:
            self.clientUserName = makeStringSQLSafe(data[1])
            self.clientPassword = makeStringSQLSafe(data[2])
        #FORMAT (Post): Message:fromUser:toUser:MessageText
        elif 'Message' in self.commandType:
            self.clientUserName = makeStringSQLSafe(data[1])
            self.destinationUser = makeStringSQLSafe(data[2])
            self.messageText = makeStringSQLSafe(data[3])
        #FORMAT (Get): PublicInfo:Username
        elif 'PublicInfo'  in self.commandType:
            self.wantedUsername = makeStringSQLSafe(data[1])
        #FORMAT (Post): UpdateBio:Username:Password:Age:Radius:Name:Gender
        #Leave blank for no update
        elif 'UpdateBio' in self.commandType:
            self.clientUserName = makeStringSQLSafe(data[1])
            self.clientPassword = makeStringSQLSafe(data[2])
            self.newAge = makeStringSQLSafe(data[3])
            self.newRadius = makeStringSQLSafe(data[4])
            self.newBio = makeStringSQLSafe(data[5])
            self.newName = makeStringSQLSafe(data[6])
            self.newGender = makeStringSQLSafe(data[7])
            
    def do_GET(self):
        #if (CONNECTION_NOT_YET_STORED):
        #print('Doing Get!')
        
        self.parseRequest()
        
        if 'Login' in self.commandType:
            logData = getLoginInfo(self.clientUserName,self.clientPassword)
            addConnectionToClient(self.clientUserName,self.address_string())
        elif 'Signup' in self.commandType:
            logData = getSignupInfo(self.clientUserName,self.clientPassword)
            addConnectionToClient(self.clientUserName,self.address_string())
        elif 'PublicInfo' in self.commandType:
            logData = getPublicInfo(self.wantedUsername)
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
        elif 'UpdateBio' in self.commandType:
            updateProfile(self.clientUserName,self.clientPassword, self.newName,self.newGender,self.newRadius, self.newAge, self.newBio)
        elif 'CompleteQuest' in self.commandType:
            addQuest(self.clientUserName,self.questJSON)
        
        

        


if __name__=='__main__':
    #initializeDatabase()
    connection = sqlite3.connect("socialite.db")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM user_table')
    print(cursor.fetchall())
    server_address = ('127.0.0.1', 8000)
    theServer = http.server.HTTPServer(server_address,serverHandler)
    theServer.serve_forever()    
    
