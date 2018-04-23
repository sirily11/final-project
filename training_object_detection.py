import keras
from keras.models import Sequential
from keras.layers import LSTM
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
file_num = 11
epochs = 300
model_name = "objectDetection.model"

def readData():
    x = []
    y = []
    for i in range(file_num):
        file_name = 'data{}.json'.format(i)
        with open(file_name,'r') as f:
            d = f.read()
            d = json.loads(d)
            for i in range(len(d['Ir_sensor'])):
                x.append([d['Ir_sensor'][i],d['Pin_sensor'][i]])
                #modify this part for labels
                y.append(d['Labels'][i])
    np_y = []
    for i in y:
        if(i == 0):
            np_y.append([1,0])
        else:
            np_y.append([0,1])
    np_x = np.array(x)
    np_y = np.array(np_y)
    print(np_y[0])
    np_x = preprocessing.scale(np_x)
    X_train, X_test, y_train, y_test = train_test_split(np_x, np_y, test_size=0.2, random_state=42)
    return (X_train,X_test,y_train,y_test)

def model():
    model = Sequential()
    model.add(Dense(10,input_shape = (2,),kernel_initializer='normal', activation='relu'))
    model.add(Dense(100,kernel_initializer='normal', activation='sigmoid'))
    model.add(Dense(200,kernel_initializer='normal', activation='relu'))
    model.add(Dense(100,kernel_initializer='normal', activation='relu'))
    model.add(Dense(10,kernel_initializer='normal', activation='relu'))
    model.add(Dense(2, kernel_initializer='normal', activation='sigmoid'))
    # model.add(Dense(1, kernel_initializer='normal', activation='relu'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    # model = svm.SVC()
    return model

#model = keras.models.load_model("/Users/qiweili/Desktop/Spring2018/CPRE288/final project/final-project/objectDetection.model")

X_train,X_test,y_train,y_test = readData()
model = model()
model.fit(X_train,y_train,epochs=epochs)
model.save(model_name)
# print("Real Label:{}".format(y_test))
# print("Prediction is:{}".format(model.predict(X_test)))
loss, acc = model.evaluate(X_test, y_test, verbose=0)
print('\nTesting loss: {}, acc: {}\n'.format(loss, acc))

