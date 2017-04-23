from CarComponent import CarComponent
import RPi.GPIO as io
import wiringpi

class Motor(CarComponent):
    'Represents the component of the car that drives'
    
    #Red is 5v
    #Brown is Gnd
    in1_pin = 4 #Orange
    in2_pin = 17 #Yellow
    enable1_pin = 27 #Green
    in3_pin = 5 #Blue
    in4_pin = 6 #Purple
    enable2_pin = 23 #Grey
    servo_pin = 18 #White

    speed1 = None
    speed2 = None

    servoOffset = 0

    def __init__(self,servoOffset):

        io.setmode(io.BCM)

        io.setup(self.in1_pin, io.OUT)
        io.setup(self.in2_pin, io.OUT)
        io.setup(self.enable1_pin, io.OUT)
        io.setup(self.in3_pin, io.OUT)
        io.setup(self.in4_pin, io.OUT)
        io.setup(self.enable2_pin, io.OUT)

        self.servoOffset = servoOffset

        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(self.servo_pin, wiringpi.GPIO.PWM_OUTPUT)
        wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
        wiringpi.pwmSetClock(192)
        wiringpi.pwmSetRange(2000)
        wiringpi.pwmWrite(self.servo_pin, 140- self.servoOffset)

        io.output(self.enable1_pin, True) #left
        io.output(self.enable2_pin, True) # right

        self.speed1 = io.PWM(self.enable1_pin,50)
        self.speed2 = io.PWM(self.enable2_pin,50)

        self.speed1.start(int(0)) #left
        self.speed2.start(int(0)) #right
        print("ininted motors")

    def drive(self, speed, servoAngle):
        io.output(self.in1_pin, True)
        io.output(self.in2_pin, False)
        io.output(self.in3_pin, False)
        io.output(self.in4_pin, True)

        if speed == 0:
            self.speed1.start(0) #left
            self.speed2.start(0) #right
        elif speed <= 100:
            self.speed1.start(int(speed)) #leftSS
            self.speed2.start(int(speed)) #right
        else:
            print("INVALID DRIVE SPEED: ", speed)
        if servoAngle >= 10 and servoAngle <= 170:
            wiringpi.pwmWrite(self.servo_pin, int(140 + (90-servoAngle)-self.servoOffset))
            #print "servo offset of %d" %(self.servoOffset)
        else:
            print("INVALID SERVO ANGLE", servoAngle)
        print("driving speed: ",speed, "angle: ", servoAngle)

    def stop(self):
        self.speed1.start(0) #left
        self.speed2.start(0) #right
        print("stopped")

    def cleanup(self):
        wiringpi.pwmWrite(self.servo_pin, 140-self.servoOffset)
        io.cleanup()
        print("cleanuped motors")
            
            

