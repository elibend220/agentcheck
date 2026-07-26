"""
Order Flow Analysis System
Detects market microstructure patterns and high-probability entry signals.
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


class OrderFlowAnalyzer:
    """
    Analyzes order flow and market microstructure.
    Detects high-probability entry opportunities.
    """

    def __init__(self, lookback_periods: int = 50):
        self.logger = logging.getLogger("OrderFlowAnalyzer")
        self.lookback_periods = lookback_periods

        # Data buffers
        self.closes = deque(maxlen=lookback_periods)
        self.volumes = deque(maxlen=lookback_periods)
        self.highs = deque(maxlen=lookback_periods)
        self.lows = deque(maxlen=lookback_periods)

        # Calculated metrics
        self.vwap_values = deque(maxlen=lookback_periods)
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

        # VWAP = Σ(TP * Volume) / Σ(Volume)
        numerator = sum(tp * vol for tp, vol in zip(typical_prices, volumes))
        denominator = sum(volumes)

        if denominator == 0:
            return typical_prices[-1] if typical_prices else 0.0

        return numerator / denominator

    def _calculate_volume_profile(self) -> Dict[str, float]:
        """Calculate volume profile (buying vs selling pressure)"""
        if len(self.closes) < 2:
            return {'buy_vol': 0.0, 'sell_vol': 0.0}

        current_close = self.closes[-1]
        previous_close = self.closes[-2]
        current_volume = self.volumes[-1]

        # Volume estimation: if close > prev close, assume buying
        if current_close > previous_close:
            return {
                'buy_vol': current_volume * 0.6,  # Estimate 60% buying
                'sell_vol': current_volume * 0.4
            }
        else:
            return {
                'buy_vol': current_volume * 0.4,
                'sell_vol': current_volume * 0.6  # Estimate 60% selling
            }

    def detect_volume_spike(self, multiplier: float = 1.5) -> bool:
        """Detect abnormal volume (volume spike)"""
        if len(self.volumes) < 10:
            return False

        current_volume = self.volumes[-1]
        avg_volume = np.mean(list(self.volumes)[:-1])

        return current_volume > avg_volume * multiplier

    def detect_vwap_cross(self) -> Optional[str]:
        """
        Detect VWAP crossovers (bullish/bearish signals).
        Returns: LONG, SHORT, or None
        """
        if len(self.closes) < 2 or len(self.vwap_values) < 2:
            return None

        prev_close = self.closes[-2]
        current_close = self.closes[-1]
        prev_vwap = self.vwap_values[-2]
        current_vwap = self.vwap_values[-1]

        # Bullish cross: price crosses above VWAP
        if prev_close <= prev_vwap and current_close > current_vwap:
            return "LONG"

        # Bearish cross: price crosses below VWAP
        if prev_close >= prev_vwap and current_close < current_vwap:
            return "SHORT"

        return None

    def calculate_momentum(self, period: int = 5) -> float:
        """Calculate momentum indicator (-1.0 to 1.0)"""
        if len(self.closes) < period + 1:
            return 0.0

        closes_list = list(self.closes)
        current_price = closes_list[-1]
        prev_price = closes_list[-period - 1]

        if prev_price == 0:
            return 0.0

        momentum_pct = (current_price - prev_price) / prev_price

        # Clamp to [-1.0, 1.0]
        return max(-1.0, min(1.0, momentum_pct * 10))

    def detect_volume_surge_entry(self) -> Optional[str]:
        """
        Detect volume surge + price momentum for entries.
        High volume + directional momentum = high-probability entry
        """
        if len(self.closes) < 5:
            return None

        volume_spike = self.detect_volume_spike(multiplier=1.5)
        momentum = self.calculate_momentum(period=3)

        if not volume_spike:
            return None

        # Strong upward momentum + volume = bullish entry
        if momentum > 0.2:
            return "LONG"

        # Strong downward momentum + volume = bearish entry
        if momentum < -0.2:
            return "SHORT"

        return None

    def detect_supertrend_signal(self, atr_value: float) -> Optional[str]:
        """
        Simplified SuperTrend detection for entries.
        Uses high/low + ATR for trend identification.
        """
        if len(self.highs) < 2 or len(self.lows) < 2:
            return None

        current_high = self.highs[-1]
        current_low = self.lows[-1]
        prev_close = self.closes[-2] if len(self.closes) >= 2 else self.closes[-1]

        # SuperTrend Upper/Lower bands
        hl_avg = (current_high + current_low) / 2
        multiplier = 3.0  # Typical SuperTrend multiplier

        basic_ub = hl_avg + (multiplier * atr_value)
        basic_lb = hl_avg - (multiplier * atr_value)

        # If price is above basic lower band = uptrend
        if prev_close > basic_lb:
            return "LONG"

        # If price is below basic upper band = downtrend
        if prev_close < basic_ub:
            return "SHORT"

        return None

    def calculate_signal_strength(self) -> float:
        """
        Calculate overall signal strength (0.0-1.0).
        Combination of volume, momentum, and technical factors.
        """
        if len(self.closes) < 5:
            return 0.0

        factors = []

        # Volume spike factor (0-1)
        if self.detect_volume_spike(multiplier=1.5):
            factors.append(0.7)
        else:
            factors.append(0.3)

        # Momentum factor (0-1)
        momentum = self.calculate_momentum(period=3)
        momentum_strength = min(abs(momentum), 1.0)
        factors.append(momentum_strength * 0.8)

        # VWAP alignment factor (0-1)
        vwap_cross = self.detect_vwap_cross()
        if vwap_cross:
            factors.append(0.8)
        else:
            factors.append(0.4)

        return np.mean(factors) if factors else 0.0

    def analyze_order_flow(self, atr_value: float = 0.0) -> Optional[OrderFlowSignal]:
        """
        Comprehensive order flow analysis.
        Returns signal if multiple conditions align.
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

        # Need at least 2 confirmations for signal
        if confirmations < 2 or direction is None:
            return None

        strength = self.calculate_signal_strength()
        volume_spike = self.detect_volume_spike(multiplier=1.5)

        confidence = min(0.95, 0.5 + (confirmations * 0.2) + (strength * 0.2))

        return OrderFlowSignal(
            direction=direction,
            strength=strength,
            volume_spike=volume_spike,
            vwap_cross=vwap_cross is not None,
            momentum=momentum,
            confidence=confidence
        )

    def get_current_vwap(self) -> float:
        """Get current VWAP value"""
        return self.vwap_values[-1] if self.vwap_values else 0.0

    def get_support_resistance_levels(self) -> Tuple[float, float, float]:
        """
        Get support and resistance levels based on order flow.
        Returns (support, current_price, resistance)
        """
        if len(self.lows) < 20 or len(self.highs) < 20:
            current_price = self.closes[-1] if self.closes else 0.0
            return current_price, current_price, current_price

        recent_lows = list(self.lows)[-20:]
        recent_highs = list(self.highs)[-20:]
        current_price = self.closes[-1]

        support = np.percentile(recent_lows, 25)  # 25th percentile = support
        resistance = np.percentile(recent_highs, 75)  # 75th percentile = resistance

        return support, current_price, resistance

    def get_analysis_state(self) -> Dict:
        """Get current analysis state for monitoring"""
        vwap_cross = self.detect_vwap_cross()
        momentum = self.calculate_momentum(period=5)
        strength = self.calculate_signal_strength()

        return {
            'vwap_cross': vwap_cross,
            'volume_spike': self.detect_volume_spike(),
            'momentum': momentum,
            'signal_strength': strength,
            'current_vwap': self.get_current_vwap(),
            'data_points': len(self.closes)
        }
