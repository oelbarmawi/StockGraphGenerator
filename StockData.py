from bs4 import BeautifulSoup
from urllib3 import PoolManager
import certifi
from GenerateSupportLines import *
import os


def child():
	tickers = ['GOOG', 'TWTR', 'SIRI', 'UGAZ']
	border = "*" * 25
	print(border)
	for t in tickers:
	# alternate_url = 'http://finance.google.com/finance?q='
	# base_url = 'http://finance.google.com/finance?q=NASDAQ%3A'
		url = "http://finance.yahoo.com/quote/" + t + "?/?p=" + t
		http = PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
		r = http.request('GET', url)
		# print("status:", r.status)
		if (r.status != 200):
			print("Something Went Wrong; Status Code:", r.status)
			# continue
		soup = BeautifulSoup(r.data, 'lxml')
		p = soup.find("div", { "class": "My(6px) smartphone_Mt(15px)"})
		current_price = p.find("span", { "class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.strip()

		print("{} price:\t\t${}".format(t, current_price))
		print(border)
	print()

def main():
	# while True:
	pid = os.fork()
	if pid == 0: # child process
		child()
		# sleep(10)
	else:
		"""If parent process runs first, wait for child process"""
		os.wait()
	
		
if __name__ == '__main__':
	main()