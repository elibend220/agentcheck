"""
Mean-Reversion Agent - Identifies overbought/oversold conditions via RSI and Bollinger Bands.
"""

"""
    MeanReversionAgent

Configuration for Mean-Reversion Agent.
"""
struct MeanReversionAgent
    rsi_period::Int             # 14-period
    rsi_overbought::Float64     # 70
    rsi_oversold::Float64       # 30
    bb_period::Int              # 20-period
    bb_std_dev::Float64         # 2.0
end

"""
    analyze(agent::MeanReversionAgent, candles::DataFrame)::Decision

Analyze mean-reversion using RSI and Bollinger Bands.

Logic:
1. RSI oversold (<30): Potential LONG
2. RSI overbought (>70): Potential SHORT
3. Bollinger Band proximity: Touches band = high confidence
4. Combine RSI and BB for direction and confidence
"""
function analyze(agent::MeanReversionAgent, candles::DataFrame)::Decision
    if nrow(candles) < max(agent.rsi_period + 5, agent.bb_period + 5)
        return Decision(
            :mean_reversion,
            :HOLD,
            0.0,
            "Insufficient data for mean-reversion analysis",
            now()
        )
    end

    closes = candles[!, :close]
    current_price = closes[end]

    # Calculate RSI
    rsi_val = rsi(closes, agent.rsi_period)

    # Calculate Bollinger Bands
    bb = bollinger_bands(closes, agent.bb_period, agent.bb_std_dev)

    # Determine direction
    if rsi_val < agent.rsi_oversold
        direction = :LONG
        rsi_strength = (agent.rsi_oversold - rsi_val) / agent.rsi_oversold
    elseif rsi_val > agent.rsi_overbought
        direction = :SHORT
        rsi_strength = (rsi_val - agent.rsi_overbought) / (100.0 - agent.rsi_overbought)
    else
        direction = :HOLD
        rsi_strength = 0.0
    end

    # Calculate Bollinger Band strength (0-1)
    if direction != :HOLD
        if direction == :LONG
            bb_strength = _bb_strength_long(current_price, bb)
        else  # SHORT
            bb_strength = _bb_strength_short(current_price, bb)
        end
    else
        bb_strength = 0.0
    end

    # Combine RSI and BB confidence
    if direction != :HOLD
        confidence = max(0.3, (rsi_strength + bb_strength) / 2.0)
        confidence = min(1.0, confidence)
    else
        confidence = 0.0
    end

    reasoning = _mean_reversion_reasoning(
        direction, rsi_val, agent.rsi_oversold, agent.rsi_overbought,
        current_price, bb, confidence
    )

    return Decision(:mean_reversion, direction, confidence, reasoning, now())
end

"""
    _bb_strength_long(price, bb)

Calculate strength of support (lower Bollinger Band).
"""
function _bb_strength_long(price::Float64, bb::NamedTuple)::Float64
    if bb.lower >= price
        return 1.0  # Touching lower band
    end

    distance_to_lower = price - bb.lower
    band_width = bb.upper - bb.lower

    if band_width == 0
        return 0.0
    end

    strength = 1.0 - (distance_to_lower / band_width)
    return max(0.0, min(1.0, strength))
end

"""
    _bb_strength_short(price, bb)

Calculate strength of resistance (upper Bollinger Band).
"""
function _bb_strength_short(price::Float64, bb::NamedTuple)::Float64
    if price >= bb.upper
        return 1.0  # Touching upper band
    end

    distance_to_upper = bb.upper - price
    band_width = bb.upper - bb.lower

    if band_width == 0
        return 0.0
    end

    strength = 1.0 - (distance_to_upper / band_width)
    return max(0.0, min(1.0, strength))
end

"""
    _mean_reversion_reasoning(direction, rsi, oversold, overbought, price, bb, conf)

Generate human-readable reasoning for the decision.
"""
function _mean_reversion_reasoning(
    direction::Symbol,
    rsi_val::Float64, oversold::Float64, overbought::Float64,
    price::Float64, bb::NamedTuple,
    confidence::Float64
)::String

    if direction == :HOLD
        return "RSI in neutral zone (no clear oversold/overbought)"
    end

    bb_width = bb.upper - bb.lower
    if direction == :LONG
        distance = price - bb.lower
    else
        distance = bb.upper - price
    end

    distance_pct = (distance / bb_width) * 100
    dir_str = direction == :LONG ? "Oversold" : "Overbought"

    return "$dir_str: RSI=$(round(rsi_val; digits=1)), Band proximity $(round(distance_pct; digits=1))%, confidence $(round(confidence; digits=2))"
end
