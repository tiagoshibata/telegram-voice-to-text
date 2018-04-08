from pathlib import Path
import sys

from google.cloud import speech
from google.cloud.speech import enums, types
import scipy.io.wavfile

from .config import project_root
from .state import get_state

vokaturi_directory = project_root() / 'deps/Vokaturi'
sys.path.append(str(vokaturi_directory / 'api'))
import Vokaturi
Vokaturi.load(str(vokaturi_directory / 'OpenVokaturi-3-0-linux64.so'))


def read_speech(path):
    import subprocess
    output = str(Path(path).resolve().parent / 'file.wav')
    subprocess.check_call(['sox', '|opusdec --force-wav {} -'.format(path), output])
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


def speech_to_text(speech_raw, sample_rate):
    client = speech.SpeechClient()
    audio = types.RecognitionAudio(content=speech_raw.tobytes())
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code=get_state().language)

    # Detects speech in the audio file
    response = client.recognize(config, audio)

    text = ""
    total_confidence = 0

    for result in response.results:
        text += result.alternatives[0].transcript + " "
        total_confidence += result.alternatives[0].confidence/len(response.results)

    print(total_confidence)

    return text


def is_important_sentiment(sentiment):
    return any(sentiment[x] > 0.5 for x in ['angry', 'fearful'])
