import http.client
import socket
import select
client1 = http.client.HTTPConnection('127.0.0.1', 8000)
print(str(client1.request('GET','','Signup:rip:zip')))
a = client1.getresponse()
print(a)
print(a.msg)
print(str(a.read()))

client2 = http.client.HTTPConnection('127.0.0.1', 8000)
print(str(client2.request('GET','Signup:bip:biperson','Signup:bob:boberson')))
b = client2.getresponse()
print(b)
print(b.msg)
print(str(b.read()))

client1.request('POST','Message:bob:biperson:heylilmamalemmewhisperinyourear'
               ,'Message:bob:biperson:heylilmamalemmewhisperinyourear')


host, port = ('127.0.0.1', 8001)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host,port))
    s.listen()
    print('Listening for server connection!')
    conn, addr = s.accept()
    print('Got server connection!')

    a = conn.recv(1024)
    if len(a)>0:
        print(a)
#while True:
#    readyRead,readyWrite,xconnections = select.select([createConnectionSocket],[],[])
#    for s in readyRead:
 #       data = s.recv(300)
 #       print(data)
#        print(data.decode('utf8'))
