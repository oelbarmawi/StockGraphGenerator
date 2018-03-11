class Stock():

	"""Price points... -1 if no specified point"""
	def __init__(self, ticker, stop_loss, target_price, entry):
		self.ticker = ticker
		self.stop_price = stop_loss
		self.target_price = target_price
		self.entry = entry
		self.current_price = -1 	# current stock price initially unknown
		self.notified = False 		# boolean value to determine if user was notified; prevents repetitive emails

	def stop_hit(self):
		return self.stop_price != -1 and self.current_price <= self.stop_price

	def target_hit(self):
		return self.target_price != -1 and self.current_price >= self.target_price

	def entry_hit(self):
		return self.entry != -1 and self.current_price >= self.entry

	def __repr__(self):
		return "Stock: {}\tPrice: ${}".format(self.ticker, self.current_price)

