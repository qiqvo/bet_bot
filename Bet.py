import binascii
import random
import arrow

locale = 'en'

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
		self.current_hash = hashing_int(random.randint(1, 100000))

	def add(self, Bet):
		bet_hash = hashing_string(str(int(self.current_hash, 16) + 1))
		self.current_hash = bet_hash
		self.counter += 1

		self.table[bet_hash] = Bet
		return bet_hash

class Bet:
	# add time limit  
	def __init__(self, bet_question='', variants=[]):
		self.question = bet_question
		self.variants = variants
		# money_table = {variant[str] : {user_id[int] : amount[int]}}
		self.money_table = dict()
		self.modifiers = dict()
		# all money 
		self.montant = 0

		# default shift by 1 week
		self.start = arrow.utcnow()
		self.deadline = self.start.shift(weeks=+1)

	def set_deadline_with_shift(self, shifts):
		try:
			self.deadline = arrow.utcnow().shift(**shifts)
			return True
		except:
			return False

	def set_deadline_with_exact(self, date):
		try:
			self.deadline = arrow.get(date + ' 12', 'DD MM YYYY HH')
			return True
		except:
			return False

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
			b = sum(self.money_table[variant].values())
			if b != 0:
				self.modifiers[variant] = self.montant / b
			else:
				self.modifiers[variant] = 0

		return self.modifiers

	def short_info(self):
		info = '*' + self.question + '*\n'
		if self.check_deadline():
			info += loc_deadline_passes[locale] + self.deadline.humanize() + '.\n'
		else:
			info += loc_bet_was_closed[locale]

		return info

	def long_info(self):
		info = self.short_info()
		info += loc_info_exactly[locale] + self.deadline.format() + '.\n'
		info += loc_info_began[locale] + self.start.humanize() + '.\n\n'
		info += loc_info_lots[locale]

		i = 1
		l_vs = []
		for v in self.variants:
			l_vs.append(str(i) + ') _' + v + '_ — ' + str(len(self.money_table[v])) + loc_info_votes[locale] + '—' + loc_info_totalling[locale] + str(sum(self.money_table[v].values()))) 
			i += 1

		info += '.\n\n'.join(l_vs)
		info += '.\n\n'

		self.calculate_modifiers()
		info += loc_info_modifiers[locale] + ' : '.join(['{:.3f}'.format(v) for v in self.modifiers.values()]) + '.'

		return info

	def check_deadline(self):
		return arrow.now() < self.deadline
	
	@staticmethod
	def check_time(key, time):
		try:
			arrow.now().shift(key, time)
		except:
			return False

bets = Bet_table()