import cv2
import datetime
from datetime import timedelta
import os
import numpy
import boto3
from statistics import mean
import cloudinary
import cloudinary.uploader
import cloudinary.api
from decimal import *
import requests

# When you need to grab image from url:
# img_data = requests.get(image_url).content
# with open('image_name.jpg', 'wb') as handler:
#     handler.write(img_data)

cloudinary.config(cloud_name='seltz',
                  api_key='346981549637338',
                  api_secret=os.environ.get('Cloudinary_Secret'))

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('maintable')
# table = dynamodb.create_table(
#     TableName='maintable',
#     KeySchema=[
#         {
#             'AttributeName': 'time',
#             'KeyType': 'HASH'
#         },
#         {
#             'AttributeName': 'speed',
#             'KeyType': 'RANGE'
#         }
#     ],
#     AttributeDefinitions=[
#         {
#             'AttributeName': 'time',
#             'AttributeType': 'S'
#         },
#         {
#             'AttributeName': 'speed',
#             'AttributeType': 'N'
#         }
#     ],
#     ProvisionedThroughput={
#         'ReadCapacityUnits': 5,
#         'WriteCapacityUnits': 5
#     }
# )

# Wait until the table exists.
# table.meta.client.get_waiter('table_exists').wait(TableName='maintable')
#
# # Print out some data about the table.
# print(table.item_count)

first_frame = None
video = cv2.VideoCapture(1)

video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

speedlist = [0]
prevx = None
prevdt = datetime.datetime.now()

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
    upload_frame = frame.copy()

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

        currdt = datetime.datetime.now()
        currtime = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S")

        if x >= 640 and (prevdt + timedelta(seconds=3)) < currdt:
            prevdt = currdt

            filename = "C:\\Users\\Thomas\\Documents\\GitHub\\Real Speedometer\\speedcaps\\speedcap-" + currtime + ".jpg"
            cv2.imwrite(filename, upload_frame)

            table.put_item(
                Item={
                    'time': currtime,
                    'speed': Decimal(str(speed)[:4]),
                    'picture': 'https://res.cloudinary.com/seltz/image/upload/v1611710806/speedcap-'+currtime+'.jpg.jpg'
                }
            )

            cloudinary.uploader.upload(filename, public_id=filename[-32:])
            cloudinary.utils.cloudinary_url(filename[-32:]+'.jpg')
            os.remove(filename)

            print(currtime)

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
