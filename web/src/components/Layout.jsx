import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styles from './Layout.module.css';

const Layout = ({ children }) => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path || location.pathname === path.replace(/\/$/, '');

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.navbar}>
          <Link to="/" className={styles.logo}>
            <span className={styles.logoIcon}>🤖</span>
            <span className={styles.logoText}>JARVIS AGI</span>
          </Link>

          <nav className={styles.nav}>
            <Link
              to="/chat"
              className={`${styles.navLink} ${isActive('/chat') || isActive('/') ? styles.active : ''}`}
            >
              💬 Chat
            </Link>
            <Link
              to="/sessions"
              className={`${styles.navLink} ${isActive('/sessions') ? styles.active : ''}`}
            >
              📋 Sessions
            </Link>
            <Link
              to="/settings"
              className={`${styles.navLink} ${isActive('/settings') ? styles.active : ''}`}
            >
              ⚙️ Settings
            </Link>
          </nav>

          <div className={styles.headerInfo}>
            <span className={styles.status}>● Online</span>
          </div>
        </div>
      </header>

      <main className={styles.main}>
        {children}
      </main>

      <footer className={styles.footer}>
        <p>JARVIS AGI v1.0.0 • Powered by FastAPI & React</p>
      </footer>
    </div>
  );
};

export default Layout;
