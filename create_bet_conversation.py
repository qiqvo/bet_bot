import logging
from uuid import uuid4

from telegram import *
from telegram.ext import *
from telegram.utils import *

from bot_logging import *
from Bet import *

TYPE, BET_QUESTION, LOOP = range(3)

def on_start(update, context):
	user = update.message.from_user
	keyboard = [[KeyboardButton("Public"), KeyboardButton("Anonymous")]]
	reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

	update.message.reply_text("Let's create a new bet. First, select the type of bet.", reply_markup=reply_markup)

	logger.info("User %s started.", user.first_name)

	return TYPE

def on_type(update, context):
	user = update.message.from_user
	mode = False
	if (update.message.text == 'Public'):
		mode = True

	logger.info("User %s selected mode %s.", user.first_name, update.message.text)

	context.user_data['current_mode'] = mode
	update.message.reply_text("Good. Now what is the pari?")
	return BET_QUESTION

def on_bet_question(update, context):
	user = update.message.from_user
	bet_question = update.message.text
	
	mode = context.user_data['current_mode']

	update.message.reply_text("Creating a new bet: '%s'." % bet_question)

	bet_hash = bets.add(Bet(bet_question=bet_question, mode=mode))
	
	if 'bets' in context.user_data:
		context.user_data['bets'].append(bet_hash)
	else:
		context.user_data['bets'] = [bet_hash]

	context.user_data['current_bet'] = bet_hash

	logger.info("User %s created a new bet: %s.", user.first_name,bet_question)
	
	update.message.reply_text("Cool! What is the first answer?")
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

	update.message.reply_text('Any more? Send /done to stop me asking.')

	return LOOP

def on_end_loop(update, context):
	user = update.message.from_user
	
	bet_hash = context.user_data['current_bet']
	bets.table[bet_hash].set_variants(context.user_data['variants'])

	logger.info("User %s finished adding new variants to a bet: %s.", user.first_name, bets.table[bet_hash].question)

	update.message.reply_text('You may find your bet by /view_%s.' % bet_hash)

	# free up for the next bet
	del context.user_data['variants']
	del context.user_data['current_bet']
	del context.user_data['current_mode']

	return ConversationHandler.END

