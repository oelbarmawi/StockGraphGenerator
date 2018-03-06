from bs4 import BeautifulSoup
from urllib3 import PoolManager
from datetime import datetime
from sys import maxsize, exit
from time import sleep
from multiprocessing import Pool
import certifi
import os
import smtplib

"""Cycle repeats every 'sleep_time' seconds"""
sleep_time = 10
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
output_file = open('output.txt', 'a')
current_time = ""

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

def getLiveData(ticker):
	global targets, output_file, current_time
	border = "\n" + ("*" * 30) + "\n"
	info = []
	info.append(border)

	# output_file.write(border)
	# output_file.write("\nTIME: ")
	# output_file.write(str(current_time))
	# for ticker in targets:
	stop_loss = targets[ticker][0]
	target_price = targets[ticker][1]

	"""Scrape data from secure http server"""
	url = "http://finance.yahoo.com/quote/" + ticker + "?/?p=" + ticker
	http = PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
	r = http.request('GET', url)

	if (r.status != 200):
		print("Something Went Wrong\nStatus Code:", r.status)
		return
		
	soup = BeautifulSoup(r.data, 'lxml')
	p = soup.find("div", { "class": "My(6px) smartphone_Mt(15px)"})
	current_price = p.find("span", { "class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.strip()
	current_price = float(current_price.replace(",", ""))

	info.append("{} price:\t\t${}".format(ticker, current_price))
	# output_file.write("\n{} price:\t${}".format(ticker, current_price))

	"""Notify me if a stop-loss or a target price has been hit!"""
	message = "The current price of {} is ${} -- Time: {}".format(ticker, current_price, current_time)
	
	if current_price < stop_loss:
		info.append("\n--->STOP LOSS hit:\t${}".format(stop_loss))
		# output_file.write(" ---> STOP LOSS hit:\t${}".format(stop_loss))
		subj = "Stop-Loss hit! Sell {}!".format(ticker)
		# sendEmail(subj, message)

	elif current_price >= target_price:
		info.append("\n--->TARGET hit:\t${}".format(target_price))
		# output_file.write(" ---> TARGET hit:\t${}".format(target_price))
		subj = "Target hit! Sell {}".format(ticker)
		# sendEmail(subj, message)
	# output_file.write("\n")
	return info
	

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
	f = open(filename)
	for line in f.readlines():
		sep = line.split(" ")
		if len(sep) == 3:
			targets[sep[0].strip()] = (float(sep[1].strip()), float(sep[2].strip()))
	f.close()
	return targets.keys()

def main():
	global output_file, current_time
	ticker_keys = readStockData('dummy_data.txt')
	getEmailCredentials('sensitive.txt')

	"""Begin web scraping"""
	while True:
		try:
			pid = os.fork()
			if pid == 0: # child process
				pool = Pool(10)
				results = pool.map(getLiveData, ticker_keys)
				# getLiveData()
				current_time = datetime.now().time()
				print("\nTIME:", current_time)
				for info in results:
					print(''.join(info))
				sleep(sleep_time)
			else:
				"""If parent process runs first, wait for child process"""
				os.wait()
		except KeyboardInterrupt:
			if pid == 0:
				print("\nExiting...")
				output_file.write("\n")
				output_file.close()
			exit() #System call
		
if __name__ == '__main__':
	main()