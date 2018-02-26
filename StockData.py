from bs4 import BeautifulSoup
from urllib3 import PoolManager
import certifi
from GenerateSupportLines import *
import os
import smtplib

"""Cycle repeats every 'time_repeat' minutes"""
time_repeat = 5 * 60
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

def child():
	global targets 
	border = "*" * 30
	print()
	current_time = datetime.now().time()
	print("TIME:", current_time)
	print(border)
	for t in targets:
		stop_loss = targets[t][0]
		target_price = targets[t][1]

		url = "http://finance.yahoo.com/quote/" + t + "?/?p=" + t
		http = PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
		r = http.request('GET', url)

		if (r.status != 200):
			print("Something Went Wrong; Status Code:", r.status)
			continue
			
		soup = BeautifulSoup(r.data, 'lxml')
		p = soup.find("div", { "class": "My(6px) smartphone_Mt(15px)"})
		current_price = p.find("span", { "class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.strip()
		current_price = float(current_price.replace(",", ""))

		print("{} price:\t\t${}".format(t, current_price))

		"""Notify me if a stop-loss or a target price has been hit!"""
		message = "The current price of {} is ${} -- Time: {}".format(t, current_price, current_time)
		if current_price < stop_loss:
			print("--->STOP LOSS hit:\t${}".format(stop_loss))
			subj = "Stop-Loss hit! Sell {}!".format(t)
			sendEmail(subj, message)

		elif current_price >= target_price:
			print("--->TARGET hit:\t${}".format(target_price))
			subj = "Target hit! Sell {}".format(t)
			sendEmail(subj, message)

		print(border)
		

def main():
	global targets, username, password, fromaddr, toaddr
	""" Read input file and store into 'tickers' and 'targets' dictionaries.
	Format of the input file: 
	<ticker_name> <stop-loss price> <target price>
	"""
	f = open('dummy_data.txt')
	for line in f.readlines():
		sep = line.split(" ")
		if len(sep) == 3:
			targets[sep[0].strip()] = (float(sep[1].strip()), float(sep[2].strip()))

	"""Conceal email information"""
	f1 = open('sensitive.txt')
	for line in f1.readlines():
		components = line.split(" ")

	"""Set up automated email credentials"""
	username = components[0]
	password = components[1]
	fromaddr = components[2]
	toaddr  = components[3]

	"""Begin web scraping"""
	while True:
		try:
			pid = os.fork()
			if pid == 0: # child process
				child()
				sleep(time_repeat)
			else:
				"""If parent process runs first, wait for child process"""
				os.wait()
		except KeyboardInterrupt:
			if pid == 0:
				print("\nExiting...")
			exit() #System call
		
if __name__ == '__main__':
	main()