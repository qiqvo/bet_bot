import binascii
import arrow

def hashing_string(a):
	return hex(binascii.crc32(bytes(a, 'utf-8')))[2:]

def hashing_int(a):
	return hex(binascii.crc32(bytes(a)))[2:]

class Bet_table:
	def __init__(self):
		# table: {hash[str] : Bet}
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
		# money_table = {variant[str] : {user_id[int] : amount[int]}}
		self.money_table = dict()
		# all bets 
		self.montant = 0

		# default shift by 1 week
		self.start = arrow.utcnow()
		self.deadline = self.start.shift(weeks=+1)


	def set_variants(self, variants):
		self.variants = variants
		self.money_table = dict((variant, dict()) for variant in self.variants)

	def add_money(self, variant, user, money):
		if not self.check_deadline():
			return # no error is send 

		self.montant += money
		if user in self.money_table[variant]:
			self.money_table[variant][user] += money
		else:
			self.money_table[variant][user] = money

	def calculate_modifiers(self):
		for variant in self.variants:
			self.modifiers[variant] = self.montant / self.money_table[variant]

		return self.modifiers

	def short_info(self):
		info = self.question + '\n'
		info += 'The deadline passes ' + self.deadline.humanize() + '.\n'
		info += 'It began ' + self.start.humanize() + '.\n'.
		info += 'The bets are: '
		info += '. \n'.join([str(i + 1) + ') ' + variants[i] + ' -- ' + len(self.money_table[variants[i]]) + ' votes  -- ' + sum(self.money_table[variants[i]].values()) for i in range(len(self.variants))])

		return info

	def check_deadline(self):
		return arrow.now() < self.deadline


bets = Bet_table()