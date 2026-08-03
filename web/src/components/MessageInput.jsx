import React from 'react';
import styles from './MessageInput.module.css';

const MessageInput = ({
  value,
  onChange,
  onSubmit,
  onKeyPress,
  disabled,
  placeholder,
}) => {
  return (
    <div className={styles.inputContainer}>
      <div className={styles.inputArea}>
        <textarea
          value={value}
          onChange={onChange}
          onKeyPress={onKeyPress}
          disabled={disabled}
          placeholder={placeholder}
          className={styles.input}
          rows="2"
        />
        <button
          onClick={onSubmit}
          disabled={disabled || !value.trim()}
          className={styles.sendButton}
          title="Send message (Shift+Enter for new line)"
        >
          <span className={styles.sendIcon}>
            {disabled ? '⏳' : '📤'}
          </span>
        </button>
      </div>
      <p className={styles.hint}>
        Press Enter to send • Shift+Enter for new line
      </p>
    </div>
  );
};

export default MessageInput;
