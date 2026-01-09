import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { API_URL } from './config';
import './App.css';

function App() {
    const [file, setFile] = useState(null);
    const [messages, setMessages] = useState([
        { sender: 'bot', text: 'Hello! Upload a PDF to start chatting about it.' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);

    // Handle File Selection
    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    // Handle File Upload to Backend
    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(`${API_URL}/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 60000 // 60 second timeout for large files
            });
            setMessages(prev => [...prev, { 
                sender: 'bot', 
                text: response.data.message || 'Document loaded. Ask me anything!' 
            }]);
        } catch (error) {
            console.error('Error uploading file:', error);
            const errorMessage = error.response?.data?.detail || 
                                error.message || 
                                'Failed to upload file. Please try again.';
            setMessages(prev => [...prev, { 
                sender: 'bot', 
                text: `Error: ${errorMessage}` 
            }]);
        } finally {
            setUploading(false);
            setFile(null);
        }
    };

    // Handle Sending Chat Message
    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = { sender: 'user', text: input };
        setMessages(prev => [...prev, userMessage]);
        const queryText = input;
        setInput('');
        setLoading(true);

        try {
            const response = await axios.post(`${API_URL}/chat`, {
                query: queryText
            }, {
                timeout: 30000 // 30 second timeout
            });

            const botMessage = { sender: 'bot', text: response.data.response };
            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error('Error querying chatbot:', error);
            const errorMessage = error.response?.data?.detail || 
                                error.message || 
                                'Error getting response. Please try again.';
            setMessages(prev => [...prev, { 
                sender: 'bot', 
                text: `Error: ${errorMessage}` 
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <h1>A very good RAG Chatbot</h1>

            {/* Upload Section */}
            <div className="upload-section">
                <input type="file" accept=".pdf" onChange={handleFileChange} />
                <button onClick={handleUpload} disabled={!file || uploading}>
                    {uploading ? 'Processing...' : 'Upload PDF'}
                </button>
            </div>

            {/* Chat Window */}
            <div className="chat-window">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender}`}>
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                    </div>
                ))}
                {loading && <div className="message bot">Thinking...</div>}
            </div>

            {/* Input Area */}
            <div className="input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask a question about your document..."
                    disabled={loading}
                />
                <button onClick={handleSend} disabled={loading}>Send</button>
            </div>
        </div>
    );
}

export default App;
