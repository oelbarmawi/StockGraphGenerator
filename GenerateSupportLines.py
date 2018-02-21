import csv
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime
from sys import maxsize

""" 
dates 	- numpy array of datetime objects used for plotting
prices 	- numpy array of closing stock price for corresponding date in 'dates'
"""
min_price, max_price = maxsize, -maxsize 
dates, prices = np.array([]), np.array([])

with open('Siri180.csv') as file:
	reader = csv.reader(file)
	for row in reader:
		if row[0] == 'Date' or row[1] == 'Price':
			continue
		p = float(row[1])
		dates = np.append(dates, datetime.strptime(row[0] , '%m/%d/%y %H:%M'))
		prices = np.append(prices, p)
		min_price = min(p, min_price)
		max_price = max(p, max_price)


"""Build the plot with x-axis as dates and y-axis as prices"""
plt.plot(dates, prices, color='green')

def between(lower, upper, val):
	return lower <= val and val <= upper


print("max: $", min_price)
print("min: $", max_price)

"""For local maxima"""
maxima = argrelextrema(prices, np.greater)

"""For local minima"""
minima = argrelextrema(prices, np.less)

critical_points = np.append(maxima[0], minima[0])

delta = abs(max_price - min_price) * 0.05
price_points = {}

""" This while loop creates bins of price ranges and
tests to see which bin each individual price falls under """
for c in critical_points:
	lo = min_price
	hi = min_price
	while (hi < max_price):
		hi = lo + delta
		mid = round((lo + hi) / 2, 2)
		if between(lo, hi, prices[c]):
			if mid in price_points:
				price_points[mid] += 1
			else:
				price_points[mid] = 1
			break
		lo = hi

"""
sorted_prices: an array of sorted keys for the dictionary 'price_points'
price_points (dictionary)
key:	price bin
value: 	number of local maxima within in this bin (TODO: update this to include minima)
"""
sorted_prices = sorted(price_points, key=price_points.__getitem__, reverse=True)

"""Draws top 3 bins with most data points within them"""
for k in range(5):
	val = sorted_prices[k]
	print("{} : {}".format(val, price_points[val]))
	# Create a horizontal support line
	plt.axhline(y=val, xmin=0, xmax=200, linewidth=2, color = 'red')


""" Display Plot """
plt.show()
