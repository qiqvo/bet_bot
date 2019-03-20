import logging
from uuid import uuid4

from telegram import *
from telegram.ext import *
from telegram.utils import *

from Bet import * 

from bot_logging import *

send_bet_button = 'SEND_BET_BUTTON'
send_bet_hash = 'SEND_BET_HASH'

def help(update, context):
	"""Send a message when the command /help is issued."""
	update.message.reply_text('Help!')

def send_bet(update, context, bet_hash):
	bet = bets.table[bet_hash]

	keyboard = [InlineKeyboardButton(variant, callback_data=send_bet_button+variant+send_bet_hash+bet_hash) for variant in bet.variants]
	reply_markup = InlineKeyboardMarkup.from_column(keyboard)

	info = bet.long_info()
	info += '\nDo you want to bet on something?\n'

	update.message.reply_markdown(info, reply_markup=reply_markup)

def my_bets(update, context):
	if 'bets' not in context.user_data:
		update.message.reply_markdown('No bets yet.', reply_markup=ReplyKeyboardRemove())

	i = 1
	msg = ''
	for bet_hash in context.user_data['bets']:
		bet = bets.table[bet_hash]
		si = bet.short_info()
		msg += str(i) + ') ' + si
		i += 1

	update.message.reply_markdown(msg, reply_markup=ReplyKeyboardRemove())


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

def inlinequery(update, context):
	"""Handle the inline query."""
	query = update.inline_query.query
	if 'bets' not in context.user_data:
		return 

	results = []
	for bet_hash in context.user_data['bets']:
		bet = bets.table[bet_hash]
		reply_markup = InlineKeyboardMarkup.from_column([InlineKeyboardButton(variant, callback_data=send_bet_button+variant+send_bet_hash+bet_hash) for variant in bet.variants])
		text = InputTextMessageContent(bet.long_info() + '\nDo you want to bet on something?\n')

		results.append(InlineQueryResultArticle(
			id=uuid4(),
			title=bet.question,
			input_message_content=text,
			reply_markup=reply_markup,
			parse_mode=ParseMode.MARKDOWN))

	update.inline_query.answer(results=results, switch_pm_text='create new bet', switch_pm_parameter='dumb_parameter') 


def error(update, context):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, context.error)


def on_view(update, context):
	user = update.message.from_user
	view_command = update.message.text
	bet_hash = view_command.split('_')[1]

	if bet_hash not in bets.table:
		update.message.reply_text('The bet does not exist.')
		return ConversationHandler.END

	context.user_data['current_betting'] = bet_hash

	send_bet(update, context, bet_hash)