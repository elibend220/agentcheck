"""
Institutional Flow Detector

Identifies institutional trading activity through:
- Volume profile analysis
- Order accumulation patterns
- Smart money indicators
- Micro-structure patterns
- Unusual volume/price movements
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
import numpy as np


@dataclass
class InstitutionalSignal:
    """Institutional flow detection signal"""
    timestamp: datetime
    flow_type: str  # 'accumulation', 'distribution', 'neutral'
    confidence: float  # 0-1
    volume_score: float  # 0-1, based on volume spike
    price_score: float  # 0-1, based on price movement efficiency
    accumulation_score: float  # 0-1, buying pressure
    distribution_score: float  # 0-1, selling pressure
    entry_signal: bool  # Should we enter?
    exit_signal: bool  # Should we exit?
    reason: str


class InstitutionalFlowDetector:
    """
    Detects institutional buying/selling activity.

    Key indicators:
    - Volume accumulation (large volume on small price moves)
    - Price absorption (price doesn't fall much despite volume)
    - Momentum divergence (volume increasing while price consolidates)
    - Unusual volume profile (deviation from normal patterns)
    """

    def __init__(self, symbol: str = 'ETHUSDT'):
        self.symbol = symbol

        # History for analysis
        self.volumes: List[float] = []
        self.close_prices: List[float] = []
        self.high_prices: List[float] = []
        self.low_prices: List[float] = []
        self.timestamps: List[datetime] = []

        # Statistics (updated rolling)
        self.avg_volume = 0.0
        self.std_volume = 0.0
        self.avg_range = 0.0  # Average High-Low range
        self.volume_zscore = 0.0

        # Detection thresholds
        self.volume_surge_threshold = 1.5  # X times average volume
        self.price_efficiency_threshold = 0.4  # How efficiently price moved relative to volume
        self.accumulation_window = 20  # Candles to look back for accumulation

    def _update_statistics(self):
        """Update rolling statistics"""
        if len(self.volumes) < 20:
            return

        recent_volumes = self.volumes[-20:]
        self.avg_volume = np.mean(recent_volumes)
        self.std_volume = np.std(recent_volumes)

        recent_ranges = [
            high - low for high, low in
            zip(self.high_prices[-20:], self.low_prices[-20:])
        ]
        self.avg_range = np.mean(recent_ranges)

    def _detect_volume_surge(self, volume: float) -> float:
        """
        Detect unusual volume spike (0-1 score).

        Institutional activity often shows:
        - Sudden volume increase
        - Volume stays elevated
        - Price doesn't react proportionally
        """
        if self.avg_volume == 0:
            return 0.0

        # Calculate Z-score
        if self.std_volume > 0:
            zscore = (volume - self.avg_volume) / self.std_volume
            zscore = min(zscore, 5.0)  # Cap at 5 std devs
        else:
            zscore = (volume - self.avg_volume) / (self.avg_volume + 0.001)

        # Convert to 0-1 score
        score = min(zscore / 3.0, 1.0)  # 3 sigma = 1.0
        return max(0.0, score)

    def _detect_price_efficiency(self, high: float, low: float, close: float, volume: float) -> float:
        """
        Detect price absorption (0-1 score).

        Smart money characteristics:
        - Large volume but small price movement
        - Absorption of selling without falling
        - Continuation despite supply
        """
        if len(self.close_prices) == 0 or volume == 0:
            return 0.0

        prev_close = self.close_prices[-1]
        price_move = abs(close - prev_close)
        intrabar_range = high - low

        # Efficiency = price move / volume * price
        # Low efficiency = price didn't move much despite large volume
        if intrabar_range == 0:
            intrabar_range = 0.001

        # Price didn't fall much = good efficiency
        low_efficiency = 1.0 - min(price_move / intrabar_range, 1.0)

        # Volume was large relative to range
        volume_efficient = self._detect_volume_surge(volume)

        # Combined: volume was large AND price didn't fall much
        efficiency_score = (low_efficiency * 0.6 + volume_efficient * 0.4)
        return min(efficiency_score, 1.0)

    def _detect_accumulation(self) -> float:
        """
        Detect accumulation phase (0-1 score).

        Characteristics:
        - Rising volume
        - Consolidating/rising price
        - Decreasing volatility
        - Absorption of supply
        """
        if len(self.close_prices) < self.accumulation_window:
            return 0.0

        window = self.accumulation_window
        recent_closes = self.close_prices[-window:]
        recent_volumes = self.volumes[-window:]

        # Check volume trend (increasing = positive)
        volume_trend = recent_volumes[-1] - np.mean(recent_volumes[:-1])
        volume_trend_score = min(volume_trend / (self.avg_volume + 0.001), 1.0)

        # Check price trend (should be flat to up)
        price_trend = (recent_closes[-1] - recent_closes[0]) / recent_closes[0]
        price_trend_score = max(0.0, min(price_trend * 100, 1.0))  # Up trend good

        # Check volatility (should be low)
        volatility = np.std(recent_closes) / np.mean(recent_closes)
        volatility_score = max(0.0, 1.0 - volatility)

        # Accumulation = high volume + flat/up price + low volatility
        accumulation = (
            volume_trend_score * 0.4 +
            price_trend_score * 0.3 +
            volatility_score * 0.3
        )

        return min(accumulation, 1.0)

    def _detect_distribution(self) -> float:
        """
        Detect distribution phase (0-1 score).

        Characteristics:
        - High volume
        - Declining price
        - Increased volatility
        - Weakness despite volume
        """
        if len(self.close_prices) < self.accumulation_window:
            return 0.0

        window = self.accumulation_window
        recent_closes = self.close_prices[-window:]
        recent_volumes = self.volumes[-window:]

        # Check volume (should be high)
        volume_score = self._detect_volume_surge(recent_volumes[-1])

        # Check price trend (should be down)
        price_trend = (recent_closes[-1] - recent_closes[0]) / recent_closes[0]
        price_trend_score = max(0.0, 1.0 - min(price_trend * 100, 1.0))  # Down trend bad

        # Check volatility (should be increasing = weakness)
        volatility = np.std(recent_closes) / np.mean(recent_closes)
        volatility_score = min(volatility * 5, 1.0)

        # Distribution = high volume + down price + high volatility
        distribution = (
            volume_score * 0.4 +
            price_trend_score * 0.3 +
            volatility_score * 0.3
        )

        return min(distribution, 1.0)

    def _detect_smart_money_absorption(self) -> float:
        """
        Detect if smart money is absorbing supply.

        Smart money signature:
        - Price doesn't fall despite high volume
        - Volume spikes on intrabar lows
        - Quick recovery from lows
        """
        if len(self.volumes) < 3:
            return 0.0

        # Get last candle
        volume = self.volumes[-1]
        high = self.high_prices[-1]
        low = self.low_prices[-1]
        close = self.close_prices[-1]

        # Absorption signals
        volume_high = self._detect_volume_surge(volume)

        # Price closed near high (absorption)
        close_range = (close - low) / (high - low + 0.001)
        close_range = min(close_range, 1.0)

        # Range expansion (volatility)
        if len(self.high_prices) > 1:
            prev_range = self.high_prices[-2] - self.low_prices[-2]
            current_range = high - low
            range_expansion = min(current_range / (prev_range + 0.001), 2.0)
        else:
            range_expansion = 1.0

        # Absorption = high volume + close near high + range expansion
        absorption = (
            volume_high * 0.4 +
            close_range * 0.4 +
            min(range_expansion / 2.0, 1.0) * 0.2
        )

        return min(absorption, 1.0)

    def process_candle(self, candle: Dict) -> Optional[InstitutionalSignal]:
        """
        Process OHLCV candle and detect institutional activity.

        Returns:
            InstitutionalSignal with entry/exit recommendations
        """
        timestamp = candle.get('timestamp', datetime.utcnow())
        open_price = candle.get('open', 0)
        high = candle.get('high', 0)
        low = candle.get('low', 0)
        close = candle.get('close', 0)
        volume = candle.get('volume', 0)

        # Store history
        self.timestamps.append(timestamp)
        self.high_prices.append(high)
        self.low_prices.append(low)
        self.close_prices.append(close)
        self.volumes.append(volume)

        # Keep only last 100 candles in memory
        max_history = 100
        if len(self.close_prices) > max_history:
            self.timestamps.pop(0)
            self.high_prices.pop(0)
            self.low_prices.pop(0)
            self.close_prices.pop(0)
            self.volumes.pop(0)

        # Update statistics
        self._update_statistics()

        # Don't analyze until we have enough history
        if len(self.close_prices) < 5:
            return None

        # Calculate scores
        volume_score = self._detect_volume_surge(volume)
        price_score = self._detect_price_efficiency(high, low, close, volume)
        accumulation_score = self._detect_accumulation()
        distribution_score = self._detect_distribution()
        absorption_score = self._detect_smart_money_absorption()

        # Determine flow type
        if accumulation_score > distribution_score:
            flow_type = 'accumulation'
            directional_score = accumulation_score
        elif distribution_score > accumulation_score:
            flow_type = 'distribution'
            directional_score = distribution_score
        else:
            flow_type = 'neutral'
            directional_score = 0.0

        # Overall confidence
        confidence = (
            volume_score * 0.2 +
            price_score * 0.2 +
            directional_score * 0.4 +
            absorption_score * 0.2
        )

        # Entry/Exit signals
        entry_signal = False
        exit_signal = False
        reason = ""

        if confidence > 0.6:
            if flow_type == 'accumulation' and accumulation_score > 0.6:
                entry_signal = True
                reason = f"Institutional accumulation detected (confidence: {confidence:.1%})"
            elif flow_type == 'distribution' and distribution_score > 0.6:
                exit_signal = True
                reason = f"Institutional distribution detected (confidence: {confidence:.1%})"

        # Additional signal: strong absorption
        if absorption_score > 0.7 and volume_score > 0.6:
            entry_signal = True
            reason = f"Smart money absorption detected (absorption: {absorption_score:.1%})"

        signal = InstitutionalSignal(
            timestamp=timestamp,
            flow_type=flow_type,
            confidence=confidence,
            volume_score=volume_score,
            price_score=price_score,
            accumulation_score=accumulation_score,
            distribution_score=distribution_score,
            entry_signal=entry_signal,
            exit_signal=exit_signal,
            reason=reason
        )

        return signal

    def get_flow_state(self) -> Dict:
        """Get current institutional flow state"""
        if len(self.close_prices) == 0:
            return {'status': 'initializing'}

        accumulation = self._detect_accumulation()
        distribution = self._detect_distribution()
        absorption = self._detect_smart_money_absorption()

        if accumulation > distribution:
            state = 'accumulation'
        elif distribution > accumulation:
            state = 'distribution'
        else:
            state = 'neutral'

        return {
            'state': state,
            'accumulation_score': accumulation,
            'distribution_score': distribution,
            'absorption_score': absorption,
            'avg_volume': self.avg_volume,
            'current_volume': self.volumes[-1] if self.volumes else 0,
            'volume_surge': self._detect_volume_surge(self.volumes[-1] if self.volumes else 0),
        }
