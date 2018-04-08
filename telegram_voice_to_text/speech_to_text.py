from collections import namedtuple

from .state import get_state
from .speech_analysis import read_speech, speech_to_text, get_sentiment, is_important_sentiment
from .text_analysis import process_text, is_emergency_text, is_desired_category

SpeechResults = namedtuple('SpeechResults', ['text', 'audio_sentiment', 'categories',
                           'text_sentiment', 'relevant'])


def process_speech(speech_file):
    sample_rate, samples = read_speech(speech_file)
    text = speech_to_text(samples, sample_rate)
    text_sentiment, text_categories = process_text(text)
    audio_sentiment = get_sentiment(sample_rate, samples)
    relevant = True
    if get_state().filters.speech_sentiments_enabled:
        relevant = is_important_sentiment(audio_sentiment)
    if is_emergency_text(text) or is_desired_category(text_categories):
        relevant = True
    return SpeechResults(
        text=text,
        audio_sentiment=audio_sentiment,
        categories=text_categories,
        text_sentiment=text_sentiment,
        relevant=relevant,
    )
