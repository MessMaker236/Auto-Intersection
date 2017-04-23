import math
import cv2

class CarComponent(object):
    'Base class for all car components'

    hostIP = '192.168.1.247'
    hostPort = 12345

    pi = math.pi
    font = cv2.FONT_HERSHEY_SIMPLEX

    frame_width = 320
    frame_height = 240

    line_thresh = 160
    frame_center = 160

    #color constants
    RED = (0,0 ,225)
    GREEN = (0,225,0)
    BLUE = (225,0,0)
    YELLOW = (0,255,255,200)
    WHITE = (255,255,255,200)
    BLACK = (0,0,0)
    PINK = (255,102,255)
