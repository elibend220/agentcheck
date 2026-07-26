/**
 * Open Positions Panel
 * Displays all currently open trades with unrealized P&L
 */

import React from 'react';
import { TrendingUp, TrendingDown, X } from 'lucide-react';
import './PositionsPanel.css';

const PositionsPanel = ({ positions = [] }) => {
  return (
    <div className="positions-panel">
      <h2>📈 Open Positions ({positions.length})</h2>

      {positions.length === 0 ? (
        <div className="empty-state">
          <p>No open positions</p>
        </div>
      ) : (
        <div className="positions-list">
          {positions.map((position, index) => {
            const isLong = position.direction === 'LONG';
            const pnlColor = position.unrealized_pnl >= 0 ? 'positive' : 'negative';

            return (
              <div key={index} className={`position-card ${pnlColor}`}>
                {/* Header */}
                <div className="position-header">
                  <div className="direction-badge">
                    {isLong ? (
                      <>
                        <TrendingUp size={16} /> LONG
                      </>
                    ) : (
                      <>
                        <TrendingDown size={16} /> SHORT
                      </>
                    )}
                  </div>
                  <div className="pnl-display">
                    <span className="pnl-value">
                      ${Math.abs(position.unrealized_pnl).toFixed(2)}
                    </span>
                    <span className="pnl-percent">
                      {position.unrealized_pnl_pct >= 0 ? '+' : ''}
                      {(position.unrealized_pnl_pct * 100).toFixed(2)}%
                    </span>
                  </div>
                </div>

                {/* Details */}
                <div className="position-details">
                  <div className="detail-row">
                    <span className="label">Entry:</span>
                    <span className="value">${position.entry_price.toFixed(2)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Current:</span>
                    <span className="value">${position.current_price.toFixed(2)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Size:</span>
                    <span className="value">${position.position_size.toFixed(2)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Stop Loss:</span>
                    <span className="value">${position.stop_loss.toFixed(2)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Take Profit:</span>
                    <span className="value">${position.take_profit.toFixed(2)}</span>
                  </div>
                </div>

                {/* Close Button */}
                <button className="close-position-btn">
                  <X size={16} /> Close
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Summary */}
      {positions.length > 0 && (
        <div className="positions-summary">
          <div className="summary-item">
            <span className="label">Total Exposure:</span>
            <span className="value">
              ${positions.reduce((sum, p) => sum + p.position_size, 0).toFixed(2)}
            </span>
          </div>
          <div className="summary-item">
            <span className="label">Total Unrealized:</span>
            <span className={`value ${positions.reduce((sum, p) => sum + p.unrealized_pnl, 0) >= 0 ? 'positive' : 'negative'}`}>
              ${positions.reduce((sum, p) => sum + p.unrealized_pnl, 0).toFixed(2)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default PositionsPanel;
