/**
 * Market State Panel
 * Displays current market session and conditions
 */

import React from 'react';
import { Clock, TrendingUp, Activity } from 'lucide-react';
import './MarketStatePanel.css';

const MarketStatePanel = ({ marketState }) => {
  if (!marketState) {
    return <div className="market-state-panel loading">Loading market data...</div>;
  }

  const sessionColors = {
    london: 'primary',
    us_close: 'success',
    us: 'info',
    asian: 'warning',
    overnight: 'danger',
  };

  const getSessionLabel = (session) => {
    const labels = {
      london: '🇬🇧 London (13:00-17:00)',
      us_close: '🇺🇸 US Close (20:00-23:00)',
      us: '🇺🇸 US (17:00-20:00)',
      asian: '🌏 Asian (0:00-13:00)',
      overnight: '🌙 Overnight (23:00-0:00)',
    };
    return labels[session] || session;
  };

  return (
    <div className="market-state-panel">
      <h2>📍 Market Session</h2>

      {/* Current Session */}
      <div className={`session-badge ${sessionColors[marketState.session]}`}>
        <Clock size={16} />
        {getSessionLabel(marketState.session)}
      </div>

      {/* Session Metrics */}
      <div className="session-metrics">
        {/* Trading Status */}
        <div className="metric">
          <label>Trading Active</label>
          <span className={`status-indicator ${marketState.is_trading_active ? 'active' : 'inactive'}`}>
            {marketState.is_trading_active ? '🟢 Yes' : '🔴 No'}
          </span>
        </div>

        {/* Prime Hour */}
        <div className="metric">
          <label>Prime Hour</label>
          <span className={`status-indicator ${marketState.is_prime_hour ? 'active' : 'inactive'}`}>
            {marketState.is_prime_hour ? '✓ Yes' : '✗ No'}
          </span>
        </div>

        {/* Expected Win Rate */}
        <div className="metric">
          <label>Expected Win Rate</label>
          <span className="metric-value">
            <TrendingUp size={14} />
            {(marketState.expected_win_rate * 100).toFixed(0)}%
          </span>
        </div>

        {/* Volatility Factor */}
        <div className="metric">
          <label>Volatility Factor</label>
          <span className="metric-value">
            <Activity size={14} />
            {marketState.volatility_factor.toFixed(2)}x
          </span>
        </div>

        {/* Liquidity */}
        <div className="metric">
          <label>Liquidity</label>
          <div className="liquidity-bar">
            <div
              className="liquidity-fill"
              style={{ width: `${marketState.liquidity * 100}%` }}
            ></div>
            <span className="liquidity-text">{(marketState.liquidity * 100).toFixed(0)}%</span>
          </div>
        </div>

        {/* Hours Until Prime */}
        <div className="metric">
          <label>Hours Until Prime</label>
          <span className="metric-value">{marketState.hours_until_prime}h</span>
        </div>
      </div>

      {/* Session Info */}
      <div className="session-info">
        <div className="info-item">
          <span className="key">📊 Best Trading Windows</span>
          <span className="value">13:00-17:00 UTC (London) & 20:00-23:00 UTC (US Close)</span>
        </div>
        <div className="info-item">
          <span className="key">📈 Win Rate Expectation</span>
          <span className="value">
            {marketState.is_prime_hour
              ? `High: ${(marketState.expected_win_rate * 100).toFixed(0)}%`
              : `Low: ${(marketState.expected_win_rate * 100).toFixed(0)}%`
            }
          </span>
        </div>
      </div>

      {/* Recommendation */}
      {!marketState.is_prime_hour && (
        <div className="recommendation">
          ⏰ Outside prime trading hours. Consider reducing position size.
        </div>
      )}
    </div>
  );
};

export default MarketStatePanel;
