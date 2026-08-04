import React, { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Shield, AlertCircle } from 'lucide-react'
import { tradingAPI } from '../api/client'
import './AgentPanel.css'

/**
 * AgentPanel - Displays multi-agent consensus voting breakdown
 * Shows individual agent decisions, confidence levels, and consensus strength
 */
export default function AgentPanel() {
  const [agentDecisions, setAgentDecisions] = useState(null)
  const [agentStats, setAgentStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchAgentData = async () => {
      try {
        const [decisions, stats] = await Promise.all([
          tradingAPI.getAgentDecisions(),
          tradingAPI.getAgentStats()
        ])

        setAgentDecisions(decisions?.data || null)
        setAgentStats(stats?.data || null)
        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchAgentData()
    const interval = setInterval(fetchAgentData, 2000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="panel agent-panel loading">
        <h2>Multi-Agent System</h2>
        <p>Loading agent data...</p>
      </div>
    )
  }

  if (!agentStats?.is_julia_running) {
    return (
      <div className="panel agent-panel">
        <h2>Multi-Agent System</h2>
        <div className="warning-box">
          <AlertCircle size={20} />
          <span>Julia agent system unavailable. Running Phase 1 single agent mode.</span>
        </div>
        <div className="stats-grid">
          <div className="stat-item">
            <label>Status</label>
            <span className="status-badge stopped">Offline</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="panel agent-panel">
      <h2>Multi-Agent Consensus</h2>

      {error && (
        <div className="warning-box">
          <AlertCircle size={20} />
          <span>Error loading agent data: {error}</span>
        </div>
      )}

      {/* Consensus Decision */}
      {agentDecisions && (
        <div className="consensus-section">
          <div className="consensus-header">
            <h3>Consensus Decision</h3>
            <div className="consensus-indicator">
              <span className="strength-label">Agreement: {(agentDecisions.consensus_strength * 100).toFixed(0)}%</span>
              <div className="strength-bar">
                <div
                  className="strength-fill"
                  style={{ width: `${agentDecisions.consensus_strength * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="consensus-result">
            <div className={`direction-badge ${agentDecisions.direction.toLowerCase()}`}>
              {agentDecisions.direction === 'LONG' && <TrendingUp size={24} />}
              {agentDecisions.direction === 'SHORT' && <TrendingDown size={24} />}
              <span>{agentDecisions.direction}</span>
            </div>

            <div className="consensus-metrics">
              <div className="metric">
                <label>Confidence</label>
                <span className="metric-value">{(agentDecisions.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="metric">
                <label>Risk Approved</label>
                <span className={`status-badge ${agentDecisions.risk_approved ? 'running' : 'stopped'}`}>
                  {agentDecisions.risk_approved ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Agent Votes Breakdown */}
      {agentDecisions && agentDecisions.agent_votes && (
        <div className="agent-votes-section">
          <h3>Agent Votes ({agentDecisions.agent_votes.length})</h3>
          <div className="votes-grid">
            {agentDecisions.agent_votes.map((vote, idx) => (
              <div key={idx} className="vote-card">
                <div className="agent-name">{_formatAgentName(vote.agent_id)}</div>

                <div className={`vote-direction ${vote.direction.toLowerCase()}`}>
                  {vote.direction === 'LONG' && <TrendingUp size={20} />}
                  {vote.direction === 'SHORT' && <TrendingDown size={20} />}
                  {vote.direction === 'HOLD' && <Shield size={20} />}
                  <span>{vote.direction}</span>
                </div>

                <div className="vote-confidence">
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{ width: `${vote.confidence * 100}%` }}
                    />
                  </div>
                  <span className="confidence-text">{(vote.confidence * 100).toFixed(0)}%</span>
                </div>

                <div className="vote-reasoning">
                  <span className="reasoning-label">Analysis:</span>
                  <p>{vote.reasoning || 'No analysis available'}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Statistics */}
      {agentStats && (
        <div className="stats-section">
          <h3>System Stats</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <label>Decisions Processed</label>
              <span className="stat-value">{agentStats.decisions_processed}</span>
            </div>
            <div className="stat-item">
              <label>Avg Latency</label>
              <span className="stat-value">{agentStats.avg_latency_ms.toFixed(1)}ms</span>
            </div>
            <div className="stat-item">
              <label>Max Latency</label>
              <span className="stat-value">{agentStats.max_latency_ms.toFixed(1)}ms</span>
            </div>
            <div className="stat-item">
              <label>Errors</label>
              <span className={`stat-value ${agentStats.error_count > 0 ? 'error' : ''}`}>
                {agentStats.error_count}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Format agent ID for display
 */
function _formatAgentName(agentId) {
  return agentId
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
