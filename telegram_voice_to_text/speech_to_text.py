from collections import namedtuple
import argparse
import io
import json
import os
import numpy
import six
import sys
from pathlib import Path

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
# import soundfile as sf
import scipy.io.wavfile
sys.path.append(str(project_root() / 'deps/Vokaturi/api'))
import Vokaturi

from telegram_voice_to_text.config import project_root

Vokaturi.load(str(project_root() / 'deps/Vokaturi/OpenVokaturi-3-0-linux64.so'))


def classify(text, verbose=True):
    """Classify the input text into categories. """

    language_client = language.LanguageServiceClient()

    document = language.types.Document(
        content=text,
        type=language.enums.Document.Type.PLAIN_TEXT)
    response = language_client.classify_text(document)
    categories = response.categories

    result = {}
    for category in categories:
        # Turn the categories into a dictionary of the form:
        # {category.name: category.confidence}, so that they can
        # be treated as a sparse vector.
        result[category.name] = category.confidence

    if verbose:
        # print(text)
        # for category in categories:
        #     print(u'=' * 20)
        #     print(u'{:<16}: {}'.format('category', category.name))
        #     print(u'{:<16}: {}'.format('confidence', category.confidence))
        print(result)
    return result


def binary_sentiment(text, verbose=True):
    client = language.LanguageServiceClient()
    # The text to analyze
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    if verbose:
        # print('Text: {}'.format(text))
        print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))

    return sentiment.score

SpeechResults = namedtuple('SpeechResults', ['text', 'sentiment', 'category'])


def process_text(text):
    bin_score = binary_sentiment(text)
    cat_dict = classify(text)
    return bin_score, cat_dict


def process_speech(speech):
    rate, data = load_path(speech)
    return SpeechResults(text='TODO text', sentiment='Happy', category=cat_dict)


def read_speech(path):
    import subprocess
    output = Path(path).resolve().parent / 'file.wav'
    subprocess.check_call(['sox', '|opusdec --force-wav {} -'.format(path), str(output)])
    # samples, sample_rate = sf.read(speech_file)
    return scipy.io.wavfile.read(output)


def get_sentiment(sample_rate, samples):
    print('Sample rate %.3f Hz' % sample_rate)

    print('Allocating Vokaturi sample array...')
    buffer_length = len(samples)
    print('%d samples, %d channels' % (buffer_length, samples.ndim))
    c_buffer = Vokaturi.SampleArrayC(buffer_length)
    if samples.ndim == 1:
        c_buffer[:] = samples[:] / 32768.0  # mono
    else:
        c_buffer[:] = 0.5*(samples[:,0]+0.0+samples[:,1]) / 32768.0  # stereo

    print('Creating VokaturiVoice...')
    try:
        voice = Vokaturi.Voice (sample_rate, buffer_length)
        voice.fill(buffer_length, c_buffer)
        quality = Vokaturi.Quality()
        emotionProbabilities = Vokaturi.EmotionProbabilities()
        voice.extract(quality, emotionProbabilities)

        if quality.valid:
            print('Neutral: %.3f' % emotionProbabilities.neutrality)
            print('Happy: %.3f' % emotionProbabilities.happiness)
            print('Sad: %.3f' % emotionProbabilities.sadness)
            print('Angry: %.3f' % emotionProbabilities.anger)
            print('Fear: %.3f' % emotionProbabilities.fear)
            sentiments = {}
            sentiments['neutral'] = emotionProbabilities.neutrality
            sentiments['happy'] = emotionProbabilities.happiness
            sentiments['sad'] = emotionProbabilities.sadness
            sentiments['angry'] = emotionProbabilities.anger
            sentiments['fearful'] = emotionProbabilities.fear
            return max(sentiments, key=lambda x: sentiments[x]).title()
    finally:
        voice.destroy()


def process_speech(speech_file):
    sample_rate, samples = read_speech(speech_file)
    return SpeechResults(text='TODO text', sentiment=get_sentiment(sample_rate, samples))
