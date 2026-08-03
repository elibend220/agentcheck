import React from 'react';
import { useJARVIS } from '../context/JARVISContext';
import styles from './MetricsDisplay.module.css';

const MetricsDisplay = () => {
  const { metrics } = useJARVIS();

  if (!metrics) {
    return null;
  }

  const getBarColor = (value) => {
    if (value >= 0.8) return '#00ff00';
    if (value >= 0.6) return '#00d4ff';
    if (value >= 0.4) return '#ffaa00';
    return '#ff6b6b';
  };

  const MetricBar = ({ label, value, icon }) => {
    const percentage = value * 100;
    const color = getBarColor(value);

    return (
      <div className={styles.metricItem}>
        <div className={styles.metricHeader}>
          <span className={styles.metricIcon}>{icon}</span>
          <span className={styles.metricLabel}>{label}</span>
          <span className={styles.metricValue} style={{ color }}>
            {percentage.toFixed(0)}%
          </span>
        </div>
        <div className={styles.metricBar}>
          <div
            className={styles.metricFill}
            style={{
              width: `${percentage}%`,
              backgroundColor: color,
            }}
          />
        </div>
      </div>
    );
  };

  return (
    <div className={styles.metricsContainer}>
      <div className={styles.metricsHeader}>
        <h3>🧠 JARVIS Metrics</h3>
      </div>

      <div className={styles.metricsBars}>
        <MetricBar
          label="Consciousness"
          value={metrics.consciousness}
          icon="🔷"
        />
        <MetricBar
          label="Emergence"
          value={metrics.emergence}
          icon="🌀"
        />
        <MetricBar
          label="Confidence"
          value={metrics.confidence}
          icon="✨"
        />
      </div>

      <div className={styles.metricsStats}>
        <div className={styles.stat}>
          <span className={styles.statLabel}>⏱️ Time</span>
          <span className={styles.statValue}>{metrics.time.toFixed(0)}ms</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>🔄 Phases</span>
          <span className={styles.statValue}>{metrics.phases}</span>
        </div>
      </div>
    </div>
  );
};

export default MetricsDisplay;
