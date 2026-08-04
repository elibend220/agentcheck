import React, { useState, useEffect } from 'react';
import styles from './UserProfile.module.css';

const UserProfile = ({ onLogout }) => {
  const [user, setUser] = useState(null);
  const [showProfile, setShowProfile] = useState(false);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Failed to parse user:', e);
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('sessionId');
    localStorage.removeItem('messages');
    setUser(null);
    if (onLogout) {
      onLogout();
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className={styles.userProfile}>
      <div className={styles.trigger} onClick={() => setShowProfile(!showProfile)}>
        <div className={styles.avatar}>
          {user.username.substring(0, 2).toUpperCase()}
        </div>
        <div className={styles.userInfo}>
          <div className={styles.username}>{user.username}</div>
          <div className={styles.userId}>ID: {user.user_id.substring(0, 8)}</div>
        </div>
      </div>

      {showProfile && (
        <div className={styles.dropdown}>
          <div className={styles.profileHeader}>
            <div className={styles.largeAvatar}>
              {user.username.substring(0, 2).toUpperCase()}
            </div>
            <div>
              <h3>{user.username}</h3>
              <p>{user.email || 'No email'}</p>
            </div>
          </div>

          <div className={styles.divider} />

          <div className={styles.stats}>
            <div className={styles.stat}>
              <span>🔒 Sandbox</span>
              <span className={styles.statValue}>Isolated</span>
            </div>
            <div className={styles.stat}>
              <span>📁 Data</span>
              <span className={styles.statValue}>Encrypted</span>
            </div>
            <div className={styles.stat}>
              <span>⚡ Status</span>
              <span className={styles.statValue}>Active</span>
            </div>
          </div>

          <div className={styles.divider} />

          <div className={styles.actions}>
            <button className={styles.actionBtn}>
              ⚙️ Settings
            </button>
            <button className={styles.actionBtn}>
              🔐 Privacy
            </button>
            <button
              className={`${styles.actionBtn} ${styles.danger}`}
              onClick={handleLogout}
            >
              🚪 Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProfile;
