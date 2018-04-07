from collections import namedtuple
from pathlib import Path
import sys

# import soundfile as sf
import scipy.io.wavfile

from telegram_voice_to_text.config import project_root

sys.path.append(str(project_root() / 'deps/Vokaturi/api'))
import Vokaturi

SpeechResults = namedtuple('SpeechResults', ['text', 'sentiment'])

Vokaturi.load(str(project_root() / 'deps/Vokaturi/OpenVokaturi-3-0-linux64.so'))


def read_speech(path):
    import subprocess
    output = Path(path).resolve().parent / 'file.wav'
    subprocess.check_call(['sox', '|opusdec --force-wav {} -'.format(path), str(output)])
    # samples, sample_rate = sf.read(speech_file)
    return scipy.io.wavfile.read(output)


def get_sentiment(speech_file):
    sample_rate, samples = read_speech(speech_file)
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

        print('Filling VokaturiVoice with samples...')
        voice.fill(buffer_length, c_buffer)

        print('Extracting emotions from VokaturiVoice...')
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
            sentiments['fear'] = emotionProbabilities.fear
            return max(sentiments, key=lambda x: sentiments[x])
    finally:
        voice.destroy()


def process_speech(speech_file):
    return SpeechResults(text='TODO text', sentiment=get_sentiment(speech_file))
