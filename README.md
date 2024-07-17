# Sasefied- Real-Time Transcription System with Speaker Diarization

This project implements a real-time transcription system using Flask for the backend and React for the frontend. It includes speaker diarization to distinguish between user and AI speech, saving conversations to a database, and providing real-time updates to the frontend.

# Setup Instructions

# Backend (Flask)

1)Clone the repository:

Copy code
git clone <repository_url>
cd <repository_name>

2)Create and activate a virtual environment:

python -m venv sas
source sas/Scripts/activate  # On Windows
source sas/bin/activate      # On Linux/Mac

3)Install dependencies:

pip install Flask Flask-SQLAlchemy Flask-CORS Flask-SocketIO SpeechRecognition pyaudio pyAudioAnalysis scikit-learn hmmlearn

4)Run the Flask application:

python app.py
The backend server will run on http://localhost:5000.

# Frontend (React)

1)Navigate to the frontend directory:

cd frontend

2)Install dependencies:

npm install  # Or yarn install

3)Start the development server:

npm start  # Or yarn start
The frontend development server will run on http://localhost:3000.

# List of Dependencies

# Backend (Python)
Flask

Flask-SQLAlchemy

Flask-CORS

Flask-SocketIO

SpeechRecognition

pyaudio

pyAudioAnalysis

scikit-learn

hmmlearn

# Frontend (React)
react

react-dom

socket.io-client

# Approach

Real-time Processing:

Audio Capture: Uses pyaudio to capture audio input in real-time.
Speech Recognition: Utilizes SpeechRecognition library to transcribe speech to text.
WebSocket: Implements Flask-SocketIO for real-time communication with the frontend.

Speaker Diarization:

Feature Extraction: Extracts audio features using pyAudioAnalysis.
Segmentation: Applies Hidden Markov Models (HMM) from hmmlearn for speaker segmentation.
Transcription and Storage: Saves segmented transcriptions with speaker identification to a SQLite database.

Assumptions and Limitations:

Assumes a controlled environment for accurate speaker diarization.
Limited to two speakers (user and AI) for simplicity.
Error handling is minimal for demonstration purposes and should be enhanced for production use.
