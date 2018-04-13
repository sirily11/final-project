import time
from random import randint
import json
from math import degrees
def randomNumberGenerator(rang = 3):
    """
    Random inter dict generator
    """
    l = []#list
    for i in range(rang):
        l.append({'x':randint(10,100),'y':randint(10,100), 
        'name':'obj{}'.format(i)})
    return l

def readData():
    with open('data2.txt','r') as f:
        data = f.read()
        data = json.loads(data)
        ir_sensor_data = data['Ir_sensor']
        ir_degress = data['Ir_degrees']
        ir_degress = r_to_degrees(ir_degress)
    return (ir_sensor_data,ir_degress)

def r_to_degrees(l : list) -> list:
    d = []
    for i in l:
        d.append(degrees(i))
    return d

