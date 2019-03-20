#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
import logging
from uuid import uuid4

from telegram import *
from telegram.ext import *
from telegram.utils import *

from create_bet_conversation import *
from bet_money_on_conversation import *
from commands import *
from Bet import * 

from bot_logging import *


def main():
	token = str(open('TOKEN').read())
	updater = Updater(token, use_context=True)

	dp = updater.dispatcher

	create_bet_handler = ConversationHandler(
		entry_points=[CommandHandler('start', on_start)],
		states={
			TYPE: [MessageHandler(Filters.regex(r'(Public|Anonymous)$'), on_type)],
			BET_QUESTION: [MessageHandler(Filters.text, on_bet_question)], 
			DEADLINE: [MessageHandler(Filters.regex(r'(Exact date|Shift)$'), on_deadline)], 

			DEADLINE_EXACT: [MessageHandler(Filters.text, on_deadline_exact)], 
			DEADLINE_SHIFT: [MessageHandler(Filters.text, on_deadline_shift), CommandHandler('done', on_end_deadline_shift)], 
			LOOP: [MessageHandler(Filters.text, on_loop), 
				  CommandHandler('done', on_end_loop)]
		},
		fallbacks=[CommandHandler('cancel', cancel)]
	)
	dp.add_handler(create_bet_handler)

	bet_money_handler = ConversationHandler(
		entry_points=[CommandHandler('bet', on_bet), 
					MessageHandler(Filters.regex(r"/view_[a-z0-9]{8}$"), on_view)],
		states={
			HASH: [MessageHandler(Filters.regex(r'[a-z0-9]{8}$'), on_bet_by_hash)],
			VARIANT: [MessageHandler(Filters.text, on_bet_by_variant)],
			SUM: [MessageHandler(Filters.regex(r'[0-9]{1,10}$'), on_bet_by_sum)],
		},
		fallbacks=[CommandHandler('cancel', cancel)]
	)
	dp.add_handler(bet_money_handler)

	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("my_bets", my_bets))


	dp.add_handler(CallbackQueryHandler(on_view_of_bet_button))
	dp.add_handler(InlineQueryHandler(inlinequery))


	dp.add_error_handler(error)

	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main()


# TODO: edit help msg

# TODO: update result and other functional button to the view menu 

# TODO: answer to button click should be a msg (in on_view_of_bet_button)

# TODO: check inline query 

# TODO: add button to bets menu -- to create a new one 