/**
 * Performance Chart Component
 * Displays P&L, Sharpe ratio, and other performance metrics
 */

import React from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown } from 'lucide-react';
import './PerformanceChart.css';

const PerformanceChart = ({ performance }) => {
  if (!performance) {
    return <div className="performance-chart loading">Loading chart data...</div>;
  }

  // Mock data for demonstration (would be real data from backend)
  const chartData = [
    { time: '09:00', equity: 10000, trades: 0 },
    { time: '10:00', equity: 10150, trades: 2 },
    { time: '11:00', equity: 10320, trades: 4 },
    { time: '12:00', equity: 10280, trades: 5 },
    { time: '13:00', equity: 10520, trades: 8 },
    { time: '14:00', equity: 10480, trades: 9 },
    { time: '15:00', equity: 10650, trades: 11 },
    { time: '16:00', equity: 10720, trades: 13 },
    { time: '17:00', equity: 10800, trades: 15 },
  ];

  const roi = ((performance.capital - 10000) / 10000) * 100;
  const isPositive = roi >= 0;

  return (
    <div className="performance-chart">
      <h2>📊 Performance Metrics</h2>

      {/* Key Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-box">
          <label>Return on Investment</label>
          <div className={`metric-value ${isPositive ? 'positive' : 'negative'}`}>
            {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            {roi >= 0 ? '+' : ''}{roi.toFixed(2)}%
          </div>
        </div>

        <div className="metric-box">
          <label>Total P&L</label>
          <div className={`metric-value ${performance.total_pnl >= 0 ? 'positive' : 'negative'}`}>
            ${performance.total_pnl >= 0 ? '+' : ''}
            {performance.total_pnl?.toFixed(2)}
          </div>
        </div>

        <div className="metric-box">
          <label>Max Drawdown</label>
          <div className={`metric-value ${performance.drawdown_pct >= 0 ? 'positive' : 'negative'}`}>
            {performance.drawdown_pct?.toFixed(2)}%
          </div>
        </div>

        <div className="metric-box">
          <label>Win Rate</label>
          <div className="metric-value">
            {(performance.win_rate * 100).toFixed(1)}%
          </div>
        </div>

        <div className="metric-box">
          <label>Profitable Trades</label>
          <div className="metric-value">
            {performance.trades_profitable}/{performance.total_trades}
          </div>
        </div>

        <div className="metric-box">
          <label>Sharpe Ratio</label>
          <div className="metric-value">
            {performance.sharpe_ratio?.toFixed(2) || 'N/A'}
          </div>
        </div>
      </div>

      {/* Equity Curve Chart */}
      <div className="chart-container">
        <h3>Equity Curve</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Area
              type="monotone"
              dataKey="equity"
              stroke="#8884d8"
              fillOpacity={1}
              fill="url(#colorEquity)"
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Trade Distribution */}
      <div className="trade-stats">
        <div className="stat-box">
          <h4>Trade Quality</h4>
          <div className="stat-value">
            <span className="wins">↗ {performance.trades_profitable} wins</span>
            <span className="losses">
              ↘ {performance.total_trades - performance.trades_profitable} losses
            </span>
          </div>
        </div>

        <div className="stat-box">
          <h4>Consecutive Losses</h4>
          <div className="stat-value">
            {performance.consecutive_losses} in a row
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceChart;
