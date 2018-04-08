TEXT = ('Currently Text and Sentiment bot supports the following commands:\n'
                              '/start to start the bot\n'
                              '/lang <language> to select your input language\n'
                              '/topics to filter transcribed messages texts\n'
                              '/help to get help on commands\n'
                              '/sentiment <ON or OFF> filter messages based on sentiment\n'
                              'Need some extra help? Don\'t hesitate to contact us!')


def help(bot, update):
    update.message.reply_text(TEXT)
