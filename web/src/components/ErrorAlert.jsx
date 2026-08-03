import React, { useEffect } from 'react';
import styles from './ErrorAlert.module.css';

const ErrorAlert = ({ message, onClose, duration = 5000 }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div className={styles.alert}>
      <span className={styles.icon}>⚠️</span>
      <span className={styles.message}>{message}</span>
      <button className={styles.closeButton} onClick={onClose}>
        ✕
      </button>
    </div>
  );
};

export default ErrorAlert;
