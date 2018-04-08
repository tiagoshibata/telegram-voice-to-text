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
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import telegram_voice_to_text.config as config
from telegram_voice_to_text.speech_to_text import process_speech, switch_language
from telegram_voice_to_text.text_analysis import process_text, is_desired_category, is_emergency_text
from telegram_voice_to_text.state import get_state
from telegram_voice_to_text.categories import CATEGORIES
import telegram_voice_to_text.private_reply as private_reply

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
        get_state().filters.enable_get_categorie = True
        get_state().filters.text_categories = []

        categorie = [cat for cat in CATEGORIES]

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

    state = get_state()
    if query.data == "OK":
        state.filters.enable_get_categorie = False
        bot.edit_message_text(text="Selection stored: " + ", ".join(state.filters.text_categories),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    elif state.filters.enable_get_categorie:
        if query.data not in state.filters.text_categories:
            state.filters.text_categories += [query.data]
            print(state.filters.text_categories)


def text_handler(bot, update):
    text  = update.message.text

    def is_relevant():
        if is_emergency_text(text):
            return True
        binary_score, categories = process_text(text)
        return is_desired_category(categories)

    if is_relevant():
        from_user = update.message.from_user
        if from_user and from_user['is_bot']:
            return
        user = '{} {}'.format(from_user['first_name'], from_user['last_name'])
        private_reply.send_message(bot, '*Important from {}*: {}'.format(user, text))

    # if update.message.text == "oi":
    #     update.effective_user.send_message(text="oiii")
    # if update.message.text == "emotion":
    #     chat_id = update.message.chat_id
    #     custom_keyboard = [['ON', 'OFF']]
    #     reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
    #     bot.send_message(chat_id=chat_id,
    #                   text="Turn emotion filter on?",
    #                   reply_markup=reply_markup)
    # if update.message.text == "ON":
    #     emotion_filter = True
    #     update.effective_user.send_message(text="Emotion filter ON!")
    # if update.message.text == "OFF":
    #     emotion_filter = False
    #     update.effective_user.send_message(text="Emotion filter OFF!")

def photo_analysis(bot, update, file_url):
    response = requests.get(file_url, stream=True)
    response.raise_for_status()

    with open('output.jpg', 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)

    with open('output.jpg', 'r') as handle:
        text = pytesseract.image_to_string(Image.open(handle))
        update.message.reply_text(u"Transcrição do texto da imagem: " + text)

    app = ClarifaiApp(api_key='d8090e6a90104ec0b190f3a975e5b912')
    model = app.models.get("general-v1.3")
    result = model.predict_by_url(url=file_url)

    i = 0
    text_result = ""
    for x in result['outputs'][0]['data']['concepts']:
        text_result += x['name'] + "\n"
        i += 1
        if i > 5:
            break
    update.message.reply_text(u"Conteúdo da imagem: " + text_result)


def photo_handler(bot, update):
    print (update.message.photo)
    file = update.message.photo[-1].get_file()
    photo_analysis(bot, update, file.file_path)


def document_handler(bot, update):
    print (update.message.document)
    file = update.message.document.get_file(timeout=120)
    photo_analysis(bot, update, file['file_path'])


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
    dp.add_handler(MessageHandler(Filters.document, document_handler))
    dp.add_handler(MessageHandler(Filters.photo, photo_handler))

    dp.add_error_handler(error)

    updater.start_polling()

    print('Entering idle mode')
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    main()
