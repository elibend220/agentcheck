/**
 * Main Trading Dashboard Component
 * Displays real-time trading status, positions, and performance metrics
 */

import React, { useState, useEffect } from 'react';
import { tradingAPI, TradingWebSocket } from '../api/client';
import StatusPanel from './StatusPanel';
import PositionsPanel from './PositionsPanel';
import PerformanceChart from './PerformanceChart';
import MarketStatePanel from './MarketStatePanel';
import AlertsPanel from './AlertsPanel';
import ControlPanel from './ControlPanel';
import './Dashboard.css';

const Dashboard = () => {
  const [status, setStatus] = useState(null);
  const [positions, setPositions] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [marketState, setMarketState] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);

  // Initialize WebSocket and API calls
  useEffect(() => {
    // Fetch initial data
    const fetchData = async () => {
      try {
        const [statusData, positionsData, perfData, marketData, alertsData] = await Promise.all([
          tradingAPI.getStatus(),
          tradingAPI.getPositions(),
          tradingAPI.getPerformance(),
          tradingAPI.getMarketState(),
          tradingAPI.getAlerts(),
        ]);

        setStatus(statusData);
        setPositions(positionsData);
        setPerformance(perfData);
        setMarketState(marketData);
        setAlerts(alertsData);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();

    // Set up polling (every 2 seconds)
    const pollInterval = setInterval(fetchData, 2000);

    // Connect WebSocket for real-time updates
    const ws = new TradingWebSocket(
      (data) => {
        // Update status from WebSocket
        setStatus(data);
        setWsConnected(true);
      },
      (error) => {
        setError(`WebSocket error: ${error.message}`);
      },
      () => {
        setWsConnected(false);
      }
    );

    ws.connect();

    // Cleanup
    return () => {
      clearInterval(pollInterval);
      ws.disconnect();
    };
  }, []);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading trading engine...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h2>⚠️ Connection Error</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <h1>🎯 NEUS_TRADER Dashboard</h1>
        <div className="header-status">
          <span className={`ws-indicator ${wsConnected ? 'connected' : 'disconnected'}`}>
            {wsConnected ? '🟢 Live' : '🔴 Offline'}
          </span>
          <span className="timestamp">{new Date().toLocaleTimeString()}</span>
        </div>
      </header>

      {/* Main Grid */}
      <div className="dashboard-grid">
        {/* Left Column */}
        <div className="dashboard-column-left">
          {/* Status Panel */}
          <StatusPanel status={status} wsConnected={wsConnected} />

          {/* Market State */}
          <MarketStatePanel marketState={marketState} />

          {/* Alerts */}
          <AlertsPanel alerts={alerts.slice(0, 5)} />
        </div>

        {/* Center Column */}
        <div className="dashboard-column-center">
          {/* Performance Chart */}
          <PerformanceChart performance={performance} />

          {/* Control Panel */}
          <ControlPanel status={status} />
        </div>

        {/* Right Column */}
        <div className="dashboard-column-right">
          {/* Positions */}
          <PositionsPanel positions={positions} />
        </div>
      </div>

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>NEUS_TRADER v1.0 | Backend API: {status?.is_running ? '🟢 Running' : '🔴 Stopped'}</p>
      </footer>
    </div>
  );
};

export default Dashboard;
