import os
#import pprint
import pygame
import time
from flask import url_for

class PS4Controller(object):
    """Class representing the PS4 controller. Pretty straightforward functionality."""

    controller = None
    axis_data = None
    button_data = None
    hat_data = None
    

    def __init__(self):
        """Initialize the joystick components"""
        self.isMoving = 0#0 is stop, 1 is moving forward, -1 is moving backward
        self.isRoutating = False
        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
         if not self.axis_data:
            self.axis_data = {}

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)
    

    async def listen(self):
        """Listen for events to happen"""
       
        print("start")
        await asyncio.sleep(1)
        for event in pygame.event.get():
            print("Start2")
            if event.type == pygame.JOYAXISMOTION:
                self.axis_data[event.axis] = round(event.value,2)
            elif event.type == pygame.JOYBUTTONDOWN:
                self.button_data[event.button] = True
            elif event.type == pygame.JOYBUTTONUP:
                self.button_data[event.button] = False
            elif event.type == pygame.JOYHATMOTION:
                self.hat_data[event.hat] = event.value

            # Insert your code on what you would like to happen for each event here!
            # In the current setup, I have the state simply printing out to the screen.
            
            #os.system('clear')
            #pprint.pprint(self.button_data)
            try:
                if self.axis_data[0] < -0.2:
                    #left()
                    time.sleep(0.1)
                    self.isRoutating = True
                
                elif self.axis_data[0] >0.2:
                    #right()
                    time.sleep(0.1)
                    self.isRoutating = True

                else:
                    if self.isRoutating is True:
                        #stop()
                        self.isRoutating = False


                if self.axis_data[4] > 0:
                    if self.isMoving == 1:
                        self.isMoving = 0
                        #stop()
                        time.sleep(0.05)
                        continue
                    #down()
                    self.isMoving = -1
    
                elif self.axis_data[5] > 0:
                    if self.isMoving == -1:
                        self.isMoving = 0
                        #stop()
                        time.sleep(0.05)
                        continue
                    #up()
                    self.isMoving = 1

                else:
                    if self.isMoving == 1 or self.isMoving == -1:
                        #stop()
                        self.isMoving = 0
                        
                #pprint.pprint(self.hat_data)
            except Exception as e:
                #print(e)
                pass
                


if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.listen()