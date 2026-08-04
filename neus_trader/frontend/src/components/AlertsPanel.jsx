/**
 * Alerts Panel Component
 * Displays recent system alerts and warnings
 */

import React from 'react';
import { AlertCircle, AlertTriangle, Info, X } from 'lucide-react';
import './AlertsPanel.css';

const AlertsPanel = ({ alerts = [] }) => {
  const getAlertIcon = (level) => {
    switch (level) {
      case 'critical':
        return <AlertTriangle size={18} className="alert-icon-critical" />;
      case 'warning':
        return <AlertCircle size={18} className="alert-icon-warning" />;
      case 'info':
        return <Info size={18} className="alert-icon-info" />;
      default:
        return <Info size={18} />;
    }
  };

  return (
    <div className="alerts-panel">
      <h2>🚨 Recent Alerts</h2>

      {alerts.length === 0 ? (
        <div className="empty-state">
          <p>✓ No alerts</p>
        </div>
      ) : (
        <div className="alerts-list">
          {alerts.map((alert, index) => (
            <div key={index} className={`alert-item alert-${alert.level}`}>
              <div className="alert-header">
                {getAlertIcon(alert.level)}
                <h4>{alert.title}</h4>
              </div>
              <p className="alert-message">{alert.message}</p>
              <span className="alert-time">
                {new Date(alert.timestamp).toLocaleTimeString()}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Alert Summary */}
      {alerts.length > 0 && (
        <div className="alert-summary">
          <span className="summary-item">
            <span className="count">{alerts.filter(a => a.level === 'critical').length}</span>
            Critical
          </span>
          <span className="summary-item">
            <span className="count">{alerts.filter(a => a.level === 'warning').length}</span>
            Warnings
          </span>
          <span className="summary-item">
            <span className="count">{alerts.filter(a => a.level === 'info').length}</span>
            Info
          </span>
        </div>
      )}
    </div>
  );
};

export default AlertsPanel;
