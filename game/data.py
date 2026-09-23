class Data:
	def __init__(self):
		self._coins = 0
		self._health = 5

		self.unlocked_level = 0
		self.current_level = 0

	@property
	def coins(self):
		return self._coins

	@coins.setter
	def coins(self, value):
		self._coins = value
		if self.coins >= 100:
			self.coins -= 100
			self.health += 1

	@property
	def health(self):
		return self._health

	@health.setter
	def health(self, value):
		self._health = value

	def update(self, item_type: str):
		if item_type == 'gold':
			self.coins += 5

		if item_type == 'silver':
			self.coins += 1

		if item_type == 'diamond':
			self.coins += 20

		if item_type == 'skull':
			self.coins += 50

		if item_type == 'potion':
			self.health += 1