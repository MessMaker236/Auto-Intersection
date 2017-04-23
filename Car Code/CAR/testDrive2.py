import car
import RPi.GPIO as io
import time

myCar = car.Motor(10)

time.sleep(1)
oldspeed = 0
oldangle = 90
while(True):
    try:
        speed = input("speed: ")
    except SyntaxError:
        speed = None    
    if speed is not None:
        if speed == -1 :
            break
        oldspeed = speed
        myCar.drive(speed,oldangle)
    try:
        angle = input("angle: ")
    except SyntaxError:
        angle = None
    if angle is not None:
        oldangle = angle
        myCar.drive(oldspeed,angle)

myCar.stop()
time.sleep(1)
myCar.cleanup()

