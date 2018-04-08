from telegram_voice_to_text.speech_to_text import process_text


def test_process_text():
    process_text('''
Far out in the uncharted backwaters of the unfashionable end of
the western spiral arm of the Galaxy lies a small unregarded
yellow sun.''')
