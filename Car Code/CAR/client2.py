import socket

s = socket.socket()
host = '192.168.1.247'
port = 12345
print "connecting"
s.connect((host, port))
print "connected"
print s.recv(1024)

