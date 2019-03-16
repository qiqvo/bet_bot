import logging
from uuid import uuid4

from telegram import *
from telegram.ext import *
from telegram.utils import *

from bot_logging import *
from Bet import *

HASH, VARIANT, SUM = range(3)

def on_bet(update, context):
	user = update.message.from_user
	# keyboard = [["Public", "Anonymous"]]
	# reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

	update.message.reply_text('Send me the hash of the pari you want to bet on')# , reply_markup=reply_markup)

	return HASH

def on_bet_by_hash(update, context):
	user = update.message.from_user
	
	if 'current_betting' not in context.user_data:
		bet_hash = update.message.text
		if bet_hash not in bets.table:
			update.message.reply_text("That pari does not exist.")
			return HASH
	else:
		bet_hash = context.user_data['current_betting']

	bet = bets.table[bet_hash]
	context.user_data['current_betting'] = bet_hash
	
	reply_markup = ReplyKeyboardMarkup.from_column(bet.variants, one_time_keyboard=True, resize_keyboard=True)

	update.message.reply_text("You're betting on the '%s'. Select the variant from the list." % bet.question, reply_markup=reply_markup)

	return VARIANT

def on_bet_by_variant(update, context):
	user = update.message.from_user
	bet_hash = context.user_data['current_betting']
	bet = bets.table[bet_hash]

	variant = update.message.text
	if variant not in bet.variants:
		reply_markup = ReplyKeyboardMarkup.from_column(bet.variants, one_time_keyboard=True, resize_keyboard=True)
		update.message.reply_text("Such variant does not exist. Try again.", reply_markup=reply_markup)
		return VARIANT
	
	context.user_data['current_variant'] = variant
	update.message.reply_text("Now send the amount of money you want to bet.")
	return SUM

def on_bet_by_sum(update, context):
	user = update.message.from_user
	bet_hash = context.user_data['current_betting']
	variant = context.user_data['current_variant']
	bet = bets.table[bet_hash]

	money = int(update.message.text)
	bet.add_money(variant, user.id, money)

	update.message.reply_text("Your bet has been taken. Now it is %i for the variant %s." % (bet.money_table[variant][user.id], variant))

	return ConversationHandler.END
