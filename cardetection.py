import os
import re
import cv2 # opencv
import numpy as np

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

    # shortlist contours appearing in the detection zone
    valid_cntrs = []
    for cntr in contours:
        x, y, w, h = cv2.boundingRect(cntr)
        if (x <= 80) & (y >= 80) & (cv2.contourArea(cntr) >= 25):
            #if (y >= 90) & (cv2.contourArea(cntr) < 40):
            valid_cntrs.append(cntr)

    # add contours to original frames
    dmy = col_images[i].copy()
    cv2.drawContours(dmy, valid_cntrs, -1, (127, 200, 0), 2)

    cv2.putText(dmy, "vehicles detected: " + str(len(valid_cntrs)), (55, 15), font, 0.6, (0, 180, 0), 2)
    #cv2.line(dmy, (0, 80), (256, 80), (100, 255, 255))
    #cv2.imwrite(pathIn + str(i) + '.png', dmy)

#frame_array = []

#files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
#files.sort(key=lambda f: int(re.sub('\D', '', f)))

#for i in range(len(files)):
#    filename = pathIn + files[i]

    # read frames
#    img = cv2.imread(filename)
#    height, width, layers = img.shape
#    size = (width, height)

    # inserting the frames into an image array
#    frame_array.append(img)

#for i in range(len(frame_array)):
    # writing to a image array
    out.write(dmy)

out.release()