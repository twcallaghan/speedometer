import cv2 # opencv
import numpy as np


def main():
    cap = cv2.VideoCapture("./DJI_0270.MP4")
    while not cap.isOpened():
        cap = cv2.VideoCapture("./DJI_0270.MP4")
        cv2.waitKey(1000)
        print("Wait for the header")

    # kernel for image dilation
    kernel = np.ones((4, 4), np.uint8)

    # font style
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Gets a previous frame before the loop
    ret, frame = cap.read()
    while True:
        prevframe = frame[:]
        ret, frame = cap.read()

        # frame differencing
        grayA = cv2.cvtColor(prevframe, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
            if (y <= 520) and cv2.contourArea(cntr) >= 10000:
                valid_cntrs.append(cntr)

        # add contours to original frames
        dmy = frame.copy()
        cv2.drawContours(dmy, valid_cntrs, -1, (127, 200, 0), 2)

        cv2.putText(dmy, "Vehicles detected: " + str(len(valid_cntrs)), (55, 15), font, 0.6, (0, 180, 0), 2)

        # Regular image window
        cv2.namedWindow("regular_window", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("regular_window", 960, 540)
        cv2.moveWindow("regular_window", 0, 0)
        cv2.imshow("regular_window", frame)

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

        # 1ms delay which makes the windows appear as if it is video with pictures
        cv2.waitKey(1)

        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            # If the number of captured frames is equal to the total number of frames, stop
            break

if __name__ == '__main__':
    main()