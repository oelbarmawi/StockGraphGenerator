from bs4 import BeautifulSoup
from urllib3 import PoolManager
from GenerateSupportLines import *


def main():
	tickers = ['GOOG', 'TWTR', 'SIRI']
	border = "*" * 25
	print(border)
	for t in tickers:
		# alternate_url = 'http://finance.google.com/finance?q='
		base_url = 'http://finance.google.com/finance?q=NASDAQ%3A'

		http = PoolManager()
		r = http.request('GET', base_url + t)
		# print("status:", r.status)
		if (r.status != 200):
			print("Something Went Wrong; Status Code:", r.status)
			continue

		soup = BeautifulSoup(r.data, 'lxml')
		p = soup.find("div", { "id": "market-data-div" })
		current_price = p.find("span", {"class" : "pr"}).text.strip()

		print("{} price:\t\t${}".format(t, current_price))
		print(border)
		
	

if __name__ == '__main__':
	main()