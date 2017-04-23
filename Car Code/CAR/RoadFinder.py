from CarComponent import CarComponent
import aruco
import numpy as np
import cv2
import math

class RoadFinder(CarComponent):
    'Use to detect the road'

    def pointDistance(p1,p2):
        return math.sqrt(math.pow(p1[0]+p2[0],2) + math.pow(p1[1]+p2[1],2))

    #get slope between points (delta y / delta x)
    def getSlope(self,p1,p2):
        deltaY = p1[1]-p2[1]
        deltaX = p1[0]-p2[0]
        slope = float(deltaY)/float(deltaX)
        return slope

    def averagePoint(self,p1,p2): #returns the avegage of two (x,y) points
        pAvg = (((p1[0]+p2[0])/2),((p1[1]+p2[1])/2))
        return pAvg

    def getPoint(self,rho,theta,y): #given rho, theta, and a y-value, return  (x,y)
        cosT = math.cos(theta)
        sinT = math.sin(theta)
        x = int((rho-(y*sinT))/cosT) #drived from rho=xcos(theta)+ysin(theta)
        return (x,y)
        
    def drawLine2(self, img, rho, theta, color,top,bottom):
        p1=(self.getPoint(rho,theta,top))
        p2 = (self.getPoint(rho,theta,bottom))
        cv2.line(img, p1, p2 , color , 3, cv2.LINE_AA) 
        return (p1,p2)

    def drawLine(self,img, rho, theta, color):
        a = math.cos(theta)
        b = math.sin(theta)
        x0, y0 = a*rho, b*rho
        pt1 = ( int(x0+1000*(-b)), int(y0+1000*(a)) )
        pt2 = ( int(x0-1000*(-b)), int(y0-1000*(a)) )
        cv2.line(img, pt1, pt2, color , 3, cv2.LINE_AA) 
        return (pt1,pt2)

    def findRoad(self, image):
        
        pi = self.pi
        frame_center = self.frame_center
        line_thresh = self.line_thresh
        
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) #turn image grayscale
        edges = cv2.Canny(gray,50,150,apertureSize = 3) #detect edges in image

        left_line_count = 0
        left_rho_sum = 0
        left_theta_sum = 0
        
        right_line_count = 0
        right_rho_sum = 0
        right_theta_sum = 0

        lines = cv2.HoughLines(edges, 1, math.pi/180.0, 50, np.array([]), 0, 0) #array of lines found
        if lines is None: #check that there are some lines
            return (0,0,0,0)
        else:
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
            a,b = self.drawLine2(image, left_rho_average, left_theta_average, self.RED , 30, 210)
            cv2.putText(image,"Left Lines: "+str(left_line_count), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.WHITE)
    #        print(a,b)
        else:
            return(0,0,left_line_count,right_line_count)
        if right_line_count > 0:                 
            right_rho_average = right_rho_sum/right_line_count
            right_theta_average = right_theta_sum/right_line_count
            cv2.putText(image,"Right Lines: "+str(right_line_count), (200,30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.WHITE)
            c,d = self.drawLine2(image, right_rho_average, right_theta_average, self.BLUE,30,210)
    #        print(c,d)
        else:
            return(0,0,left_line_count,right_line_count)
            
        roadCenterP1, roadCenterP2 = self.averagePoint(a,c), self.averagePoint(b,d)
        roadSlope = 0#self.getSlope(roadCenterP1, roadCenterP2)
        
        roadCenterPoint = self.averagePoint(roadCenterP1,roadCenterP2)
        
        distanceToCenter = roadCenterPoint[0]-frame_center
        
        cv2.putText(image,"Distance: "+str(distanceToCenter), (frame_center,100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.WHITE)
        cv2.line(image, roadCenterPoint, (frame_center,roadCenterPoint[1]), self.WHITE , 2, cv2.LINE_AA) #CENTER OF ROAD!
        
        cv2.putText(image,"Road SLope: "+str(roadSlope), (100,10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.WHITE)        
        cv2.line(image, roadCenterP1, roadCenterP2, self.YELLOW , 3, cv2.LINE_AA) #CENTER OF ROAD!
        
        self.drawLine2(image,frame_center,0,self.GREEN,100,140) #Center of frame
        
        return (distanceToCenter, roadSlope, left_line_count, right_line_count)

