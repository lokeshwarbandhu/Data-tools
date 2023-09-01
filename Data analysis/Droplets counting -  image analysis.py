import cv2
import pylab
from scipy import ndimage
import matplotlib.pyplot as plt

im = cv2.imread("C:\\Users\\LokeshwarBandhu\\Pictures\\PEN067\\PEN067-OI001.jpg")
pylab.figure(0)
pylab.imshow(im)

gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5,5), 0)
maxValue = 255
adaptiveMethod = cv2.ADAPTIVE_THRESH_GAUSSIAN_C#cv2.ADAPTIVE_THRESH_MEAN_C #cv2.ADAPTIVE_THRESH_GAUSSIAN_C
thresholdType = cv2.THRESH_BINARY#cv2.THRESH_BINARY #cv2.THRESH_BINARY_INV
blockSize = 11 #odd number like 3,5,7,9,11
C = -3 # constant to be subtracted
im_thresholded = cv2.adaptiveThreshold(gray, maxValue, adaptiveMethod, thresholdType, blockSize, C) 
labelarray, particle_count = ndimage.measurements.label(im_thresholded)
print(particle_count)
pylab.figure(1)
pylab.imshow(im_thresholded)
pylab.show()

cnts, _ = cv2.findContours(im_thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
AREA_THRESHOLD = 10
points_list = []
points_size = []
size_list = []

for c in cnts:
    area = cv2.contourArea(c)
    if area < AREA_THRESHOLD:
        cv2.drawContours(im_thresholded, [c], -1, 0, -1)
    else:
        (x, y), radius = cv2.minEnclosingCircle(c)
        points_list.append((int(x), int(y)))
        points_size.append(radius)
        size_list.append(area)
# Plot particle size distribution (histograms)

points_size_um = [i*5 for i in points_size] # assuming 1 pixel = 5 um
plt.hist(points_size_um, color = 'blue', edgecolor = 'black', bins = 100)
# Add labels
plt.title('Particle size distribution')
plt.xlabel('Particle size (um)')
plt.ylabel('No. of particles')
plt.show()
print("Number of particles: {}".format(len(points_list)))
print("Average particle size: {:.3f}".format(sum(size_list)/len(size_list)))