from CarComponent import CarComponent as CC
from picamera.array import PiRGBArray
from picamera import PiCamera
from car import Motor
from arucoFinder import ArUcoFinder
from RoadFinder import RoadFinder
import cv2
import math
import time

myCar = Motor()
arUcoFinder = ArUcoFinder()
roadFinder = RoadFinder()

camera = PiCamera()
camera.resolution = (CC.frame_width, CC.frame_height)
camera.framerate = 15
camera.hflip = True
camera.vflip = True
camera.video_stabilization = False
camera.exposure_mode = 'sports'
rawCapture = PiRGBArray(camera, size=(CC.frame_width, CC.frame_height))

# allow the camera to warmup
time.sleep(0.2)

speed = 50
servoAngle = 90

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    img = frame.array

    arUcoFinder.search(img)

    if img is not None:
        dist, ang, leftcount, rightcount = roadFinder.findRoad(img)
    print(dist , "  " ,ang, " " ,leftcount , "  " ,rightcount)

    img = arUcoFinder.draw(img)

    servoAngle = 90 + (dist*.3)
    
##    if leftcount <= 2 or rightcount <= 2: #no road - stop
##        speed = 0
##    elif leftcount < 5 or rightcount <= 5: #trouble finding road - slow down
##        speed = 40
##    else:   
##        speed = 60 #full speed ahead
    if(leftcount+rightcount > 10):
        speed = leftcount+rightcount +40
    else:
        speed = 0

    myCar.drive(speed,servoAngle)

##    servoAngleRadians = servoAngle*3.14/180
##    servodialCenter = (30,40)
##    servodialEnd = (int(servodialCenter[0]+(50*math.cos(servoAngleRadians))),int(servodialCenter[1]+(50*math.sin(servoAngleRadians))))
##    cv2.line(img, servodialCenter, servodialEnd, PINK , 3, cv2.LINE_AA) 
##    cv2.putText(img,str(servoAngle)+" degrees", (10,110), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE)

    cv2.imshow("live",img)

    key = cv2.waitKey(1) & 0xFF
    
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
     
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

myCar.cleanup()


