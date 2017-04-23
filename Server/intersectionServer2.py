import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.1.247' #IP adress of host laptop
port = 12345        #random port to use
s.bind((host,port))
print "socket bound at %s:%d"%(host,port) 
s.listen(5)

cars = {'192.168.1.112': 1, '192.168.1.168': 2} 

queries = []

laneCount = 4   #Total number of lanes in and out of intersection
laneIDs = [10,11,12,13] #Lane IDs, Clockwise
interiorDimmension = laneCount/4 #Length in Lanes of square inside intersection
intersectionOccupied = False
                   
while True:
    
    c, addr = s.accept()
    
    print "Connection accepted from %s:%d" %(addr[0],addr[1]) 
    
    carReport =(str(c.recv(1024))).split()
    
    carID = cars[addr[0]]
    stage = int(carReport[0])
    
#==============================================================================    
    if stage == 1: #Base Stage, driving normal, no server action
        print "Stage 1 should not be triggered :("
        queries = []
        intersectionOccupied = False
        print intersectionOccupied

#==============================================================================
    elif stage == 2: #return the ID of the target Lane, should run once
    
        sourceLaneID = int(carReport[1])
        bearing = carReport[2]

        currentLaneNum = laneIDs.index(sourceLaneID)+1
        if bearing == "left":
            DestinationLaneNum = currentLaneNum + interiorDimmension
        elif bearing == "right":
            DestinationLaneNum = currentLaneNum - interiorDimmension
        elif bearing == "straight":
            DestinationLaneNum = currentLaneNum + (interiorDimmension*2)
            
        if DestinationLaneNum > laneCount:
            DestinationLaneNum = DestinationLaneNum - laneCount
        elif DestinationLaneNum < 1:
            DestinationLaneNum = DestinationLaneNum + laneCount
            
        targetLaneID = laneIDs[DestinationLaneNum-1]

        if carID not in queries:
            queries.append(carID)
                
            
        c.send(str(targetLaneID))

#==============================================================================
    elif stage == 3:    #Car approaching intersection, give instructions
    
        sourceLaneID = carReport[1]
        distToMarker = carReport[2]
        
        quePos = queries.index(carID)
        
        if quePos == 0 and len(queries) > 1:
            speed = "fast"
        elif quePos > 1:
            speed = "slow"
        else:
            speed = "normal"
            
        c.send(speed)
        
#==============================================================================
    elif stage == 4:    #At intersection, send car final confirmation 
    
        if intersectionOccupied:
            c.send("0")
        else:
            c.send("1")
            intersectionOccupied = True
            print intersectionOccupied

            
#==============================================================================
    elif stage == 5:    #In intersection, send directions
    
        bearing = carReport[1]    
            
        if quePos == 0 and len(queries) > 1:
            speed = "fast"
        elif quePos > 1:
            speed = "slow"
        else:
            speed = "normal"
            
        if bearing == "straight":
            angle = 90
        if bearing == "left":
            angle = 45
        if bearing == "right":
            angle = 135
            
        c.send("%s %d" %(speed, angle))
        intersectionOccupied = True
        
#==============================================================================
    elif stage == 6:    #Left intersection, remove from que
        
        queries.remove(carID)
        intersectionOccupied = False
        print intersectionOccupied

#==============================================================================
            
    c.close()
    print queries