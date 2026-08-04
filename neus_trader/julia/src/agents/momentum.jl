"""
Momentum Agent - Detects fast-moving trends via EMA crossover and MACD.
"""

"""
    MomentumAgent

Configuration for Momentum Agent.
"""
struct MomentumAgent
    ema_short::Int              # 9-period
    ema_long::Int               # 21-period
    macd_fast::Int              # 12-period
    macd_slow::Int              # 26-period
    macd_signal::Int            # 9-period
    trend_strength_threshold::Float64  # 0.6
end

"""
    analyze(agent::MomentumAgent, candles::DataFrame)::Decision

Analyze momentum using EMA crossover and MACD.

Logic:
1. EMA crossover: short EMA > long EMA (bullish)
2. MACD divergence: MACD > signal line (bullish momentum)
3. Combine signals for direction and confidence
"""
function analyze(agent::MomentumAgent, candles::DataFrame)::Decision
    if nrow(candles) < agent.ema_long + 5
        return Decision(
            :momentum,
            :HOLD,
            0.0,
            "Insufficient data for momentum analysis",
            now()
        )
    end

    closes = candles[!, :close]

    # Calculate EMAs
    ema_short_val = ema(closes, agent.ema_short)
    ema_long_val = ema(closes, agent.ema_long)

    # Calculate MACD
    macd_result = macd(closes, agent.macd_fast, agent.macd_slow, agent.macd_signal)

    # Determine direction
    ema_bullish = ema_short_val > ema_long_val
    macd_bullish = macd_result.macd > macd_result.signal

    if ema_bullish && macd_bullish
        direction = :LONG
        confidence = _calculate_momentum_confidence(
            ema_short_val, ema_long_val,
            macd_result.macd, macd_result.signal,
            agent.trend_strength_threshold
        )
    elseif !ema_bullish && !macd_bullish
        direction = :SHORT
        confidence = _calculate_momentum_confidence(
            ema_long_val, ema_short_val,
            macd_result.signal, macd_result.macd,
            agent.trend_strength_threshold
        )
    else
        direction = :HOLD
        confidence = 0.3  # Conflicting signals
    end

    reasoning = _momentum_reasoning(
        direction, ema_short_val, ema_long_val,
        macd_result.macd, macd_result.signal, confidence
    )

    return Decision(:momentum, direction, confidence, reasoning, now())
end

"""
    _calculate_momentum_confidence(ema1, ema2, macd_val, signal_val, threshold)

Calculate confidence based on strength of momentum signals.
"""
function _calculate_momentum_confidence(
    ema1::Float64, ema2::Float64,
    macd_val::Float64, signal_val::Float64,
    threshold::Float64
)::Float64
    # EMA separation strength (0-1)
    ema_diff_pct = abs(ema1 - ema2) / ema2
    ema_strength = min(1.0, ema_diff_pct / threshold)

    # MACD separation strength (0-1)
    macd_diff = abs(macd_val - signal_val)
    macd_strength = min(1.0, macd_diff / (0.01 * abs(signal_val) + 0.0001))

    # Combine with equal weight
    confidence = (ema_strength + macd_strength) / 2.0
    confidence = max(0.3, min(1.0, confidence))  # Clamp to 0.3-1.0

    return confidence
end

"""
    _momentum_reasoning(direction, ema_short, ema_long, macd, signal, conf)

Generate human-readable reasoning for the decision.
"""
function _momentum_reasoning(
    direction::Symbol,
    ema_short::Float64, ema_long::Float64,
    macd_val::Float64, signal_val::Float64,
    confidence::Float64
)::String

    if direction == :HOLD
        return "EMA and MACD showing conflicting signals"
    end

    ema_pct = round((abs(ema_short - ema_long) / ema_long) * 100; digits=2)
    macd_pct = round((abs(macd_val - signal_val) / abs(signal_val + 0.0001)) * 100; digits=2)

    dir_str = direction == :LONG ? "Bullish" : "Bearish"
    return "$dir_str momentum: EMA separation $(ema_pct)%, MACD divergence $(macd_pct)%, confidence $(round(confidence; digits=2))"
end
