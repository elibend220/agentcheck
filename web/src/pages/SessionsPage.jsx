import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useJARVIS } from '../context/JARVISContext';
import ErrorAlert from '../components/ErrorAlert';
import styles from './SessionsPage.module.css';

const SessionsPage = () => {
  const {
    sessions,
    loadSessions,
    loadSessionHistory,
    deleteSession,
    error,
    clearError,
  } = useJARVIS();

  const navigate = useNavigate();

  useEffect(() => {
    loadSessions();
  }, []);

  const handleSelectSession = async (sessionId) => {
    try {
      await loadSessionHistory(sessionId);
      navigate('/chat');
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  };

  const handleDeleteSession = (sessionId, e) => {
    e.stopPropagation();
    if (
      window.confirm('Are you sure you want to delete this session?')
    ) {
      deleteSession(sessionId);
    }
  };

  return (
    <div className={styles.page}>
      {error && <ErrorAlert message={error} onClose={clearError} />}

      <div className={styles.container}>
        <div className={styles.header}>
          <div>
            <h1>📋 Session History</h1>
            <p>Manage your JARVIS conversations</p>
          </div>
          <div className={styles.sessionCount}>
            {sessions.length} session{sessions.length !== 1 ? 's' : ''}
          </div>
        </div>

        {sessions.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>📭</div>
            <h2>No Sessions Yet</h2>
            <p>Start a new chat to create your first session</p>
            <button
              className={styles.newSessionBtn}
              onClick={() => navigate('/chat')}
            >
              Start New Chat
            </button>
          </div>
        ) : (
          <div className={styles.sessionsList}>
            {sessions.map((session) => {
              const createdDate = new Date(session.created_at);
              const formattedDate = createdDate.toLocaleDateString();
              const formattedTime = createdDate.toLocaleTimeString();

              return (
                <div
                  key={session.id}
                  className={styles.sessionCard}
                  onClick={() => handleSelectSession(session.id)}
                >
                  <div className={styles.sessionInfo}>
                    <div className={styles.sessionId}>
                      <code>
                        {session.id.substring(0, 8)}...
                        {session.id.substring(session.id.length - 4)}
                      </code>
                    </div>
                    <div className={styles.sessionMeta}>
                      📅 {formattedDate} • 🕐 {formattedTime}
                    </div>
                    <div className={styles.sessionMessages}>
                      💬 {session.message_count} messages
                    </div>
                  </div>
                  <button
                    className={styles.deleteBtn}
                    onClick={(e) => handleDeleteSession(session.id, e)}
                    title="Delete session"
                  >
                    🗑️
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default SessionsPage;
