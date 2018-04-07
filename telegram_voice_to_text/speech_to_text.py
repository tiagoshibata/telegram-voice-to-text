from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

from collections import namedtuple
import argparse
import io
import json
import os
import numpy
import six
import sys

sys.path.insert('../deps/Vokaturi')
import sent_analysis

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
