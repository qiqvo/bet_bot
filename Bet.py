import binascii

def hashing_string(a):
	return hex(binascii.crc32(bytes(a, 'utf-8')))[2:]

def hashing_int(a):
	return hex(binascii.crc32(bytes(a)))[2:]

class Bet_table:
	def __init__(self):
		# bets: {variant[str] : {user_id[int] : amount[int]}}
		self.table = dict()
		# how many bets. counter is then hashed by crc32
		self.counter = 1

	def add(self, Bet):
		self.counter += 1
		bet_hash = hashing_int(self.counter)
		self.table[bet_hash] = Bet
		return bet_hash

class Bet:
	# add time limit  
	def __init__(self, bet_question='', mode=False, variants=[]):
		self.mode = mode
		self.question = bet_question
		self.variants = variants
		self.money_table = dict()
		self.montant = 0
		# self.add_money(money)

	def set_variants(self, variants):
		self.variants = variants
		self.money_table = dict((variant, dict()) for variant in self.variants)

	def add_money(self, variant, user, money):
		self.montant += money
		if user in self.money_table[variant]:
			self.money_table[variant][user] += money
		else:
			self.money_table[variant][user] = money

	def calculate_modifiers(self):
		for variant in self.variants:
			self.modifiers[variant] = self.montant / self.money_table[variant]

		return self.modifiers

bets = Bet_table()