from bs4 import BeautifulSoup
from urllib3 import PoolManager
from datetime import datetime
from sys import maxsize, exit
from time import sleep
from threading import Thread
import certifi
import smtplib


"""Cycle repeats every 'sleep_time' seconds"""
sleep_time = 5
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
output_file = open('output.txt', 'a')


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
	<ticker_name> <stop-loss price> <target price>
	"""
	tickers = []
	f = open(filename)
	for line in f.readlines():
		sep = line.split(" ")
		if len(sep) == 3:
			t = sep[0].strip()
			targets[t] = (float(sep[1].strip()), float(sep[2].strip()))
			tickers.append(t)
	f.close()
	return tickers

def getLiveData(ticker, unused_arg=None):
	global targets, output_file, current_time

	info = []
	stop_loss = targets[ticker][0]
	target_price = targets[ticker][1]

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

	info.append("\n{} price:\t\t${}".format(ticker, current_price))

	"""Notify me if a stop-loss or a target price has been hit!"""
	if current_price < stop_loss:
		info.append(" ---> STOP LOSS hit:\t${}".format(stop_loss))
		message = "The current price of {} is ${} -- Time: {}".format(ticker, current_price, current_time)
		subj = "Stop-Loss hit! Sell {}!".format(ticker)
		# sendEmail(subj, message)

	elif current_price >= target_price:
		info.append(" ---> TARGET hit:\t${}".format(target_price))
		message = "The current price of {} is ${} -- Time: {}".format(ticker, current_price, current_time)
		subj = "Target hit! Sell {}".format(ticker)
		# sendEmail(subj, message)

	result = ''.join(info)
	output_file.write(result)
	print(result)
	return None

def main():
	global output_file, current_time

	ticker_keys = readStockData('dummy_data.txt')
	getEmailCredentials('sensitive.txt')
	border = "\n" + ("*" * 30)

	"""Begin web scraping"""
	while True:
		try:
			threads = []
			for t in ticker_keys:
				threads.append(Thread(target=getLiveData, args=(t, None)))

			current_time = "\nTIME: {}".format(datetime.now().time())
			print(current_time)
			print(border)
			output_file.write(current_time)
			output_file.write(border)
			
			for thread in threads:
				thread.start()

			for thread in threads:
				thread.join()

			sleep(sleep_time)

		except KeyboardInterrupt:
			"""Make sure all threads finish execution before exiting"""
			for thread in threads:
				thread.join()
			output_file.close()
			print("\nExiting...")
			exit() #System call


if __name__ == '__main__':
	main()
