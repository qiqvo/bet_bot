import logging
from uuid import uuid4

from telegram import *
from telegram.ext import *
from telegram.utils import *

from bot_logging import *
from Bet import *
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
				parse_mode=ParseMode.MARKDOWN, \
				reply_markup=reply_markup)
	else:
		query.answer("Something went wrong!")