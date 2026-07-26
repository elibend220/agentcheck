"""
Adaptive Risk Management System
Dynamically adjusts position sizing and risk based on market conditions and performance
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime
import numpy as np


@dataclass
class RiskMetrics:
    """Current risk state"""
    volatility: float  # Current market volatility (%)
    current_drawdown: float  # Current drawdown (%)
    win_rate: float  # Recent win rate (0-1)
    consecutive_losses: int  # Number of consecutive losses
    recent_pnl: List[float]  # Recent trade P&L
    equity_peak: float  # Peak equity
    current_equity: float  # Current equity


@dataclass
class RiskParams:
    """Adaptive risk parameters"""
    position_size: float  # In USDT
    risk_per_trade: float  # Risk as % of capital
    kelly_fraction: float  # Kelly criterion fraction (0.25 = conservative)
    stop_loss_pct: float  # Stop loss distance (%)
    take_profit_pct: float  # Take profit distance (%)
    max_positions: int  # Maximum open positions
    daily_loss_limit: float  # Daily loss limit in USDT


class AdaptiveRiskManager:
    """
    Manages dynamic risk allocation based on market regime and performance.
    Implements multi-dimensional risk adjustment.
    """

    def __init__(
        self,
        initial_capital: float = 10000.0,
        base_risk_per_trade: float = 0.015,  # 1.5%
        kelly_fraction: float = 0.25,
        max_consecutive_losses: int = 3
    ):
        self.logger = logging.getLogger("AdaptiveRiskManager")

        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.base_risk_per_trade = base_risk_per_trade
        self.kelly_fraction = kelly_fraction
        self.max_consecutive_losses = max_consecutive_losses

        # Risk history
        self.trade_history: List[Dict] = []
        self.equity_history: List[float] = [initial_capital]
        self.volatility_history: List[float] = []

        # Current metrics
        self.peak_equity = initial_capital
        self.consecutive_losses = 0
        self.recent_win_rate = 0.5  # Start neutral

    def update_performance(self, pnl: float, trade_price: float, stop_loss: float, take_profit: float):
        """Record trade performance and update metrics"""
        self.current_capital += pnl
        self.equity_history.append(self.current_capital)

        # Update peak
        if self.current_capital > self.peak_equity:
            self.peak_equity = self.current_capital
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1 if pnl < 0 else 0

        # Track trade
        self.trade_history.append({
            'timestamp': datetime.utcnow(),
            'pnl': pnl,
            'price': trade_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit
        })

        # Update win rate (last 20 trades)
        recent_trades = self.trade_history[-20:]
        if recent_trades:
            winning = sum(1 for t in recent_trades if t['pnl'] > 0)
            self.recent_win_rate = winning / len(recent_trades)

        self.logger.info(
            f"Performance update: Capital=${self.current_capital:.2f}, "
            f"Win rate={self.recent_win_rate:.2%}, "
            f"Consecutive losses={self.consecutive_losses}"
        )

    def calculate_volatility(self, returns: List[float]) -> float:
        """Calculate volatility from returns"""
        if len(returns) < 2:
            return 1.0  # Default 1% volatility
        return float(np.std(returns) * 100)  # As percentage

    def get_current_drawdown(self) -> float:
        """Calculate current drawdown"""
        if not self.equity_history or len(self.equity_history) < 2:
            return 0.0

        peak = max(self.equity_history)
        current = self.equity_history[-1]

        if peak == 0:
            return 0.0

        return (current - peak) / peak * 100

    def calculate_adaptive_position_size(
        self,
        volatility: float,
        win_rate: float = None,
        max_position_capital: float = 0.05
    ) -> float:
        """
        Calculate position size adapting to market conditions.

        Factors:
        - Volatility regime (higher volatility = smaller position)
        - Win rate (lower win rate = smaller position)
        - Drawdown (deeper drawdown = smaller position)
        - Consecutive losses (more losses = smaller position)
        """
        if win_rate is None:
            win_rate = self.recent_win_rate

        drawdown = abs(self.get_current_drawdown())

        # Base position from capital
        base_position = self.current_capital * max_position_capital

        # Volatility adjustment (inverse relationship)
        volatility_factor = 1.0 / (1.0 + volatility / 10.0)

        # Win rate adjustment
        win_rate_factor = min(win_rate * 2.0, 1.0)  # Cap at 1.0

        # Drawdown adjustment (reduces position as drawdown increases)
        drawdown_factor = max(1.0 - (drawdown / 100.0), 0.3)  # Min 30%

        # Consecutive losses penalty
        loss_penalty = max(1.0 - (self.consecutive_losses * 0.2), 0.4)  # Min 40%

        # Combined adjustment
        adjustment = volatility_factor * win_rate_factor * drawdown_factor * loss_penalty

        position_size = base_position * adjustment

        return max(position_size, 50.0)  # Minimum $50

    def calculate_risk_per_trade(self) -> float:
        """
        Calculate dynamic risk per trade based on conditions.
        Base: 1.5% of capital
        Adjusted by: win rate, drawdown, volatility
        """
        drawdown = abs(self.get_current_drawdown())

        # Reduce risk during losing streaks
        loss_multiplier = max(1.0 - (self.consecutive_losses * 0.3), 0.5)

        # Reduce risk when in drawdown
        drawdown_multiplier = max(1.0 - (drawdown / 200.0), 0.5)

        # Reduce risk if win rate is poor
        win_rate_multiplier = self.recent_win_rate

        adjusted_risk = (
            self.base_risk_per_trade *
            loss_multiplier *
            drawdown_multiplier *
            win_rate_multiplier
        )

        return max(adjusted_risk, 0.005)  # Minimum 0.5%

    def get_stop_loss_distance(self, current_price: float, volatility: float) -> float:
        """
        Calculate stop loss distance based on volatility.
        Higher volatility = wider stop
        """
        base_stop = 0.008  # 0.8% base
        volatility_adjustment = (volatility / 100.0) * 0.5
        stop_pct = base_stop + volatility_adjustment
        return current_price * stop_pct

    def get_take_profit_targets(self, current_price: float, volatility: float) -> tuple:
        """
        Return (tp1, tp2) - two take profit targets.
        TP1: Conservative target (0.75%)
        TP2: Aggressive target (1.2%)
        Adjust for volatility.
        """
        volatility_factor = 1.0 + (volatility / 100.0) * 0.3

        tp1 = current_price * (1.0 + 0.0075 * volatility_factor)
        tp2 = current_price * (1.0 + 0.012 * volatility_factor)

        return tp1, tp2

    def should_reduce_risk(self) -> bool:
        """Determine if risk should be reduced"""
        reasons = []

        if self.consecutive_losses >= self.max_consecutive_losses:
            reasons.append(f"excessive consecutive losses ({self.consecutive_losses})")

        if abs(self.get_current_drawdown()) > 10.0:  # 10% drawdown
            reasons.append("deep drawdown")

        if self.recent_win_rate < 0.45:  # < 45% win rate
            reasons.append("poor win rate")

        if reasons:
            self.logger.warning(f"Risk reduction triggered: {', '.join(reasons)}")
            return True

        return False

    def should_pause_trading(self) -> bool:
        """Determine if trading should be paused"""
        drawdown = abs(self.get_current_drawdown())

        if drawdown > 20.0:  # 20% drawdown = circuit breaker
            self.logger.error(f"Trading pause triggered: {drawdown:.1f}% drawdown exceeds limit")
            return True

        if self.consecutive_losses >= 5:  # 5 consecutive losses
            self.logger.error(f"Trading pause triggered: {self.consecutive_losses} consecutive losses")
            return True

        return False

    def get_risk_parameters(self, volatility: float) -> RiskParams:
        """
        Get complete risk parameters for current market conditions.
        This is the main interface for the trading system.
        """
        position_size = self.calculate_adaptive_position_size(volatility)
        risk_per_trade = self.calculate_risk_per_trade()

        return RiskParams(
            position_size=position_size,
            risk_per_trade=risk_per_trade,
            kelly_fraction=self.kelly_fraction,
            stop_loss_pct=self.get_stop_loss_distance(1.0, volatility),
            take_profit_pct=0.012,  # 1.2% default
            max_positions=3,
            daily_loss_limit=self.current_capital * 0.03  # 3% daily loss limit
        )

    def get_metrics(self) -> Dict:
        """Get current risk metrics for monitoring"""
        return {
            'capital': self.current_capital,
            'equity_peak': self.peak_equity,
            'drawdown_pct': self.get_current_drawdown(),
            'win_rate': self.recent_win_rate,
            'consecutive_losses': self.consecutive_losses,
            'total_trades': len(self.trade_history),
            'trades_profitable': sum(1 for t in self.trade_history if t['pnl'] > 0),
            'total_pnl': sum(t['pnl'] for t in self.trade_history)
        }
