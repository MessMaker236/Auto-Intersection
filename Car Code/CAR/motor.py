import RPi.GPIO as io
import time
io.setmode(io.BCM)
 
#Red is 5v
#Brown is Gnd
in1_pin = 4 #Orange
in2_pin = 17 #Yellow
enable1_pin = 18 #Green
in3_pin = 5 #Blue
in4_pin = 6 #Purple
enable2_pin = 23 #Grey

io.setup(in1_pin, io.OUT)
io.setup(in2_pin, io.OUT)
io.setup(enable1_pin, io.OUT)
io.setup(in3_pin, io.OUT)
io.setup(in4_pin, io.OUT)
io.setup(enable2_pin, io.OUT)

io.output(enable1_pin, True)
io.output(enable2_pin, True)

speed1 = io.PWM(enable1_pin,50)
speed2 = io.PWM(enable2_pin,50)

reverse = True
control = 50
speed1.start(int(control))
speed2.start(int(control))
while True:
    if not reverse:
        io.output(in1_pin, False)
        io.output(in2_pin, True)
        io.output(in3_pin, True)
        io.output(in4_pin, False)
    else:
        io.output(in1_pin, True)
        io.output(in2_pin, False)
        io.output(in3_pin, False)
        io.output(in4_pin, True)
        
    control=raw_input('speed: ')

    if control == 's':
        break
    
    if control == 'reverse':
        if reverse:
            reverse = False
        else:
            reverse = True
    else:
        speed1.start(int(control))
        speed2.start(int(control))
        
io.cleanup()
                
    
