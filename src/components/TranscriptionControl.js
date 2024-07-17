import React, { useState } from 'react';
import axios from 'axios';

const TranscriptionControl = () => {
    const [isTranscribing, setIsTranscribing] = useState(false);

    const toggleTranscription = async () => {
        const response = await axios.post('http://127.0.0.1:5000/start_transcription');
        console.log(response.data.message);
        setIsTranscribing(!isTranscribing);
    };

    return (
        <div>
            <button onClick={toggleTranscription}>
                {isTranscribing ? 'Stop Transcribing' : 'Start Transcribing'}
            </button>
        </div>
    );
};

export default TranscriptionControl;
