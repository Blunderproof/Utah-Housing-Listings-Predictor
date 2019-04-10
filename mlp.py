# mlp.py

import random
import pandas as pd
# import seaborn.apionly as sn
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor

df = pd.read_csv(filepath_or_buffer = "listings-reduced.csv")
# df = pd.read_csv(filepath_or_buffer = "export_dataframe (with Zip and City Means).csv")

df['Acres'] = pd.to_numeric(df['Acres'], errors='coerce')
df['Bedrooms'] = pd.to_numeric(df['Bedrooms'], errors='coerce')
df['Year Built'] = pd.to_numeric(df['Year Built'], errors='coerce', downcast='integer')
df['Square Feet'] = pd.to_numeric(df['Square Feet'], errors='coerce', downcast='integer')

# Break some categories into more nuanced ones
df['Carpet'] = pd.np.where(df['Floor Covering'].str.contains("carpet"), True, False)
df['Hard Wood'] = pd.np.where(df['Floor Covering'].str.contains("hardwood"), True, False)
df['Tile'] = pd.np.where(df['Floor Covering'].str.contains("tile"), True, False)
df['Laminate'] = pd.np.where(df['Floor Covering'].str.contains("laminate"), True, False)

df['Fireplace'] = pd.np.where(df['Special Features'].str.contains("fireplace"), True, False)
df['Deck'] = pd.np.where(df['Special Features'].str.contains("deck"), True, False)
df['Sprinklers'] = pd.np.where(df['Special Features'].str.contains("sprinklers"), True, False)
df['Pool'] = pd.np.where(df['Special Features'].str.contains("pool"), True, False)

df['Fenced'] = pd.np.where(df['Yard'].str.contains("fenced full|fenced partial"), True, False)
df['Landscape'] = pd.np.where(df['Yard'].str.contains("landscape full|landscape partial|landscape front|landscape back"), True, False)

# Drop Extreme price outliers (between 50k and 1.5m)
df = df[df['Asking Price'] < 1500000] 
df = df[df['Asking Price'] > 50000]

# Drop improper years
df = df[df['Year Built'] > 1850]

# Drop extremely high/low Sqaure Feet listings (11000sqft = .25 acre (roughly))
df = df[df['Square Feet'] < 11000]
df = df[df['Square Feet'] > 500]

# print(df.apply(lambda x: pd.factorize(x)[0]))

df['Category'] = pd.factorize(df['Category'])[0]
df['Yard'] = pd.factorize(df['Yard'])[0]
df['City'] = pd.factorize(df['City'])[0]
df['School District'] = pd.factorize(df['School District'])[0]
df['Special Features'] = pd.factorize(df['Special Features'])[0]
df['Floor Covering'] = pd.factorize(df['Floor Covering'])[0]

toDrop = ['Time Posted']
df = df.drop(toDrop, axis=1)

df = df.dropna(how='any',axis=0)
# df[''] = pd.factorize(df[''])[0]
# df['Yard'] = df['Yard'].apply(lambda x: pd.factorize(x)[0])
# df['City'] = df['City'].apply(lambda x: pd.factorize(x)[0])
# df['Special Features'] = df['Special Features'].apply(lambda x: pd.factorize(x)[0])
# df['Floor Covering'] = df['Floor Covering'].apply(lambda x: pd.factorize(x)[0])

# print(df)

# for category in df:
# 	print(category)

def my_tt_split(df):
    train, test = train_test_split(df, test_size=0.2)

    # seperate Y and X
    train_y = train['Asking Price']
    train_y = train_y.values
    del train['Asking Price']
    train_x = train.values

    test_y = test['Asking Price']
    test_y = test_y.values
    del test['Asking Price']
    test_x = test.values
    
    return train_x, train_y, test_x, test_y

train_x, train_y, test_x, test_y = my_tt_split(df)

# mlp_model = MLPClassifier(hidden_layer_sizes=(1000, 20), max_iter=1000)
# mlp_model.fit(train_x, train_y)
# mlp_score = mlp_model.score(test_x, test_y)
# roundedScore = round(mlp_score, 4)

# print()
# for i in range(0,10):
# 	rand = random.randint(0, len(test_y))
# 	prediction = mlp_model.predict([test_x[rand]])[0]
# 	real = test_y[rand]

# 	print("Prediction: {}".format(prediction))
# 	print("Actual: {}".format(real))
# 	print("Difference: {}".format(abs(prediction-real)))
# 	print()

# print()
# print("******************************")
# print("MLP Accuracy: {} -- {}%".format(roundedScore, roundedScore*100.0))
# print("******************************")

# clf = MLPRegressor(hidden_layer_sizes=(1000, 20), max_iter=1000)
# clf.fit(train_x, train_y)
# clf_score = clf.score(test_x, test_y)
# clf_roundedScore = round(clf_score, 4)

# MAPE = 0
# n = 0

# print()
# for i in range(0,10):
# 	rand = random.randint(0, len(test_y))
# 	prediction = clf.predict([test_x[rand]])[0]
# 	real = test_y[rand]

# 	thisMAPE = abs((real - prediction)/real)

# 	MAPE += thisMAPE
# 	n += 1
	
# 	thisMAPE = round(thisMAPE, 3)

# 	print("Prediction: {}".format(round(prediction), 2))
# 	print("Actual: {}".format(real))
# 	print("Difference: {}".format(round(abs(prediction-real),2)))
# 	print("Current MAPE: {} -- {}%".format(thisMAPE, thisMAPE*100.0))
# 	print()

# totalMAPE = MAPE/n
# totalMAPE = round(totalMAPE, 3)
# print("Overall MAPE: {} -- {}%".format(totalMAPE, totalMAPE*100.0))

# print()
# print("******************************")
# print("MLP Regression Accuracy: {} -- {}%".format(clf_roundedScore, clf_roundedScore*100.0))
# print("******************************")
# print()

print("Multiple Instances MLPRegressor Testing...")

totalScore = 0
iterations = 0

totalMAPE = 0
numMAPE = 0

for i in range(20):
	mlp_reg = MLPRegressor(hidden_layer_sizes=(1000, 20), max_iter=1000)
	train_x, train_y, test_x, test_y = my_tt_split(df)
	mlp_reg.fit(train_x, train_y)
	mlp_reg_score = mlp_reg.score(test_x, test_y)

	totalScore += mlp_reg_score
	iterations += 1

	for j in range(10):
		rand = random.randint(0, len(test_y)-1)
		prediction = mlp_reg.predict([test_x[rand]])[0]
		real = test_y[rand]

		curMAPE = abs((real - prediction)/real)
		totalMAPE += curMAPE
		numMAPE += 1

	print("...")


finalScore = totalScore/iterations
finalMAPE = totalMAPE/numMAPE

finalScore = round(finalScore, 4)
finalMAPE = round(finalMAPE, 4) 

print()
print("******************************")
print("{} Different Instances of MLPRegressor".format(iterations))
print("\tAccuracy: {} -- {}%".format(finalScore, finalScore*100))
print("******************************")
print()
print("******************************")
print("Mean Absolute Percent Error/Loss Function ({} Instances)".format(numMAPE))
print("\tAccuracy: {} -- {}%".format(finalMAPE, finalMAPE*100))
print("******************************")
print()


# Run tests on house values less than 600,000