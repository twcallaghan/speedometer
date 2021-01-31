import cv2
import datetime
from datetime import timedelta
import os
import boto3
from statistics import mean
import cloudinary
import cloudinary.uploader
import cloudinary.api
from decimal import *
import threading
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import statsmodels

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

app = dash.Dash('Real Speedometer', external_stylesheets=['/static/reset.css'])


def dashapp():
    # app.css.append_css({'external_stylesheets': '/static/reset.css'})
    colors = {
        'background': '#eee2d2',
        'text': '#505050'
    }

    app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
        html.H1(
            children='Elm Street Speedometer',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),

        html.P(
            children='Created in 2021 by Thomas Callaghan.',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }),

        html.P(
            children=['Connect with me on LinkedIn at ', dcc.Link(href='linkedin.com/in/twcallaghan'),
                      ' or checkout my other work at ', dcc.Link(href='thomascallaghan.me'), '.'],
            style={
                'textAlign': 'center',
                'color': colors['text']
            }),

        html.Br(),
        html.Br(),

        html.Div(style={'clear': 'both'}, children=[
            html.H2(
                children=['Top speed of the day (mph): ', ],
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'margin-right': '25%',
                    'margin-left': '15%',
                    'display': 'inline',
                }
            ),

            html.H2(
                children=['Top speed of all time (mph):', ],
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'display': 'inline',
                    'margin-left': '5%',
                }
            ),

            # html.Hr(style={'clear': 'both'})
        ]),

        html.Div(style={'clear': 'both'}, children=[
            html.H2(
                id='topofday',
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'margin-right': '25%',
                    'margin-left': '23%',
                    'display': 'inline',
                }
            ),

            html.H2(
                id='topalltime',
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'margin-left': '23%',
                    'display': 'inline',
                }
            ),

            # html.Hr(style={'clear': 'both'})
        ]),

        html.Br(),

        html.Div(style={'clear': 'both', 'backgroundColor': colors['background']}, children=[
            html.Img(
                id='toptodayimg',
                style={
                    'textAlign': 'center',
                    'width': '30%',
                    'height': '30%',
                    'margin-left': '10%'
                }
            ),

            html.Img(
                id='topalltimeimg',
                style={
                    'textAlign': 'center',
                    'width': '30%',
                    'height': '30%',
                    'margin-left': '19%'
                }
            ),

            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),


            html.H2(
                children=['All Speeds Captured'],
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
            ),

            dcc.Graph(
                id='alldatascatter',
                style={'backgroundColor': colors['background'],
                       'width': '75%',
                       'height': '75%',
                       'textAlign': 'center',
                       'margin-left': '12.5%'}
            ),
        ]),

        # dcc.Graph(
        #     id='Graph1',
        #     figure={
        #         'data': [
        #             {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
        #             {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
        #         ],
        #         'layout': {
        #             'plot_bgcolor': colors['background'],
        #             'paper_bgcolor': colors['background'],
        #             'font': {
        #                 'color': colors['text']
        #             }
        #         }
        #     }
        # ),

        dcc.Interval(
            id='interval-component',
            interval=30000,
            n_intervals=0
        )
    ])

    app.run_server(debug=True)


@app.callback([Output('topofday', 'children'), Output('topalltime', 'children'), Output('toptodayimg', 'src'),
               Output('topalltimeimg', 'src'), Output('alldatascatter', 'figure')],
              Input('interval-component', 'n_intervals')
              )
def fastest(trigger):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('maintable')

    # Going to have to get all the results and go through them manually because nosql queries suck
    result = table.scan()
    items = result['Items']

    time = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S")

    # Checking if this new entry is the top speed of the day or the top speed ever
    entries = []
    todaysentries = []
    topspeed = 5
    topspeedurl = ''
    todaystopspeed = 5
    todaystopurl = ''

    for entry in items:
        entry['speed'] = float(entry['speed'])
        if entry['speed'] > topspeed:
            topspeed = entry['speed']
            topspeedurl = entry['picture']

        if entry['time'][:10] == time[:10]:
            todaysentries.append(entry)
            if entry['speed'] > todaystopspeed:
                todaystopspeed = entry['speed']
                todaystopurl = entry['picture']
        entry['time'] = datetime.datetime.strptime(entry['time'][:13], "%m-%d-%Y-%H")
        entries.append(entry)
        # print(entry)

    entries = sorted(entries, key=lambda i: i['time'])
    dates = [x['time'] for x in entries]
    speeds = [x['speed'] for x in entries]

    df = pd.DataFrame({
        "Dates": dates,
        "Speeds": speeds,
    })

    fig = px.scatter(df, x="Dates", y='Speeds', trendline='ols')
    fig.update_traces(marker_size=15)
    # fig.update_layout(plot_bgcolor='#eee2d2')

    # topspeedurl_img = requests.get(topspeedurl).content
    # with open('speedcaps/topspeedpic.jpg', 'wb') as handler:
    #     handler.write(topspeedurl_img)
    #
    # topofday_img = requests.get(todaystopurl).content
    # with open('speedcaps/topofdaypic.jpg', 'wb') as handler:
    #     handler.write(topofday_img)

    print(topspeed)
    print(todaystopspeed)

    return todaystopspeed, topspeed, todaystopurl, topspeedurl, fig


def checkdb(time, passedspeed, frame):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('maintable')

    # Going to have to get all the results and go through them manually because nosql queries suck
    result = table.scan()
    items = result['Items']

    # Checking if this new entry is the top speed of the day or the top speed ever
    todayentries = [{'time': '', 'speed': 5}]
    allentries = []
    for entry in items:
        entry['speed'] = float(entry['speed'])
        if entry['time'][:10] == time[:10]:
            todayentries.append(entry)
        allentries.append(entry)

    todayentries = sorted(todayentries, key=lambda i: i['speed'])
    allentries = sorted(allentries, key=lambda k: k['speed'])
    print('Current top speed: {}'.format(todayentries[-1]['speed']))
    print('Most recent speed: {}'.format(passedspeed))
    # print(mostrecent)
    if passedspeed > todayentries[-1]['speed'] or passedspeed > allentries[-1]['speed']:
        filename = "C:\\Users\\Thomas\\Documents\\GitHub\\Real Speedometer\\speedcaps\\speedcap-" + time + ".jpg"
        cv2.imwrite(filename, frame)

        table.put_item(
            Item={
                'time': time,
                'speed': Decimal(str(passedspeed)[:4]),
                'picture': 'https://res.cloudinary.com/seltz/image/upload/v1611710806/speedcap-' + time + '.jpg.jpg'
            }
        )

        cloudinary.uploader.upload(filename, public_id=filename[-32:])
        cloudinary.utils.cloudinary_url(filename[-32:] + '.jpg')
        os.remove(filename)

    else:
        table.put_item(
            Item={
                'time': time,
                'speed': Decimal(str(passedspeed)[:4])
            }
        )


def main():
    # When you need to grab image from url:
    # img_data = requests.get(image_url).content
    # with open('image_name.jpg', 'wb') as handler:
    #     handler.write(img_data)
    from boto3.dynamodb.conditions import Key

    cloudinary.config(cloud_name='seltz',
                      api_key='346981549637338',
                      api_secret=os.environ.get('Cloudinary_Secret'))

    first_frame = None
    video = cv2.VideoCapture(1)

    video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    speedlist = [0]
    prevx = None
    prevdt = datetime.datetime.now()

    while True:
        check, frame = video.read()
        frameinuse = frame.copy()
        gray = cv2.cvtColor(frameinuse, cv2.COLOR_BGR2GRAY)
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
            if cv2.contourArea(contour) < 10000:
                continue
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frameinuse, (x, y), (x + w, y + h), (0, 255, 0), 3)
            if prevx is None or prevx < 200 or prevx > 1000:
                prevx = x
            inches = abs(x - prevx) * (504 / 1280)
            speed = inches * (30 / 17.6)  # inches * fps of video / 17.6 to convert into mph
            speedlist.append(speed)
            carx = x
            cary = y

            currdt = datetime.datetime.now()
            currtime = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S")

            if 200 <= x <= 1000 and (prevdt + timedelta(seconds=3)) < currdt and speed > 15 and x > prevx:
                prevdt = currdt
                dbthread = threading.Thread(target=checkdb, args=(currtime, speed, frame))
                dbthread.start()

            prevx = x

        frame_copy = frameinuse.copy()
        recentavgspeed = mean(speedlist[-10:])
        cv2.putText(frame_copy, "Current (avg) speed: {:.2f}".format(recentavgspeed), (carx, cary - 60), font, 0.7,
                    (0, 0, 200), 2)
        cv2.imshow('Capturing', frame)
        cv2.imshow('Contour_window', frame_copy)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # main()
    # MAY HAVE TO THREAD MAIN AND THE APP AT THE SAME TIME?
    opencvthread = threading.Thread(target=main)
    opencvthread.start()
    dashapp()
