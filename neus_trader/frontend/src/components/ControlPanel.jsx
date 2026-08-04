/**
 * Control Panel Component
 * Start/Stop trading and view risk parameters
 */

import React, { useState } from 'react';
import { Play, Square, Settings } from 'lucide-react';
import { tradingAPI } from '../api/client';
import './ControlPanel.css';

const ControlPanel = ({ status }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleStartTrading = async () => {
    try {
      setLoading(true);
      await tradingAPI.startTrading();
      setMessage({ type: 'success', text: 'Trading started' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  const handleStopTrading = async () => {
    try {
      setLoading(true);
      await tradingAPI.stopTrading();
      setMessage({ type: 'success', text: 'Trading stopped' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="control-panel">
      <h2>⚙️ Controls</h2>

      {/* Status Display */}
      <div className="status-display">
        <div className={`status-circle ${status?.is_running ? 'running' : 'stopped'}`}></div>
        <span>{status?.is_running ? 'Trading Active' : 'Trading Inactive'}</span>
      </div>

      {/* Control Buttons */}
      <div className="control-buttons">
        <button
          className="btn btn-start"
          onClick={handleStartTrading}
          disabled={loading || status?.is_running}
        >
          <Play size={18} />
          Start Trading
        </button>
        <button
          className="btn btn-stop"
          onClick={handleStopTrading}
          disabled={loading || !status?.is_running}
        >
          <Square size={18} />
          Stop Trading
        </button>
      </div>

      {/* Message */}
      {message && (
        <div className={`message message-${message.type}`}>
          {message.text}
        </div>
      )}

      {/* Risk Settings */}
      <div className="risk-settings">
        <div className="settings-header">
          <Settings size={16} />
          <h3>Risk Parameters</h3>
        </div>

        <div className="settings-form">
          <div className="setting-item">
            <label>Max Position Size (USDT)</label>
            <input type="number" placeholder="450" defaultValue="450" />
          </div>

          <div className="setting-item">
            <label>Risk Per Trade (%)</label>
            <input type="number" placeholder="1.5" defaultValue="1.5" step="0.1" />
          </div>

          <div className="setting-item">
            <label>Max Drawdown (%)</label>
            <input type="number" placeholder="20" defaultValue="20" />
          </div>

          <button className="btn btn-apply">Apply Settings</button>
        </div>
      </div>

      {/* Quick Info */}
      <div className="quick-info">
        <div className="info-box">
          <span className="label">Strategy</span>
          <span className="value">Golden Hour Scalper</span>
        </div>
        <div className="info-box">
          <span className="label">Timeframe</span>
          <span className="value">4H / 1H / 5m</span>
        </div>
        <div className="info-box">
          <span className="label">Target Trade</span>
          <span className="value">30-50 min</span>
        </div>
      </div>
    </div>
  );
};

export default ControlPanel;
