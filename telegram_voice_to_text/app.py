#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import sys
import tempfile

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import telegram_voice_to_text.config as config
from telegram_voice_to_text.speech_to_text import process_speech, switch_language
from telegram_voice_to_text.state import get_state
from telegram_voice_to_text.categories import CATEGORIES


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hello! I am the Voice to Text and Sentiment bot!')


def help(bot, update):
    update.message.reply_text('TODO Help text')


def command_handler(bot, update):
    def language_handler(words):
        if len(words) != 1:
            reply = 'Usage: /lang <language code> or /language <language code>'
        else:
            reply = switch_language(words[0])
        update.message.reply_text(reply)

    def categories_handler(words):
        if words:
            if all(x in CATEGORIES for x in words):
                get_state().filters.text_categories = words
                reply = 'Categories updated: {}'.format(', '.join(words))
            else:
                reply = 'Invalid category found. Valid categories are: {}'.format(', '.join(CATEGORIES))
        else:
            pass  # TODO show inline options

    handlers = [
        (('lang', 'language'), language_handler),
        ('categories', categories_handler),
    ]

    words = update.message.text.split()
    for command, handler in handlers:
        if isinstance(command, str):
            command = [command]
        if words[0].lower()[1:] in command:
            return handler(words[1:])
    else:
        update.message.reply_text('Unknown command')


def voice_handler(bot, update):
    from_user = update.message.from_user
    if from_user and from_user['is_bot']:
        return
    data = update.message.voice.get_file()
    with tempfile.TemporaryDirectory() as directory:
        custom_path = Path(directory, data.file_path.rsplit('/', 1)[-1])
        data.download(custom_path=custom_path)
        result = process_speech(custom_path)
    user = '{} {}'.format(from_user['first_name'], from_user['last_name'])
    update.message.reply_text('{}, {}, {} speech from {}: {}'.format(result.audio_sentiment, result.text_sentiment, result.categories, user, result.text))


def text_handler(bot, update):
    if update.message.text == "oi":
        update.effective_user.send_message(text="oiii")
        bot.send_message(126470144, text="oii")  # erich's ID


def error(bot, update, error):
    logging.warning('Update "%s": error "%s"', update, error)


def main():
    updater = Updater(config.get('TOKEN'))
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler(Filters.command, command_handler))
    dp.add_handler(MessageHandler(Filters.voice, voice_handler))
    dp.add_handler(MessageHandler(Filters.text, text_handler))

    dp.add_error_handler(error)

    updater.start_polling()

    print('Entering idle mode')
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    main()
