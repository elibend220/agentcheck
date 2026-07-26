"""
Trading orchestrator - Manages agent lifecycle and decision flow.
"""

"""
    TradingOrchestrator

Main orchestrator for the multi-agent trading system.
Manages agent instances and decision aggregation.
"""
mutable struct TradingOrchestrator
    momentum::MomentumAgent
    mean_reversion::MeanReversionAgent
    volatility::VolatilityAgent
    arbitrage::ArbitrageAgent
    risk_management::RiskManagementAgent
    agent_weights::Dict{Symbol, Float64}
    performance::Dict{Symbol, NamedTuple}
    decision_history::Vector{Tuple{DateTime, VotingResult}}
end

"""
    TradingOrchestrator(config::Dict)

Create an orchestrator from configuration dictionary.
Expected keys: momentum, mean_reversion, volatility, arbitrage, risk_management
"""
function TradingOrchestrator(config::Dict)
    momentum = MomentumAgent(
        config[:momentum][:ema_short],
        config[:momentum][:ema_long],
        config[:momentum][:macd_fast],
        config[:momentum][:macd_slow],
        config[:momentum][:macd_signal],
        config[:momentum][:trend_strength_threshold]
    )

    mean_reversion = MeanReversionAgent(
        config[:mean_reversion][:rsi_period],
        config[:mean_reversion][:rsi_overbought],
        config[:mean_reversion][:rsi_oversold],
        config[:mean_reversion][:bb_period],
        config[:mean_reversion][:bb_std_dev]
    )

    volatility = VolatilityAgent(
        config[:volatility][:atr_period],
        config[:volatility][:kc_period],
        config[:volatility][:breakout_multiplier]
    )

    arbitrage = ArbitrageAgent(
        Symbol(config[:arbitrage][:venue_1]),
        Symbol(config[:arbitrage][:venue_2]),
        config[:arbitrage][:spread_threshold]
    )

    risk_management = RiskManagementAgent(
        config[:risk_management][:max_position_size],
        config[:risk_management][:max_concurrent_positions],
        config[:risk_management][:max_drawdown_pct],
        config[:risk_management][:max_daily_loss_pct]
    )

    return TradingOrchestrator(
        momentum,
        mean_reversion,
        volatility,
        arbitrage,
        risk_management,
        Dict(:momentum => 1.0, :mean_reversion => 1.0, :volatility => 1.0, :arbitrage => 1.0),
        Dict(
            :momentum => (wins=0, losses=0, trades=0),
            :mean_reversion => (wins=0, losses=0, trades=0),
            :volatility => (wins=0, losses=0, trades=0),
            :arbitrage => (wins=0, losses=0, trades=0)
        ),
        Tuple{DateTime, VotingResult}[]
    )
end

"""
    process_decision_request(orchestrator::TradingOrchestrator, candles::DataFrame, state::EngineState, prices::Dict)::VotingResult

Process a decision request from the trading engine.

Flow:
1. Analyze with all agents (parallel in production)
2. Apply consensus voting
3. Record decision and return
"""
function process_decision_request(
    orchestrator::TradingOrchestrator,
    candles::DataFrame,
    state::EngineState,
    prices::Dict = Dict()
)::VotingResult

    # Analyze with all agents
    momentum_decision = analyze(orchestrator.momentum, candles)
    mean_reversion_decision = analyze(orchestrator.mean_reversion, candles)
    volatility_decision = analyze(orchestrator.volatility, candles)
    arbitrage_decision = analyze(orchestrator.arbitrage, candles, prices)
    risk_decision = analyze(orchestrator.risk_management, state)

    # Aggregate decisions
    agent_decisions = Dict(
        :momentum => momentum_decision,
        :mean_reversion => mean_reversion_decision,
        :volatility => volatility_decision,
        :arbitrage => arbitrage_decision,
        :risk_management => risk_decision
    )

    # Apply consensus voting
    voting_result = consensus_vote(agent_decisions, orchestrator.agent_weights)

    # Record decision
    push!(orchestrator.decision_history, (now(), voting_result))

    # Keep only last 1000 decisions
    if length(orchestrator.decision_history) > 1000
        deleteat!(orchestrator.decision_history, 1)
    end

    return voting_result
end

"""
    record_trade_outcome(orchestrator::TradingOrchestrator, pnl::Float64)

Record outcome of a trade for agent performance tracking.
Updates win/loss counts for adaptive weighting.
"""
function record_trade_outcome(orchestrator::TradingOrchestrator, pnl::Float64)
    is_win = pnl > 0

    for agent_id in [:momentum, :mean_reversion, :volatility, :arbitrage]
        perf = orchestrator.performance[agent_id]
        wins = perf.wins + (is_win ? 1 : 0)
        losses = perf.losses + (is_win ? 0 : 1)
        trades = perf.trades + 1

        orchestrator.performance[agent_id] = (wins=wins, losses=losses, trades=trades)
    end

    # Update agent weights based on new performance
    orchestrator.agent_weights = calculate_agent_weights(orchestrator.performance)
end

"""
    shutdown_orchestrator(orchestrator::TradingOrchestrator)::Dict

Shutdown orchestrator and return final statistics.
"""
function shutdown_orchestrator(orchestrator::TradingOrchestrator)::Dict
    stats = Dict(
        :total_decisions => length(orchestrator.decision_history),
        :agent_performance => orchestrator.performance,
        :agent_weights => orchestrator.agent_weights
    )

    if length(orchestrator.decision_history) > 0
        # Calculate consensus statistics
        long_count = 0
        short_count = 0
        hold_count = 0

        for (_, result) in orchestrator.decision_history
            if result.direction == :LONG
                long_count += 1
            elseif result.direction == :SHORT
                short_count += 1
            else
                hold_count += 1
            end
        end

        stats[:decision_distribution] = Dict(
            :LONG => long_count,
            :SHORT => short_count,
            :HOLD => hold_count
        )
    end

    return stats
end

"""
    get_orchestrator_status(orchestrator::TradingOrchestrator)::Dict

Get current status of the orchestrator.
"""
function get_orchestrator_status(orchestrator::TradingOrchestrator)::Dict
    return Dict(
        :decisions_count => length(orchestrator.decision_history),
        :agent_weights => orchestrator.agent_weights,
        :agent_performance => orchestrator.performance
    )
end
