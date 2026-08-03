import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { JARVISProvider } from './context/JARVISContext';
import Layout from './components/Layout';
import ChatPage from './pages/ChatPage';
import SessionsPage from './pages/SessionsPage';
import SettingsPage from './pages/SettingsPage';
import './styles/global.css';

function App() {
  return (
    <JARVISProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/sessions" element={<SessionsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<ChatPage />} />
          </Routes>
        </Layout>
      </Router>
    </JARVISProvider>
  );
}

export default App;
