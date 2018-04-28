from flask import Flask, render_template, request
from static.model.data import randomNumberGenerator, readData, r_to_degrees
from static.model.robot import Robot
import ps4Controller
import json
import time
import threading
import pprint
import asyncio
from math import cos, sin, radians
app = Flask(__name__)
global x
global y
import math
import random

controller = ps4Controller.PS4Controller()
thread = threading.Thread(target=controller.listen)
thread.start()

@app.route('/')
@app.route('/home')
def home():
    """
    This is the function where the home page has been displayed.\n
    This will auto generate the data for display usage.\n
    """

    xAxis = {'title': "X"}
    yAxis = {'title': 'Y'}
    data = randomNumberGenerator()

    chart_title = "iRobot"
    return render_template('header.html', chart_title=chart_title, xAxis=xAxis,
                           yAxis=yAxis, data=0)


@app.route('/scan')
def send_command():
    """
    This is the function for the web page to do the\n
    background processing for the controller.

    Returns:
        The data of the objects which robot gets.
    """
    # data = {}
    # try:
    #     robot = Robot()
    #     robot.send_command('look around')

    #     done = robot.read_from_robots()
    #     while done is not True:
    #         done = robot.read_from_robots()
    #         # wait for done
    #     data = listObjects(robot, x, y)
        
    # # robot.move_to_smallest_obj()
    # except Exception as e:
    #     print(e)
    # return json.dumps(data)
    # thread = threading.Thread(target=robot.read_from_robots)
    # thread.start()
    ir = []
    pin = []
    data = {}
    robot = Robot()
    robot.send_command('look around')
    done = robot.read_from_robots()
    while done is not True:
        done = robot.read_from_robots()
    print(len(robot.objects))
    robot.send_command("stop")
    x = robot.x_pos
    y = robot.y_pos
    data = listObjects(robot, x, y,robot.angle)

    # Dict of ir data and ping data
    return json.dumps(data)


@app.route('/raw_data')
def get_raw_data():
    """[summary]
    This is the function for getting the raw data from robot
    Returns:
        [type] -- [description]
    """

    ir = []
    pin = []
    data = {}
    try:
        robot = Robot()
        robot.send_command('look around')
        done = robot.read_from_robots()
        while done is not True:
            done = robot.read_from_robots()
        print("Getting the raw data")
        ir_data = robot.ir_sensor_data
        ir_degress = r_to_degrees(robot.ir_sensor_radians)
        cal_ir_data = []
        for i in ir_data:
            #cal_ir_data.append(robot.calculate_the_distance(selection="use",ir_data=i))
            cal_ir_data.append(i)
        pin_data = robot.pin_sensor_data
        pin_degress = r_to_degrees(robot.pin_sensor_radians)
        robot.send_command("stop")
        for i, d in enumerate(cal_ir_data):
            ir.append([ir_degress[i], d])

        for i, d in enumerate(pin_data):
            pin.append([pin_degress[i], d])


        # Dict of ir data and ping data
        data = {'pin': pin, 'ir': ir}
    except Exception as e:
        print(e)
    return json.dumps(data)


@app.route('/up')
def up():
    """[summary]
    Moving forward
    Returns:
        [type] -- [description]
    """

    robot = Robot()
    robot.send_command('forward')
    #distance = robot.read_from_robots()
    x = 0
    y = 0
    return json.dumps(0)


@app.route('/down')
def down():
    """[summary]
    Moving backward
    Returns:
        [type] -- [description]
    """

    robot = Robot()
    robot.send_command('backward')
    #distance = robot.read_from_robots()
    data = {"1": 1}
    return json.dumps(0)


@app.route('/stop')
def stop():
    """[summary]
    Stop the robot
    Returns:
        [type] -- [description]
    """

    robot = Robot()
    robot.send_command('stop')
    time.sleep(0.1)
    for i in range(2):
        robot.read_from_robots()
    # Data from robot
    # 
    # obj = listObjectWhileMoving(robot.calculate_the_distance(selection="use",ir_data=robot.ir_data), 
    #                             robot.x_pos,
    #                             robot.y_pos, robot.angle)
    #cancel the print object while moving
    data = {"x": robot.x_pos, "y": robot.y_pos, "angle": robot.angle}
    return json.dumps(data)


@app.route('/right')
def right():
    """[summary]
    Turning right
    
    Returns:
        [type] -- [description]
    """

    robot = Robot()
    robot.send_command('right')
    #distance = robot.read_from_robots()
    return json.dumps(0)


@app.route('/left')
def left():
    """[summary]
    Turnning left
    Returns:
        [type] -- [description]
    """

    robot = Robot()
    robot.send_command('left')
    #distance = robot.read_from_robots()
    return json.dumps(0)


@app.route('/music')
def music():
    """[summary]
    Play music
    Returns:
        [type] -- [description]
    """

    robot = Robot()
    robot.send_command('music')
    data = {"1": 1}
    return json.dumps(data)


@app.route('/reset_pos')
def reset_pos():
    """[summary]
    Reset the robot
    Returns:
        [type] -- [description]
    """

    robot = Robot()
    robot.send_command('reset')
    print("Reset")
    data = {"1": 1}
    return json.dumps(data)

@app.route('/auto')
def auto():
    """
    Let the robot auto move
    """

    
    robot = Robot()
    starting_time = time.time()
    turned = False
    while True:
        robot.send_command("forward")
        time.sleep(random.uniform(1,2))
        robot.send_command("stop")
        time.sleep(4.6)
        time.sleep(0.5)
        robot.send_command("look around")
        print("Looking around")
        done = robot.read_from_robots()
        while done is not True:
            done = robot.read_from_robots()
        robot.send_command("stop")
        time.sleep(4)
        print(len(robot.objects))

        if turned is False and time.time() - starting_time > 260:
            robot.send_command("left")
            time.sleep(4)
            robot.send_command("stop")
            turned = True

        if(len(robot.objects) > 2):
            count = 0
            for i in robot.objects:
                if i.calculate_width() < 13:
                    count = count + 1
            if(count >= 2):
                robot.send_command("music") 
                robot.send_command("stop")
                print("Finished!!!")
            break
        if time.time() - starting_time > 300:
            robot.send_command("music")
            robot.send_command("stop")
            print("Finished!!!")
            break
        robot.objects = []
    return 

def ping():
    robot = Robot()
    robot.send_command('ping')


def listObjects(r, add_x=0, add_y=0,angle=0):
    """
    read the objects from robot.
    Arguments:
        r {[list of dict]} -- [list of the objects dict]
    """
    l = []
    #l.append({'x': 100, 'y': 0, 'z': 32, 'name': 'robot'})
    for i, obj in enumerate(r.objects):
        pos = obj.calculate_the_x_y_pos(angle,add_x,add_y)
        obj.calculate_width()
        width =0
        if obj.type =="small":
            width = 5
        else:
            width = 11

        l.append({'x': pos[0] + add_x, 'y': pos[1]+add_y,
                  'z':width,
                  'name': 'obj{}'.format(i)})
    return l


def listObjectWhileMoving(distance, x, y, angle):
    
    x = round(math.cos(math.radians(angle))*distance + x,2)
    y = round(math.sin(math.radians(angle))*distance + y,2)
    if(distance < 50):
        return {'x' : x , 'y' : y, 'z' : 3, 'name' : 'obj'}
    else:
        return {}


if __name__ == '__main__':
    
    app.run(port=8080, debug=True)
    # controller = ps4Controller.PS4Controller()
    # controller.listen()