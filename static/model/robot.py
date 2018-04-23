import math
import pickle
import threading
import matplotlib.pyplot as plt
import numpy as np
import serial
from keras import Sequential
from keras.layers import Dense, Dropout, Activation
from matplotlib import animation
from sklearn import preprocessing
from sklearn.svm import SVR
import json
import time
import keras


class Robot:
    def __init__(self, baudrate=115200):
        # Setting the connection
        self.ip = '192.168.1.1'
        self.port = 288
        self.serial = serial.serial_for_url(
            "socket://{}:{}".format(self.ip, self.port))
        self.serial.baudrate = baudrate
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.stopbits = serial.STOPBITS_TWO
        self.serial.parity = serial.PARITY_NONE
        '''
        Setting the machine learning
        '''
        self.model = SVR(kernel='rbf', C=1e3, gamma=0.1)
        # self.model = self.__create_model__()
        self.times = 0
        self.data = 0
        '''
        Setting the robot's data
        '''
        self.pin_degree = 0
        self.pin_sensor_radians = []
        self.ir_degree = 0
        self.ir_sensor_radians = []
        self.pin_sensor_data = []
        self.ir_sensor_data = []
        self.ir_data = 0
        self.distances = []
        self.labels = []
        '''
        Setting the plotting
        '''
        # self.fig = plt.figure()
        # self.ax1 = self.fig.add_subplot(1, 1, 1, projection='polar')
        # self.ax1.set_rmax(120)
        # self.ax2 = self.fig.add_subplot(1, 1, 1, projection='polar')
        # self.ax1.set_rmax(120)

        '''
        Object detection
        '''
        self.hasObject = False
        self.obj_num = 0
        self.start_edge_degree = 0
        self.end_edge_degree = 0
        self.obj_distance = 0
        self.objects = []
        

        # This is the data from moving
        self.distance = 0
        self.x_pos = 0
        self.y_pos = 0
        self.angle = 0
        self.source = None

    def read_from_robots(self):
        # 24cm is 1314
        reply = str(self.serial.readline())

        if reply[2] == 'd':
            print("Object number is " + str(len(self.objects)))
            self.obj_num = 0
            # with open('data24.json', 'w') as f:
            #     data = {'Pin_sensor': self.pin_sensor_data, 'Pin_degrees': self.pin_sensor_radians,
            #             'Ir_sensor': self.ir_sensor_data, 'Ir_degrees': self.ir_sensor_radians}
            #     f.write(json.dumps(data))
            #     f.close()
            self.object_detection(self.ir_sensor_data,self.pin_sensor_data)
            return True

        # p stands for ping sensor data
        if reply[2] == 'p':
            data = float(reply[3:-3])
            if(data < 0):
                data = 0
            self.pin_sensor_data.append(data)
            self.pin_degree += 2
            self.pin_sensor_temp_data = data
            self.pin_sensor_radians.append(math.radians(self.pin_degree))
            self.distance = data

        # i stands for ir sensor data
        if reply[2] == 'i':
            data = float(reply[3:-3])
            if(data < 0):
                data = 0
            self.ir_sensor_data.append(data)
            self.ir_degree += 2
            self.ir_sensor_radians.append(math.radians(self.ir_degree))
            self.ir_data = data

        # m stands for moving distance data
        if reply[2] == 'm':
            data = float(reply[3:-3])
            self.x_pos += data

        if reply[2] == 'a':
            data = float(reply[3:-3])
            self.angle += data

        if reply[2] == 'x':
            data = float(reply[3:-3])
            self.x_pos = data

        if reply[2] == 'y':
            data = float(reply[3:-3])
            self.y_pos = data

        # For label
        if reply[2] == 'l':
            data = float(reply[3:-3])
            self.labels.append(data)

        return reply

    def calculate_the_distance(self, selection="train", ir_data=None, save=True, model_name=None):
        """
        This method is using machine learning to calibrate the IR sensor.
        This using pin_sensor data as the label and ir sensor data as the
        data sources\n.
        param selection:\n
        train --- train the model \n
        use --- use the pre-train model
        :return:
        """
        if selection == "train":
            try:

                # x = np.reshape(self.ir_sensor_data, (-1, 1))
                # y = np.reshape(self.pin_sensor_data, (-1, 1))
                # print("Get data size : {} ".format(len(x)))
                # print("Get all the data")
                # # X_scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
                # # y_scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
                # print("transform the data")
                # # x = X_scaler.fit_transform(x)
                # # y = y_scaler.fit_transform(y)
                # # print(x.shape,y.shape)
                # # self.model.fit(x, y,epochs=200)
                # self.model.fit(x,y.ravel())
                # print("Finished training")
                # if save == True:
                #     if model_name is not None:
                #         self.__saving_model__(model_name)
                #     else:
                #         self.__saving_model__()
                # return self.model.predict(X_scaler.inverse_transform(x))
                with open('ir_sensor_model', 'w') as f:
                    d = {'ir_data': self.ir_sensor_data,
                         'pin_data': self.pin_sensor_data}
                    d = json.dumps(d)
                    f.write(d)
            except Exception as e:
                print(e)
                pass
        if selection == "use":
            # if ir_data is None:
            #     raise Exception("you need to have your ir data")
            # try:
            #     if model_name is not None:
            #         self.__load_model__(model_name)
            #     else:
            #         self.__load_model__()
            #     #ir_data = np.reshape(ir_data,(-1,1))
            #     return self.model.predict(ir_data)
            with open('ir_sensor_model', 'r') as f:
                d = f.read()
                d = json.loads(d)
                pin = d['pin_data']
                ir = d['ir_data']
                select = 0
                for i, d in enumerate(ir):
                    if ir_data > d:
                        continue
                    else:
                        select = i - 1
                unit = (pin[select] - pin[select - 1]) / \
                    (ir[select] - ir[select - 1])
                return pin[select] + (ir_data - ir[select])*unit

    def calibration(self):
        for i in range(30):
            self.send_command("backward")
            time.sleep(0.08)
            self.send_command("stop")

            for i in range(5):
                self.read_from_robots()

            time.sleep(0.5)
        prediction = self.calculate_the_distance()

    def move_to_smallest_obj(self):
        try:
            angle = self.find_smallest_objets().degree
            angle = int(math.degrees(angle))
            #print("Move to {} degree".format(angle))
            self.send_command('turn around', angle)
        except Exception as e:
            self.send_command('turn around', 0)

    def __saving_model__(self, pkl_filename='ir_sensor_model'):
        with open(pkl_filename, 'wb') as f:
            pickle.dump(self.model, f)
        # self.model.save(pkl_filename)

    def __load_model__(self, pkl_filename='ir_sensor_model'):
        # with open(pkl_filename, 'rb') as f:
        #     self.model = pickle.load(f)
        return keras.models.load_model("/Users/qiweili/Desktop/Spring2018/CPRE288/final project/final-project/static/model/model.h5")

    def send_command(self, command, degree=None):
        """
        This should send a command to robot\n
        :param command: Command for robot\n
        'forward' - 1\n
        'backward' - 2\n
        """
        if command == 'forward':
            self.serial.write(str.encode('1'))

        if command == 'backward':
            self.serial.write(str.encode('2'))

        if command == 'stop':
            self.serial.write(str.encode('3'))

        if command == 'left':
            self.serial.write(str.encode('5'))

        if command == 'right':
            self.serial.write(str.encode('4'))

        if command == 'look around':
            print("Sending command look around")
            self.serial.write(str.encode('9'))

        if command == 'ping':
            self.serial.write(str.encode('p'))

        if command == 'turn around':
            d = ''
            print("Got the command " + str(degree))
            if degree < 0 or degree > 180:
                degree = 0
            if(degree < 100):
                d = '0' + str(degree)
            else:
                d = str(degree)
            self.serial.write(str.encode('8'))
            self.serial.write(str.encode(d))
            print("Turnning to " + d)

        if command == 'music':
            self.serial.write(str.encode('m'))

        if command == 'reset':
            self.serial.write(str.encode('r'))

    def send_str(self, message):
        self.serial.write(str.encode(message))

    def object_detection(self, ir_data,pin_data):
        """[summary]
        Helper method for object detection

        Arguments:
            ir_data {[type]} -- [description]
        """
        # if ir_data > 100:
        #     return
        print(len(self.ir_sensor_data))
        #prev_ir_data = self.ir_sensor_data[len(self.ir_sensor_data) - 4]
        # if  ir_data - self.pin_sensor_data[len(self.pin_sensor_data) - 1]< 18 and self.hasObject is False:
        #     self.hasObject = True
        #     self.obj_num = self.obj_num + 1
        #     print("Object!")
        #     #in radiens
        #     self.start_edge = self.ir_sensor_radians[len(self.ir_sensor_radians) -1]

        # #If there is a object in front of the robot, then save them into a objects list
        # if  ir_data - self.pin_sensor_data[len(self.pin_sensor_data) - 1]> 18 and self.hasObject is True:
        #     self.hasObject = False
        #     self.end_edge = self.ir_sensor_radians[len(self.ir_sensor_radians) - 1]
        #     distance = (self.pin_sensor_data[len(self.pin_sensor_data) - 3] +
        #                 self.pin_sensor_data[len(self.pin_sensor_data) - 4])/2

        #     obj = objs(starting_edge=self.start_edge,
        #                              ending_edge=self.end_edge,distance=distance)
        #     if obj.calculate_width() != 0:
        #         self.objects.append(obj)

        #     print("Width is {}".format(self.objects[len(self.objects) - 1].calculate_width()))
        #     print()
        self.model = self.__load_model__()
        for i,d in enumerate(ir_data):
            predict_value = np.array([ir_data[i],pin_data[i]])
            predict_value = predict_value.reshape((1,2))
            #print("Prediction : {}".format(self.model.predict(predict_value)[0]))
            if self.model.predict(predict_value)[0][1] >= 5.0e-05 and self.hasObject is False:
                self.hasObject = True
                self.obj_num = self.obj_num + 1
                print("Object!")
                self.start_edge = self.ir_sensor_radians[len(
                    self.ir_sensor_radians) - 1]
            if  self.model.predict(predict_value)[0][1] < 3.0e-05 and self.hasObject is True:
                self.hasObject = False
                self.end_edge = self.ir_sensor_radians[i - 1]
                distance = pin_data[i]

                obj = objs(starting_edge=self.start_edge,
                        ending_edge=self.end_edge, distance=distance)
                # if obj.calculate_width() != 0:
                self.objects.append(obj)

                # print("Width is {}".format(
                #     self.objects[len(self.objects) - 1].calculate_width()))
                # print()

    def normalized_raw_data(self):
        returnData = []
        for i in self.ir_sensor_data:
            returnData.append(self.calculate_the_distance("use", ir_data=i))
        return returnData

    def __create_model__(self):

        model = Sequential()
        model.add(Dense(2, input_shape=(2,),
                        kernel_initializer='normal', activation='relu'))
        model.add(Dense(100, kernel_initializer='normal', activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(200, kernel_initializer='normal', activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(100, kernel_initializer='normal', activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(1, kernel_initializer='normal', activation='sigmoid'))
        model.compile(loss='binary_crossentropy',
                      optimizer='adam', metrics=['accuracy'])

        return model

    def find_smallest_objets(self):
        time.sleep(0.1)
        smallest_width = self.objects[0].calculate_width()
        smallest_index = 0
        for c, i in enumerate(self.objects):
            if i.calculate_width() < smallest_width:
                smallest_width = i.calculate_width()
                smallest_index = c
        print("Move to the object{}".format(smallest_index))
        return self.objects[smallest_index]


class objs:
    def __init__(self, starting_edge, ending_edge, distance):
        self.starting_edge = starting_edge
        self.ending_edge = ending_edge
        # the distance from robot to the front of the object
        self.distance = distance
        # calculate the center degree
        self.angle = starting_edge + (ending_edge - starting_edge)/2

    def calculate_width(self):
        width = (self.distance *
                 math.tan(self.ending_edge - self.starting_edge)/2)*2
        # if width < 3:
        #     return 0
        # if width > 25:
        #     return 0
        return width

    def calculate_the_x_y_pos(self,angle,x_pos,y_pos):
        dis_from_surface_to_center = self.calculate_width()/2

        dis_from_robot_to_center = dis_from_surface_to_center + self.distance
        angle_from_x_to_center = self.angle + angle
        x = dis_from_robot_to_center * \
            math.cos(math.radians(angle_from_x_to_center)) + x_pos
        y = dis_from_robot_to_center * \
            math.sin(math.radians(angle_from_x_to_center)) + y_pos
        return [x, y]


class moving_obj:
    def __init__(self, angle, distance):
        self.angle = angle
        self.distance = distance

    def calculate_the_x_y_pos(self):
        x = math.cos(math.radians(self.angle))*self.distance
        y = math.sin(math.radians(self.angle))*self.distance

# robot = Robot()
# robot.calibration()
