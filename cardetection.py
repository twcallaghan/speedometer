import os
import re
import cv2 # opencv
import numpy as np
import time

# get file names of the frames
col_frames = os.listdir('./dji_0270_frames/')

# sort file names
col_frames.sort(key=lambda f: int(re.sub('\D', '', f)))

# empty list to store the frames
col_images=[]

for i in col_frames:
    # read the frames
    img = cv2.imread('./dji_0270_frames/'+i)
    # append the frames to the list
    col_images.append(img)

# kernel for image dilation
kernel = np.ones((4, 4), np.uint8)

# font style
font = cv2.FONT_HERSHEY_SIMPLEX

# directory to save the ouput frames
pathIn = "./temp_frames_0270/"

# specify video name
pathOut = './dji270_withcountours.mp4v'

# specify frames per second
fps = 30.0

out = cv2.VideoWriter(pathOut, cv2.VideoWriter_fourcc(*'DIVX'), fps, (1920, 1080))

for i in range(len(col_images) - 1):

    # frame differencing
    grayA = cv2.cvtColor(col_images[i], cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(col_images[i + 1], cv2.COLOR_BGR2GRAY)
    diff_image = cv2.absdiff(grayB, grayA)

    # image thresholding
    ret, thresh = cv2.threshold(diff_image, 50, 255, cv2.THRESH_BINARY)

    # image dilation
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    # find contours
    contours, hierarchy = cv2.findContours(dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # countours
    valid_cntrs = []
    for cntr in contours:
        x, y, w, h = cv2.boundingRect(cntr)
        # Setting the minimum size of something to be a contour
        if (y <= 520) and cv2.contourArea(cntr) >= 1000:
            valid_cntrs.append(cntr)

    # add contours to original frames
    dmy = col_images[i].copy()
    cv2.drawContours(dmy, valid_cntrs, -1, (127, 200, 0), 2)

    cv2.putText(dmy, "Vehicles detected: " + str(len(valid_cntrs)), (55, 15), font, 0.6, (0, 180, 0), 2)

    out.write(dmy)

    # Regular image window

    # Image difference window
    cv2.namedWindow("Diff_image_window", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Diff_image_window", 960, 540)
    cv2.moveWindow("Diff_image_window", 960, 0)
    cv2.imshow("Diff_image_window", diff_image)

    # Thresh window

    # Countour window

    cv2.waitKey(1)

out.release()