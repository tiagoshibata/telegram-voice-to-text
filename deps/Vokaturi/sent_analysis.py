import sys
import scipy.io.wavfile

sys.path.append("api/")
import Vokaturi

def sentiment_analysis (path=sys.argv[1]):
    print("Loading library...")
    Vokaturi.load("./OpenVokaturi-3-0-linux64.so")
    print("Analyzed by: %s" % Vokaturi.versionAndLicense())

    print("Reading sound file...")
    file_name = path
    (sample_rate, samples) = scipy.io.wavfile.read(file_name)
    print("   sample rate %.3f Hz" % sample_rate)

    print("Allocating Vokaturi sample array...")
    buffer_length = len(samples)
    print("   %d samples, %d channels" % (buffer_length, samples.ndim))
    c_buffer = Vokaturi.SampleArrayC(buffer_length)
    if samples.ndim == 1:
        c_buffer[:] = samples[:] / 32768.0  # mono
    else:
        c_buffer[:] = 0.5*(samples[:,0]+0.0+samples[:,1]) / 32768.0  # stereo

    print("Creating VokaturiVoice...")
    voice = Vokaturi.Voice (sample_rate, buffer_length)

    print("Filling VokaturiVoice with samples...")
    voice.fill(buffer_length, c_buffer)

    print("Extracting emotions from VokaturiVoice...")
    quality = Vokaturi.Quality()
    emotionProbabilities = Vokaturi.EmotionProbabilities()
    voice.extract(quality, emotionProbabilities)

    if quality.valid:
        print("Neutral: %.3f" % emotionProbabilities.neutrality)
        print("Happy: %.3f" % emotionProbabilities.happiness)
        print("Sad: %.3f" % emotionProbabilities.sadness)
        print("Angry: %.3f" % emotionProbabilities.anger)
        print("Fear: %.3f" % emotionProbabilities.fear)
        out_dict = {}
        out_dict['neutral'] = emotionProbabilities.neutrality
        out_dict['happy'] = emotionProbabilities.happiness
        out_dict['sad'] = emotionProbabilities.sadness
        out_dict['angry'] = emotionProbabilities.anger
        out_dict['fear'] = emotionProbabilities.fear
        voice.destroy()
        return out_dict

sentiment_analysis()
