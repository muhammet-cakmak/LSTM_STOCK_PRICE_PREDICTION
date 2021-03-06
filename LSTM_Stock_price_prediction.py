# -*- coding: utf-8 -*-
"""LSTM_STOCK_Price

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1W3H-UbOnRW9i8yqeSREvqc8iflguj687

# Stock Market Prediction and Forecasting Using Stacked LSTM
"""

from google.colab import drive
drive.mount('/content/drive')

"""# 1. Data Collection

Pandas datareader : https://pandas-datareader.readthedocs.io/en/latest/remote_data.html

#!python -m pip install --user pandas_datareader
"""

import pandas_datareader as pdr
import pandas as pd
import numpy as np

my_api = " " # write your own Tiingo API
data = pdr.get_data_tiingo('AAPL', api_key = my_api)
data.to_csv('/content/AAPL1.csv') # AAPL is the stock name of APPLE company

pwd

# reading csv data
df = pd.read_csv('/content/AAPL1.csv')

df.head()

df.tail()

df1 = df.reset_index()['close']

df1.head()

df1.shape

import matplotlib.pyplot as plt
plt.plot(df1);

"""**LSTM İS SENSİTİVE TO THE SCALE OF THE DATA. SO WE APPLY MinMax scaler**"""

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0,1))
df1 = scaler.fit_transform(np.array(df1).reshape(-1,1))

df1.shape

"""## Train-Test Split

**NOT: Time series problemlerinde datasetini bölerken belirli bir zamandan öncesine train sonrasına test set diyecek şekilde bölmelisiniz. Çünkü günler bir önceki günlerden etkileniyorlar.**
"""

# splitiing dataset into train and test split
training_size = int(len(df1)*0.85)
test_size = len(df1 - training_size)
train_data, test_data = df1[0:training_size,:], df1[training_size:len(df1),:]

train_data.shape

test_data.shape

"""Now we have to decide how many days ago we will get the data to predict the next day."""

# convert an array of values into a dataset matrix

def create_dataset(dataset, time_step =1):
    dataX, dataY = [],[]
    for i in range(len(dataset)-time_step-1):
        a = dataset[i:(i+time_step), 0]  
        dataX.append(a)
        dataY.append(dataset[i+time_step,0])
    return np.array(dataX), np.array(dataY)

time_step = 100

X_train, y_train = create_dataset(train_data, time_step)
X_test, y_test = create_dataset(test_data, time_step)

print(X_train)

X_train.shape, y_train.shape, X_test.shape, y_test.shape

"""Dataları LSTM'e sokmadan önce mutlaka reshape yapıp 3 boyuta getirmemiz lazım."""

# reshape input to be [samples, time steps, features] which is required for LSTM
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

"""# Model Building"""

# Create the LSTM model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM

model = Sequential()
model.add(LSTM(50, return_sequences = True, input_shape = (100,1))) # input_shape =(num_of_features, 1)
model.add(LSTM(50, return_sequences = True))
model.add(LSTM(50))
model.add(Dense(1))
model.compile(loss = 'mean_squared_error', optimizer = 'adam')

model.summary()

#from keras.utils import plot_model
#plot_model(model, to_file='/content/drive/My Drive/Colab Notebooks/model.png')

model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=100, batch_size = 64, verbose =1)

# Predicting train and test data
train_pred = model.predict(X_train)
test_pred = model.predict(X_test)

train_pred.shape, test_pred.shape

# transform data sets back to orginal form from scaled form
train_pred = scaler.inverse_transform(train_pred)
test_pred = scaler.inverse_transform(test_pred)

# Calculate RMSE performance form
import math
from sklearn.metrics import mean_squared_error
math.sqrt(mean_squared_error(y_train, train_pred))

math.sqrt(mean_squared_error(y_test, test_pred))

# plotting
# shift train predictions for plotting
lock_back = 100
trainPredictPlot = np.empty_like(df1)
trainPredictPlot[:,:] = np.nan
trainPredictPlot[lock_back:len(train_pred)+lock_back, :] = train_pred

# shift test predictions for plotting
testPredictPlot = np.empty_like(df1)
testPredictPlot[:,:] = np.nan
testPredictPlot[len(train_pred)+(lock_back*2)+1:len(df1)-1, :] = test_pred

# plot real and prediction data
plt.plot(scaler.inverse_transform(df1))
plt.plot(trainPredictPlot)
plt.plot(testPredictPlot)
plt.show();

"""Here, the blue color shows my actual data, and the orange color shows the prediction made by using the train set. The green color indicates the forecast made using the test set."""

testPredictPlot.shape

"""# Predict Next 30 Days in the Future

Let's say today is the 28th of the month and I want to predict the stock on the 29th. In this case, I have to use data up to 100 days ago.
"""

len(test_data)

x_input = test_data[len(test_data)-lock_back:].reshape(1, -1)
x_input.shape

temp_input = list(x_input)
temp_input = temp_input[0].tolist()

len(temp_input)

# demonstrate prediction for next 10 days
from numpy import array

lst_output=[]
n_steps=100
i=0
while(i<30):
    
    if(len(temp_input)>100):
        #print(temp_input)
        x_input=np.array(temp_input[1:])
        print("{} day input {}".format(i,x_input))
        x_input=x_input.reshape(1,-1)
        x_input = x_input.reshape((1, n_steps, 1))
        #print(x_input)
        yhat = model.predict(x_input, verbose=0)
        print("{} day output {}".format(i,yhat))
        temp_input.extend(yhat[0].tolist())
        temp_input=temp_input[1:]
        #print(temp_input)
        lst_output.extend(yhat.tolist())
        i=i+1
    else:
        x_input = x_input.reshape((1, n_steps,1))
        yhat = model.predict(x_input, verbose=0)
        print(yhat[0])
        temp_input.extend(yhat[0].tolist())
        print(len(temp_input))
        lst_output.extend(yhat.tolist())
        i=i+1
    

print(lst_output)

day_new=np.arange(1,101)
day_pred=np.arange(101,131)

len(df1)

predict_future_days = day_pred,scaler.inverse_transform(lst_output)

predict_future_days[1]

plt.plot(day_new,scaler.inverse_transform(df1[len(df1)-lock_back:]))
plt.plot(day_pred,scaler.inverse_transform(lst_output))

df3=df1.tolist()
df3.extend(lst_output)
plt.plot(df3[1200:])

df3=scaler.inverse_transform(df3).tolist()

plt.plot(df3)





