from imutils.video import FileVideoStream
from imutils.video import FPS
import numpy as np
import time
import cv2
import os
import initialdistance


def validspeed(speedlist, speed):
    speedlist = sorted(speedlist)
    medianspeed = speedlist[len(speedlist) // 2]
    if abs(speed - medianspeed) > medianspeed // 2:
        return False
    return True


def main():
    # start the file video stream thread and allow the buffer to  start to fill
    fvs = FileVideoStream("./DJI_0270.MP4").start()
    time.sleep(1.0)

    # start the FPS timer
    fps = FPS().start()

    # kernel for image dilation
    kernel = np.ones((4, 4), np.uint8)

    # font style
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Gets a previous frame before the loop
    frame = fvs.read()

    prevx = None
    speed = 0
    speedvals = []
    key = None
    framecount = 0

    initialdist = initialdistance.InitialDistance()

    # TODO: make the user input the fps when they give initial measurement
    videofps = 30
    while fvs.more():
        framecount += 1

        # Call out to get the user to give a distance
        if key == ord("m"):
            cv2.imwrite("./firstframe.ppm", frame)
            initialdist.getinitialdistance()
            os.remove("./firstframe.ppm")

        prevframe = frame[:]
        frame = fvs.read()

        # frame differencing
        graya = cv2.cvtColor(prevframe, cv2.COLOR_BGR2GRAY)
        grayb = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff_image = cv2.absdiff(grayb, graya)

        # image thresholding
        ret, thresh = cv2.threshold(diff_image, 50, 255, cv2.THRESH_BINARY)

        # image dilation
        dilated = cv2.dilate(thresh, kernel, iterations=1)

        # find contours
        contours, hierarchy = cv2.findContours(dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # countours
        # Approx 0.61222 inches / pixel (for DJI 270 only)
        valid_cntrs = []
        cary = 0
        carx = 0
        for cntr in contours:
            x, y, w, h = cv2.boundingRect(cntr)
            # Setting the minimum size of something to be a contour
            if (y <= 850) and cv2.contourArea(cntr) >= 10000:
                if prevx is None:
                    prevx = x
                else:
                    inches = abs(x - prevx) * initialdist.inchperpixel  # inches in 1/30 of a second
                    speed = inches * (videofps / 17.6)  # should be mph as in/s -> mph is 1/17.6
                    if len(speedvals) < 10 or validspeed(speedvals, speed) is True:
                        speedvals.append(speed)
                    prevx = x
                valid_cntrs.append(cntr)
                cary = y
                carx = x

        # If there are no contours then continue processing and reset variables until there is something interesting
        # Also displays the first 10 seconds of video for the user to give initial measurement
        if len(valid_cntrs) == 0 and framecount > (videofps * 10):
            speedvals = []
            cv2.destroyAllWindows()
            continue

        # add contours to original frames
        dmy = frame.copy()
        cv2.drawContours(dmy, valid_cntrs, -1, (127, 200, 0), 2)

        cv2.putText(dmy, "Vehicles detected: " + str(len(valid_cntrs)), (55, 800), font, 2, (0, 0, 200), 7)
        cv2.putText(dmy, "Speed: {:.2f} mph".format(speed), (800, 800), font, 2, (0, 0, 200), 7)
        if len(speedvals) >= 10:
            cv2.putText(dmy, "Median Speed: {:.2f} mph".format(speedvals[len(speedvals) // 2]), (55, 900), font, 2,
                        (0, 0, 200), 7)

        # Image difference window
        cv2.namedWindow("Diff_image_window", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Diff_image_window", 960, 540)
        cv2.moveWindow("Diff_image_window", 960, 0)
        cv2.imshow("Diff_image_window", diff_image)

        # Thresh window
        cv2.namedWindow("thresh_window", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("thresh_window", 960, 540)
        cv2.moveWindow("thresh_window", 0, 540)
        cv2.imshow("thresh_window", thresh)

        # Countour window
        cv2.namedWindow("contour_window", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("contour_window", 960, 540)
        cv2.moveWindow("contour_window", 960, 540)
        cv2.imshow("contour_window", dmy)

        # Regular image window
        cv2.namedWindow("regular_window", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("regular_window", 960, 540)
        cv2.moveWindow("regular_window", 0, 0)
        fps.update()
        # stop the timer and display FPS information
        fps.stop()
        frame_copy = frame.copy()
        cv2.putText(frame_copy, "Elasped time: {:.2f} secs".format(fps.elapsed()), (55, 80), font, 1.5, (0, 0, 200), 5)
        cv2.putText(frame_copy, "FPS: {:.2f}".format(fps.fps()), (900, 80), font, 1.5, (0, 0, 200), 5)
        cv2.putText(frame_copy, "Current speed: {:.2f}".format(speed), (carx, cary - 60), font, 1.5, (0, 0, 200), 5)
        if len(speedvals) > 10:
            cv2.putText(frame_copy, "Median speed: {:.2f}".format(speedvals[len(speedvals) // 2]),
                        (carx, cary), font, 1.5, (0, 0, 200), 5)
        cv2.imshow("regular_window", frame_copy)

        # 1ms delay which makes the windows appear as if it is video with pictures
        key = cv2.waitKey(1)


if __name__ == '__main__':
    main()
