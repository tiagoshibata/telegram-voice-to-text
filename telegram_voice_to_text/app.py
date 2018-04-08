#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import sys
import tempfile

import requests
import pytesseract
from PIL import Image
from clarifai.rest import ClarifaiApp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import telegram_voice_to_text.config as config
from telegram_voice_to_text.speech_to_text import process_speech, switch_language
from telegram_voice_to_text.state import get_state, Filter
from telegram_voice_to_text.categories import CATEGORIES

selected_topics = []


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

    def topic_selection_handler(words):
        Filter.enable_get_categorie = True
        Filter.text_categories = []

        categorie = [CATEGORIES[cat] for cat in CATEGORIES]

        keyboard = [InlineKeyboardButton(x, callback_data=x) for x in categorie]

        keyboard = [keyboard[x:x + 4] for x in range(0, len(keyboard), 4)]

        keyboard += [[InlineKeyboardButton("OK", callback_data="OK")]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('Please choose the topics you have interest and press ok:',
                                  reply_markup=reply_markup)

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
        (('topics', 'topic'), topic_selection_handler),
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
        data.download(custom_path=str(custom_path))
        result = process_speech(custom_path)
    user = '{} {}'.format(from_user['first_name'], from_user['last_name'])
    update.message.reply_text('{}, {}, {} speech from {}: {}'.format(result.audio_sentiment, result.text_sentiment, result.categories, user, result.text))


def button_handler(bot, update):
    query = update.callback_query

    global selected_topics

    if query.data == "OK":
        Filter.enable_get_categorie = False
        bot.edit_message_text(text="Selection stored: " + str(Filter.text_categories),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    elif Filter.enable_get_categorie:
        if query.data not in Filter.text_categories:
            Filter.text_categories += [query.data]
            print(Filter.text_categories)


def text_handler(bot, update):
    text  = update.message.text
    if update.message.text == "oi":
        update.effective_user.send_message(text="oiii")
        bot.send_message(126470144, text="oii")  # erich's ID


def photo_handler(bot, update):
    file = update.message.document.get_file(timeout=120)

    response = requests.get(file['file_path'], stream=True)
    response.raise_for_status()

    with open('output.jpg', 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)

    with open('output.jpg', 'r') as handle:
        text = pytesseract.image_to_string(Image.open(handle))
        update.message.reply_text(u"Transcrição do texto da imagem: " + text)

    app = ClarifaiApp(api_key='d8090e6a90104ec0b190f3a975e5b912')
    model = app.models.get("general-v1.3")
    result = model.predict_by_url(url=file['file_path'])

    i = 0
    text_result = ""
    for x in result['outputs'][0]['data']['concepts']:
        text_result += x['name'] + "\n"
        i += 1
        if i > 5:
            break
    update.message.reply_text(u"Conteúdo da imagem: " + text_result)


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
    dp.add_handler(MessageHandler(Filters.document, photo_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_handler))

    dp.add_error_handler(error)

    updater.start_polling()

    print('Entering idle mode')
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    main()
