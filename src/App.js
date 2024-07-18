import React, { useState, useEffect } from 'react';
import './App.css';
import io from 'socket.io-client';

const socket = io('http://127.0.0.1:5000');

function App() {
  const [transcription, setTranscription] = useState('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    socket.on('transcription', (data) => {
      setTranscription((prev) => prev + ' ' + data.transcription);
    });

    clearHistory(); // Clear history when the app loads
    fetchHistory();
  }, []);

  const clearHistory = async () => {
    await fetch('http://127.0.0.1:5000/clear_history', {
      method: 'POST',
    });
    setHistory([]);
  };

  const fetchHistory = async () => {
    const response = await fetch('http://127.0.0.1:5000/conversation_history');
    const data = await response.json();
    setHistory(data);
  };

  const toggleTranscription = async () => {
    const response = await fetch('http://127.0.0.1:5000/start_transcription', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const result = await response.json();
    if (result.message === 'Transcription started') {
      setIsTranscribing(true);
    } else {
      setIsTranscribing(false);
      setTranscription('');
      fetchHistory(); // Refresh history after stopping transcription
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Real-time Transcription</h1>
        <button onClick={toggleTranscription}>
          {isTranscribing ? 'Stop Transcribing' : 'Start Transcribing'}
        </button>
        <div className="transcription">
          <h2>Current Transcription:</h2>
          <p>{transcription}</p>
        </div>
        <div className="history">
          <h2>Conversation History:</h2>
          {history.map((item) => (
            <div key={item.id}>
              <strong>{item.speaker}:</strong> {item.text} <em>({new Date(item.timestamp).toLocaleString()})</em>
            </div>
          ))}
        </div>
      </header>
    </div>
  );
}

export default App;
