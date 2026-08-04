/**
 * Status Panel Component
 * Displays current trading status and key metrics
 */

import React from 'react';
import { TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import './StatusPanel.css';

const StatusPanel = ({ status, wsConnected }) => {
  if (!status) {
    return <div className="status-panel loading">Loading...</div>;
  }

  const isRunning = status.is_running;
  const drawdown = status.drawdown_pct || 0;
  const isLosing = drawdown < 0;

  return (
    <div className="status-panel">
      <h2>📊 Trading Status</h2>

      {/* Status Badge */}
      <div className={`status-badge ${isRunning ? 'running' : 'stopped'}`}>
        {isRunning ? '🟢 Running' : '🔴 Stopped'}
      </div>

      {/* Key Metrics Grid */}
      <div className="metrics-grid">
        {/* Capital */}
        <div className="metric">
          <label>Capital</label>
          <value className="metric-value">${status.capital?.toFixed(2)}</value>
        </div>

        {/* Equity */}
        <div className="metric">
          <label>Current Equity</label>
          <value className="metric-value">${status.equity?.toFixed(2)}</value>
        </div>

        {/* Drawdown */}
        <div className={`metric ${isLosing ? 'negative' : 'positive'}`}>
          <label>Drawdown</label>
          <value className="metric-value">
            {isLosing ? <TrendingDown size={16} /> : <TrendingUp size={16} />}
            {Math.abs(drawdown).toFixed(2)}%
          </value>
        </div>

        {/* Win Rate */}
        <div className="metric">
          <label>Win Rate</label>
          <value className="metric-value">{(status.win_rate * 100).toFixed(1)}%</value>
        </div>

        {/* Open Positions */}
        <div className="metric">
          <label>Open Positions</label>
          <value className="metric-value">{status.open_positions}</value>
        </div>

        {/* Total Trades */}
        <div className="metric">
          <label>Total Trades</label>
          <value className="metric-value">{status.total_trades}</value>
        </div>
      </div>

      {/* Status Info */}
      <div className="status-info">
        <div className="info-item">
          <span className="label">Symbol:</span>
          <span className="value">{status.symbol}</span>
        </div>
        <div className="info-item">
          <span className="label">API Connection:</span>
          <span className={`value ${wsConnected ? 'ok' : 'error'}`}>
            {wsConnected ? '✓ Connected' : '✗ Disconnected'}
          </span>
        </div>
        <div className="info-item">
          <span className="label">Last Update:</span>
          <span className="value">{new Date(status.timestamp).toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Warning if losing */}
      {drawdown < -10 && (
        <div className="warning-box">
          <AlertCircle size={20} />
          <span>⚠️ Significant drawdown detected. Review strategy.</span>
        </div>
      )}
    </div>
  );
};

export default StatusPanel;
