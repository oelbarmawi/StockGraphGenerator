import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime


with open('GoogStock.csv') as file:
	reader = csv.reader(file)
	dates = []
	prices = []
	for row in reader:
		if row[1] != 'Close' and row[0] != 'Date': # TODO: change this
			#Converting string date to datetime object in order to plot
			dates.append(datetime.strptime(row[0] , '%m/%d/%y %H:%M'))
			prices.append(float(row[1]))

	plt.plot(dates, prices, color='green')
	plt.show()

close('GoogStock.csv')