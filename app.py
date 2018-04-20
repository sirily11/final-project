from flask import Flask, render_template, request
from model.data import randomNumberGenerator, readData, r_to_degrees
from model.robot import Robot
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


# controller = ps4Controller.PS4Controller()
# thread = threading.Thread(target=controller.listen)
# thread.start()

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
    data = {}
    try:
        robot = Robot()
        robot.send_command('look around')
        robot.read_from_robots()
        robot.read_from_robots()
        robot.read_from_robots()
        x = robot.x_pos
        y = robot.y_pos
        done = robot.read_from_robots()
        while done is not True:
            done = robot.read_from_robots()
            # wait for done
        data = listObjects(robot, x, y)
    # robot.move_to_smallest_obj()
    except Exception as e:
        print(e)
    return json.dumps(data)
    # thread = threading.Thread(target=robot.read_from_robots)
    # thread.start()


@app.route('/raw_data')
def get_raw_data():
    ir = []
    pin = []
    data = {}
    try:
        robot = Robot()
        robot.send_command('look around')
        done = robot.read_from_robots()
        while done is not True:
            done = robot.read_from_robots()

        ir_data = robot.ir_sensor_data
        ir_degress = r_to_degrees(robot.ir_sensor_radians)
        pin_data = robot.pin_sensor_data
        pin_degress = r_to_degrees(robot.pin_sensor_radians)

        for i, d in enumerate(ir_data):
            ir.append([ir_degress[i], d])

        for i, d in enumerate(pin_data):
            pin.append([pin_degress[i], d])

        # Dict of ir data and ping data
        data = {'pin': pin, 'ir': ir}
        print(data)
    except Exception as e:
        print(e)
    return json.dumps(data)


@app.route('/up')
def up():
    robot = Robot()
    robot.send_command('forward')
    #distance = robot.read_from_robots()
    x = 0
    y = 0
    return json.dumps(0)


@app.route('/down')
def down():
    robot = Robot()
    robot.send_command('backward')
    #distance = robot.read_from_robots()
    data = {"1": 1}
    return json.dumps(0)


@app.route('/stop')
def stop():
    robot = Robot()
    robot.send_command('stop')
    time.sleep(0.1)
    for i in range(5):
        robot.read_from_robots()
    # Data from robot
    print("IR data: {} {}".format(robot.calculate_the_distance(selection="use",ir_data=robot.ir_data),robot.ir_data))
    obj = listObjectWhileMoving(robot.distance, robot.x_pos,
                                robot.y_pos, robot.angle)
    data = {"x": robot.x_pos, "y": robot.y_pos, "angle": robot.angle,'obj' : obj,'distance':robot.distance}
    pprint.pprint(data)
    return json.dumps(data)


@app.route('/right')
def right():
    robot = Robot()
    robot.send_command('right')
    #distance = robot.read_from_robots()
    return json.dumps(0)


@app.route('/left')
def left():
    robot = Robot()
    robot.send_command('left')
    #distance = robot.read_from_robots()
    return json.dumps(0)


@app.route('/music')
def music():
    robot = Robot()
    robot.send_command('music')
    data = {"1": 1}
    return json.dumps(data)


@app.route('/reset_pos')
def reset_pos():

    robot = Robot()
    robot.send_command('reset')
    print("Reset")
    data = {"1": 1}
    return json.dumps(data)

@app.route('/machine_learning')
def machine_learning():
     robot = Robot()
     robot.calibration()
     return "Done"

def ping():
    robot = Robot()
    robot.send_command('ping')


def listObjects(r, add_x=0, add_y=0):
    """
    read the objects from robot.
    Arguments:
        r {[list of dict]} -- [list of the objects dict]
    """
    add_x = add_x + 15
    add_y = add_y + 15
    l = []
    #l.append({'x': 100, 'y': 0, 'z': 32, 'name': 'robot'})
    for i, obj in enumerate(r.objects):
        pos = obj.calculate_the_x_y_pos()
        l.append({'x': pos[0] + add_x, 'y': pos[1]+add_y,
                  'z': obj.calculate_width(),
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
