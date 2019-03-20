import logging
from uuid import uuid4

from telegram import *
from telegram.ext import *
from telegram.utils import *

from Bet import * 

from bot_logging import *


def help(update, context):
	"""Send a message when the command /help is issued."""
	update.message.reply_text('Help!')

def send_bet(update, context, bet_hash):
	bet = bets.table[bet_hash]

	keyboard = [InlineKeyboardButton(variant, callback_data=variant) for variant in bet.variants]

	reply_markup = InlineKeyboardMarkup.from_column(keyboard)

	info = bet.long_info()
	info += '\nDo you want to bet on something?\n'

	update.message.reply_markdown(info, reply_markup=reply_markup)


def on_view_of_bet_button(update, context):
	query = update.callback_query
	context.user_data['current_variant'] = query.data

	# need to be sent as a msg not as a notif 
	query.answer("Now send the amount of money you want to bet.")

def my_bets(update, context):
	i = 1
	for bet_hash in context.user_data['bets']:
		bet = bets.table[bet_hash]
		si = bet.short_info()
		msg += str(i) + ') ' + si
		i += 1

	update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove(), parse_mode=telegram.ParseMode.MARKDOWN)


def clean_up(update, context):
	if 'variants' in context.user_data:
		del context.user_data['variants']
	if 'current_bet' in context.user_data:
		del context.user_data['current_bet']
	if 'current_mode' in context.user_data:
		del context.user_data['current_mode']
	if 'current_betting' in context.user_data:
		del context.user_data['current_betting']
	if 'current_variant' in context.user_data:
		del context.user_data['current_variant']
	if 'pattern' in context.user_data:
		del context.user_data['pattern']
	if 'shift' in context.user_data:
		del context.user_data['shift']

### rewrite 
def cancel(update, context):
	user = update.message.from_user
	logger.info("User %s canceled the conversation.", user.first_name)
	update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())

	clean_up(update, context)

	return ConversationHandler.END


inline_button_text = 'create new bet'
def inlinequery(update, context):
	"""Handle the inline query."""
	query = update.inline_query.query
	if 'bets' not in context.user_data:
		return 
		
	bet_hash_s = context.user_data['bets']

	results = [
		InlineQueryResultArticle(
			id=uuid4(),
			title=bets.table[bet_hash].question,
			input_message_content=InputTextMessageContent('/view_'+bet_hash)) 
		for bet_hash in bet_hash_s]

	update.inline_query.answer(results=results)#, switch_pm_text=inline_button_text) #, switch_pm_parameter='start') 


def error(update, context):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, context.error)