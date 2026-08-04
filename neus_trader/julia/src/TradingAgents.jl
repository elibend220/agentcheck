"""
    TradingAgents

Multi-agent trading system with consensus voting for NEUS_TRADER Phase 2.

Five specialized agents:
- Momentum Agent: EMA/MACD trend detection
- Mean-Reversion Agent: RSI/Bollinger Band oversold/overbought
- Volatility Agent: ATR/Keltner breakout detection
- Arbitrage Agent: Cross-venue price discrepancy
- Risk Management Agent: Position sizing & circuit breaker

Consensus voting aggregates decisions with confidence weighting and dissent tracking.
"""
module TradingAgents

using DataFrames
using Statistics
using JSON
using Dates

# Core types
include("types.jl")

# Indicators
include("indicators.jl")

# Agent implementations
include("agents/momentum.jl")
include("agents/mean_reversion.jl")
include("agents/volatility.jl")
include("agents/arbitrage.jl")
include("agents/risk_management.jl")

# Consensus voting
include("voting.jl")

# Main orchestrator
include("orchestrator.jl")

# Export public API
export
    # Types
    Decision, VotingResult, EngineState,

    # Agents
    MomentumAgent, MeanReversionAgent, VolatilityAgent, ArbitrageAgent, RiskManagementAgent,

    # Functions
    analyze, consensus_vote,

    # Orchestrator
    TradingOrchestrator, process_decision_request, shutdown_orchestrator

end # module TradingAgents
