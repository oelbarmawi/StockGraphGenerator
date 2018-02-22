import csv
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime
from sys import maxsize


min_price, max_price = maxsize, -maxsize 
dates, prices = np.array([]), np.array([])
critical_points = np.array([])
price_points = {}


def plot_data(horizontal_lines):
	global dates, prices
	"""Build the plot with x-axis as dates and y-axis as prices"""
	plt.plot(dates, prices, color='green')
	for h in horizontal_lines:
		"""Create a horizontal support line"""
		plt.axhline(y=h, xmin=0, xmax=200, linewidth=2, color = 'red')
	""" Display Plot """
	plt.show()


def compute_price_points(min_price, max_price):
	global critical_points, price_points
	delta = abs(max_price - min_price) * 0.05
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

def between(lower, upper, val):
	return lower <= val and val <= upper

def main():
	""" 
	dates 	- numpy array of datetime objects used for plotting
	prices 	- numpy array of closing stock price for corresponding date in 'dates'
	"""
	global min_price, max_price, dates, prices
	global critical_points, price_points

	with open('Siri45.csv') as file:
		reader = csv.reader(file)
		for row in reader:
			if row[0] == 'Date' or row[1] == 'Price':
				continue
			p = float(row[1])
			dates = np.append(dates, datetime.strptime(row[0] , '%m/%d/%y %H:%M'))
			prices = np.append(prices, p)
			min_price = min(p, min_price)
			max_price = max(p, max_price)

	print("max: $", min_price)
	print("min: $", max_price)

	"""For local maxima"""
	maxima = argrelextrema(prices, np.greater)

	"""For local minima"""
	minima = argrelextrema(prices, np.less)

	"""critical_points: all price points in which their derivates are approximately zero"""
	critical_points = np.append(maxima[0], minima[0])

	compute_price_points(min_price, max_price)
	"""
	sorted_keys: an array of sorted keys for the dictionary 'price_points'
	price_points: (dictionary)
	key:	price bin
	value: 	number of local maxima within in this bin (TODO: update this to include minima)
	"""
	sorted_keys = sorted(price_points, key=price_points.__getitem__, reverse=True)

	support_lines = []
	"""Pulls top 5 bins with most data points within them"""
	for i in range(5):
		val = sorted_keys[i]
		print("{} : {}".format(val, price_points[val]))
		support_lines.append(val)
	
	# plot_data(support_lines)


if __name__ == "__main__":
	main()




