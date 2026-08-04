import React, { createContext, useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

const JARVISContext = createContext();

export const JARVISProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiUrl, setApiUrlState] = useState(
    localStorage.getItem('apiUrl') || 'http://localhost:8000'
  );
  const [sessions, setSessions] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);

  // Initialize session
  const initializeSession = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`${apiUrl}/session/create`);
      const newSessionId = response.data.session_id;
      setSessionId(newSessionId);
      setMessages([]);

      // Save to localStorage
      const existingSessions = JSON.parse(
        localStorage.getItem('sessions') || '[]'
      );
      const newSession = {
        id: newSessionId,
        created_at: new Date().toISOString(),
        message_count: 0,
      };
      existingSessions.push(newSession);
      localStorage.setItem('sessions', JSON.stringify(existingSessions));

      return newSessionId;
    } catch (err) {
      const errorMsg = `Failed to initialize session: ${err.message}`;
      setError(errorMsg);
      console.error(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  // Send message
  const sendMessage = useCallback(
    async (userMessage) => {
      if (!userMessage.trim()) return;

      try {
        setLoading(true);
        setError(null);
        const currentSessionId =
          sessionId || (await initializeSession());

        // Add user message to UI immediately
        const userMsg = {
          id: uuidv4(),
          text: userMessage,
          role: 'user',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMsg]);

        // Send to backend
        const response = await axios.post(`${apiUrl}/chat`, {
          session_id: currentSessionId,
          message: userMessage,
        });

        const data = response.data;

        // Add AI response
        const aiMsg = {
          id: uuidv4(),
          text: data.response,
          role: 'assistant',
          timestamp: new Date(data.timestamp),
        };
        setMessages((prev) => [...prev, aiMsg]);

        // Store metrics
        setMetrics({
          consciousness: data.consciousness_level,
          emergence: data.emergence_level,
          confidence: data.confidence_score,
          time: data.execution_time_ms,
          phases: data.phases_executed.length,
        });

        // Update session message count
        const existingSessions = JSON.parse(
          localStorage.getItem('sessions') || '[]'
        );
        const updatedSessions = existingSessions.map((s) =>
          s.id === currentSessionId
            ? { ...s, message_count: s.message_count + 2 }
            : s
        );
        localStorage.setItem('sessions', JSON.stringify(updatedSessions));

        return data;
      } catch (err) {
        const errorMsg = `Error sending message: ${err.message}`;
        setError(errorMsg);
        console.error(errorMsg);

        // Add error message to chat
        const errorMessageObj = {
          id: uuidv4(),
          text: '❌ Failed to get response. Please check your connection.',
          role: 'system',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessageObj]);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [sessionId, apiUrl, initializeSession]
  );

  // Load sessions from localStorage
  const loadSessions = useCallback(async () => {
    try {
      const storedSessions = localStorage.getItem('sessions');
      if (storedSessions) {
        setSessions(JSON.parse(storedSessions));
      }
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  }, []);

  // Load session history
  const loadSessionHistory = useCallback(
    async (id) => {
      try {
        setLoading(true);
        setError(null);
        const response = await axios.get(`${apiUrl}/session/${id}/history`);
        const data = response.data;

        // Convert to message format
        const chatMessages = data.messages.map((msg) => ({
          id: uuidv4(),
          text: msg.content,
          role: msg.role,
          timestamp: new Date(msg.timestamp),
        }));

        setSessionId(id);
        setMessages(chatMessages);
        return chatMessages;
      } catch (err) {
        const errorMsg = `Failed to load session history: ${err.message}`;
        setError(errorMsg);
        console.error(errorMsg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiUrl]
  );

  // Delete session
  const deleteSession = useCallback(async (id) => {
    try {
      const existingSessions = JSON.parse(
        localStorage.getItem('sessions') || '[]'
      );
      const updatedSessions = existingSessions.filter((s) => s.id !== id);
      localStorage.setItem('sessions', JSON.stringify(updatedSessions));
      setSessions(updatedSessions);
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  }, []);

  // Update API URL
  const updateApiUrl = useCallback((url) => {
    setApiUrlState(url);
    localStorage.setItem('apiUrl', url);
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value = {
    sessionId,
    messages,
    loading,
    apiUrl,
    sessions,
    metrics,
    error,
    initializeSession,
    sendMessage,
    loadSessions,
    loadSessionHistory,
    deleteSession,
    updateApiUrl,
    clearError,
    setMessages,
  };

  return (
    <JARVISContext.Provider value={value}>
      {children}
    </JARVISContext.Provider>
  );
};

export const useJARVIS = () => {
  const context = React.useContext(JARVISContext);
  if (!context) {
    throw new Error('useJARVIS must be used within JARVISProvider');
  }
  return context;
};
