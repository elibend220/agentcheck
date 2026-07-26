"""
Technical indicator library for agent analysis.
All indicators operate on DataFrame with OHLCV data.
"""

"""
    ema(prices::Vector{Float64}, period::Int)::Float64

Exponential Moving Average.
Returns current EMA value.
"""
function ema(prices::Vector{Float64}, period::Int)::Float64
    if length(prices) < period
        return NaN
    end

    alpha = 2.0 / (period + 1)
    ema_val = mean(prices[1:period])

    for i in (period+1):length(prices)
        ema_val = alpha * prices[i] + (1 - alpha) * ema_val
    end

    return ema_val
end

"""
    rsi(prices::Vector{Float64}, period::Int)::Float64

Relative Strength Index (Wilder's method).
Returns RSI value 0-100.
"""
function rsi(prices::Vector{Float64}, period::Int)::Float64
    if length(prices) < period + 1
        return NaN
    end

    deltas = diff(prices)
    gains = zeros(length(deltas))
    losses = zeros(length(deltas))

    for i in 1:length(deltas)
        if deltas[i] > 0
            gains[i] = deltas[i]
        else
            losses[i] = -deltas[i]
        end
    end

    avg_gain = mean(gains[1:period])
    avg_loss = mean(losses[1:period])

    for i in (period+1):length(gains)
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    end

    if avg_loss == 0
        return avg_gain == 0 ? 50.0 : 100.0
    end

    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))
end

"""
    macd(prices::Vector{Float64}, fast::Int, slow::Int, signal::Int)::NamedTuple

MACD (Moving Average Convergence Divergence).
Returns (macd=value, signal=line, histogram=macd-signal).
"""
function macd(prices::Vector{Float64}, fast::Int=12, slow::Int=26, signal::Int=9)
    if length(prices) < slow + signal - 1
        return (macd=NaN, signal=NaN, histogram=NaN)
    end

    ema_fast_val = ema(prices, fast)
    ema_slow_val = ema(prices, slow)
    macd_val = ema_fast_val - ema_slow_val

    # Calculate signal line as EMA of MACD
    # Simplified: use recent MACD values
    macd_series = Float64[]
    for i in slow:length(prices)
        ema_f = ema(prices[1:i], fast)
        ema_s = ema(prices[1:i], slow)
        push!(macd_series, ema_f - ema_s)
    end

    if length(macd_series) < signal
        signal_val = mean(macd_series)
    else
        signal_val = ema(macd_series, signal)
    end

    histogram = macd_val - signal_val

    return (macd=macd_val, signal=signal_val, histogram=histogram)
end

"""
    bollinger_bands(prices::Vector{Float64}, period::Int, std_dev::Float64)::NamedTuple

Bollinger Bands (upper, middle, lower).
Returns (upper=value, middle=sma, lower=value).
"""
function bollinger_bands(prices::Vector{Float64}, period::Int=20, std_dev::Float64=2.0)
    if length(prices) < period
        return (upper=NaN, middle=NaN, lower=NaN)
    end

    sma = mean(prices[end-period+1:end])
    std = std(prices[end-period+1:end])

    upper = sma + std_dev * std
    lower = sma - std_dev * std

    return (upper=upper, middle=sma, lower=lower)
end

"""
    atr(candles::DataFrame, period::Int)::Float64

Average True Range.
Requires DataFrame with high, low, close columns.
Returns ATR value.
"""
function atr(candles::DataFrame, period::Int=14)
    if nrow(candles) < period + 1
        return NaN
    end

    n = nrow(candles)
    true_ranges = zeros(n)

    true_ranges[1] = candles[1, :high] - candles[1, :low]

    for i in 2:n
        high_low = candles[i, :high] - candles[i, :low]
        high_close = abs(candles[i, :high] - candles[i-1, :close])
        low_close = abs(candles[i, :low] - candles[i-1, :close])
        true_ranges[i] = max(high_low, high_close, low_close)
    end

    return mean(true_ranges[end-period+1:end])
end

"""
    keltner_channels(candles::DataFrame, period::Int, atr_mult::Float64)::NamedTuple

Keltner Channels (upper, middle, lower).
Returns (upper=value, middle=ema, lower=value).
"""
function keltner_channels(candles::DataFrame, period::Int=20, atr_mult::Float64=2.0)
    if nrow(candles) < period + 1
        return (upper=NaN, middle=NaN, lower=NaN)
    end

    closes = candles[!, :close]
    ema_val = ema(closes, period)
    atr_val = atr(candles, period)

    upper = ema_val + atr_mult * atr_val
    lower = ema_val - atr_mult * atr_val

    return (upper=upper, middle=ema_val, lower=lower)
end

"""
    sma(prices::Vector{Float64}, period::Int)::Float64

Simple Moving Average.
Returns current SMA value.
"""
function sma(prices::Vector{Float64}, period::Int)::Float64
    if length(prices) < period
        return NaN
    end
    return mean(prices[end-period+1:end])
end
