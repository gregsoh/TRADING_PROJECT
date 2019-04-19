	
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
	return pred, v

def linearRegression():
	p, v = download()
	#for _ in p:
	reg = LinearRegression().fit(v, p[0])
	print(reg.score(v, p[0]))

	print("nothing yet")
linearRegression()