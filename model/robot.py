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

class Robot:
    def __init__(self, baudrate=115200):
        # Setting the connection
        self.ip = '192.168.1.1'
        self.port = 42880
        self.serial = serial.serial_for_url("socket://{}:{}".format(self.ip, self.port))
        self.serial.baudrate = baudrate
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.stopbits = serial.STOPBITS_TWO
        self.serial.parity = serial.PARITY_NONE
        '''
        Setting the machine learning
        '''
        #self.model = SVR(kernel='rbf', C=1e3, gamma=0.1)
        self.model = self.__create_model__()
        self.times = 0
        self.data = 0
        '''
        Setting the robot's data
        '''
        self.pin_degree = 0
        self.pin_sensor_degrees = []
        self.ir_degree = 0
        self.ir_sensor_degrees = []
        self.pin_sensor_data = []
        self.pin_sensor_temp_data = 0
        self.ir_sensor_data = []
        self.distances = []
        '''
        Setting the plotting
        '''
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1, 1, 1, projection='polar')
        self.ax1.set_rmax(120)
        self.ax2 = self.fig.add_subplot(1, 1, 1, projection='polar')
        self.ax1.set_rmax(120)

        '''
        Object detection
        '''
        self.hasObject = False
        self.obj_num = 0
        self.start_edge_degree = 0
        self.end_edge_degree = 0
        self.obj_distance = 0
        self.objects = []


        self.moving_distance = 0
        self.source = None

    def read_from_robots(self):
        # 24cm is 1314
        reply = str(self.serial.readline())

        if reply[2] == 'd':
            print("Object number is " + str(self.obj_num))
            self.obj_num = 0
            # with open('data2.txt','w') as f:
            #     data = {'Pin_sensor' : self.pin_sensor_data,'Pin_degrees' : self.pin_sensor_degrees,
            #             'Ir_sensor' : self.ir_sensor_data,'Ir_degrees':self.ir_sensor_degrees}
            #     f.write(json.dumps(data))
            #     f.close()
            # angle  = self.find_smallest_objets().degree
            # angle = math.degrees(angle)
            # print("Move to {} degree".format(angle))
            # self.send_command('turn around',angle)
            return True

        if reply[2] == 'p':
            data = float(reply[3:-3])
            self.pin_sensor_data.append(data)
            self.pin_degree += 2
            self.pin_sensor_temp_data = data
            self.pin_sensor_degrees.append(math.radians(self.pin_degree))

        if reply[2] == 'i':
            data = float(reply[3:-3])

            self.ir_sensor_data.append(data)
            self.ir_degree += 2
            self.ir_sensor_degrees.append(math.radians(self.ir_degree))
            self.object_detection(data)
        return reply

    def __reset_degree__(self):
        if self.pin_degree >= 180 and self.ir_degree >= 180:
            self.pin_degree = 0
            self.ir_degree = 0
            self.ir_sensor_degrees = []
            self.pin_sensor_degrees = []
            self.pin_sensor_data = []
            self.ir_sensor_data = []

    def grah_plot(self, i):
        """
        :param ir_raw_data: using raw data from IR sensor
        :return:
        """
        try:
            self.read_from_robots()
            self.read_from_robots()
        except Exception as e :
            print(e)
        self.ax1.clear()
        self.ax2.clear()
        #self.ax1.plot(np.array(self.pin_sensor_degrees), np.array(self.pin_sensor_data),label='pin')
        self.ax2.plot(np.array(self.ir_sensor_degrees), np.array(self.ir_sensor_data),label='ir')
        plt.legend()

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
                x = np.reshape(self.ir_sensor_data, (-1, 1))
                y = np.reshape(self.pin_sensor_data, (-1, 1))
                print("Get all the data")
                X_scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
                y_scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
                print("transform the data")
                x = X_scaler.fit_transform(x)
                y = y_scaler.fit_transform(y)
                # print(x.shape,y.shape)
                self.model.fit(x, y,epochs=200)
                if save == True:
                    if model_name is not None:
                        self.__saving_model__(model_name)
                    else:
                        self.__saving_model__()
                return self.model.predict(X_scaler.inverse_transform(x))
            except Exception as e:
                print(e)
        if selection == "use":
            if ir_data is None:
                raise Exception("you need to have your ir data")
            try:
                if model_name is not None:
                    self.__load_model__(model_name)
                else:
                    self.__load_model__()
                return self.model.predict(ir_data)[0]
            except Exception as e:
                print(e)

    def calibration(self):
        done = False
        print("Start calibration")
        self.send_command("look around")
        while done is not True:
            done = self.read_from_robots()
            if done is True:
                prediction = self.calculate_the_distance()
                print(prediction)
                self.ax1.plot(self.pin_sensor_degrees,self.pin_sensor_data,label="Pin")
                self.ax2.plot(self.ir_sensor_degrees,prediction,label='IR')
                plt.legend()
                plt.show()

            self.read_from_robots()

    def __saving_model__(self, pkl_filename='ir_sensor_model'):
        #with open(pkl_filename, 'wb') as f:
            #pickle.dump(self.model, f)
        self.model.save(pkl_filename)

    def __load_model__(self, pkl_filename='ir_sensor_model'):
        # with open(pkl_filename, 'rb') as f:
        #     self.model = pickle.load(f)
        self.model.load_weights(filepath=pkl_filename)

    def send_command(self, command,degree = None):
        """
        This should send a command to robot\n
        :param command: Command for robot\n
        'forward' - 1\n
        'backward' - 2\n
        """
        if command == 'forward':
            self.serial.write(str.encode('1'))
            self.moving_distance -= 5

        if command == 'backward':
            self.serial.write(str.encode('2'))
            self.moving_distance += 5

        if command == 'stop':
            self.serial.write(str.encode('3'))

        if command == 'look around':
            self.serial.write(str.encode('9'))

        if command == 'turn around':
            d = ''
            if(degree < 100):
                d = '0' + str(degree)
            else:
                d = str(degree)
            self.serial.write(str.encode('8'))
            self.serial.write(str.encode(d))


    def send_str(self, message):
        self.serial.write(str.encode(message))

    def object_detection(self,ir_data):
        """[summary]
        Helper method for object detection
        
        Arguments:
            ir_data {[type]} -- [description]
        """
        try:
            if ir_data > 400 and self.hasObject is False :
                self.hasObject = True
                self.obj_num = self.obj_num + 1
                print("Object!")
                self.start_edge_degree = self.ir_sensor_degrees[len(self.ir_sensor_degrees) -1]

            #If there is a object in front of the robot, then save them into a objects list
            if ir_data < 400 and self.hasObject is True:
                self.hasObject = False
                self.end_edge_degree = self.ir_sensor_degrees[len(self.ir_sensor_degrees) - 1]
                degree = self.end_edge_degree - self.start_edge_degree
                distance = self.pin_sensor_data[len(self.pin_sensor_data) - 4]

                self.objects.append(objs(starting_edge_degree=self.start_edge_degree,
                                         ending_edge_degree=self.end_edge_degree,distance=distance))

                print("Degree is :{}".format(degree))
                print("Width is {}".format(self.objects[len(self.objects) - 1].calculate_width()))
                print()

        except Exception as e:
            pass

    def normalized_raw_data(self):
        returnData = []
        for i in self.ir_sensor_data:
            returnData.append(self.calculate_the_distance("use", ir_data=i))
        return returnData

    def __create_model__(self):
        model = Sequential()
        model.add(Dense(512, input_dim=1, activation='relu'))
        model.add(Dropout(.2))
        model.add(Activation("linear"))
        model.add(Dense(256, activation='relu'))
        model.add(Activation("linear"))
        model.add(Dense(128, activation='relu'))
        model.add(Activation("linear"))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(1))
        model.compile(loss='mse', optimizer='adam', metrics=["accuracy"])
        #model.summary()
        return model

    def find_smallest_objets(self):
        smallest_width = self.objects[0].calculate_width()
        smallest_index = 0
        for c,i in enumerate(self.objects):
            if i.calculate_width() < smallest_width:
                smallest_width = i.calculate_width()
                smallest_index = c
        print("Move to the object{}".format(smallest_index))
        return self.objects[smallest_index]


class objs:
    def __init__(self,starting_edge_degree,ending_edge_degree,distance):
        self.starting_edge = starting_edge_degree
        self.ending_edge = ending_edge_degree
        #the distance from robot to the front of the object
        self.distance = distance
        #calculate the center degree
        self.degree = starting_edge_degree + (ending_edge_degree - starting_edge_degree)/2

    def calculate_width(self):
        return (self.distance * math.tan((self.ending_edge - self.starting_edge)/2))*2

    def calculate_the_x_y_pos(self):
        dis_from_surface_to_center = self.calculate_width()/2

        dis_from_robot_to_center = dis_from_surface_to_center + self.distance
        degree_from_x_to_center = self.degree
        x = dis_from_robot_to_center * math.cos(degree_from_x_to_center)
        y = dis_from_robot_to_center * math.sin(degree_from_x_to_center)
        return [x,y]


# robot = Robot()
# #robot.calibration()
# robot.send_command('look around')
# #robot.send_command(command='turn around',degree=95)

# while True:
#     command  = input("Command: ")
#     robot.send_command(command)
#     ani = animation.FuncAnimation(robot.fig, robot.grah_plot, interval=155)
#     plt.show()


#robot.send_command("look around")
# print(robot.normalized_raw_data())
# fig = plt.figure()
# ax1 = fig.add_subplot(1, 1, 1, projection='polar')
# ax2 = fig.add_subplot(1, 1, 1, projection='polar')
# ax1.plot(robot.ir_sensor_degrees, robot.normalized_raw_data(), label='ir')
# ax2.plot(robot.pin_sensor_degrees, robot.pin_sensor_data, label='pin')
# ax1.legend()
# plt.show()
