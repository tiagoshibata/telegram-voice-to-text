#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import tempfile

import requests
import pytesseract
from PIL import Image
from clarifai.rest import ClarifaiApp
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import telegram_voice_to_text.config as config
from telegram_voice_to_text.speech_to_text import process_speech
from telegram_voice_to_text.text_analysis import process_text, is_desired_category, is_emergency_text
from telegram_voice_to_text.state import get_state
from telegram_voice_to_text.command_handler import command_handler
from telegram_voice_to_text.start_command import start
from telegram_voice_to_text.help_command import help
import telegram_voice_to_text.private_reply as private_reply

selected_topics = []


def parse_user(update):
    from_user = update.message.from_user
    if from_user and from_user['is_bot']:
        return
    return '{} {}'.format(from_user['first_name'], from_user['last_name'])


def voice_handler(bot, update):
    user = parse_user(update)
    if not user:
        return
    data = update.message.voice.get_file()
    with tempfile.TemporaryDirectory() as directory:
        custom_path = Path(directory, data.file_path.rsplit('/', 1)[-1])
        data.download(custom_path=str(custom_path))
        result = process_speech(custom_path)


    reply = []
    if result.audio_sentiment:
        print(result.audio_sentiment)
        sentiment = max(
            result.audio_sentiment.keys(),
            key=lambda x: result.audio_sentiment[x])
        reply.append("Speaker's voice is {}".format(sentiment))
    if result.text_sentiment:
        if result.text_sentiment < -0.25:
            emoji = '🙁'
        elif result.text_sentiment < 0.25:
            emoji = '😐'
        else:
            emoji = '🙂'
        reply.append('Text mood: {}'.format(emoji))
    if result.categories:
        categories = result.categories.keys()
        categories = set([x.split('/', 2)[1] for x in categories])
        reply.append('Related categories: {}'.format(', '.join(categories)))

    update.message.reply_markdown('. '.join(reply) + '.\n*{}*\n{}'.format(
        user, result.text or '_No text detected_'
    ))
    private_message_if_emergency(bot, update, result.text, categories=result.categories)


def button_handler(bot, update):
    query = update.callback_query

    global selected_topics

    state = get_state()
    if query.data == "OK":
        state.filters.enable_get_categories = False
        bot.edit_message_text(text="Selection stored: " + ", ".join(state.filters.text_categories),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    elif state.filters.enable_get_categories:
        if query.data not in state.filters.text_categories:
            state.filters.text_categories += [query.data]
            print(state.filters.text_categories)


def text_handler(bot, update):
    private_message_if_emergency(bot, update, update.message.text)


def photo_analysis(bot, update, file_url):
    response = requests.get(file_url, stream=True)
    response.raise_for_status()

    with open('output.jpg', 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)

    with open('output.jpg', 'rb') as handle:
        text = pytesseract.image_to_string(Image.open(handle))
        if text:
            print('*OCR:* {}'.format(text))
            update.message.reply_text(text)

    app = ClarifaiApp(api_key='d8090e6a90104ec0b190f3a975e5b912')
    model = app.models.get("general-v1.3")
    result = model.predict_by_url(url=file_url)

    text_result = []
    for x in result['outputs'][0]['data']['concepts'][:5]:
        text_result.append(x['name'])
    update.message.reply_markdown('*Image content:* {}'.format(', '.join(text_result)))


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


def private_message_if_emergency(bot, update, text, categories=None):
    user = parse_user(update)
    if not user:
        return
    relevant = False
    if is_emergency_text(text):
        relevant = True
    else:
        if categories is None:
            _, categories = process_text(text)
        relevant = is_desired_category(categories)
    if relevant:
        private_reply.send_message(bot, '*Important from {}*: {}'.format(user, text))


def main():
    updater = Updater(config.get('TOKEN'))
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler(Filters.command, command_handler))
    dp.add_handler(MessageHandler(Filters.voice, voice_handler))
    dp.add_handler(MessageHandler(Filters.text, text_handler))
    dp.add_handler(MessageHandler(Filters.document, photo_handler))
    dp.add_handler(MessageHandler(Filters.document, document_handler))
    dp.add_handler(MessageHandler(Filters.photo, photo_handler))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_error_handler(error)

    updater.start_polling()

    print('Entering idle mode')
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    main()
