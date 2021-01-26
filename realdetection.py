import cv2
import datetime
import os
import numpy
from statistics import mean

first_frame = None
video = cv2.VideoCapture(1)

speedlist = [0]
prevx = None

while True:
    check, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if first_frame is None:
        first_frame = gray
        continue

    delta_frame = cv2.absdiff(first_frame, gray)
    th_delta = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    th_delta = cv2.dilate(th_delta, None, iterations=0)
    (cnts, _) = cv2.findContours(th_delta.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 1280 x 720 for logitech c270
    # current test is using ~22 inches of length for whole screen thus 22 inches/1280 pixels
    carx = 0
    cary = 0
    speed = 0
    font = cv2.FONT_HERSHEY_SIMPLEX

    for contour in cnts:
        if cv2.contourArea(contour) < 4000:
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        if prevx is None:
            prevx = 0
        inches = abs(x - prevx) * (22/1280)
        speed = inches * (30 / 17.6)  # inches * fps of video / 17.6 to convert into mph
        speedlist.append(speed)
        prevx = x
        carx = x
        cary = y

    frame_copy = frame.copy()
    recentavgspeed = mean(speedlist[-10:])
    cv2.putText(frame_copy, "Current (avg) speed: {:.2f}".format(recentavgspeed), (carx, cary - 60), font, 0.7, (0, 0, 200), 2)
    cv2.imshow('Capturing', frame)
    cv2.imshow('basic_window', frame_copy)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# for i in range(0, len(times), 2):
#     df = df.append({"Start": times[i], "End": times[i+1]}, ignore_index=True)
#
# df.to_csv("Times_"+datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")+".csv")
video.release()
cv2.destroyAllWindows()
