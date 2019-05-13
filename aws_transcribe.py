import boto3
import requests
import time
import json

transcribe = boto3.client('transcribe')

#def upload_to_s3():

#def create_vocabulary():

def transcribe_audio(job_name, file_uri, file_type, custom_vocab, filename):
    
    if file_type == 'mp3':
        file_uri = "https://s3.us-east-2.amazonaws.com/ap-test-bucket-3/" + str(filename)
    elif file_type == 'mp4':
        file_uri = "https://s3.us-east-2.amazonaws.com/ap-test-bucket-3/" + str(filename)
    elif file_type == 'wav':
        file_uri = "https://s3.us-east-2.amazonaws.com/ap-test-bucket-3/wayne-olson.long.wav"
    
    #print(file_uri)
    
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat=file_type,
        LanguageCode='en-US',
        Settings={
            'VocabularyName': custom_vocab,
            'ShowSpeakerLabels': True,
            'MaxSpeakerLabels': 10
        }
    )

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)
    

    transcriptionURL = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    req = requests.get(transcriptionURL)

    with open('transcription_file.json', 'wb') as transcription_file:
        transcription_file.write(req.content)

    
    with open('transcription_file.json', 'r') as transcription_file:
        transcription_text = json.load(transcription_file)

    num_speaker = 1
    if 'speaker_labels' in transcription_text['results'].keys():
        num_speaker = transcription_text['results']['speaker_labels']['speakers']

    
    return {'transcription': transcription_text['results']['transcripts'][0]['transcript'], 'num_speaker': num_speaker}


def create_custom_vocabulary(vocab_name, vocab):
    phrases = [phrase.strip() for phrase in list(vocab.split(","))]
    print(phrases)
    transcribe.create_vocabulary(
        VocabularyName = vocab_name,
        LanguageCode = 'en-US',
        Phrases = phrases
    )

    while True:
        create_vocab_status = transcribe.get_vocabulary(VocabularyName = vocab_name)
        if create_vocab_status['VocabularyState'] in ['READY', 'FAILED']:
            break
        print("Vocabulary not ready yet...")
        time.sleep(5)
    return create_vocab_status['VocabularyState']
