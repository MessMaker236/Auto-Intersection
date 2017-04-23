from CarComponent import CarComponent as CC

from car import Motor
from arucoFinder import ArUcoFinder
from RoadFinder import RoadFinder
from Camera import Camera
from ServerComm import ServerComm

import cv2

car = Motor(10)
arUcoFinder = ArUcoFinder()
roadFinder = RoadFinder()
frontcamera = Camera()
serverComm = ServerComm()

stage = 1
sourceLaneID = None
sourceMarker = None
targetLaneID = None
targetMarker = None
distToMarker = None
bearing = 'straight'

for frame in frontcamera.camera.capture_continuous(frontcamera.rawCapture, format="bgr", use_video_port=True):

    img = frame.array
    frontcamera.rawCapture.truncate(0)  # clear the stream in preparation for the next frame
    
#==================================================================================================================================
    if stage == 1:    #Base Stage, driving is normal, alert for intersections
        
        arUcoFinder.search(img) #Find Markers
        if img is not None:
            dist, ang, leftcount, rightcount = roadFinder.findRoad(img) #Find Road
            print(dist ,ang,leftcount ,rightcount)
            
        servoAngle = 90 + (dist*.3)
        if(leftcount+rightcount > 10):
            speed = leftcount+rightcount +40
        else:
            speed = 0
        car.drive(speed,servoAngle)
        
        for marker in arUcoFinder.found:
            if marker.id < 10: #ID of car
                if arUcoFinder.getSize(marker) > 40: #car is close
                    car.stop()
                    print "Car %d Detected" %(marker.id)
            elif marker.id < 30: #ID of road Marker
                sourceLaneID = marker.id
                sourceMarker = marker
                stage = stage +1
                print "Approaching intersection %d" %(marker.id)
                
#==================================================================================================================================
    elif stage == 2:      #get the ID of the Lane that will be turned into, should run once
        
        targetLaneID = int(serverComm.getResponse("%d %d %s"%(stage,sourceLaneID,bearing)))
        stage = stage+1
        
#==================================================================================================================================
    elif stage == 3:    #Approaching intersection, calculating distance, recieving updates from server

        arUcoFinder.search(img) #Find Markers
        img = arUcoFinder.draw(img)
        if img is not None:
            dist, ang, leftcount, rightcount = roadFinder.findRoad(img) #Find Road
            print(dist ,ang,leftcount ,rightcount)
            
        servoAngle = 90 + (dist*.3)

        sourceMarker = arUcoFinder.getMarker(sourceLaneID)
        if sourceMarker is not None:
            distToMarker = arUcoFinder.getDistance(sourceMarker)

        if  distToMarker is not None and distToMarker < 40: #VERY CLOSE TO INTERSECTION
            stage = stage+1
        else:
            speed = serverComm.getResponse("%d %d %s"%(stage,sourceLaneID,distToMarker))
            if speed == 'normal':
                power = 60
            elif speed == 'fast':
                power = 80
            elif speed == 'slow':
                power = 55
            car.drive(power, servoAngle)
            
#==================================================================================================================================
    elif stage == 4:    #At Intersection, get final word from server if its okey to cross

        if int(serverComm.getResponse("%d %d %s"%(stage,sourceLaneID,bearing))):
            stage = stage +1
        else:
            car.stop()
        
#==================================================================================================================================
    elif stage == 5:    #In intersection!, Drive at speed and angle provided by server, check for exit

        arUcoFinder.search(img) #Find Markers
        img = arUcoFinder.draw(img)
        
        directions = serverComm.getResponse("%d %s"%(stage,bearing)).split()
        speed = directions[0]
        angle = int(directions[1])

        if speed == 'normal':
            power = 60
        elif speed == 'fast':
            power = 80
        elif speed == 'slow':
            power = 55
        car.drive(power,angle)

        print 'targeting %d'%(targetLaneID)

        for marker in arUcoFinder.found:
            if marker.id == targetLaneID:
                targetMarker = marker
                if arUcoFinder.getDistance(targetMarker) < 80:
                    stage = stage+1
               
#==================================================================================================================================
    elif stage == 6:    #Exited Intersection, Let server know

        serverComm.getResponse("%d "%(stage)).split()
        stage = 1
        sourceLaneID = None
        sourceMarker = None
        targetLaneID = None
        targetMarker = None
        distToMarker = None
        break
        
#==================================================================================================================================
        
    cv2.imshow("live",img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    
car.cleanup()
