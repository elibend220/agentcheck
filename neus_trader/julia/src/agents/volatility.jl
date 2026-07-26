"""
Volatility Agent - Detects breakouts via ATR and Keltner Channels.
"""

"""
    VolatilityAgent

Configuration for Volatility Agent.
"""
struct VolatilityAgent
    atr_period::Int             # 14-period
    kc_period::Int              # 20-period
    breakout_multiplier::Float64 # 1.5
end

"""
    analyze(agent::VolatilityAgent, candles::DataFrame)::Decision

Analyze volatility breakouts using ATR and Keltner Channels.

Logic:
1. Keltner Channels: EMA ± (2 * ATR)
2. Upper breakout: Price > upper channel (LONG)
3. Lower breakout: Price < lower channel (SHORT)
4. Confidence based on breakout magnitude vs ATR
"""
function analyze(agent::VolatilityAgent, candles::DataFrame)::Decision
    if nrow(candles) < max(agent.kc_period + 5, agent.atr_period + 5)
        return Decision(
            :volatility,
            :HOLD,
            0.0,
            "Insufficient data for volatility analysis",
            now()
        )
    end

    current_price = candles[end, :close]

    # Calculate Keltner Channels
    kc = keltner_channels(candles, agent.kc_period, agent.breakout_multiplier)
    atr_val = atr(candles, agent.atr_period)

    # Determine direction based on breakout
    if current_price > kc.upper
        direction = :LONG
        breakout_magnitude = (current_price - kc.middle) / atr_val
    elseif current_price < kc.lower
        direction = :SHORT
        breakout_magnitude = (kc.middle - current_price) / atr_val
    else
        direction = :HOLD
        breakout_magnitude = 0.0
    end

    # Calculate confidence based on breakout strength
    if direction != :HOLD
        # Breakout magnitude 0-2 ATR = 0.5-1.0 confidence
        confidence = min(1.0, 0.5 + (breakout_magnitude / 4.0))
        confidence = max(0.4, confidence)
    else
        confidence = 0.0
    end

    reasoning = _volatility_reasoning(
        direction, current_price, kc, atr_val, confidence
    )

    return Decision(:volatility, direction, confidence, reasoning, now())
end

"""
    _volatility_reasoning(direction, price, kc, atr, conf)

Generate human-readable reasoning for the decision.
"""
function _volatility_reasoning(
    direction::Symbol,
    price::Float64, kc::NamedTuple, atr_val::Float64,
    confidence::Float64
)::String

    if direction == :HOLD
        return "Price within Keltner Channels, no clear breakout"
    end

    if direction == :LONG
        distance = price - kc.upper
    else
        distance = kc.lower - price
    end

    distance_atr = distance / atr_val
    dir_str = direction == :LONG ? "Upper breakout" : "Lower breakout"

    return "$dir_str: $(round(distance_atr; digits=2)) ATR above channel, confidence $(round(confidence; digits=2))"
end
