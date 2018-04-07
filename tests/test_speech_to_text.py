import numpy as np

from telegram_voice_to_text.speech_to_text import get_sentiment, process_speech_text, process_text, read_speech
from telegram_voice_to_text.config import project_root


def test_get_sentiment():
    sentiment = get_sentiment(*read_speech(project_root() / 'tests/file_6.oga'))
    assert sentiment[0] == 'sad'
    assert sentiment[1] > .99


def test_process_speech_text():
    process_speech_text(np.array([0, 0, 0]), 16000)


def test_process_text():
    process_text('''
Far out in the uncharted backwaters of the unfashionable end of
the western spiral arm of the Galaxy lies a small unregarded
yellow sun.''')
