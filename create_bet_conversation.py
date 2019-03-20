import logging
from uuid import uuid4

from telegram import *
from telegram.ext import *
from telegram.utils import *

from bot_logging import *
from Bet import *
from commands import *

BET_QUESTION, DEADLINE, DEADLINE_EXACT, DEADLINE_SHIFT, LOOP = range(5)

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
	reply_markup = ReplyKeyboardMarkup.from_column(['Exact date', 'Shift'], one_time_keyboard=True, resize_keyboard=True)
	update.message.reply_text("Cool! Now create a dealine for betting. \nDo you want to enter your the exact date? Or do you want to shift by some time from today?", reply_markup=reply_markup)
	return DEADLINE

def on_deadline(update, context):
	if update.message.text == 'Exact date':
		update.message.reply_text('Send date in a way: DD MM YYYY.', reply_markup=ReplyKeyboardRemove())
		return DEADLINE_EXACT
	else: # update.message.text == 'Shift':
		update.message.reply_text('Send what parameters do you want to shift and a relative number. You may choose one the following parameters: weeks, years, days, hours, seconds, minutes, months. For example: weeks 1.', reply_markup=ReplyKeyboardRemove())
		context.user_data['shift'] = dict()
		return DEADLINE_SHIFT

def on_deadline_exact(update, context):
	date = update.message.text
	bet_hash = context.user_data['current_bet']
	bet = bets.table[bet_hash]
	if not bet.set_deadline_with_exact(date):
		reply_markup = ReplyKeyboardMarkup.from_column(['Exact date', 'Shift'], one_time_keyboard=True, resize_keyboard=True)
		update.message.reply_text('Something went wrong. Try again entering the deadline.', reply_markup=reply_markup)
		return DEADLINE

	update.message.reply_text('The deadline was succesfully set up on %s. \nToday is %s.\nNow send the first variant of the reply.' % (bet.deadline.format('DD:MM:YYYY HH:mm ZZ'), bet.start.format('DD:MM:YYYY HH:mm ZZ')), reply_markup=ReplyKeyboardRemove())
	return LOOP

def on_deadline_shift(update, context):
	key, shift = update.message.text.split()
	context.user_data['shift'][key] = int(shift)
	
	update.message.reply_text('Any more? Send /done to stop me asking.', reply_markup=ReplyKeyboardRemove())
	return DEADLINE_SHIFT

def on_end_deadline_shift(update, context):
	shift = context.user_data['shift']
	bet_hash = context.user_data['current_bet']
	bet = bets.table[bet_hash]
	if not bet.set_deadline_with_shift(shift):
		reply_markup = ReplyKeyboardMarkup.from_column(['Exact date', 'Shift'], one_time_keyboard=True, resize_keyboard=True)
		update.message.reply_text('Something went wrong. Try again entering the deadline.', reply_markup=reply_markup)
		return DEADLINE

	update.message.reply_text('The deadline was succesfully set up to %s. \nToday is %s.\nNow send the first variant of the reply.' % (bet.deadline.format('DD:MM:YYYY HH:mm ZZ'), bet.start.format('DD:MM:YYYY HH:mm ZZ')))
	return LOOP

def on_loop(update, context):
	user = update.message.from_user
	variant = update.message.text
	bet_hash = context.user_data['current_bet']

	logger.info("User %s added a new variant %s to a bet: %s.", user.first_name, variant, bets.table[bet_hash].question)

	if 'variants' in context.user_data:
		context.user_data['variants'].append(variant)
	else:
		context.user_data['variants'] = [variant]

	update.message.reply_text('Any more? Send /done to stop me asking.', reply_markup=ReplyKeyboardRemove())
	return LOOP

def on_end_loop(update, context):
	user = update.message.from_user
	
	bet_hash = context.user_data['current_bet']
	bets.table[bet_hash].set_variants(context.user_data['variants'])

	logger.info("User %s finished adding new variants to a bet: %s.", user.first_name, bets.table[bet_hash].question)

	update.message.reply_text('You may find your bet by /view_%s.' % bet_hash, reply_markup=ReplyKeyboardRemove())

	# free up for the next bet
	clean_up(update, context)

	return ConversationHandler.END

