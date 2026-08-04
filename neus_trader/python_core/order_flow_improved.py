"""
Improved Order Flow Analysis System
Phase 2: Tighter entry filters to increase Profit Factor

Key improvements:
1. Require 2+ confirmations (instead of trying extreme counts)
2. Add RSI filter (avoid extreme overbought/oversold)
3. Add trend strength validation for weaker signals
4. Stricter individual signal detection (higher volume multipliers)
5. Reduce false signals by filtering out extreme RSI conditions

Target: Improve Profit Factor from 0.92 → 1.3+
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import numpy as np


@dataclass
class OrderFlowSignal:
    """Order flow signal detection"""
    direction: str  # LONG or SHORT
    strength: float  # 0.0-1.0
    volume_spike: bool
    vwap_cross: bool
    momentum: float
    confidence: float
    signal_quality: str  # "HIGH", "MEDIUM", "LOW"


class OrderFlowAnalyzerImproved:
    """
    IMPROVED: Balanced entry signal filtering.
    Reduces false signals and improves Profit Factor.
    """

    def __init__(self, lookback_periods: int = 50):
        self.logger = logging.getLogger("OrderFlowAnalyzerImproved")
        self.lookback_periods = lookback_periods

        # Data buffers
        self.closes = deque(maxlen=lookback_periods)
        self.volumes = deque(maxlen=lookback_periods)
        self.highs = deque(maxlen=lookback_periods)
        self.lows = deque(maxlen=lookback_periods)

        # Calculated metrics
        self.vwap_values = deque(maxlen=lookback_periods)
        self.rsi_values = deque(maxlen=lookback_periods)
        self.volume_profile = deque(maxlen=lookback_periods)

    def add_candle(self, close: float, volume: float, high: float, low: float):
        """Add candle data to analyzer"""
        self.closes.append(close)
        self.volumes.append(volume)
        self.highs.append(high)
        self.lows.append(low)

        # Update VWAP
        vwap = self._calculate_vwap()
        self.vwap_values.append(vwap)

        # Calculate RSI
        rsi = self._calculate_rsi()
        self.rsi_values.append(rsi)

        # Update volume profile
        vol_profile = self._calculate_volume_profile()
        self.volume_profile.append(vol_profile)

    def _calculate_vwap(self) -> float:
        """Calculate Volume Weighted Average Price"""
        if len(self.closes) < 2:
            return self.closes[-1] if self.closes else 0.0

        typical_prices = []
        volumes = list(self.volumes)

        for i in range(len(self.closes)):
            tp = (self.highs[i] + self.lows[i] + self.closes[i]) / 3
            typical_prices.append(tp)

        numerator = sum(tp * vol for tp, vol in zip(typical_prices, volumes))
        denominator = sum(volumes)

        if denominator == 0:
            return typical_prices[-1] if typical_prices else 0.0

        return numerator / denominator

    def _calculate_rsi(self, period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        if len(self.closes) < period + 1:
            return 50.0

        closes_list = list(self.closes)
        deltas = []

        for i in range(len(closes_list) - period, len(closes_list)):
            if i > 0:
                deltas.append(closes_list[i] - closes_list[i-1])

        if not deltas:
            return 50.0

        gains = [d for d in deltas if d > 0]
        losses = [abs(d) for d in deltas if d < 0]

        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0

        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_volume_profile(self) -> Dict[str, float]:
        """Calculate volume profile (buying vs selling pressure)"""
        if len(self.closes) < 2:
            return {'buy_vol': 0.0, 'sell_vol': 0.0}

        current_close = self.closes[-1]
        previous_close = self.closes[-2]
        current_volume = self.volumes[-1]

        if current_close > previous_close:
            return {
                'buy_vol': current_volume * 0.6,
                'sell_vol': current_volume * 0.4
            }
        else:
            return {
                'buy_vol': current_volume * 0.4,
                'sell_vol': current_volume * 0.6
            }

    def detect_volume_spike(self, multiplier: float = 2.0) -> bool:
        """
        IMPROVED: Stricter volume spike detection
        Reduces false signals from normal volatility
        """
        if len(self.volumes) < 20:
            return False

        current_volume = self.volumes[-1]
        # Use 20-period average, excluding current
        avg_volume = np.mean(list(self.volumes)[:-1][-20:])

        return current_volume > avg_volume * multiplier

    def detect_vwap_cross(self) -> Optional[str]:
        """Detect VWAP crossovers (bullish/bearish signals)"""
        if len(self.closes) < 2 or len(self.vwap_values) < 2:
            return None

        prev_close = self.closes[-2]
        current_close = self.closes[-1]
        prev_vwap = self.vwap_values[-2]
        current_vwap = self.vwap_values[-1]

        if prev_close <= prev_vwap and current_close > current_vwap:
            return "LONG"

        if prev_close >= prev_vwap and current_close < current_vwap:
            return "SHORT"

        return None

    def calculate_momentum(self, period: int = 5) -> float:
        """
        IMPROVED: Stronger momentum requirement
        Must show sustained momentum, not just spike
        """
        if len(self.closes) < period + 1:
            return 0.0

        closes_list = list(self.closes)
        current_price = closes_list[-1]
        prev_price = closes_list[-period - 1]

        if prev_price == 0:
            return 0.0

        momentum_pct = (current_price - prev_price) / prev_price
        return max(-1.0, min(1.0, momentum_pct * 10))

    def detect_volume_surge_entry(self) -> Optional[str]:
        """Detect volume surge + price momentum for entries"""
        if len(self.closes) < 5:
            return None

        # IMPROVED: Require 2.0x volume spike
        volume_spike = self.detect_volume_spike(multiplier=2.0)
        momentum = self.calculate_momentum(period=3)

        if not volume_spike:
            return None

        # IMPROVED: Require strong momentum
        if momentum > 0.3:
            return "LONG"

        if momentum < -0.3:
            return "SHORT"

        return None

    def detect_supertrend_signal(self, atr_value: float) -> Optional[str]:
        """
        IMPROVED SuperTrend detection.
        Requires sustained trend, not just one candle.
        """
        if len(self.highs) < 3 or len(self.lows) < 3:
            return None

        current_high = self.highs[-1]
        current_low = self.lows[-1]
        prev_close = self.closes[-2] if len(self.closes) >= 2 else self.closes[-1]
        prev_prev_close = self.closes[-3] if len(self.closes) >= 3 else self.closes[-1]

        hl_avg = (current_high + current_low) / 2
        multiplier = 3.0

        basic_ub = hl_avg + (multiplier * atr_value)
        basic_lb = hl_avg - (multiplier * atr_value)

        # IMPROVED: Require trend for last 2 candles
        if prev_close > basic_lb and prev_prev_close > basic_lb:
            return "LONG"

        if prev_close < basic_ub and prev_prev_close < basic_ub:
            return "SHORT"

        return None

    def calculate_signal_strength(self) -> float:
        """
        Calculate overall signal strength (0.0-1.0).
        More conservative calculation.
        """
        if len(self.closes) < 5:
            return 0.0

        factors = []

        # Volume spike factor (0-1)
        if self.detect_volume_spike(multiplier=2.0):
            factors.append(0.8)
        else:
            factors.append(0.2)

        # Momentum factor (0-1)
        momentum = self.calculate_momentum(period=3)
        momentum_strength = min(abs(momentum), 1.0)
        factors.append(momentum_strength * 0.7)

        # VWAP alignment factor (0-1)
        vwap_cross = self.detect_vwap_cross()
        if vwap_cross:
            factors.append(0.9)
        else:
            factors.append(0.2)

        return np.mean(factors) if factors else 0.0

    def is_rsi_valid_for_entry(self, direction: str) -> bool:
        """
        NEW: Filter out extreme overbought/oversold entries
        Avoid buying at top, selling at bottom
        """
        if len(self.rsi_values) == 0:
            return True

        rsi = self.rsi_values[-1]

        # Avoid extreme conditions
        return 20 <= rsi <= 80

    def is_trend_strong(self) -> bool:
        """NEW: Ensure trend is strong before entering"""
        if len(self.closes) < 10:
            return False

        closes_list = list(self.closes)
        price_10_ago = closes_list[-10]
        current_price = closes_list[-1]

        price_change_pct = abs((current_price - price_10_ago) / price_10_ago)

        # Require at least 0.5% move in last 10 candles
        return price_change_pct > 0.005

    def analyze_order_flow(self, atr_value: float = 0.0) -> Optional[OrderFlowSignal]:
        """
        IMPROVED: Comprehensive order flow analysis with balanced filters.
        Returns signal only for quality entries with 2+ confirmations.
        """
        if len(self.closes) < 5:
            return None

        # Check individual signals
        vwap_cross = self.detect_vwap_cross()
        volume_surge = self.detect_volume_surge_entry()
        supertrend = self.detect_supertrend_signal(atr_value)
        momentum = self.calculate_momentum(period=5)

        # Count confirmations
        confirmations = 0
        direction = None
        signal_quality = "LOW"

        # VWAP confirmation
        if vwap_cross == "LONG":
            confirmations += 1
            direction = "LONG"
        elif vwap_cross == "SHORT":
            confirmations += 1
            direction = "SHORT"

        # Volume surge confirmation
        if volume_surge == "LONG":
            confirmations += 1
            direction = "LONG"
        elif volume_surge == "SHORT":
            confirmations += 1
            direction = "SHORT"

        # SuperTrend confirmation
        if supertrend == "LONG":
            confirmations += 1
            direction = "LONG"
        elif supertrend == "SHORT":
            confirmations += 1
            direction = "SHORT"

        # IMPROVED: Require at least 2 confirmations (balanced)
        if confirmations < 2 or direction is None:
            return None

        # NEW: RSI filter - avoid extreme overbought/oversold
        rsi = self.get_current_rsi()
        if rsi <= 20 or rsi >= 80:
            return None

        # NEW: For 2-confirmation signals, require trend strength
        if confirmations == 2 and not self.is_trend_strong():
            return None

        # Calculate metrics
        strength = self.calculate_signal_strength()
        volume_spike = self.detect_volume_spike(multiplier=2.0)

        # Confidence calculation
        confidence = min(0.95, 0.4 + (confirmations * 0.15) + (strength * 0.15))

        # Determine signal quality
        if confirmations >= 3 and strength > 0.7 and volume_spike:
            signal_quality = "HIGH"
        elif confirmations >= 3:
            signal_quality = "MEDIUM"
        else:
            signal_quality = "LOW"

        return OrderFlowSignal(
            direction=direction,
            strength=strength,
            volume_spike=volume_spike,
            vwap_cross=vwap_cross is not None,
            momentum=momentum,
            confidence=confidence,
            signal_quality=signal_quality
        )

    def get_current_vwap(self) -> float:
        """Get current VWAP value"""
        return self.vwap_values[-1] if self.vwap_values else 0.0

    def get_current_rsi(self) -> float:
        """Get current RSI value"""
        return self.rsi_values[-1] if self.rsi_values else 50.0
