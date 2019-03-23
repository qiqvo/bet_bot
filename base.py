#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
import logging
from uuid import uuid4

from telegram import *
from telegram.ext import *
from telegram.utils import *

from create_bet_conversation import *
from button_conversation import *
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
			BET_QUESTION: [MessageHandler(Filters.text, on_bet_question)], 
			
			ANSWER_LOOP: [MessageHandler(Filters.text, on_loop), 
				  CommandHandler('done', on_end_loop)],

			DEADLINE_SHIFT: [MessageHandler(Filters.text, on_deadline_shift), CommandHandler('done', on_end_deadline_shift)], 
			
		},
		fallbacks=[CommandHandler('cancel', cancel)]
	)
	dp.add_handler(create_bet_handler)

	bet_money_button_handler = ConversationHandler(
		entry_points=[CallbackQueryHandler(callback_query_handler)],
		fallbacks=[CallbackQueryHandler(callback_query_handler), CommandHandler('cancel', cancel)],
		states = {},
		per_message=True
	)
	dp.add_handler(bet_money_button_handler)

	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("my_bets", my_bets))
	dp.add_handler(MessageHandler(Filters.regex(r"/view_[a-z0-9]{8}$"), on_view))

	dp.add_handler(InlineQueryHandler(inlinequery))
	#dp.add_handler(CallbackQueryHandler(callback_query_handler))
	#dp.add_handler()

	dp.add_error_handler(error)

	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main()


# TODO: edit help msg

# TODO: update result and other functional button to the view menu 

# TODO: add button to bets menu -- to create a new one 

# TODO: add pattern to callbacks https://python-telegram-bot.readthedocs.io/en/latest/telegram.ext.callbackqueryhandler.html?highlight=Handler