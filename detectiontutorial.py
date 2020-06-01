import os
import re
import cv2 # opencv
import numpy as np
from os.path import isfile, join
import matplotlib.pyplot as plt


# get file names of the frames
col_frames = os.listdir('frames/')

# sort file names
col_frames.sort(key=lambda f: int(re.sub('\D', '', f)))

# empty list to store the frames
col_images=[]

for i in col_frames:
    # read the frames
    img = cv2.imread('frames/'+i)
    # append the frames to the list
    col_images.append(img)

# plot 1st frame
i = 0

for frame in [i, i+1]:
    #plt.imshow(cv2.cvtColor(col_images[frame], cv2.COLOR_BGR2RGB))
    plt.title("frame: "+str(frame))
    #plt.show()

    # convert the frames to grayscale
    grayA = cv2.cvtColor(col_images[i], cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(col_images[i+1], cv2.COLOR_BGR2GRAY)

    diff_image = cv2.absdiff(grayB, grayA)

    # perform image thresholding
    ret, thresh = cv2.threshold(diff_image, 50, 255, cv2.THRESH_BINARY)

    # plot image after thresholding
    plt.imshow(thresh, cmap = 'gray')
    plt.show()

# plot the image after frame differencing
#plt.imshow(cv2.absdiff(grayB, grayA), cmap = 'gray')
#plt.show()