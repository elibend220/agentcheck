"""
Core types for the multi-agent trading system.
"""

"""
    Decision

Agent decision from technical analysis.
"""
struct Decision
    agent_id::Symbol            # :momentum, :mean_reversion, etc
    direction::Symbol           # :LONG, :SHORT, :HOLD
    confidence::Float64         # 0.0 - 1.0
    reasoning::String           # Human-readable reason
    timestamp::DateTime
end

"""
    VotingResult

Consensus voting result from all agents.
"""
struct VotingResult
    direction::Symbol           # :LONG, :SHORT, :HOLD
    confidence::Float64         # 0.0 - 1.0 (average across agents)
    agent_votes::Dict           # agent_id => Decision
    consensus_strength::Float64 # 0.0 - 1.0 (agreement level)
    risk_approved::Bool         # Risk agent approval
    timestamp::DateTime
end

"""
    EngineState

Current trading engine state passed to agents.
"""
mutable struct EngineState
    symbol::String
    current_price::Float64
    capital::Float64
    equity::Float64
    drawdown_pct::Float64
    open_positions::Int
    total_trades::Int
    win_rate::Float64
    last_trade_pnl::Float64
    is_running::Bool
    timestamp::DateTime
end

"""
    CandleData

OHLCV candlestick data.
"""
struct CandleData
    timestamp::DateTime
    open::Float64
    high::Float64
    low::Float64
    close::Float64
    volume::Float64
end

"""
    IndicatorResult

Result from indicator calculation.
"""
struct IndicatorResult
    value::Float64              # Current value
    prev_value::Float64         # Previous value
    is_valid::Bool              # True if enough data for calculation
end
