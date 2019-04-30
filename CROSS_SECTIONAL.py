'''
Trading strategies based on explained cross-sectional returns
'''
import pandas as pd
import numpy as np
from pandas_datareader import data
from pandas import ExcelWriter
from pandas import ExcelFile
from sklearn.linear_model import LinearRegression

def pandasToExcel(df, name):
	wr = pd.ExcelWriter(name, engine = 'xlsxwriter')
	df.to_excel(wr, sheet_name = "data")
	wr.save()

'''
function HML
	Inputs: df (pandas), percentage (we usually assume 30%)
	Outputs: pandas dataframe with more data
	Formula: 0.5 * (small val + big val) - 0.5 * (small growth + big growth)
'''
def HML(df, percentage):
	df['LASTDATE'] = pd.to_datetime(df.LASTDATE)
	numStocks = int(round(percentage * 500))
	df['HML_VALUE'], df["HML_GROWTH"], df["HML"] = "", "", ""
	df['HML_VALUE'] = df.sort_values(['BMR'],ascending=False).groupby(['LASTDATE'])['RETURN'].transform(lambda x: sum(x.head(numStocks)) / numStocks)
	df['HML_GROWTH'] = df.sort_values(['BMR'],ascending=False).groupby(['LASTDATE'])['RETURN'].transform(lambda x: sum(x.tail(numStocks)) / numStocks)
	for idx, row in df.iterrows():
		df.at[idx, 'HML'] = 0.5 * row['HML_VALUE'] - 0.5 * row['HML_GROWTH']
	return df

'''
function SMB
	Inputs: df (pandas), percentage (we usually assume 30%)
	Outputs: pandas dataframe with more data
	Formula: 0.33 * (small val + small neutral + small growth) - 0.33 * (big val + big neutral + big growth)
'''
def SMB(df, percentage):
	numStocks = int(round(percentage * 500))
	df['SMB_SMALL'], df["SMB_LARGE"], df["SMB"] = "", "", "" 
	df['SMB_SMALL'] = df.sort_values(['MARKET_CAP'],ascending=False).groupby(['LASTDATE'])['RETURN'].transform(lambda x: sum(x.head(numStocks)) / numStocks)
	df['SMB_LARGE'] = df.sort_values(['MARKET_CAP'],ascending=False).groupby(['LASTDATE'])['RETURN'].transform(lambda x: sum(x.tail(numStocks)) / numStocks)
	for idx, row in df.iterrows():
		df.at[idx, 'SMB'] = row['SMB_SMALL'] / 3 - row['SMB_LARGE'] / 3
	return df

'''
function stockreturns
	Inputs: s1, s2, s3, s4 -- steps on whether we need to continue
	Outputs: Excel file
'''
def dataProcessing(s1, s2, s3, s4):
	# This function only keeps the last of month data
	def removeDaily(data):
		return data[data['DATE'].dt.date == data['LASTDATE'].dt.date]
	# This function returns 2017 and 2018 data
	def trim(data):
		return data[data['YEAR'] <= 2016]
	# Step 1: We only keep the last day of month data (represent monthly)
	CP = None
	if s1: 
		CP = pd.read_excel('CLOSING.xlsx', sheet_name='WRDS')
		CP = removeDaily(CP)
		CP = trim(CP)
		pandasToExcel(CP, "Step1.xlsx")
	else:
		CP = pd.read_excel('Step1.xlsx', sheet_name='data')

	# Step 2: Read from BVPS to determine BV ratio data
	if s2: 
		missing = []
		BVPS = pd.read_excel('BVPS.xlsx', sheet_name='WRDS')
		#print(BVPS['KEY'], BVPS['YEAR'], CP['KEY'], CP['YEAR'])
		CP = pd.merge(CP, BVPS, how = "inner", on = ['KEY', 'YEAR'])
		CP['BMR'], CP['MARKET_CAP'] = "", ""
		for idx, row in CP.iterrows():
			if row['BVPS'] != None and row['BVPS'] != 0:
				CP.at[idx, 'BMR'] = row['BVPS'] / row['PRICE']
			else:
				missing.append((row['KEY'], row['YEAR']))
		for idx, row in CP.iterrows():
			CP.at[idx, 'MARKET_CAP'] = row['SHARE'] * row['PRICE']
		pandasToExcel(CP, "Step2.xlsx")
	else:
		CP = pd.read_excel('Step2.xlsx', sheet_name='data')

	if s3: 
		# Step 3: Include HML
		CP = HML(CP, 0.3)
		# Step 4: Include SMB
		CP = SMB(CP, 0.4)
		pandasToExcel(CP, "Step3.xlsx")
	else:
		CP = pd.read_excel('Step3.xlsx', sheet_name='data')

	#Step 5: risk free rates 
	if s4: 
		TR = pd.read_excel('Treasury.xls', sheet_name='FRED')
		TR = TR[TR['DATE'].dt.date == TR['LASTDATE'].dt.date]
		CP = pd.merge(CP, TR, how = "left", on = ['LASTDATE'])
		
		#Step 6: market returns
		MRTN = pd.read_excel('Market_Returns.xlsx', sheet_name='WRDS')
		MRTN = MRTN[MRTN['DATE'].dt.date == MRTN['LASTDATE'].dt.date]
		CP = pd.merge(CP, MRTN, how = "left", on = ['LASTDATE'])
		CP['RM-RF'], CP["RETURN-RF"] = '', ''
		for idx, row in CP.iterrows():
			CP.at[idx,'RETURN-RF'] = row['RETURN'] - row['RF'] / 100
			CP.at[idx,'RM-RF'] = row['MK_RETURN'] - row['RF'] / 100
		CP = CP[['RETURN-RF','RM-RF', 'HML', 'SMB', 'LASTDATE']]
		pandasToExcel(CP, "Step4.xlsx")
		CP = CP[['RETURN-RF','RM-RF', 'HML', 'SMB']]
		pandasToExcel(CP, "final.xlsx")
	else:
		CP = pd.read_excel('final.xlsx', sheet_name='data')
	return CP.dropna()

def processing():
	data = dataProcessing(0, 0, 0, 1)
	k = data.values
	f = k[:, 1:]
	p = k[:, 0:1]
	reg = LinearRegression().fit(f, p)
	print(reg.coef_)
processing()



'''
NOTE: THE CODE BELOW IS AN OLDER-VERSION CODE
'''


'''
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
'''