from CarComponent import CarComponent
import aruco
import numpy as np
import math
import cv2

class ArUcoFinder(CarComponent):
    'Use to identify ArUco Markers'

    found = []
    foundIDs = []
    detector = None

    def __init__(self):
        self.detector = aruco.MarkerDetector()
        print("inited ArUco Finder")

    def search(self, frame):
        markers = self.detector.detect(frame)
        self.found = []
        self.foundIDs = []
        for marker in markers:
            self.found.append(marker)
            self.foundIDs.append(marker.id)
        if len(self.found)>0:
            print("detected ids: {}".format(", ".join(str(m.id) for m in markers)))
        else:
            print("no markers found")

    def getMarker(self, markerID):
        for marker in self.found:
            if marker.id == markerID:
                return marker
        return None

    def getSize(self, marker): #returns the relative size of a marker in pixels
        dx = int(abs(marker[1][0] - marker[0][0]))
        dy = int(abs(marker[1][1] - marker[0][1]))
        return int(math.sqrt((dx*dx)+(dy*dy))) #pythagorean theorem

    def getDistance(self, marker): #returns the relative distace to bottom of marker marker in pixels
        leftDist = abs(marker[3][1] - self.frame_height)
        rightDist = abs(marker[2][1] - self.frame_height)
        return (leftDist+rightDist)/2
    
    def draw(self, img):
        for marker in self.found:
            img = cv2.line(img,(marker[0][0],marker[0][1]),(marker[1][0],marker[1][1]),self.RED,5)
            img = cv2.line(img,(marker[1][0],marker[1][1]),(marker[2][0],marker[2][1]),self.GREEN,5)
            img = cv2.line(img,(marker[2][0],marker[2][1]),(marker[3][0],marker[3][1]),self.BLUE,5)
            img = cv2.line(img,(marker[3][0],marker[3][1]),(marker[0][0],marker[0][1]),self.BLUE,5)
            cv2.putText(img,"id: "+str(marker.id),(marker[1][0],marker[2][1]), self.font, 0.8,self.WHITE,2,cv2.LINE_AA)
            cv2.putText(img,"size: "+str(self.getSize(marker)),(marker[1][0],int(marker[2][1])-30), self.font, 0.8,self.WHITE,2,cv2.LINE_AA)
            cv2.putText(img,"dist: "+str(self.getDistance(marker)),(marker[1][0],int(marker[2][1])+30), self.font, 0.8,self.WHITE,2,cv2.LINE_AA)

        return img

    
    

