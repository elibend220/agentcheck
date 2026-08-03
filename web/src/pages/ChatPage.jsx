import React, { useState, useEffect, useRef } from 'react';
import { useJARVIS } from '../context/JARVISContext';
import MetricsDisplay from '../components/MetricsDisplay';
import MessageList from '../components/MessageList';
import MessageInput from '../components/MessageInput';
import ErrorAlert from '../components/ErrorAlert';
import styles from './ChatPage.module.css';

const ChatPage = () => {
  const {
    messages,
    loading,
    sessionId,
    sendMessage,
    initializeSession,
    error,
    clearError,
  } = useJARVIS();

  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef(null);

  // Initialize session on mount
  useEffect(() => {
    if (!sessionId) {
      initializeSession();
    }
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (message) => {
    if (!message.trim() || isSending) return;

    setInputValue('');
    setIsSending(true);
    try {
      await sendMessage(message);
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputValue);
    }
  };

  return (
    <div className={styles.page}>
      {error && <ErrorAlert message={error} onClose={clearError} />}

      <div className={styles.container}>
        <div className={styles.header}>
          <div className={styles.headerContent}>
            <h1>💬 Chat with JARVIS</h1>
            <p>Advanced AI Communication Platform</p>
          </div>
          {sessionId && (
            <div className={styles.sessionBadge}>
              Session: <code>{sessionId.substring(0, 8)}</code>
            </div>
          )}
        </div>

        <MetricsDisplay />

        <div className={styles.chatArea}>
          <MessageList messages={messages} loading={loading} />
          <div ref={messagesEndRef} />
        </div>

        <MessageInput
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onSubmit={() => handleSendMessage(inputValue)}
          onKeyPress={handleKeyPress}
          disabled={isSending || loading}
          placeholder="Ask JARVIS anything..."
        />
      </div>
    </div>
  );
};

export default ChatPage;
