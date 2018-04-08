TEXT = ('Hello! I am the Voice to Text and Sentiment bot!\n\n'
'Have you ever received audio while in the bus or in subway, without headphones? Did *eyes roll* when when playing it? '
'Has your music been interrupted by a friend who *insists* on using audio? Do you have a hearing disability? '
'Your problems are over! With the *Voice to Text and Sentiment* bot, you can convert speech to text '
'and sentiment information.\n\n'
'Furthermore, the bot can listen in group chats and notify you whenever a topic of your interest is being discussed, in text or speech, or whenever an urgent message is sent, so you can keep track of long conversations. See /help for commands!')


def start(bot, update):
    update.message.reply_markdown(TEXT)
