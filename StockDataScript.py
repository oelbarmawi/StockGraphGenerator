from bs4 import BeautifulSoup
from urllib3 import PoolManager
from datetime import datetime
from sys import maxsize, exit
from time import sleep
from threading import Thread
from Stock import *
import certifi
import smtplib


"""Cycle repeats every 'sleep_time' seconds"""
sleep_time = 60
"""
'targets' (dictonary)
key: ticker (string)
value: target prices (tuple of floats)
		value[0] - STOP-LOSS price
		value[1] - TARGET price
"""
targets = {}
username, password = "", ""
fromaddr, toaddr = "", ""
current_time = ""
output_filename = "output.txt"
out_file = open(output_filename, 'a') # the second argurment 'a' - append


def sendEmail(subject, message_body):
	global username, password, fromaddr, toaddr
	try:
		msg = 'Subject: {}\n\n{}'.format(subject, message_body)
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login(username, password)
		server.sendmail(fromaddr, toaddr, msg)
		server.quit()
	except:
		print("Unable to send email.")

def getEmailCredentials(filename):
	global username, password, fromaddr, toaddr
	"""Read from a text file to conceal sensitive email information"""
	f = open(filename)
	for line in f.readlines():
		components = line.split(" ")

	"""Set up automated email credentials"""
	username = components[0]
	password = components[1]
	fromaddr = components[2]
	toaddr  = components[3]
	f.close()

def readStockData(filename):
	global targets, ticker_keys
	""" Read input file and store into the 'targets' dictionary.
	Format of each line in the input file: 
	<ticker_name> <stop-loss price> <target price> <entry point>
	"""
	tickers = []
	f = open(filename)
	for line in f.readlines():
		sep = line.split(" ")
		assert len(sep) == 4, "Invalid .txt file format --> readStockData()"
		t = sep[0].strip()
		stock_data = Stock(t, float(sep[1].strip()), float(sep[2].strip()), float(sep[3].strip()))
		targets[t] = stock_data
		tickers.append(t)
	f.close()
	return tickers

def getLiveData(ticker, unused_arg=None):
	global targets, out_file, current_time

	info = []
	stock = targets[ticker]

	"""Scrape data from secure http server"""
	try:
		url = "http://finance.yahoo.com/quote/" + ticker + "?/?p=" + ticker
		http = PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
		r = http.request('GET', url)
	except:
		return "\nCould not find stock price for " + ticker

	if (r.status != 200):
		print("Something Went Wrong\nStatus Code:", r.status)
		return
	
	"""Parsing through returned html code to find stock price"""
	soup = BeautifulSoup(r.data, 'lxml')
	p = soup.find("div", { "class": "My(6px) smartphone_Mt(15px)"})
	current_price = p.find("span", { "class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.strip()
	current_price = float(current_price.replace(",", ""))

	stock.current_price = current_price

	info.append("\n{} price:\t\t${}".format(ticker, current_price))

	"""Notify me if a stop-loss, target price, or an entry point has been hit!"""
	if stock.stop_hit() or stock.target_hit() or stock.entry_hit():
		message = "The current price of {} is ${} -- Time: {}".format(ticker, current_price, current_time)
		if stock.stop_hit():
			info.append(" ---> STOP LOSS hit:\t${}".format(stock.stop_price))
			subj = "Stop-Loss hit! Sell {}!".format(ticker)

		elif stock.entry_hit():
			info.append(" ---> Entry point hit:\t${}".format(stock.entry))
			subj = "Entry point hit! Buy {}!".format(ticker)

		else:
			info.append(" ---> TARGET hit:\t${}".format(stock.target_price))
			subj = "Target hit! Sell {}".format(ticker)

		if not stock.notified:
			# sendEmail(subj, message)
			stock.notified = True

	""" Results of http response formatted and appended to the specified output file"""
	result = ''.join(info)
	out_file.write(result)
	print(result)
	return None

def main():
	global out_file, current_time

	ticker_keys = readStockData('test_data.txt')
	getEmailCredentials('sensitive.txt')
	border = "\n" + ("*" * 30)

	"""Begin web scraping -- press Ctrl+C to terminate execution"""
	while True:
		try:
			threads = []
			"""Create a thread for each ticker"""
			for t in ticker_keys:
				threads.append(Thread(target=getLiveData, args=(t, None)))

			"""Output formatting"""
			current_time = "\nTIME: {}".format(datetime.now().time())
			print(current_time)
			print(border)
			out_file.write(current_time)
			out_file.write(border)
			
			"""Begin execution of each thread in the thread list"""
			for thread in threads:
				thread.start()

			"""Wait for each thread to complete execution"""
			for thread in threads:
				thread.join()

			"""Sleep for the specified amount of time to prevent overusage of CPU"""
			sleep(sleep_time)

		except KeyboardInterrupt:
			"""Make sure all threads finish execution before exiting"""
			for thread in threads:
				thread.join()
			out_file.close()
			print("\nExiting...")
			exit() #System call

if __name__ == '__main__':
	main()

"""
Testing Purposes - 'test_data.txt' should print the following:
--------------------------------------------------------------
UGAZ price:		$59.7

GOOG price:		$1160.04 ---> TARGET hit:	$1.0

TWTR price:		$35.35 ---> STOP LOSS hit:	$100000.0

UAA price:		$17.05

CERN price:		$64.91

TSLA price:		$327.17

SIRI price:		$6.54 ---> Entry point hit:	$0.1

AAPL price:		$179.98 ---> TARGET hit:	$1.0

EBAY price:		$43.81 ---> STOP LOSS hit:	$100000.0
"""
