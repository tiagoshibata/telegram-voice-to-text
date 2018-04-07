from collections import namedtuple

SpeechResults = namedtuple('SpeechResults', ['text', 'sentiment'])


def process_speech(speech_raw, sample_rate):

    text = process_speech_text(speech_raw, sample_rate)

    return SpeechResults(text=text, sentiment='Happy')


def process_speech_text(speech_raw, sample_rate):
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types

    client = speech.SpeechClient()

    audio = types.RecognitionAudio(content=speech_raw)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code='en-US')

    # Detects speech in the audio file
    response = client.recognize(config, audio)

    text = ""
    total_confidence = 0

    for result in response.results:
        text += result.alternatives[0].transcript + " "
        total_confidence += result.alternatives[0].confidence/len(response.results)

    print(total_confidence)

    return text
