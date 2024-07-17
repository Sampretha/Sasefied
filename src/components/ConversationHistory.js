import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ConversationHistory = () => {
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const fetchHistory = async () => {
            const response = await axios.get('http://127.0.0.1:5000/conversation_history');
            setHistory(response.data);
        };
        fetchHistory();
    }, []);

    return (
        <div>
            <h2>Conversation History</h2>
            <ul>
                {history.map((item) => (
                    <li key={item.id}>
                        <strong>{item.speaker}:</strong> {item.text} <em>({item.timestamp})</em>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ConversationHistory;
