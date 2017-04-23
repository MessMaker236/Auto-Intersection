# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import math
import RPi.GPIO as io
import wiringpi
io.setmode(io.BCM)

#Red is 5v
#Brown is Gnd
in1_pin = 4 #Orange
in2_pin = 17 #Yellow
enable1_pin = 27 #Green
in3_pin = 5 #Blue
in4_pin = 6 #Purple
enable2_pin = 23 #Grey
servo_pin = 18 #White

io.setup(in1_pin, io.OUT)
io.setup(in2_pin, io.OUT)
io.setup(enable1_pin, io.OUT)
io.setup(in3_pin, io.OUT)
io.setup(in4_pin, io.OUT)
io.setup(enable2_pin, io.OUT)

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(18, wiringpi.GPIO.PWM_OUTPUT)
wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)
wiringpi.pwmWrite(18, 150)

io.output(enable1_pin, True) #left
io.output(enable2_pin, True) # right

speed1 = io.PWM(enable1_pin,50)
speed2 = io.PWM(enable2_pin,50)

speed1.start(int(0)) #left
speed2.start(int(0)) #right

#colors
RED = (0,0 ,225)
GREEN = (0,225,0)
BLUE = (225,0,0)
YELLOW = (0,255,255,200)
WHITE = (255,255,255,200)
BLACK = (0,0,0)
PINK = (255,102,255)

#some constants:
frame_width = 320
frame_height = 240
frame_center = frame_width/2
line_thresh = 160
base_speed = 55
turn_thresh = 10
pi = math.pi
font = cv2.FONT_HERSHEY_SIMPLEX

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (frame_width, frame_height)
camera.framerate = 15
camera.hflip = True
camera.vflip = True
camera.video_stabilization = False
camera.exposure_mode = 'sports'
rawCapture = PiRGBArray(camera, size=(frame_width, frame_height))
 
# allow the camera to warmup
time.sleep(0.2)

def pointDistance(p1,p2):
    return math.sqrt(math.pow(p1[0]+p2[0],2) + math.pow(p1[1]+p2[1],2))

def getSlope(p1,p2):
    deltaY = p1[1]-p2[1]
    deltaX = p1[0]-p2[0]
    slope = deltaX/deltaY
    return slope

def averagePoint(p1,p2): #returns the avegage of two (x,y) points
    pAvg = (((p1[0]+p2[0])/2),((p1[1]+p2[1])/2))
    return pAvg

def getPoint(rho,theta,y): #given rho, theta, and a y-value, return  (x,y)
    cosT = math.cos(theta)
    sinT = math.sin(theta)
    x = int((rho-(y*sinT))/cosT) #drived from rho=xcos(theta)+ysin(theta)
    return (x,y)
    
def drawLine2(img, rho, theta, color,top,bottom):
    p1=(getPoint(rho,theta,top))
    p2 = (getPoint(rho,theta,bottom))
    cv2.line(img, p1, p2 , color , 3, cv2.LINE_AA) 
    return (p1,p2)

def drawLine(img, rho, theta, color):
    a = math.cos(theta)
    b = math.sin(theta)
    x0, y0 = a*rho, b*rho
    pt1 = ( int(x0+1000*(-b)), int(y0+1000*(a)) )
    pt2 = ( int(x0-1000*(-b)), int(y0-1000*(a)) )
    cv2.line(img, pt1, pt2, color , 3, cv2.LINE_AA) 
    return (pt1,pt2)    

def servodrive(speed, servoAngle):
    io.output(in1_pin, True)
    io.output(in2_pin, False)
    io.output(in3_pin, False)
    io.output(in4_pin, True)

    if speed == 0:
        speed1.start(0) #left
        speed2.start(0) #right
    else:
        speed1.start(int(speed)) #leftSS
        speed2.start(int(speed)) #right
    if servoAngle > 0:
        wiringpi.pwmWrite(18, int(150 + (90-servoAngle)))

def processImage(image):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) #turn image grayscale
    edges = cv2.Canny(gray,50,150,apertureSize = 3) #detect edges in image

    left_line_count = 0
    left_rho_sum = 0
    left_theta_sum = 0
    
    right_line_count = 0
    right_rho_sum = 0
    right_theta_sum = 0
    
    lines = cv2.HoughLines(edges, 1, math.pi/180.0, 50, np.array([]), 0, 0) #array of lines found
    if lines is not None: #check that there are some lines
        a,b,c = lines.shape
        for i in range(a):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            if theta > (5*pi)/6 or theta < pi/6: #verticalish line
                if abs(rho) > frame_center - line_thresh and abs(rho) < frame_center+line_thresh: #centeredish line
                    if rho > 0: #left line
                        left_line_count += 1
                        left_rho_sum += rho
                        left_theta_sum += theta
                    else: #right line
                        right_line_count += 1
                        right_rho_sum += rho
                        right_theta_sum += theta
    if left_line_count > 0:                 
        left_rho_average = left_rho_sum/left_line_count
        left_theta_average = left_theta_sum/left_line_count
        a,b = drawLine2(image, left_rho_average, left_theta_average, RED,30,210)
        cv2.putText(image,"Left Lines: "+str(left_line_count), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE)
#        print(a,b)
    else:
        return(0,0)
    if right_line_count > 0:                 
        right_rho_average = right_rho_sum/right_line_count
        right_theta_average = right_theta_sum/right_line_count
        cv2.putText(image,"Right Lines: "+str(right_line_count), (200,30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE)
        c,d = drawLine2(image, right_rho_average, right_theta_average, BLUE,30,210)
#        print(c,d)
    else:
        return(0,0)
        
    roadCenterP1, roadCenterP2 = averagePoint(a,c), averagePoint(b,d)
    roadSlope = getSlope(roadCenterP1, roadCenterP2)
    
    roadCenterPoint = averagePoint(roadCenterP1,roadCenterP2)
    
    distanceToCenter = roadCenterPoint[0]-frame_center
    cv2.putText(image,"Distance: "+str(distanceToCenter), (frame_center,100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE)
    cv2.line(image, roadCenterPoint, (frame_center,roadCenterPoint[1]), WHITE , 2, cv2.LINE_AA) #CENTER OF ROAD!
    
    cv2.putText(image,"Road SLope: "+str(roadSlope), (100,10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE)        
    cv2.line(image, roadCenterP1, roadCenterP2, YELLOW , 3, cv2.LINE_AA) #CENTER OF ROAD!
    drawLine2(image,frame_center,0,GREEN,100,140) #Center of frame
    
    if left_line_count > 0 and right_line_count > 0:
        servoAngle = 90 + (distanceToCenter*.5)
        speed = 60
        if left_line_count <= 2 or right_line_count <= 2: #trouble finding road - slow down
            speed = 40
    else:   #no road
        speed = 0   #stop

    servoAngleRadians = servoAngle*pi/180
    servodialCenter = (30,40)
    servodialEnd = (int(servodialCenter[0]+(50*math.cos(servoAngleRadians))),int(servodialCenter[1]+(50*math.sin(servoAngleRadians))))
    cv2.line(image, servodialCenter, servodialEnd, PINK , 3, cv2.LINE_AA) 
    cv2.putText(image,str(servoAngle)+" degrees", (10,110), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE)
    
    return (speed, servoAngle)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    
    img = frame.array
    top_half = img[0:frame_height/3,0:frame_width]
    bottom_half = img[frame_height/3:frame_height,0:frame_width]
    speed, servoAngle = processImage(bottom_half)
    cv2.imshow("live",img)

    if speed == 0:
        servodrive(0,0)
        print('NO ROAD')
    else:
        servodrive(speed,servoAngle)

    key = cv2.waitKey(1) & 0xFF
    
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        wiringpi.pwmWrite(18, 150) #Center servo
        io.cleanup()
        break
     
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
     
        
