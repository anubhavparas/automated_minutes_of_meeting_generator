import io
import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

client = speech.SpeechClient()

audio = types.RecognitionAudio(uri='gs://mom_tip_files/wayne-olson.long.wav')
config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
        use_enhanced=True,
        model='phone_call'
        )

operation = client.long_running_recognize(config, audio)

print('Waiting for op to complete...')

response = operation.result(timeout=600)

for result in response.results:
    print('Transcript: {}'.format(result.alternatives[0].transcript))
    print('Confidence: {}'.format(result.alternatives[0].confidence))

