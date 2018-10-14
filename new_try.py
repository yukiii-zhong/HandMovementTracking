import numpy as np
import cv2
import argparse
from collections import deque
import time
from pynput.keyboard import Key, Controller

class CameraCapture():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.Lower_green = np.array([110,50,50])
        self.Upper_green = np.array([130,255,255])
        self.pts = deque(maxlen=64)
        self.img = None
        self.mask = None
        self.res = None

    def visualize_trace(self):
        for i in range (1,len(self.pts)):
            if self.pts[i-1]is None or self.pts[i] is None:
                continue
            thick = int(np.sqrt(len(self.pts) / float(i + 1)) * 2.5)
            cv2.line(self.img, self.pts[i-1],self.pts[i],(0,0,225),thick)
    
    def visualize_frame(self):
        self.img = cv2.flip(self.img, 1)
        cv2.imshow("Frame", self.img)
        # cv2.imshow("mask", self.mask)
        # cv2.imshow("res", self.res)

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def capture_one_fram(self):
        ret, self.img=self.cap.read()
        hsv=cv2.cvtColor(self.img,cv2.COLOR_BGR2HSV)
        kernel=np.ones((5,5),np.uint8)
        self.mask=cv2.inRange(hsv,self.Lower_green,self.Upper_green)
        self.mask = cv2.erode(self.mask, kernel, iterations=2)
        self.mask=cv2.morphologyEx(self.mask,cv2.MORPH_OPEN,kernel)
        #mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel)
        self.mask = cv2.dilate(self.mask, kernel, iterations=1)
        self.res=cv2.bitwise_and(self.img,self.img,mask=self.mask)
        cnts,heir=cv2.findContours(self.mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
        center = None

        x, y = -1, -1
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
            print(x, y)

            if radius > 5:
                cv2.circle(self.img, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                cv2.circle(self.img, center, 5, (0, 0, 255), -1)

            # self.visualize_trace()

            print(x, y)

        self.pts.appendleft(center)
        self.visualize_trace()
        return x,y


class MoveFinder(CameraCapture):
    def __init__(self):
        super().__init__()
        self.consecutive_three = deque(maxlen=3)
        self.start_pos = (0, 0)
        self.end_pos = (0, 0)


if __name__ == '__main__':
    cam = CameraCapture()
    while True:
        cam.capture_one_fram()
        # cam.visualize_trace()
        cam.visualize_frame()
        k = cv2.waitKey(ord('p')) & 0xFF
        if k == ord('p'):
            break
    cam.cleanup()
