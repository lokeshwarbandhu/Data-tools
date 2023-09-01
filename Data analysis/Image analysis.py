import cv2
import numpy as np
import pylab
import matplotlib.pyplot as plt
import pandas as pd

# Kmeans 
def kmeans_color_quantization(image, clusters=2, rounds=1000):
    h, w = image.shape[:2]
    samples = np.zeros([h*w,3], dtype=np.float32)
    count = 0

    for x in range(h):
        for y in range(w):
            samples[count] = image[x][y]
            count += 1

    compactness, labels, centers = cv2.kmeans(samples,
            clusters, 
            None,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.1), 
            rounds, 
            cv2.KMEANS_RANDOM_CENTERS)

    centers = np.uint8(centers)
    res = centers[labels.flatten()]
    return res.reshape((image.shape))

# Load image
image = cv2.imread("C:\\Users\\LokeshwarBandhu\\Pictures\\PEN067\\PEN067-OI008-BF.jpg")
original = image.copy()

# Perform kmeans color segmentation, grayscale, Otsu's threshold
kmeans = kmeans_color_quantization(image, clusters=2)
gray = cv2.cvtColor(kmeans, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Find contours, remove tiny specs using contour area filtering, gather points
points_list = []
points_size = []
size_list = []
cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
AREA_THRESHOLD = 2
for c in cnts:
    area = cv2.contourArea(c)
    if area < AREA_THRESHOLD:
        cv2.drawContours(thresh, [c], -1, 0, -1)
    else:
        (x, y), radius = cv2.minEnclosingCircle(c)
        points_list.append((int(x), int(y)))
        points_size.append(radius)
        size_list.append(area)

# Apply mask onto original image
result = cv2.bitwise_and(original, original, mask=thresh)
result[thresh==255] = (36,255,12)

# Overlay on original
original[thresh==255] = (36,255,12)

print("Number of particles: {}".format(len(points_list)))
print("Average particle size: {:.3f}".format(sum(size_list)/len(size_list)))
#print(points_size)

# Display counted particles in image
# Display
cv2.imshow('kmeans', kmeans)
cv2.imshow('original', original)
cv2.imshow('thresh', thresh)
cv2.imshow('result', result)
#cv2.waitKey()


# Plot particle size distribution (histograms)
points_size_um = [i*5 for i in points_size] # assuming 1 pixel = 5 um
plt.hist(points_size_um, color = 'blue', edgecolor = 'black', bins = 100)
# Add labels
plt.title('Particle size distribution')
plt.xlabel('Particle size (um)')
plt.ylabel('No. of particles')
plt.show()
