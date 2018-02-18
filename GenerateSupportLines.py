import csv
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# data = pd.read_csv("Goog180.csv", low_memory=False)
# print(data)
with open('Siri180.csv') as file:
	reader = csv.reader(file)
	dates = []
	prices = []
	for row in reader:
		if row[1] != 'Close' and row[0] != 'Date': # TODO: get rid of this check
			#Converting string date to datetime object in order to plot
			dates.append(datetime.strptime(row[0] , '%m/%d/%y %H:%M'))
			prices.append(float(row[1]))

# Build plot
plt.plot(dates, prices, color='green')
# Draw horizontal line
# plt.axhline(y=5.75, xmin=0, xmax=200, linewidth=2, color = 'red')
# plt.axhline(y=5.44, xmin=0, xmax=200, linewidth=2, color = 'red')

def between(lower, upper, val):
	return lower <= val and val <= upper

# Convert lists to numpy arrays for future functions
date_array = np.array(dates)
price_array = np.array(prices)

# TODO: Find min and max values within first loop
min_val = min(prices) 
max_val = max(prices)

print(min_val)
print(max_val)

# for local maxima
print("local maxima")
maxima = argrelextrema(price_array, np.greater)

lo = min_val
hi = min_val
delta = abs(max_val - min_val)* 0.05
price_points = {}

# Create bins
while (hi < max_val):
	hi = lo + delta # 5% delta price
	mid = round((lo + hi)/2, 2)
	price_points[mid] = 0
	for m in maxima[0]:
		if between(lo, hi, prices[m]):
			price_points[mid] += 1;
	lo = hi


# Sort the keys according to the values:
sorted_prices = sorted(price_points, key=price_points.__getitem__, reverse=True)
for k in sorted_prices:
    print("{} : {}".format(k, price_points[k]))
    if price_points[k] >= 5:
    	plt.axhline(y=k, xmin=0, xmax=200, linewidth=2, color = 'red')

# for k in sorted_prices:
# # print([prices[m] for m in maxima])

# # for local minima
# print("local minima")
# minima = argrelextrema(date_array, np.less)
# # print([dates[mi] for mi in minima])

# # Display plot 
plt.show()
