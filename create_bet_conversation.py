import logging
from uuid import uuid4
import re

from telegram import *
from telegram.ext import *
from telegram.utils import *

from bot_logging import *
from Bet import *
from commands import *

BET_QUESTION, ANSWER_LOOP, DEADLINE_SHIFT = range(3)

def on_start(update, context):
	user = update.message.from_user
	update.message.reply_text("Let's create a new bet. Send the question.", reply_markup=ReplyKeyboardRemove())

	logger.info("User %s started.", user.first_name)

	return BET_QUESTION

def on_bet_question(update, context):
	user = update.message.from_user
	bet_question = update.message.text

	update.message.reply_markdown("Creating a new bet: *%s*." % bet_question, reply_markup=ReplyKeyboardRemove())

	bet_hash = bets.add(Bet(bet_question=bet_question))
	if 'bets' in context.user_data:
		context.user_data['bets'].append(bet_hash)
	else:
		context.user_data['bets'] = [bet_hash]

	context.user_data['current_bet'] = bet_hash
	logger.info("User %s created a new bet: %s.", user.first_name,bet_question)
	update.message.reply_text("Cool! Now send me lots.")
	return ANSWER_LOOP

def on_loop(update, context):
	user = update.message.from_user
	variant = update.message.text
	bet_hash = context.user_data['current_bet']

	logger.info("User %s added a new variant %s to a bet: %s.", user.first_name, variant, bets.table[bet_hash].question)

	if 'variants' in context.user_data:
		context.user_data['variants'].append(variant)
	else:
		context.user_data['variants'] = [variant]

	update.message.reply_text('Any more variants? Send /done to stop me asking.', reply_markup=ReplyKeyboardRemove())
	return ANSWER_LOOP

def on_end_loop(update, context):
	user = update.message.from_user
	
	bet_hash = context.user_data['current_bet']
	bets.table[bet_hash].set_variants(context.user_data['variants'])

	logger.info("User %s finished adding new variants to a bet: %s.", user.first_name, bets.table[bet_hash].question)

	update.message.reply_text('Postpone for weeks, years, days, hours, seconds, minutes, months. For example: in 1 week. Or backwards: in -3 hours.', reply_markup=ReplyKeyboardRemove())
	context.user_data['shift'] = dict()
	
	return DEADLINE_SHIFT

def on_deadline_shift(update, context):
	num_param_regex = re.compile(r'(-?[0-9]+) (day|week|year|hour|minute|month|second)s?')

	try:
		shift, key = num_param_regex.search(update.message.text).groups()
		key += 's'
		context.user_data['shift'][key] = int(shift)
	except:
		update.message.reply_text('Something wrong. Try for example "in 3 days"')
		return DEADLINE_SHIFT

	update.message.reply_text('Any more postpones? Send /done to stop me asking.', reply_markup=ReplyKeyboardRemove())
	return DEADLINE_SHIFT

def on_end_deadline_shift(update, context):
	shift = context.user_data['shift']
	bet_hash = context.user_data['current_bet']
	bet = bets.table[bet_hash]

	logger.info(";; %s %i", list(shift.items())[0][0], list(shift.items())[0][1])
	if not bet.set_deadline_with_shift(shift):
		update.message.reply_text('Something went wrong. Try again entering the deadline.')
		return DEADLINE_SHIFT

	update.message.reply_text('The deadline was succesfully set up to %s. \nToday is %s.\nNow send the first variant of the reply.' % (bet.deadline.format('DD:MM:YYYY HH:mm ZZ'), bet.start.format('DD:MM:YYYY HH:mm ZZ')))

	update.message.reply_text('You may find your bet by /view_%s.' % bet_hash, reply_markup=ReplyKeyboardRemove())
	return ConversationHandler.END
