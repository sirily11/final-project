import time
from random import randint

def randomNumberGenerator(rang = 3):
    """
    Random inter dict generator
    """
    l = []#list
    for i in range(rang):
        l.append({'x':randint(10,100),'y':randint(10,100), 
        'name':'obj{}'.format(i)})
    return l

