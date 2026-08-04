/**
 * API Client for NEUS_TRADER Backend
 * Handles all communication with the trading engine API
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    throw error;
  }
);

// API Endpoints
export const tradingAPI = {
  // Status
  getStatus: () => apiClient.get('/api/status'),

  // Market
  getMarketState: () => apiClient.get('/api/market-state'),

  // Risk
  getRiskParameters: () => apiClient.get('/api/risk-parameters'),

  // Performance
  getPerformance: () => apiClient.get('/api/performance'),

  // Positions
  getPositions: () => apiClient.get('/api/positions'),

  // Alerts
  getAlerts: (minutes = 60) => apiClient.get(`/api/alerts?minutes=${minutes}`),

  // Control
  startTrading: () => apiClient.post('/api/start'),
  stopTrading: () => apiClient.post('/api/stop'),

  // Diagnostics
  getDiagnostics: () => apiClient.get('/api/diagnostics'),

  // Phase 2: Multi-agent system
  getAgentDecisions: () => apiClient.get('/api/agent-decisions'),
  getAgentStats: () => apiClient.get('/api/agent-stats'),
};

// WebSocket for real-time updates
export class TradingWebSocket {
  constructor(onMessage, onError, onClose) {
    this.ws = null;
    this.onMessage = onMessage;
    this.onError = onError;
    this.onClose = onClose;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/market-updates`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.onError?.(error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.onClose?.();
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.attemptReconnect();
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.pow(2, this.reconnectAttempts) * 1000;
      console.log(`Attempting to reconnect in ${delay}ms...`);
      setTimeout(() => this.connect(), delay);
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default apiClient;
