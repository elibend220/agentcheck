import React, { createContext, useState, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

const JARVISContext = createContext();

export const JARVISProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiUrl, setApiUrl] = useState('http://10.0.2.2:8000');
  const [sessions, setSessions] = useState([]);
  const [metrics, setMetrics] = useState(null);

  // Initialize session
  const initializeSession = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${apiUrl}/session/create`);
      const newSessionId = response.data.session_id;
      setSessionId(newSessionId);
      setMessages([]);

      // Save to AsyncStorage
      const existingSessions = JSON.parse(await AsyncStorage.getItem('sessions') || '[]');
      const newSession = {
        id: newSessionId,
        created_at: new Date().toISOString(),
        message_count: 0,
      };
      existingSessions.push(newSession);
      await AsyncStorage.setItem('sessions', JSON.stringify(existingSessions));

      return newSessionId;
    } catch (error) {
      console.error('Failed to initialize session:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  // Send message
  const sendMessage = useCallback(async (userMessage) => {
    if (!userMessage.trim()) return;

    try {
      setLoading(true);
      const currentSessionId = sessionId || (await initializeSession());

      // Add user message to UI immediately
      const userMsg = {
        _id: uuidv4(),
        text: userMessage,
        createdAt: new Date(),
        user: {
          _id: 1,
          name: 'You',
        },
      };
      setMessages(previousMessages => [userMsg, ...previousMessages]);

      // Send to backend
      const response = await axios.post(`${apiUrl}/chat`, {
        session_id: currentSessionId,
        message: userMessage,
      });

      const data = response.data;

      // Add AI response
      const aiMsg = {
        _id: uuidv4(),
        text: data.response,
        createdAt: new Date(),
        user: {
          _id: 2,
          name: 'JARVIS',
          avatar: 'https://via.placeholder.com/50?text=JARVIS',
        },
      };
      setMessages(previousMessages => [aiMsg, ...previousMessages]);

      // Store metrics
      setMetrics({
        consciousness: data.consciousness_level,
        emergence: data.emergence_level,
        confidence: data.confidence_score,
        time: data.execution_time_ms,
        phases: data.phases_executed.length,
      });

      // Update session message count
      const existingSessions = JSON.parse(await AsyncStorage.getItem('sessions') || '[]');
      const updatedSessions = existingSessions.map(s =>
        s.id === currentSessionId
          ? { ...s, message_count: s.message_count + 2 }
          : s
      );
      await AsyncStorage.setItem('sessions', JSON.stringify(updatedSessions));

      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMsg = {
        _id: uuidv4(),
        text: '❌ Failed to get response from JARVIS. Check your connection and try again.',
        createdAt: new Date(),
        user: {
          _id: 2,
          name: 'System',
        },
      };
      setMessages(previousMessages => [errorMsg, ...previousMessages]);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [sessionId, apiUrl]);

  // Load sessions from AsyncStorage
  const loadSessions = useCallback(async () => {
    try {
      const storedSessions = await AsyncStorage.getItem('sessions');
      if (storedSessions) {
        setSessions(JSON.parse(storedSessions));
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  }, []);

  // Load session history
  const loadSessionHistory = useCallback(async (id) => {
    try {
      setLoading(true);
      const response = await axios.get(`${apiUrl}/session/${id}/history`);
      const data = response.data;

      // Convert to GiftedChat format
      const chatMessages = data.messages.map((msg, index) => ({
        _id: index,
        text: msg.content,
        createdAt: new Date(msg.timestamp),
        user: {
          _id: msg.role === 'user' ? 1 : 2,
          name: msg.role === 'user' ? 'You' : 'JARVIS',
        },
      }));

      setSessionId(id);
      setMessages(chatMessages.reverse());
      return chatMessages;
    } catch (error) {
      console.error('Failed to load session history:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  // Delete session
  const deleteSession = useCallback(async (id) => {
    try {
      const existingSessions = JSON.parse(await AsyncStorage.getItem('sessions') || '[]');
      const updatedSessions = existingSessions.filter(s => s.id !== id);
      await AsyncStorage.setItem('sessions', JSON.stringify(updatedSessions));
      setSessions(updatedSessions);
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  }, []);

  // Update API URL
  const updateApiUrl = useCallback(async (url) => {
    setApiUrl(url);
    await AsyncStorage.setItem('apiUrl', url);
  }, []);

  const value = {
    sessionId,
    messages,
    loading,
    apiUrl,
    sessions,
    metrics,
    initializeSession,
    sendMessage,
    loadSessions,
    loadSessionHistory,
    deleteSession,
    updateApiUrl,
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
