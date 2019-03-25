import logging
from uuid import uuid4

from telegram import *
from telegram.ext import *
from telegram.utils import *

from Bet import * 
from bot_logging import *

send_bet_button = 'SEND_BET_BUTTON'
manage_bet_button = 'MANAGE_BET_BUTTON'

def help(update, context):
	"""Send a message when the command /help is issued."""
	update.message.reply_text('Help!')

def create_buttons_keyboard(bet_hash):
	bet = bets.table[bet_hash]
	keyboard = []
	for variant in bet.variants:
		callback_data = send_bet_button + bet_hash + '$|`' + variant + '$|`'
		bttns = [InlineKeyboardButton(am, callback_data=callback_data + am) \
					for am in ['0', '1', '10', '100']]
		bttns[0].text = variant
		keyboard.append(bttns)

	reply_markup = InlineKeyboardMarkup(keyboard)
	return reply_markup	

def create_manage_keyboard(bet_hash):
	bet = bets.table[bet_hash]
	callback_data = manage_bet_button + bet_hash + '$|`'

	keyboard = [[InlineKeyboardButton('Show lots', callback_data=callback_data + 'show_lots')],
		[InlineKeyboardButton('Delete', callback_data=callback_data + 'delete'), 
		InlineKeyboardButton('Close', callback_data=callback_data + 'close')],
		[InlineKeyboardButton('Publish', switch_inline_query=bet.question)]]

	reply_markup = InlineKeyboardMarkup(keyboard)
	return reply_markup

def send_bet(update, context, bet_hash):
	if bet_hash not in bets.table:
		update.message.reply_text('There is no such bet.')

	bet = bets.table[bet_hash]
	reply_markup = create_manage_keyboard(bet_hash)

	info = bet.long_info()
	info += '\nDo you want to bet on something?\n'

	update.message.reply_markdown(info, reply_markup=reply_markup)

def my_bets(update, context):
	if 'bets' not in context.user_data:
		update.message.reply_markdown('No bets yet.',\
			reply_markup=ReplyKeyboardRemove())

	i = 1
	msg = ''
	for bet_hash in context.user_data['bets']:
		bet = bets.table[bet_hash]
		si = bet.short_info()
		msg += str(i) + ') /view_' + bet_hash + ' ' + si
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
	update.message.reply_text('Bye! I hope we can talk\
		 again some day.', reply_markup=ReplyKeyboardRemove())

	clean_up(update, context)

	return ConversationHandler.END

def inlinequery(update, context):
	"""Handle the inline query."""
	query = update.inline_query.query

	results = []
	if 'bets' in context.user_data:
		for bet_hash in context.user_data['bets']:
			bet = bets.table[bet_hash]
			reply_markup = create_buttons_keyboard(bet_hash)
			text = InputTextMessageContent(bet.long_info() + \
				'\nDo you want to bet on something?\n', \
				parse_mode=ParseMode.MARKDOWN)

			results.append(InlineQueryResultArticle(
				id=uuid4(),
				title=bet.question,
				input_message_content=text,
				reply_markup=reply_markup))

	update.inline_query.answer(results=results, \
		switch_pm_text='create new bet', \
		switch_pm_parameter='dumb_parameter') 


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