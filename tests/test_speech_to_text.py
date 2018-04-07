from telegram_voice_to_text.speech_to_text import get_sentiment
from telegram_voice_to_text.config import project_root


def test_get_sentiment():
    assert get_sentiment(project_root() / 'tests/file_6.oga') == 'sad'
