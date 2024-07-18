from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import speech_recognition as sr
import pyaudio
import threading
from datetime import datetime
import logging

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

# Function to capture and transcribe audio
def capture_audio():
    global is_transcribing, current_transcription
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    logging.debug("Audio stream opened for capturing.")
    while is_transcribing:
        try:
            frames = []
            for _ in range(0, int(44100 / 1024 * 5)):  # Capture 5 seconds of audio
                data = stream.read(1024)
                frames.append(data)
            logging.debug("Captured audio frames for transcription.")
            audio_data = sr.AudioData(b''.join(frames), 44100, 2)
            transcribed_text = transcribe_audio(audio_data)
            current_transcription += transcribed_text + " "
            logging.debug(f"Transcription result: {transcribed_text}")
            socketio.emit('transcription', {'transcription': transcribed_text})
        except Exception as e:
            logging.error(f"Error capturing audio: {e}")
    stream.stop_stream()
    stream.close()
    logging.debug("Audio stream closed after capturing.")

# Function to transcribe audio
def transcribe_audio(audio_data):
    try:
        logging.debug("Starting audio transcription.")
        text = recognizer.recognize_google(audio_data)
        logging.debug(f"Transcription successful: {text}")
        return text
    except sr.UnknownValueError:
        logging.warning("Could not understand audio.")
        return "Could not understand audio"
    except sr.RequestError as e:
        logging.error(f"Speech recognition request error: {e}")
        return f"Error: {e}"

# Endpoint to start/stop transcription
@app.route('/start_transcription', methods=['POST'])
def start_transcription():
    global is_transcribing, current_transcription
    if is_transcribing:
        is_transcribing = False
        save_conversation("User", current_transcription.strip())
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

# Endpoint to clear conversation history
@app.route('/clear_history', methods=['POST'])
def clear_history():
    db.session.query(Conversation).delete()
    db.session.commit()
    return jsonify({"message": "Conversation history cleared"})

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
