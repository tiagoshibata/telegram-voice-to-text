from telegram import Chat

CHAT_IDS = [537816449, 126470144]


def get_private_chat():
    return [Chat(x, Chat.PRIVATE) for x in CHAT_IDS]
