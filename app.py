from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import speech_recognition as sr
import pyaudio
import threading
from datetime import datetime
import logging
from pyAudioAnalysis import audioSegmentation as aS
import wave
import numpy as np
import os

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversation.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# SQLAlchemy models
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    speaker = db.Column(db.String(50))
    text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)

# Initialize recognizer and PyAudio
recognizer = sr.Recognizer()
audio = pyaudio.PyAudio()
is_transcribing = False  # Global variable to control transcription
current_transcription = ""  # Store the current transcription
current_speaker = "User"  # Initial speaker

# Function to capture and transcribe audio
def capture_audio():
    global is_transcribing, current_transcription
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    frames = []
    logging.debug("Audio stream opened for capturing.")
    while is_transcribing:
        try:
            data = stream.read(1024)
            frames.append(data)
            if len(frames) >= int(44100 / 1024 * 5):  # Process every 5 seconds
                transcribed_text = transcribe_audio(frames)
                if transcribed_text:
                    current_transcription += transcribed_text + " "
                    logging.debug(f"Transcription result: {transcribed_text}")
                    socketio.emit('transcription', {'transcription': transcribed_text, 'speaker': current_speaker})
                frames = []
        except Exception as e:
            logging.error(f"Error capturing audio: {e}")
    stream.stop_stream()
    stream.close()
    logging.debug("Audio stream closed after capturing.")

# Function to transcribe audio
def transcribe_audio(frames):
    global current_speaker
    try:
        logging.debug("Starting audio transcription.")
        # Save audio frames to temporary WAV file
        wf = wave.open("temp.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Perform speaker diarization
        [flagsInd, classesAll, _, _] = aS.mtFileClassification("temp.wav", "pyAudioAnalysis/data/svmSM", "svm", True, "pyAudioAnalysis/data/svmSM")
        speaker = "User" if np.argmax(classesAll) == 0 else "AI"

        # Load audio data and transcribe
        audio_data = sr.AudioFile("temp.wav")
        with audio_data as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)

        os.remove("temp.wav")  # Clean up temporary file

        current_speaker = speaker
        save_conversation(speaker, text)  # Save transcription with speaker
        logging.debug(f"Transcription successful: {text}")
        return text
    except sr.UnknownValueError:
        logging.warning("Could not understand audio.")
        return "Could not understand audio"
    except sr.RequestError as e:
        logging.error(f"Speech recognition request error: {e}")
        return f"Error: {e}"
    except Exception as e:
        logging.error(f"Error during transcription or diarization: {e}")
        return None

# Endpoint to start/stop transcription
@app.route('/start_transcription', methods=['POST'])
def start_transcription():
    global is_transcribing, current_transcription
    if is_transcribing:
        is_transcribing = False
        current_transcription = ""
        return jsonify({"message": "Transcription stopped"})
    else:
        is_transcribing = True
        threading.Thread(target=capture_audio).start()
        return jsonify({"message": "Transcription started"})

# Function to save conversation to the database
def save_conversation(speaker, text):
    conversation = Conversation(speaker=speaker, text=text)
    db.session.add(conversation)
    db.session.commit()

# Endpoint to save conversation (manually)
@app.route('/save_conversation', methods=['POST'])
def manual_save_conversation():
    data = request.get_json()
    speaker = data.get('speaker')
    text = data.get('text')
    save_conversation(speaker, text)
    return jsonify({"message": "Conversation saved successfully"})

# Endpoint to retrieve conversation history
@app.route('/conversation_history', methods=['GET'])
def get_conversation_history():
    conversations = Conversation.query.all()
    history = [{'id': conv.id, 'speaker': conv.speaker, 'text': conv.text, 'timestamp': conv.timestamp} for conv in conversations]
    return jsonify(history)

# WebSocket route
@socketio.on('connect')
def handle_connect():
    logging.debug('Client connected')
    emit('message', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    logging.debug('Client disconnected')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
