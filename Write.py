import numpy as np
import cv2
import argparse
from collections import deque

from pynput.keyboard import Key, Controller

keyboard = Controller()

cap=cv2.VideoCapture(0)

pts = deque(maxlen=64)

Lower_green = np.array([110,50,50])
Upper_green = np.array([130,255,255])

counter = 0
prev_x = 0
prev_y = 0
while True:
	ret, img=cap.read()
	hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
	kernel=np.ones((5,5),np.uint8)
	mask=cv2.inRange(hsv,Lower_green,Upper_green)
	mask = cv2.erode(mask, kernel, iterations=2)
	mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
	#mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel)
	mask = cv2.dilate(mask, kernel, iterations=1)
	res=cv2.bitwise_and(img,img,mask=mask)
	cnts,heir=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
	center = None
 
	if len(cnts) > 0:
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
		print(x,y)
		# time.sleep(0.1)
		counter += 1
		print(counter / 100)
		if abs(x - prev_x) > abs(y - prev_y):
			if x - prev_x > 50 and counter % 10 == 0:
				print('right')
				keyboard.press(Key.left)
				keyboard.release(Key.left)
				
			elif x - prev_x < -50 and counter % 10 == 0:
				print('left')
				keyboard.press(Key.right)
				keyboard.release(Key.right)
				# time.wait(0.7)
		else:
			if y - prev_y > 50 and counter % 10 == 0:
				print('up')
				keyboard.press(Key.down)
				keyboard.release(Key.down)
				# time.sleep(0.7)
			elif y - prev_y < -50 and counter % 10 == 0:
				print('down')
				keyboard.press(Key.up)
				keyboard.release(Key.up)
				# time.sleep(0.7)

		prev_x = x
		prev_y = y

		if radius > 5:
			cv2.circle(img, (int(x), int(y)), int(radius),(0, 255, 255), 2)
			cv2.circle(img, center, 5, (0, 0, 255), -1)
		
	pts.appendleft(center)
	for i in range (1,len(pts)):
		if pts[i-1]is None or pts[i] is None:
			continue
		thick = int(np.sqrt(len(pts) / float(i + 1)) * 2.5)
		cv2.line(img, pts[i-1],pts[i],(0,0,225),thick)
		
	
	cv2.imshow("Frame", img)
	# cv2.imshow("mask",mask)
	# cv2.imshow("res",res)
	
	
	k=cv2.waitKey(30) & 0xFF
	if k==32:
		break
# cleanup the camera and close any open windows
cap.release()
cv2.destroyAllWindows()