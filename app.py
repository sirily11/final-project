from flask import Flask,render_template
from model.data import randomNumberGenerator
app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    xAxis = {'title' : "X"}
    yAxis = {'title' : 'Y'}
    data = randomNumberGenerator()
    robot = {'x':20,'y':20,'name':'robot'}
    chart_title = "iRobot"
    return render_template('GUI.html',chart_title=chart_title,xAxis=xAxis,
                            yAxis=yAxis,data=data,robot=robot)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
