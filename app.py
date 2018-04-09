from flask import Flask,render_template
from model.data import randomNumberGenerator
from model.robot import Robot
import json
import time
import threading
app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    """
    This is the function where the home page has been displayed.\n
    This will auto generate the data for display usage.\n
    """

    xAxis = {'title' : "X"}
    yAxis = {'title' : 'Y'}
    data = randomNumberGenerator()
    robot = {'x':20,'y':20,'name':'robot'}
    chart_title = "iRobot"
    return render_template('header.html',chart_title=chart_title,xAxis=xAxis,
                            yAxis=yAxis,data=data,robot=robot)

@app.route('/send_command')
def send_command():
    """
    This is the function for the web page to do the\n
    background processing for the controller.
    
    Returns:
        The data of the objects which robot gets.
    """

    print("clicked")
    try:
        robot = Robot()
        robot.send_command('look around')
        done = robot.read_from_robots()
        while done is not True:
            done = robot.read_from_robots()
            #wait for done
        data = listObjects(robot)
        print(data)
    except Exception as e:
        print(e)
    # thread = threading.Thread(target=robot.read_from_robots)
    # thread.start()
    # 
    return json.dumps(data)

@app.route('/up')
def up():
    robot = Robot()
    robot.send_command('forward')
    data = {"1":1}
    return json.dumps(data)

@app.route('/down')
def down():
    robot = Robot()
    robot.send_command('backward')
    data = {"1":1}
    return json.dumps(data)

@app.route('/stop')
def stop():
    robot = Robot()
    robot.send_command('stop')
    data = {"1":1}
    return json.dumps(data)

@app.route('/right')
def right():
    data = {"1":1}
    return json.dumps(data)


def listObjects(r):
    """
    read the objects from robot.
    Arguments:
        r {[list of dict]} -- [list of the objects dict]
    """
    l = []
    l.append({'x':100,'y': 0,'z' : 32,'name':'robot'})
    for i,obj in enumerate(r.objects):
        pos = obj.calculate_the_x_y_pos()
        l.append({'x':pos[0] + 100,'y':pos[1], 
        'z' :obj.calculate_width(),
        'name':'obj{}'.format(i)})
    return l

    

if __name__ == '__main__':
    app.run(port=8080, debug=True)
