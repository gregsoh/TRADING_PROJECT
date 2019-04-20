'''
Trading strategies based on explained cross-sectional returns
'''
import pandas as pd
import numpy as np
from pandas_datareader import data
from sklearn.linear_model import LinearRegression

def download(ticker, start_date, end_date):
	pd = data.DataReader(ticker, 'yahoo', start_date, end_date)
	t = pd["Close"].values #temporary
	return np.reshape(t, (len(t), 1))

def factors(start_date, end_date):
	# Oil stocks: https://www.fool.com/investing/2018/09/06/the-5-biggest-oil-stocks-in-the-us.aspx
	F1 = data.DataReader("XOM", 'yahoo', start_date, end_date)["Close"].values
	F1 = np.reshape(F1, (len(F1), 1))
	F2 = data.DataReader("CVX", 'yahoo', start_date, end_date)["Close"].values
	F2 = np.reshape(F2, (len(F2), 1))
	v = np.hstack((F1, F2))
	F3 = data.DataReader("COP", 'yahoo', start_date, end_date)["Close"].values
	F3 = np.reshape(F3, (len(F3), 1))
	v = np.hstack((v, F3))
	F4 = data.DataReader("EOG", 'yahoo', start_date, end_date)["Close"].values
	F4 = np.reshape(F4, (len(F4), 1))
	v = np.hstack((v, F4))
	F5 = data.DataReader("OXY", 'yahoo', start_date, end_date)["Close"].values
	F5 = np.reshape(F5, (len(F5), 1))
	v = np.hstack((v, F5))
	
	# Aircraft providers
	F6 = data.DataReader("BA", 'yahoo', start_date, end_date)["Close"].values
	F6 = np.reshape(F6, (len(F6), 1))
	v = np.hstack((v, F6))
	F7 = data.DataReader("AB", 'yahoo', start_date, end_date)["Close"].values
	F7 = np.reshape(F7, (len(F7), 1))
	v = np.hstack((v, F7))
	return v

def loss(start_date, end_date, ticker, reg):
	f = factors(start_date, end_date)
	p = download(ticker, start_date, end_date)
	return reg.score(f, p)

def linearRegression():
	# American Airlines, Delta Airlines, Spirit Airlines, SouthWest Airlines
	ticker = ["AAL", "DAL", "SAVE", "LUV"]
	start, end = '2016-01-01', '2017-12-31'
	for tick in ticker: 
		p = download(tick, start, end)
		f = factors(start, end)
		reg = LinearRegression().fit(f, p)
		#Testing error
		teststart, testend = '2018-01-01', '2018-12-31'
		print(tick, loss(teststart, testend, tick, reg))

def mainFn():
	linearRegression()

mainFn()