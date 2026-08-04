import React from 'react';
import { View, StyleSheet, Text } from 'react-native';

const MetricsBar = ({ metrics }) => {
  if (!metrics) return null;

  const getBarColor = (value) => {
    if (value >= 0.8) return '#00ff00';
    if (value >= 0.6) return '#00d4ff';
    if (value >= 0.4) return '#ffaa00';
    return '#ff6b6b';
  };

  const renderMetricBar = (label, value, icon) => {
    const percentage = value * 100;
    return (
      <View style={styles.metricContainer}>
        <View style={styles.metricHeader}>
          <Text style={styles.metricIcon}>{icon}</Text>
          <Text style={styles.metricLabel}>{label}</Text>
          <Text style={styles.metricValue}>{percentage.toFixed(0)}%</Text>
        </View>
        <View style={styles.barBackground}>
          <View
            style={[
              styles.barFill,
              {
                width: `${percentage}%`,
                backgroundColor: getBarColor(value),
              },
            ]}
          />
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerText}>🧠 JARVIS Metrics</Text>
      </View>

      <View style={styles.metricsGrid}>
        {renderMetricBar(
          'Consciousness',
          metrics.consciousness,
          '🔷'
        )}
        {renderMetricBar(
          'Emergence',
          metrics.emergence,
          '🌀'
        )}
        {renderMetricBar(
          'Confidence',
          metrics.confidence,
          '✨'
        )}
      </View>

      <View style={styles.statsRow}>
        <View style={styles.stat}>
          <Text style={styles.statLabel}>Time</Text>
          <Text style={styles.statValue}>
            {metrics.time.toFixed(0)}ms
          </Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statLabel}>Phases</Text>
          <Text style={styles.statValue}>{metrics.phases}</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#16213e',
    borderBottomWidth: 2,
    borderBottomColor: '#00d4ff',
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  header: {
    marginBottom: 8,
  },
  headerText: {
    color: '#00d4ff',
    fontWeight: 'bold',
    fontSize: 13,
  },
  metricsGrid: {
    marginBottom: 8,
  },
  metricContainer: {
    marginBottom: 6,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  metricIcon: {
    fontSize: 14,
    marginRight: 6,
  },
  metricLabel: {
    flex: 1,
    color: '#aaa',
    fontSize: 11,
    fontWeight: '500',
  },
  metricValue: {
    color: '#00d4ff',
    fontSize: 11,
    fontWeight: 'bold',
    minWidth: 35,
    textAlign: 'right',
  },
  barBackground: {
    height: 4,
    backgroundColor: 'rgba(0, 212, 255, 0.1)',
    borderRadius: 2,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: 2,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: 6,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0, 212, 255, 0.1)',
  },
  stat: {
    alignItems: 'center',
  },
  statLabel: {
    color: '#888',
    fontSize: 10,
  },
  statValue: {
    color: '#00d4ff',
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: 2,
  },
});

export default MetricsBar;
