import cv2

cap = cv2.VideoCapture("./DJI_0270.MP4")
while not cap.isOpened():
    cap = cv2.VideoCapture("./DJI_0270.MP4")
    cv2.waitKey(1000)
    print("Wait for the header")

pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
count = 0
while True:
    flag, frame = cap.read()
    cv2.imwrite("./dji_0270_frames/frame%d.jpg" % count, frame)
    count += 1
    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    if count % 100 == 0:
        print(str(pos_frame)+" frames")

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        # If the number of captured frames is equal to the total number of frames, stop
        break