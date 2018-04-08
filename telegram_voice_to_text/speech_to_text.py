from collections import namedtuple

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.api_core.exceptions import InvalidArgument
import scipy.io.wavfile

lang = 'en-US'

language_codes = {
    'english': 'en-US',
    'português': 'pt-BR',
}

languages = {
    'en-US': 'Now language is english',
    'pt-BR': 'Agora a o bot está em português',
}

def switch_language(language):
    global lang
    language_code = language_codes.get(language, language)
    if language_code in languages:
        lang = language_code
        return languages[language_code]
    return 'Invalid language code. '


def process_speech_text(speech_raw, sample_rate):
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types

    client = speech.SpeechClient()

    audio = types.RecognitionAudio(content=speech_raw.tobytes())

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code=lang)

    # Detects speech in the audio file
    response = client.recognize(config, audio)

    text = ""
    total_confidence = 0

    for result in response.results:
        text += result.alternatives[0].transcript + " "
        total_confidence += result.alternatives[0].confidence/len(response.results)

    print(total_confidence)

    return text



def classify(text, verbose=True):
    """Classify the input text into categories. """

    language_client = language.LanguageServiceClient()

    document = language.types.Document(
        content=text,
        type=language.enums.Document.Type.PLAIN_TEXT,
        lang=lang)
    try:
        response = language_client.classify_text(document)
    except InvalidArgument as e:
        print(e)
        return
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
        type=enums.Document.Type.PLAIN_TEXT,
        lang=lang)

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    if verbose:
        # print('Text: {}'.format(text))
        print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))

    return sentiment.score

SpeechResults = namedtuple('SpeechResults', ['text', 'audio_sentiment', 'categories', 'text_sentiment'])


def process_text(text):
    bin_score = binary_sentiment(text)
    categories_dict = classify(text)
    return bin_score, categories_dict


def read_speech(path):
    import subprocess
    output = Path(path).resolve().parent / 'file.wav'
    subprocess.check_call(['sox', '|opusdec --force-wav {} -'.format(path), str(output)])
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
            sentiments = {
                'neutral': emotionProbabilities.neutrality,
                'happy': emotionProbabilities.happiness,
                'sad': emotionProbabilities.sadness,
                'angry': emotionProbabilities.anger,
                'fearful': emotionProbabilities.fear,
            }
            print('Sentiments: {}'.format(sentiments))
            sentiment = max(sentiments, key=lambda x: sentiments[x])
            return sentiment, sentiments[sentiment]
    finally:
        voice.destroy()


def process_speech(speech_file):
    sample_rate, samples = read_speech(speech_file)
    text = process_speech_text(samples, sample_rate)
    text = preprocess_text(text)
    text_sentiment, text_categories = process_text(text)
    return SpeechResults(
        text=text,
        audio_sentiment=get_sentiment(sample_rate, samples),
        categories=text_categories,
        text_sentiment=text_sentiment,
    )


def process_speech_text(speech_raw, sample_rate):
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types

    client = speech.SpeechClient()

    audio = types.RecognitionAudio(content=speech_raw.tobytes())

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code=lang)

    # Detects speech in the audio file
    response = client.recognize(config, audio)

    text = ""
    total_confidence = 0

    for result in response.results:
        text += result.alternatives[0].transcript + " "
        total_confidence += result.alternatives[0].confidence/len(response.results)

    print(total_confidence)

    return text



def classify(text, verbose=True):
    """Classify the input text into categories. """

    language_client = language.LanguageServiceClient()

    document = language.types.Document(
        content=text,
        type=language.enums.Document.Type.PLAIN_TEXT)
    try:
        response = language_client.classify_text(document)
    except InvalidArgument as e:
        print(e)
        return
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

SpeechResults = namedtuple('SpeechResults', ['text', 'audio_sentiment', 'categories', 'text_sentiment'])


def process_text(text):
    bin_score = binary_sentiment(text)
    categories_dict = classify(text)
    return bin_score, categories_dict


def read_speech(path):
    import subprocess
    output = Path(path).resolve().parent / 'file.wav'
    subprocess.check_call(['sox', '|opusdec --force-wav {} -'.format(path), str(output)])
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
            sentiments = {
                'neutral': emotionProbabilities.neutrality,
                'happy': emotionProbabilities.happiness,
                'sad': emotionProbabilities.sadness,
                'angry': emotionProbabilities.anger,
                'fearful': emotionProbabilities.fear,
            }
            print('Sentiments: {}'.format(sentiments))
            sentiment = max(sentiments, key=lambda x: sentiments[x])
            return sentiment, sentiments[sentiment]
    finally:
        voice.destroy()


def process_speech(speech_file):
    sample_rate, samples = read_speech(speech_file)
    text = process_speech_text(samples, sample_rate)
    text = preprocess_text(text)
    text_sentiment, text_categories = process_text(text)
    return SpeechResults(
        text=text,
        audio_sentiment=get_sentiment(sample_rate, samples),
        categories=text_categories,
        text_sentiment=text_sentiment,
    )


def preprocess_text(raw_text):
    words = len(raw_text.split(sep=' '))
    if words < 10:
         return raw_text
    elif words < 20:
        extended_text = raw_text + ' ' + raw_text
        return extended_text
    else: return raw_text
