import keras
from keras.models import Sequential
from keras.layers import LSTM,Conv1D,MaxPooling1D,Flatten
from keras.layers.core import Flatten, Dense, Dropout
from keras.layers.convolutional import Convolution2D, MaxPooling2D, ZeroPadding2D
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import matplotlib.pyplot as plt
import pandas as pd
import json
import numpy as np
from sklearn import svm

#number of files
file_num = 25
epochs = 100
model_name = "objectDetection.model"

def readData():
    x = []
    y = []
    for i in range(file_num):
        file_name = 'data{}.json'.format(i)
        try:
            with open(file_name,'r') as f:
                d = f.read()
                d = json.loads(d)
                data = []
                for j in range(len(d['Ir_sensor'])):
                    data.append([d['Ir_sensor'][j],d['Pin_sensor'][j]])
                    #modify this part for labels
                if(i < 10):
                    y.append(1)
                else:
                    y.append(0)
            x.append(data)
        except Exception as e:
            continue
    
    np_y = []
    for i in y:
        if(i == 0):
            np_y.append([1,0])
        else:
            np_y.append([0,1])
    np_x = np.array(x)
    np_y = np.array(np_y)
    print("X shape is {}".format(np_x.shape))
    print("Y shape is {}".format(np_y.shape))
    # np_x = preprocessing.scale(np_x)
    print(np_x[0])
    X_train, X_test, y_train, y_test = train_test_split(np_x, np_y, test_size=0.2, random_state=42)
    return (X_train,X_test,y_train,y_test)

def model():
    # model = Sequential()
    # model.add(Dense(10,input_dim=2,kernel_initializer='normal', activation='relu'))
    # model.add(Dense(100,kernel_initializer='normal', activation='sigmoid'))
    # model.add(Dense(200,kernel_initializer='normal', activation='relu'))
    # model.add(Dense(100,kernel_initializer='normal', activation='relu'))
    # model.add(Dense(10,kernel_initializer='normal', activation='relu'))
    # model.add(Dense(2, kernel_initializer='normal', activation='sigmoid'))
    # model.add(Dense(1, kernel_initializer='normal', activation='relu'))

    model = Sequential()
    model.add(Conv1D(32, kernel_size=5, strides=1,
                    activation='relu',
                    input_shape=(90,2)))
    model.add(Conv1D(64, 5, activation='relu'))
    model.add(Conv1D(128, 5, activation='relu'))
    model.add(Conv1D(64, 5, activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Flatten())
    model.add(Dense(10, activation='relu'))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.summary()
    # model = svm.SVC()
    return model

#model = keras.models.load_model("/Users/qiweili/Desktop/Spring2018/CPRE288/final project/final-project/objectDetection.model")

X_train,X_test,y_train,y_test = readData()
# model = model()
# model.fit(X_train,y_train,epochs=epochs)
# model.save(model_name)
# print(y_test)
# print(model.predict(X_test))
# loss, acc = model.evaluate(X_test, y_test, verbose=0)
# print('\nTesting loss: {}, acc: {}\n'.format(loss, acc))

