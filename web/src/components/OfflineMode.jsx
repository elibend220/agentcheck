import React, { useEffect, useState } from 'react';
import styles from './OfflineMode.module.css';

const OfflineMode = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [offlineSynced, setOfflineSynced] = useState(
    localStorage.getItem('offlineSynced') === 'true'
  );

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Trigger sync when coming back online
      syncOfflineData();
    };

    const handleOffline = () => {
      setIsOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const syncOfflineData = async () => {
    try {
      const pendingSyncs = JSON.parse(
        localStorage.getItem('pendingSyncs') || '[]'
      );

      if (pendingSyncs.length === 0) {
        setOfflineSynced(true);
        return;
      }

      // Sync each pending action
      for (const sync of pendingSyncs) {
        // Send to backend
        const apiUrl = localStorage.getItem('apiUrl') || 'http://localhost:8000';
        await fetch(`${apiUrl}/sync`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(sync),
        });
      }

      // Clear pending syncs on success
      localStorage.removeItem('pendingSyncs');
      setOfflineSynced(true);
    } catch (error) {
      console.error('Sync failed:', error);
      setOfflineSynced(false);
    }
  };

  if (isOnline) {
    return null;
  }

  return (
    <div className={styles.offlineBanner}>
      <div className={styles.content}>
        <span className={styles.icon}>📡</span>
        <span className={styles.text}>
          Offline Mode • Using cached data
        </span>
        {!offlineSynced && (
          <span className={styles.syncStatus}>
            • Pending syncs: {JSON.parse(
              localStorage.getItem('pendingSyncs') || '[]'
            ).length}
          </span>
        )}
      </div>
    </div>
  );
};

export default OfflineMode;
