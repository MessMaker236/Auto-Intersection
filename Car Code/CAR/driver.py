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

approachingInersection = False
sourceLaneID = None
targetLaneID = None
bearing = 'straight'
status = ''
targetMarker = None
distToTarget = None

for frame in frontcamera.camera.capture_continuous(frontcamera.rawCapture, format="bgr", use_video_port=True):
    img = frame.array

    arUcoFinder.search(img)

    if img is not None:
        dist, ang, leftcount, rightcount = roadFinder.findRoad(img)
    print(dist ,ang,leftcount ,rightcount)

    for marker in arUcoFinder.found:
        if not approachingInersection:
            if marker.id < 10: #ID of car
                if arUcoFinder.getSize(marker) > 40: #car is close
                    car.stop()
                    print "Car %d Detected" %(marker.id)
            elif marker.id < 30: #ID of road Marker
                approachingInersection = True
                targetMarker = marker
                sourceLaneID = marker.id
                print "Approaching intersection %d" %(marker.id)
        else:
            if marker.id == targetLaneID:
                approachingInersection = False
                sourceLaneID = None
                targetLaneID = None
                status = ''
                
    if not approachingInersection: #drive as normal
        servoAngle = 90 + (dist*.3)
        if(leftcount+rightcount > 10):
            speed = leftcount+rightcount +40
        else:
            speed = 0
        myCar.drive(speed,servoAngle)
    else:   #Approaching intersection (freak out)
        if targetLaneID is None:
            ans = serverComm.getResponse("%d %s %s"%(sourceLaneID,bearing,status)).split()
            ServerSpeed = ans[0]
            targetLaneID = ans[1]
        else:
            ans = serverComm.getResponse("%d %s %s"%(sourceLaneID,targetLaneID,status)).split()
            ServerSpeed = ans[0]
            
        distToTarget = arUcoFinder.getDistance(targetMarker)
        

        
                
    img = arUcoFinder.draw(img)
    
    cv2.imshow("live",img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
     
    frontcamera.rawCapture.truncate(0)  # clear the stream in preparation for the next frame
    
car.cleanup()
