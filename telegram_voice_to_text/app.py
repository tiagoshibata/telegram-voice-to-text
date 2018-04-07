#!/usr/bin/env python
import logging
from pathlib import Path
import sys
import tempfile

import telegram_voice_to_text.config as config
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from telegram_voice_to_text.speech_to_text import process_speech, switch_language


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hello! I am the Voice to Text and Sentiment bot!')


def help(bot, update):
    command_code = update.message.text.startswith('/lang')
    if command_code.startswith('/lang'):
        reply = switch_language(command_code.split(" ")[1])
        update.message.reply_text(reply)
    else:
        update.message.reply_text('TODO Help text')


def command_handler(bot, update):
    update.message.reply_text('TODO commands')


def voice_handler(bot, update):
    from_user = update.message.from_user
    if from_user and from_user['is_bot']:
        return
    data = update.message.voice.get_file()
    print(data.file_path)
    with tempfile.TemporaryDirectory() as directory:
        custom_path = Path(directory, data.file_path.rsplit('/', 1)[-1])
        data.download(custom_path=custom_path)
        result = process_speech(custom_path)
    user = '{} {}'.format(from_user['first_name'], from_user['last_name'])
    update.message.reply_text('{}, {}, {} speech from {}: {}'.format(result.audio_sentiment, result.text_sentiment, result.categories, user, result.text))


def error(bot, update, error):
    logging.warning('Update "%s": error "%s"', update, error)


def main():
    updater = Updater(config.get('TOKEN'))
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler(Filters.command, command_handler))
    dp.add_handler(MessageHandler(Filters.voice, voice_handler))

    dp.add_error_handler(error)

    updater.start_polling()

    print('Entering idle mode')
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    main()
