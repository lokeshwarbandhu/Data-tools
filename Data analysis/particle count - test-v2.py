import cv2
import numpy

frame = cv2.imread("C:\\Users\\LokeshwarBandhu\\Pictures\\PEN067\\PEN067-OI001.jpg")

if frame is None:
    print('Error loading image')
    exit()

frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
ret, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)

frame, contours = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

areas = []

for i in range(0, len(contours)):
    areas.append(cv2.contourArea(contours[i]))

mass_centres_x = []
mass_centres_y = []

for i in range(0, len(contours)):
    M = cv2.moments(contours[i], 0)
    mass_centres_x.append(int(M['m10']/M['m00']))
    mass_centres_y.append(int(M['m01']/M['m00']))

print('Num particles: ', len(contours))

for i in range(0, len(contours)):
    print('Area', (i + 1), ':', areas[i])

for i in range(0, len(contours)):
    print('Centre',(i + 1),':', mass_centres_x[i], mass_centres_y[i])

cv2.imshow("Frame", frame)

cv2.waitKey(0)