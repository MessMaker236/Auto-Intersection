from CarComponent import CarComponent
import socket

class ServerComm(CarComponent):
    'The component of the car that wirelessly communicates'
    
    def __init__(self):
        print "inited comms"

    def getResponse(self, message):
        s =socket.socket()
        s.connect((CarComponent.hostIP,CarComponent.hostPort))
        print "sent ",message
        s.send(message)
        recieved = s.recv(1024)
        print "recieved " , recieved
        s.close()
        return recieved

    
        
