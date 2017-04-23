from CarComponent import CarComponent
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

class Camera(CarComponent):
    'Car component that takes care of everything camera'

    camera = None
    rawCapture = None
        
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (CarComponent.frame_width, CarComponent.frame_height)
        self.camera.framerate = 15
        self.camera.hflip = True
        self.camera.vflip = True
        self.camera.video_stabilization = False
        self.camera.exposure_mode = 'sports'
        self.rawCapture = PiRGBArray(self.camera, size=(CarComponent.frame_width, CarComponent.frame_height))
        print "ininted Camera"
        # allow the camera to warmup
        time.sleep(0.2)

    
        
