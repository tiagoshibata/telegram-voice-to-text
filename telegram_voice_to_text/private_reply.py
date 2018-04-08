# from telegram import Chat
from telegram import ParseMode

CHAT_IDS = [537816449, 126470144]


# def get_private_chats():
#     return [Chat(x, Chat.PRIVATE) for x in CHAT_IDS]


def send_message(bot, *args, **kwargs):
    for chat_id in CHAT_IDS:
        bot.send_message(chat_id, parse_mode=ParseMode.MARKDOWN, *args, **kwargs)
