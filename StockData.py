from bs4 import BeautifulSoup
from urllib3 import PoolManager
import certifi
from GenerateSupportLines import *
import os

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

def child():
	global targets
	border = "*" * 30
	print()
	print("TIME:", datetime.now().time())
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
		if current_price < stop_loss:
			print("--->STOP LOSS hit:\t${}".format(stop_loss))
		elif current_price >= target_price:
			print("--->TARGET hit:\t${}".format(target_price))
		print(border)
	

def main():
	global targets
	""" Read input file and store into 'tickers' and 'targets' dictionaries.
	Format of the input file: 
	<ticker_name> <stop-loss price> <target price>
	"""
	f = open('dummy_data.txt')
	for line in f.readlines():
		sep = line.split(" ")
		if len(sep) == 3:
			targets[sep[0].strip()] = (float(sep[1].strip()), float(sep[2].strip()))

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