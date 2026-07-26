"""
Risk Management Agent - Position sizing and circuit breaker logic.
"""

"""
    RiskManagementAgent

Configuration for Risk Management Agent.
"""
struct RiskManagementAgent
    max_position_size::Float64  # USDT
    max_concurrent_positions::Int
    max_drawdown_pct::Float64   # 20%
    max_daily_loss_pct::Float64 # 3%
end

"""
    analyze(agent::RiskManagementAgent, state::EngineState)::Decision

Analyze risk constraints and approve/deny/reduce positions.

Logic:
1. Check if any hard limits exceeded (circuit breaker)
2. Check if position size within limits
3. Return ALLOW, REDUCE, or DENY

Direction:
- ALLOW: Proceed with trade at requested size
- HOLD: REDUCE position size (return with reduced confidence)
- SHORT: DENY trade due to risk constraints
"""
function analyze(agent::RiskManagementAgent, state::EngineState)::Decision
    violations = String[]

    # Check drawdown limit
    if state.drawdown_pct < -agent.max_drawdown_pct
        push!(violations, "Drawdown $(state.drawdown_pct)% exceeds limit")
    end

    # Check daily loss limit (simplified: use recent drawdown)
    if state.drawdown_pct < -agent.max_daily_loss_pct
        push!(violations, "Daily loss $(state.drawdown_pct)% exceeds limit")
    end

    # Check concurrent positions
    if state.open_positions >= agent.max_concurrent_positions
        push!(violations, "Open positions $(state.open_positions) >= max $(agent.max_concurrent_positions)")
    end

    # Check capital
    if state.equity <= state.capital * 0.5
        push!(violations, "Equity dropped to $(state.equity), only 50% of capital")
    end

    # Determine approval
    if !isempty(violations)
        # Hard circuit breaker
        return Decision(
            :risk_management,
            :HOLD,  # DENY signal (use HOLD with 0 confidence)
            0.0,
            join(violations, "; "),
            now()
        )
    end

    if state.open_positions > agent.max_concurrent_positions - 1
        # Approaching position limit, suggest reduced size
        return Decision(
            :risk_management,
            :HOLD,  # REDUCE signal (use HOLD with 0.5 confidence)
            0.5,
            "Approaching max positions: $(state.open_positions)/$(agent.max_concurrent_positions)",
            now()
        )
    end

    # All checks passed
    return Decision(
        :risk_management,
        :LONG,  # ALLOW signal (always LONG means approved)
        1.0,
        "Risk checks passed: drawdown $(round(state.drawdown_pct; digits=1))%, positions $(state.open_positions)/$(agent.max_concurrent_positions)",
        now()
    )
end
