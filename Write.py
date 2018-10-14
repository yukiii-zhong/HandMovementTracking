import numpy as np
import cv2
import argparse
from collections import deque
import keyboard as kb
import time
from pynput.keyboard import Key, Controller, Listener

class points(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

sm_threshold = 100
lg_threshold = 200



guiding = True

keyboard = Controller()

cap = cv2.VideoCapture(0)

pts = deque(maxlen=64)

Lower_green = np.array([110, 50, 50])
Upper_green = np.array([130, 255, 255])

startPoint =endPoint = points(0,0)


recentPoints = deque()
# counter = 0
# prev_x = 0
# prev_y = 0
while True:

    if kb.is_pressed('q'):
        guiding = False
    if kb.is_pressed('w'):
        guiding = True
    ret, img = cap.read()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.inRange(hsv, Lower_green, Upper_green)
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel)
    mask = cv2.dilate(mask, kernel, iterations=1)
    res = cv2.bitwise_and(img, img, mask=mask)
    cnts, heir = cv2.findContours(
        mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
    center = None

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # Added code 
        recentPoints.append(points(x,y))

        if len(recentPoints)>16:
            recentPoints.popleft()

        if len(recentPoints) == 16:
            min_X = min([p.x for p in recentPoints])
            max_X = max([p.x for p in recentPoints])
            min_Y = min([p.y for p in recentPoints])
            max_Y = max([p.y for p in recentPoints])


            if max_X-min_X <= sm_threshold or max_Y-min_Y<=sm_threshold:
                # EndPoint as average of recentPoints
                # endPoint_X = sum([p.x for p in recentPoints])/len(recentPoints)
                # endPoint_Y = sum([p.y for p in recentPoints])/ len(recentPoints)
                # endPoint = points(endPoint_X, endPoint_Y)
                endPoint = points(x,y)

            if abs(startPoint.x-endPoint.x)*0.625 > abs(startPoint.y- endPoint.y):
                if startPoint.x - endPoint.x > lg_threshold:
                    print('right')
                    keyboard.press(Key.right)
                    keyboard.release(Key.right)
                    startPoint = endPoint
                    recentPoints = deque()


                elif startPoint.x - endPoint.x < -lg_threshold:
                    print('left')
                    keyboard.press(Key.left)
                    keyboard.release(Key.left)
                    startPoint = endPoint
                    recentPoints = deque()


            else:
                if startPoint.y - endPoint.y > lg_threshold*0.625 :
                    print('up')
                    keyboard.press(Key.up)
                    keyboard.release(Key.up)
                    startPoint = endPoint 
                    recentPoints = deque()                  
             
                elif startPoint.y - endPoint.y < -lg_threshold*0.625:
                    print('down')
                    keyboard.press(Key.down)
                    keyboard.release(Key.down)
                    startPoint = endPoint   
                    recentPoints = deque()



        #print(x, y)
        # time.sleep(0.1)
        # counter += 1
        # if counter == 32:
        #     prev_x = x
        #     prev_y = y
        # if counter > 32:
        #     if abs(x - prev_x) > abs(y - prev_y):
        #         if x - prev_x > 100:
        #             print('left')
        #             keyboard.press(Key.left)
        #             keyboard.release(Key.left)
        #             # time.sleep(0.7)
        #             counter = 0

        #         elif x - prev_x < -100:
        #             print('right')
        #             keyboard.press(Key.right)
        #             keyboard.release(Key.right)
        #             counter = 0
        #     else:
        #         if y - prev_y > 100:
        #             print('down')
        #             keyboard.press(Key.down)
        #             keyboard.release(Key.down)
        #             counter = 0
        #             # time.sleep(0.7)
        #         elif y - prev_y < -100:
        #             print('up')
        #             keyboard.press(Key.up)
        #             keyboard.release(Key.up)
        #             counter = 0
        #             # time.sleep(0.7)

        if radius > 5:
            cv2.circle(img, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(img, center, 5, (0, 0, 255), -1)

    pts.appendleft(center)
    for i in range(1, len(pts)):
        if pts[i - 1]is None or pts[i] is None:
            continue
        thick = int(np.sqrt(len(pts) / float(i + 1)) * 2.5)
        cv2.line(img, pts[i - 1], pts[i], (0, 0, 225), thick)

    cv2.imshow("Frame", img)
    # cv2.imshow("mask",mask)
    # cv2.imshow("res",res)

    k = cv2.waitKey(1) & 0xFF
    if k == ord("p"):
        break
# cleanup the camera and close any open windows
cap.release()
cv2.destroyAllWindows()
