"""
Market Hour Detection System
Identifies optimal trading windows based on historical volatility patterns.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from enum import Enum


class TradingSession(Enum):
    """Major market sessions"""
    ASIAN = "asian"  # 0:00-13:00 UTC
    LONDON = "london"  # 13:00-17:00 UTC (best for ETH scalping)
    US = "us"  # 17:00-21:00 UTC
    US_CLOSE = "us_close"  # 20:00-23:00 UTC (high volatility)
    OVERNIGHT = "overnight"  # 23:00-0:00 UTC


class MarketHourDetector:
    """
    Detects current market session and volatility characteristics.
    Optimizes for ETH scalping during high-liquidity windows.
    """

    # Win rate and volatility by session (from research)
    SESSION_PROFILES = {
        TradingSession.ASIAN: {
            'win_rate': 0.35,
            'volatility': 0.4,
            'liquidity': 0.6,
            'spreads': 8,  # bps
            'active': False  # Not recommended for scalping
        },
        TradingSession.LONDON: {
            'win_rate': 0.65,  # 65% - BEST
            'volatility': 0.8,
            'liquidity': 0.95,
            'spreads': 2,  # bps
            'active': True
        },
        TradingSession.US: {
            'win_rate': 0.60,
            'volatility': 1.0,
            'liquidity': 0.90,
            'spreads': 2,  # bps
            'active': True
        },
        TradingSession.US_CLOSE: {
            'win_rate': 0.60,  # 60% - GOOD
            'volatility': 1.2,
            'liquidity': 0.85,
            'spreads': 3,  # bps
            'active': True
        },
        TradingSession.OVERNIGHT: {
            'win_rate': 0.40,
            'volatility': 0.3,
            'liquidity': 0.5,
            'spreads': 10,  # bps
            'active': False
        }
    }

    def __init__(self):
        self.logger = logging.getLogger("MarketHourDetector")

    def get_current_session(self, timestamp: Optional[datetime] = None) -> TradingSession:
        """Get current market session based on UTC time"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        hour = timestamp.hour

        if hour < 13:
            return TradingSession.ASIAN
        elif hour < 17:
            return TradingSession.LONDON
        elif hour < 20:
            return TradingSession.US
        elif hour < 23:
            return TradingSession.US_CLOSE
        else:
            return TradingSession.OVERNIGHT

    def is_prime_trading_hour(self, timestamp: Optional[datetime] = None) -> bool:
        """Check if current time is within prime trading window"""
        session = self.get_current_session(timestamp)

        # London + US high volatility hours are prime
        if session in [TradingSession.LONDON, TradingSession.US_CLOSE]:
            return True

        return False

    def get_session_profile(self, session: TradingSession) -> Dict:
        """Get profile for a market session"""
        return self.SESSION_PROFILES.get(session, {})

    def get_hours_until_prime(self, timestamp: Optional[datetime] = None) -> int:
        """Hours until next prime trading window"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        hour = timestamp.hour

        # If already in prime window
        if 13 <= hour < 17 or 20 <= hour < 23:
            return 0

        # Hours until London open (13:00 UTC)
        if hour < 13:
            return 13 - hour

        # Hours until US close high volatility (20:00 UTC)
        if 17 <= hour < 20:
            return 20 - hour

        # Hours until next London open
        hours_to_midnight = 24 - hour
        hours_to_london = hours_to_midnight + 13
        return hours_to_london

    def should_trade(self, timestamp: Optional[datetime] = None, require_prime: bool = False) -> bool:
        """
        Determine if trading should be active.

        Args:
            timestamp: UTC datetime to check
            require_prime: If True, only trade during prime hours
        """
        session = self.get_current_session(timestamp)
        profile = self.get_session_profile(session)

        if require_prime:
            return self.is_prime_trading_hour(timestamp)

        return profile.get('active', False)

    def get_expected_win_rate(self, session: TradingSession) -> float:
        """Expected win rate for a session"""
        return self.SESSION_PROFILES[session]['win_rate']

    def get_session_volatility_factor(self, session: TradingSession) -> float:
        """Volatility multiplier for position sizing"""
        return self.SESSION_PROFILES[session]['volatility']

    def get_best_trading_window_today(self) -> Tuple[int, int]:
        """
        Return (start_hour, end_hour) for best trading window today.
        Based on research: London (13-17 UTC) is best for ETH scalping.
        """
        return (13, 17)  # 13:00-17:00 UTC

    def get_high_volatility_windows(self) -> list:
        """Get all high volatility windows (for scalping)"""
        return [
            {'session': TradingSession.LONDON, 'start': 13, 'end': 17},
            {'session': TradingSession.US_CLOSE, 'start': 20, 'end': 23}
        ]

    def minutes_in_current_session(self, timestamp: Optional[datetime] = None) -> int:
        """Minutes elapsed in current session"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        hour = timestamp.hour
        minute = timestamp.minute

        if hour < 13:
            # Asian session start (0:00)
            elapsed = hour * 60 + minute
        elif hour < 17:
            # London session start (13:00)
            elapsed = (hour - 13) * 60 + minute
        elif hour < 20:
            # US session start (17:00)
            elapsed = (hour - 17) * 60 + minute
        elif hour < 23:
            # US Close session start (20:00)
            elapsed = (hour - 20) * 60 + minute
        else:
            # Overnight session start (23:00)
            elapsed = (hour - 23) * 60 + minute

        return elapsed

    def get_session_time_remaining(self, session: TradingSession, timestamp: Optional[datetime] = None) -> int:
        """Minutes remaining in session"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Session durations
        durations = {
            TradingSession.ASIAN: 13 * 60,      # 13 hours
            TradingSession.LONDON: 4 * 60,      # 4 hours
            TradingSession.US: 3 * 60,          # 3 hours
            TradingSession.US_CLOSE: 3 * 60,    # 3 hours
            TradingSession.OVERNIGHT: 1 * 60    # 1 hour
        }

        current_session = self.get_current_session(timestamp)

        if current_session == session:
            elapsed = self.minutes_in_current_session(timestamp)
            duration = durations[session]
            return max(0, duration - elapsed)

        return 0

    def get_market_state(self, timestamp: Optional[datetime] = None) -> Dict:
        """Get comprehensive market state for decision making"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        session = self.get_current_session(timestamp)
        profile = self.get_session_profile(session)

        return {
            'session': session.value,
            'is_trading_active': profile.get('active', False),
            'is_prime_hour': self.is_prime_trading_hour(timestamp),
            'expected_win_rate': profile.get('win_rate', 0.5),
            'volatility_factor': profile.get('volatility', 0.5),
            'liquidity': profile.get('liquidity', 0.5),
            'typical_spreads_bps': profile.get('spreads', 5),
            'minutes_in_session': self.minutes_in_current_session(timestamp),
            'hours_until_prime': self.get_hours_until_prime(timestamp)
        }

    def log_market_status(self, timestamp: Optional[datetime] = None):
        """Log market status for monitoring"""
        state = self.get_market_state(timestamp)
        self.logger.info(
            f"Market Session: {state['session']} | "
            f"Active: {state['is_trading_active']} | "
            f"Prime: {state['is_prime_hour']} | "
            f"Expected Win Rate: {state['expected_win_rate']:.0%} | "
            f"Volatility Factor: {state['volatility_factor']:.1f}x"
        )
