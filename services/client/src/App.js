import React, { useState, useEffect, useRef } from 'react';
import './styles.css';
import CryptoJS from 'crypto-js';
function App() {
  return (
      <Chat />
  );
}

export default App;

const Chat = () => {
  const [clientIp, setClientIp] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState([
    { from: 'bot', text: 'Hello' },
    { from: 'bot', text: 'How can I help you?' }
  ]);
  
  const [ws, setWs] = useState(null);
  const clientIdRef = useRef(null);

  const getClientIp = () => {
    return fetch('https://api.ipify.org?format=json')
      .then((response) => response.json())
      .then((data) => data.ip);
  };

  useEffect(() => {
    getClientIp().then((ip) => {
      setClientIp(ip);
      const now = Date.now();
      const timestamp = new Date(now).toLocaleTimeString();
      const finalId = `${ip}-${timestamp}`;
      clientIdRef.current = CryptoJS.SHA256(finalId).toString(CryptoJS.enc.Hex);

      const socket = new WebSocket(`ws://127.0.0.1:8000/ws/${clientIdRef.current}`);

      socket.onopen = () => {
        console.log('Connected to the server');
      };

      socket.onmessage = (message) => {
        console.log('Received from server:', message.data);
        setMessages(prevMessages => [
          ...prevMessages,
          { from: 'server', text: message.data }
        ]);
      };

      socket.onclose = () => {
        console.log('Disconnected from the server');
      };

      setWs(socket);
    });

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  // Handle prompt input change
  const handlePromptChange = (e) => {
    setPrompt(e.target.value);
  };

  // Handle sending message to WebSocket
  const handleSendMessage = () => {
    if (ws && prompt.trim()) {
      ws.send(prompt); // Send prompt to the server
      setMessages(prevMessages => [
        ...prevMessages,
        { from: 'client', text: prompt }
      ]);
      setPrompt(''); // Clear input field
    }
  };

  return (
    <div>
      <div className="chat-container">
        <div className="chat-list">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`chat-item-${message.from}`}
            >
              <div className="chat-item__message">{message.text}</div>
            </div>
          ))}
        </div>

        <div className="chat-input">
          <input
            value={prompt}
            onChange={handlePromptChange}
            type="text"
            className="chat-input__field"
            placeholder="How can I help you?"
          />
          <button onClick={handleSendMessage} className="chat-input__send">
            Ask
          </button>
        </div>
      </div>
    </div>
  );
};

