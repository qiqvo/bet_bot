import logging
from uuid import uuid4

from telegram import *
from telegram.ext import *
from telegram.utils import *

from bot_logging import *
from Bet import *
import arrow
from commands import *

def callback_query_handler(update, context):
	raw_query = update.callback_query
	if send_bet_button in raw_query.data:
		query = raw_query.data.split(send_bet_button)[1]
		bet_hash, variant, amount = query.split('$|`')
		bet = bets.table[bet_hash]
		money = int(amount)
		user_id = raw_query.from_user.id

		if money == 0:
			if user_id in bet.money_table[variant]:
				raw_query.answer("You have bet %i on this one." % \
					bet.money_table[variant][user_id])
			else:
				raw_query.answer("You haven't yet bet on this one.")
		else:
			bet.add_money(variant, user_id, money)
			reply_markup = create_buttons_keyboard(bet_hash)
			raw_query.edit_message_text(bet.long_info() + \
				'\nDo you want to bet on something?\n', \
				parse_mode=ParseMode.HTML, \
				reply_markup=reply_markup)
	elif manage_bet_button in raw_query.data:
		query = raw_query.data.split(manage_bet_button)[1]
		bet_hash, query = query.split('$|`')
		bet = bets.table[bet_hash]
		callback_data = manage_bet_button + bet_hash + '$|`' 
		if query == 'show_lots':
			reply_markup = create_buttons_keyboard(bet_hash)
			raw_query.edit_message_reply_markup(reply_markup=reply_markup)
		elif query == 'delete':
			raw_query.answer('Action cannot be undone.')
			keyboard = [InlineKeyboardButton('Delete', callback_data=callback_data + 'delete_delete'),
						InlineKeyboardButton('Abort', callback_data=callback_data + 'delete_abort')] 
			reply_markup = InlineKeyboardMarkup.from_row(keyboard)
			raw_query.edit_message_reply_markup(reply_markup=reply_markup)
		elif query == 'delete_delete':
			raw_query.edit_message_reply_markup(reply_markup=None)
			context.user_data['bets'].remove(bet_hash)
			del bets.table[bet_hash]
		elif query == 'delete_abort':
			reply_markup = create_manage_keyboard(bet_hash)
			raw_query.edit_message_reply_markup(reply_markup=reply_markup)
		elif query == 'close':
			keyboard = InlineKeyboardButton('Restore', callback_data=callback_data + 'close_restore')
			reply_markup = InlineKeyboardMarkup.from_button(keyboard)
			raw_query.edit_message_reply_markup(reply_markup=reply_markup)
			bet.real_deadline = bet.deadline
			bet.deadline = arrow.utcnow()
		elif query == 'close_restore':
			bet.deadline = bet.real_deadline
			reply_markup = create_manage_keyboard(bet_hash)
			raw_query.edit_message_reply_markup(reply_markup=reply_markup)
	else:
		query.answer("Something went wrong!")