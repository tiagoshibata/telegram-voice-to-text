from collections import namedtuple
import sys

from .state import get_state
from .speech_analysis import read_speech, speech_to_text, get_sentiment, is_important_sentiment
from .text_analysis import preprocess_text, process_text, is_emergency_text, is_desired_category

language_codes = {
    'english': 'en-US',
    'português': 'pt-BR',
}

languages = {
    'en-US': 'Language set to English!',
    'pt-BR': 'Português selecionado!',
}

SpeechResults = namedtuple('SpeechResults', ['text', 'audio_sentiment', 'categories',
                           'text_sentiment', 'relevant'])

def switch_language(new_language):
    state = get_state()
    language_code = language_codes.get(new_language, new_language)
    if language_code in languages:
        state.language = language_code
        return languages[language_code]
    return 'Invalid language code. '


def process_speech(speech_file):
    sample_rate, samples = read_speech(speech_file)
    text = speech_to_text(samples, sample_rate)
    text = preprocess_text(text)
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
