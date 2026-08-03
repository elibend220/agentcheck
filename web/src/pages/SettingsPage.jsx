import React, { useState } from 'react';
import { useJARVIS } from '../context/JARVISContext';
import styles from './SettingsPage.module.css';

const SettingsPage = () => {
  const { apiUrl, updateApiUrl } = useJARVIS();
  const [localApiUrl, setLocalApiUrl] = useState(apiUrl);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  const handleSaveApiUrl = () => {
    if (!localApiUrl.trim()) {
      setError('API URL cannot be empty');
      return;
    }

    try {
      new URL(localApiUrl);
    } catch {
      setError('Invalid URL format');
      return;
    }

    updateApiUrl(localApiUrl);
    setError('');
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleReset = () => {
    if (
      window.confirm(
        'Reset all settings to defaults?'
      )
    ) {
      setLocalApiUrl('http://localhost:8000');
      updateApiUrl('http://localhost:8000');
      setError('');
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>⚙️ Settings</h1>
          <p>Configure JARVIS backend connection</p>
        </div>

        {saved && (
          <div className={styles.successAlert}>
            ✅ Settings saved successfully!
          </div>
        )}

        {error && (
          <div className={styles.errorAlert}>
            ⚠️ {error}
          </div>
        )}

        <div className={styles.settingsGrid}>
          <div className={styles.settingSection}>
            <h2>Backend Configuration</h2>

            <div className={styles.settingItem}>
              <label htmlFor="apiUrl">API URL</label>
              <input
                id="apiUrl"
                type="text"
                value={localApiUrl}
                onChange={(e) => setLocalApiUrl(e.target.value)}
                placeholder="http://localhost:8000"
                className={styles.input}
              />
              <p className={styles.helpText}>
                Where is your JARVIS backend running?
              </p>
            </div>

            <div className={styles.urlPresets}>
              <button
                className={styles.preset}
                onClick={() => setLocalApiUrl('http://localhost:8000')}
              >
                Local
              </button>
              <button
                className={styles.preset}
                onClick={() => setLocalApiUrl('http://10.0.2.2:8000')}
              >
                Android Emulator
              </button>
              <button
                className={styles.preset}
                onClick={() => setLocalApiUrl('http://192.168.1.100:8000')}
              >
                Local Network
              </button>
            </div>

            <div className={styles.urlGuide}>
              <h3>Quick Reference</h3>
              <ul>
                <li>
                  <strong>Local:</strong> http://localhost:8000
                </li>
                <li>
                  <strong>Android Emulator:</strong> http://10.0.2.2:8000
                </li>
                <li>
                  <strong>Physical Device:</strong> http://192.168.x.x:8000
                </li>
                <li>
                  <strong>Cloud:</strong> https://api.example.com
                </li>
              </ul>
            </div>
          </div>

          <div className={styles.settingSection}>
            <h2>About</h2>

            <div className={styles.aboutItem}>
              <span className={styles.aboutLabel}>Application</span>
              <span className={styles.aboutValue}>JARVIS AGI Web</span>
            </div>

            <div className={styles.aboutItem}>
              <span className={styles.aboutLabel}>Version</span>
              <span className={styles.aboutValue}>1.0.0</span>
            </div>

            <div className={styles.aboutItem}>
              <span className={styles.aboutLabel}>Frontend</span>
              <span className={styles.aboutValue}>React 18 + Vite</span>
            </div>

            <div className={styles.aboutItem}>
              <span className={styles.aboutLabel}>Backend</span>
              <span className={styles.aboutValue}>FastAPI 0.104.1</span>
            </div>

            <div className={styles.aboutItem}>
              <span className={styles.aboutLabel}>Features</span>
              <span className={styles.aboutValue}>
                23 Phase Orchestration • Real-time Chat • Session Management •
                Live Metrics
              </span>
            </div>
          </div>

          <div className={styles.settingSection}>
            <h2>Keyboard Shortcuts</h2>

            <div className={styles.shortcutList}>
              <div className={styles.shortcut}>
                <kbd>Enter</kbd>
                <span>Send message</span>
              </div>
              <div className={styles.shortcut}>
                <kbd>Shift + Enter</kbd>
                <span>New line in message</span>
              </div>
              <div className={styles.shortcut}>
                <kbd>Ctrl/Cmd + K</kbd>
                <span>Focus message input</span>
              </div>
            </div>
          </div>
        </div>

        <div className={styles.actions}>
          <button className={styles.saveBtn} onClick={handleSaveApiUrl}>
            💾 Save Settings
          </button>
          <button className={styles.resetBtn} onClick={handleReset}>
            🔄 Reset to Defaults
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
