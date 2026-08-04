import React from 'react';
import styles from './MessageList.module.css';

const MessageList = ({ messages, loading }) => {
  if (messages.length === 0) {
    return (
      <div className={styles.emptyState}>
        <div className={styles.emptyIcon}>🤖</div>
        <h2>Start Chatting with JARVIS</h2>
        <p>Ask any question and JARVIS will respond with 23 phases of analysis</p>
      </div>
    );
  }

  return (
    <div className={styles.messageList}>
      {messages.map((message) => (
        <div
          key={message.id}
          className={`${styles.message} ${styles[message.role]}`}
        >
          <div className={styles.messageContent}>
            <div className={styles.messageBubble}>
              {message.text}
            </div>
            <span className={styles.timestamp}>
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          </div>
        </div>
      ))}
      {loading && (
        <div className={`${styles.message} ${styles.system}`}>
          <div className={styles.messageContent}>
            <div className={styles.messageBubble}>
              <div className={styles.loadingDots}>
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageList;
