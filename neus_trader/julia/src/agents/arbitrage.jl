"""
Arbitrage Agent - Detects cross-venue price discrepancies.
"""

"""
    ArbitrageAgent

Configuration for Arbitrage Agent.
"""
struct ArbitrageAgent
    venue_1::Symbol             # :binance
    venue_2::Symbol             # :coinbase
    spread_threshold::Float64   # 0.002 (0.2%)
end

"""
    analyze(agent::ArbitrageAgent, candles::DataFrame, prices::Dict)::Decision

Analyze cross-venue arbitrage opportunities.

Logic:
1. Monitor prices on two venues
2. Calculate spread: (price_venue1 - price_venue2) / avg_price
3. LONG if venue_1 cheaper (buy there, sell on venue_2)
4. SHORT if venue_2 cheaper (buy there, sell on venue_1)
5. Confidence based on spread size relative to threshold

Note: This is a simplified implementation for Phase 2.1
In production, would connect to real exchange APIs.
"""
function analyze(agent::ArbitrageAgent, candles::DataFrame, prices::Dict)::Decision
    # Check if we have prices for both venues
    venue_1_price = get(prices, agent.venue_1, nothing)
    venue_2_price = get(prices, agent.venue_2, nothing)

    if isnothing(venue_1_price) || isnothing(venue_2_price)
        return Decision(
            :arbitrage,
            :HOLD,
            0.0,
            "Missing price data for one or both venues",
            now()
        )
    end

    # Calculate spread
    avg_price = (venue_1_price + venue_2_price) / 2.0
    spread_pct = abs(venue_1_price - venue_2_price) / avg_price

    # Determine direction
    if spread_pct < agent.spread_threshold
        return Decision(
            :arbitrage,
            :HOLD,
            0.0,
            "Spread $(round(spread_pct * 100; digits=3))% below threshold $(round(agent.spread_threshold * 100; digits=2))%",
            now()
        )
    end

    if venue_1_price < venue_2_price
        direction = :LONG  # Cheaper on venue_1
    else
        direction = :SHORT  # Cheaper on venue_2
    end

    # Confidence based on spread magnitude
    confidence = min(1.0, spread_pct / (agent.spread_threshold * 2))
    confidence = max(0.5, confidence)

    reasoning = _arbitrage_reasoning(
        direction, agent.venue_1, agent.venue_2,
        venue_1_price, venue_2_price, spread_pct, confidence
    )

    return Decision(:arbitrage, direction, confidence, reasoning, now())
end

"""
    _arbitrage_reasoning(direction, v1, v2, price1, price2, spread, conf)

Generate human-readable reasoning for the decision.
"""
function _arbitrage_reasoning(
    direction::Symbol,
    venue_1::Symbol, venue_2::Symbol,
    price_1::Float64, price_2::Float64,
    spread_pct::Float64,
    confidence::Float64
)::String

    spread_pct_display = round(spread_pct * 100; digits=3)
    cheaper = direction == :LONG ? venue_1 : venue_2
    expensive = direction == :LONG ? venue_2 : venue_1

    return "Arbitrage: $cheaper cheaper by $(spread_pct_display)%, buy $cheaper sell $expensive, confidence $(round(confidence; digits=2))"
end
