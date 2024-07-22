from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import sounddevice as sd
import scipy.io.wavfile as wavfile
import numpy as np
import threading
import asyncio
import google.generativeai as genai
import os
from deepgram import Deepgram
from gtts import gTTS
import time

<<<<<<< HEAD

=======
>>>>>>> 863df5c (Second commit)
DEEPGRAM_API_KEY = '37f44a0681fb3d285f4cd9d5e090e277e86b49ba'
deepgram = Deepgram(DEEPGRAM_API_KEY)

app = Flask(__name__)

SAMPLERATE = 16000
FILENAME = "output.wav"
TTS_FILENAME = "tts_output.mp3"
is_recording = False
stop_event = threading.Event()
silence_threshold = 500
silence_duration = 2 

genai.configure(api_key="AIzaSyBUGkWLAS5ruT9qCwAmbJzLv1CpPdrhM6k")
model = genai.GenerativeModel('gemini-pro')

def record_audio():
    global is_recording
    stop_event.clear()
    recording = []
    def callback(indata, frames, time, status):
        if stop_event.is_set():
            raise sd.CallbackStop()
        recording.append(indata.copy())
        if len(recording) > SAMPLERATE * silence_duration:
            if np.mean(np.abs(np.concatenate(recording[-SAMPLERATE * silence_duration:]))) < silence_threshold:
                stop_event.set()

    with sd.InputStream(samplerate=SAMPLERATE, channels=1, callback=callback):
        while not stop_event.is_set():
            sd.sleep(100)
    recording = np.concatenate(recording, axis=0)
    wavfile.write(FILENAME, SAMPLERATE, recording)

async def recognize_speech():
    with open(FILENAME, 'rb') as audio_file:
        source = {
            'buffer': audio_file,
            'mimetype': 'audio/wav'
        }
        response = await deepgram.transcription.prerecorded(source, {'punctuate': True})
        return response['results']['channels'][0]['alternatives'][0]['transcript']

async def generate_text(prompt):
    print(prompt)
    response = model.generate_content(prompt)
    return response.text

def text_to_speech(text):
    tts = gTTS(text)
    tts.save(TTS_FILENAME)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle_recording', methods=['POST'])
def toggle_recording():
    global is_recording
    global stop_event

    if not is_recording:
        stop_event.clear()
        threading.Thread(target=record_audio).start()
        is_recording = True
        return jsonify({"status": "recording"})
    else:
        start_time = time.time()
        is_recording = False
        stop_event.set()
        recognition_start_time = time.time()
        text = asyncio.run(recognize_speech())
        recognition_time = time.time() - recognition_start_time
        generation_start_time = time.time()
        generated_text = asyncio.run(generate_text(text))
        generation_time = time.time() - generation_start_time
        text_to_speech(generated_text)
        end_time = time.time()
        response_time = end_time - start_time
        return jsonify({"status": "stopped", "text": text, "generated_text": generated_text, 
                        "recognition_time": recognition_time, "generation_time": generation_time, 
                        "response_time": response_time})

@app.route('/download_tts')
def download_tts():
    return send_file(TTS_FILENAME, as_attachment=True)

@app.route('/play_tts')
def play_tts():
    return send_from_directory('.', TTS_FILENAME)

<<<<<<< HEAD
if __name__ == '_main_':
=======
if __name__ == '__main__':
>>>>>>> 863df5c (Second commit)
    app.run(debug=True)