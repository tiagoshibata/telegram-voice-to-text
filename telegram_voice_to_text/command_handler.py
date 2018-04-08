from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram_voice_to_text.speech_to_text import process_speech, switch_language
from telegram_voice_to_text.state import get_state
from telegram_voice_to_text.categories import CATEGORIES


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
