import pandas as pd
import numpy as np
from pandas_datareader import data
from pandas import ExcelWriter
from pandas import ExcelFile
from sklearn.linear_model import LinearRegression
import seaborn as sns
import matplotlib.pyplot as plt

data = pd.read_excel('train.xlsm', sheet_name = 'train')

X = data.iloc[: , 0:161]  #independent columns
y = data.iloc[ : , -1]    #target column i.e price range
#get correlations of each features in dataset
corrmat = X.corr()
#print("CORR", corrmat)
#top_corr_features = corrmat.index
#print("ABC", top_corr_features)
plt.figure(figsize = (161, 161))

# plot heat map
g = sns.heatmap(corrmat, annot = True, cmap = "RdYlGn")
plt.savefig("heatmap.png")