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
from Bet import * 

from bot_logging import *


def help(update, context):
	"""Send a message when the command /help is issued."""
	update.message.reply_text('Help!')

def on_view(update, context):
	user = update.message.from_user
	view_command = update.message.text
	bet_hash = view_command.split('_')[1]

	context.user_data['current_betting'] = bet_hash
	if bet_hash not in bets.table:
		update.message.reply_text('The bet does not exist.')
		return ConversationHandler.END

	send_bet(update, context, bet_hash)

	return SUM

def send_bet(update, context, bet_hash):
	bet = bets.table[bet_hash]

	keyboard = [InlineKeyboardButton(variant, callback_data=variant) for variant in bet.variants]

	reply_markup = InlineKeyboardMarkup.from_column(keyboard)

	update.message.reply_text('Pari %s: \n"%s"\nYou may choose one of the variants to bet on:' % (bet_hash, bet.question), reply_markup=reply_markup)


def on_view_of_bet_button(update, context):
	query = update.callback_query
	context.user_data['current_variant'] = query.data

	# need to be sent as a msg not as a notif 
	query.answer("Now send the amount of money you want to bet.")

def my_bets(update, context):
	for bet_hash in context.user_data['bets']:
		bet = bets.table[bet_hash]
		si = bet.short_info()

		msg += si + '\n'

	update.message.reply_text('Pari %s: \n"%s"\nYou may choose one of the variants to bet on:' % (bet_hash, bet.question), reply_markup=reply_markup)


### rewrite 
def cancel(update, context):
	user = update.message.from_user
	logger.info("User %s canceled the conversation.", user.first_name)
	update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())

	# free up for the next bet
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

	return ConversationHandler.END


inline_button_text = 'create new bet'
def inlinequery(update, context):
	"""Handle the inline query."""
	query = update.inline_query.query
	
	results = []
	update.inline_query.answer(results=results, switch_pm_text=inline_button_text, switch_pm_parameter='')

	results = [
		InlineQueryResultArticle(
			id=uuid4(),
			title="Caps",
			input_message_content=InputTextMessageContent(
				query.upper()))]

	update.inline_query.answer(results=results, switch_pm_text=inline_button_text, switch_pm_parameter='')


def error(update, context):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
	token = str(open('TOKEN').read())
	updater = Updater(token, use_context=True)

	dp = updater.dispatcher

	create_bet_handler = ConversationHandler(
		entry_points=[CommandHandler('start', on_start)],
		states={
			TYPE: [MessageHandler(Filters.regex(r'(Public|Anonymous)$'), on_type)],
			BET_QUESTION: [MessageHandler(Filters.text, on_bet_question)], 
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
# TODO: check cleaners in the end of the conversations

# TODO: update result and other functional button to the view menu 

# TODO: answer to button click should be a msg (in on_view_of_bet_button)

# TODO: send short info with parse_mode=telegram.ParseMode.MARKDOWN
# TODO: menu of all bets by user "context.user_data['bets']"

# TODO: inline should show the paris this user has created and a button to create a new one