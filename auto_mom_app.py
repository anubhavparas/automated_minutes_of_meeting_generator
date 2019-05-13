import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

from aws_transcribe import transcribe_audio, create_custom_vocabulary
from text_summarizer import summarize_text

from gensim.summarization.textcleaner import get_sentences

import datetime

import sys

UPLOAD_FOLDER = './uploads'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/preview/<filename>', methods=['GET'])
def preview(filename):
    if filename == None or filename == '':
        return 'No preview available.'
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

app_data = {
    'file_address': '',
    'file_type' : 'mp3',
    'vocab': '',
    'vocab_status': '',
    'summary': '',
    'num_speaker': '',
    'ratio' : 50,
    'error' : False,
    'error_msg' : '',
    'preview' : preview,
    'loading' : True
}
transcription = ''

@app.route('/', methods=['GET'])
def launch_app():
    global app_data
    return render_template('app_index1.html', app_data=app_data)
    #return 'This is the homepage!'


@app.route('/submit', methods=['GET', 'POST'])
def send_for_transcription():
    global transcription
    global app_data
    if request.method == 'POST':
        if request.form['process_btn'] == "Start":
            print(request.form['file_type'])
            print(app_data['file_type'])
            app_data['loading'] = False

            app_data['file_type'] = request.form['file_type']
            

            if 'file_address' not in request.files:
                print('No files found.')
                return 'No files'
            file = request.files['file_address']
            app_data['file_address'] = file
            #print(file)
            #print(file.filename)

            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


            # upload the file to s3 bucket - to be done

            # create vocab if any
            custom_vocab_name = 'default_custom_vocab'
            app_data['vocab'] = str(request.form['vocab']).strip()
            print(app_data['vocab'])
            if app_data['vocab']:
                custom_vocab_name = str("custom_vocab_" + str(datetime.datetime.now().strftime("%y-%m-%d-%H.%M.%S")) )
                custom_vocab_status = create_custom_vocabulary(custom_vocab_name, app_data['vocab'])
                if custom_vocab_status == 'READY':
                    app_data['vocab_status'] = 'Custom Vocabulary Ready'
                else :
                    app_data['vocab_status'] = 'Custom Vocabulary Creation Failed'


            
            



            # get transcription
            
            transciption_job_name = str("transcribe-job-" + str(datetime.datetime.now().strftime("%y-%m-%d-%H.%M.%S")) )

            #print(transciption_job_name)
            #print(app_data['file_type'])

            if app_data['file_type'] == None or app_data['file_type'] == '':
                print('no file type')
            else:
                transcription_result = transcribe_audio(transciption_job_name, '', app_data['file_type'], custom_vocab_name, file.filename)
                transcription = transcription_result['transcription']
                

                transcription_sent_count = len(list(get_sentences(transcription)))
                threshold_sent_count = min(10, transcription_sent_count)
                ratio = threshold_sent_count / transcription_sent_count
                app_data['ratio'] = int(round(((1 - ratio) * 100)))

                text_summary = summarize_text(transcription, ratio)

                app_data['summary'] = text_summary
                app_data['num_speaker'] = transcription_result['num_speaker']

        if request.form['process_btn'] == "Go":
             app_data['ratio'] = request.form['ratio']
             summ_ratio = (100 - float(request.form['ratio']))/100
             if summ_ratio < 0.05:
                summ_ratio = 0.1

             app_data['summary'] = summarize_text(transcription, summ_ratio)


        print(app_data['vocab'])
        return redirect(url_for('launch_app'))
         #return render_template('app_index.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/summary', methods=['GET', 'POST'])
def summarize_with_ratio():
    if request.method == 'POST':
        app_data['ratio'] = request.form['ratio']
        summ_ratio = (100 - float(request.form['ratio']))/100
        if summ_ratio < 0.05:
            summ_ratio = 0.1

        app_data['summary'] = summarize_text(transcription, summ_ratio)
        return render_template('app_index.html', app_data=app_data)

 


if __name__ == "__main__":
    args = sys.argv
    port = 5000
    if len(args) > 1:
        port = int(args[1])
    app.run(debug=True, port=port)