import React, { useState, useEffect, useRef } from "react";
import "./styles.css";
import CryptoJS from "crypto-js";

interface Message {
  sender: string;
  text: string;
}

const Chat = () => {
  const [prompt, setPrompt] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const clientIdRef = useRef<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const getClientIp = (): Promise<string> => {
    return fetch("https://api.ipify.org?format=json")
      .then((response) => response.json())
      .then((data) => data.ip);
  };

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          sender: "bot",
          text: "Welcome to chat. What can I help you with today?",
        },
      ]);
    }

    getClientIp().then((ip) => {
      const now = Date.now();
      const timestamp = new Date(now).toLocaleTimeString();
      const finalId = `${ip}-${timestamp}`;
      clientIdRef.current = CryptoJS.SHA256(finalId).toString(CryptoJS.enc.Hex);

      const socket = new WebSocket(
        `ws://127.0.0.1:8000/ws/${clientIdRef.current}`
      );

      socket.onopen = () => {};

      socket.onmessage = (message: MessageEvent) => {
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: "bot", text: message.data },
        ]);
        setIsLoading(false);
      };

      socket.onclose = () => {};

      setWs(socket);
    });

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const handlePromptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value);
  };

  const handleSendMessage = () => {
    if (ws && prompt.trim()) {
      if (
        messages.length === 1 &&
        messages[0].sender === "bot" &&
        messages[0].text === "Welcome to chat. What can I help you with today?"
      ) {
        setMessages((prevMessages) => prevMessages.slice(1));
      }

      ws.send(prompt);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "client", text: prompt },
      ]);
      setPrompt("");
      setIsLoading(true);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter") {
      if (event.altKey) {
        setPrompt(prompt + "\n");
      } else {
        handleSendMessage();
      }
    }
  };

  console.log(isLoading);

  return (
    <div>
      <div className="chat-container">
        <div className="chat-list">
          {messages.map((message, index) => (
            <div key={index} className={`chat-item-${message.sender}`}>
              <div className="chat-item__message">{message.text}</div>
            </div>
          ))}
          {isLoading && (
            <div className="loading">
              <div className="span"></div>
              <div className="span"></div>
              <div className="span"></div>
            </div>
          )}
        </div>

        <div className="chat-input">
          <textarea
            value={prompt}
            onChange={handlePromptChange}
            placeholder="How can I help you?"
            onKeyDown={handleKeyDown}
          />
          <button onClick={handleSendMessage} className="chat-input__send">
            Ask
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
