import numpy as np

from telegram_voice_to_text.speech_to_text import get_sentiment, speech_to_text, read_speech
from telegram_voice_to_text.config import project_root


def test_get_sentiment():
    sentiment = get_sentiment(*read_speech(project_root() / 'tests/file_6.oga'))
    assert sentiment[0] == 'sad'
    assert sentiment[1] > .99


def test_speech_to_text():
    speech_to_text(np.array([0, 0, 0]), 16000)
