"""
Unit tests for HistoricalBacktester.

Tests signal generation, metrics calculation, and data loading.
"""

import pytest
import pandas as pd
from datetime import datetime
from backtester import HistoricalBacktester, BacktestMetrics


class MockTradingEngine:
    """Mock trading engine for testing."""

    def __init__(self):
        self.symbol = 'ETHUSDT'
        self.is_running = True
        self.open_positions = {}
        self.last_candle = {}
        self.volatility_estimate = 0.0

        # Mock risk manager
        class RiskManager:
            def __init__(self):
                self.current_capital = 10000.0

        self.risk_manager = RiskManager()

        # Mock julia_bridge
        self.julia_bridge = None

    def stop(self):
        pass

    def on_candle(self, timestamp, open_price, high, low, close, volume, atr):
        """Mock on_candle method for testing."""
        return None


class TestHistoricalBacktester:
    """Test suite for HistoricalBacktester."""

    def test_initialization(self):
        """Test backtester initialization."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine, use_julia_agents=False)

        assert backtester.use_julia_agents == False
        assert len(backtester.trades) == 0
        assert len(backtester.equity_history) == 0
        assert backtester.start_equity == 10000.0

    def test_ema_calculation(self):
        """Test EMA calculation in backtester."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine)

        prices = [100.0, 102.0, 101.0, 103.0, 105.0]
        ema = backtester._calc_ema(prices, 3)

        # EMA should be within price range
        assert min(prices) <= ema <= max(prices)

    def test_signal_generation_insufficient_data(self):
        """Test that signal is not generated with insufficient data."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine)

        # Add only 10 prices (need 30 for signal generation)
        candle = {
            'timestamp': datetime.utcnow(),
            'open': 2500.0,
            'high': 2501.0,
            'low': 2499.0,
            'close': 2500.0,
            'volume': 100.0
        }

        for i in range(10):
            result = backtester._get_signal_phase1(candle)
            assert result is None

    def test_position_sizing_calculation(self, initial_capital, risk_per_trade):
        """Test position size calculation."""
        engine = MockTradingEngine()
        engine.risk_manager.current_capital = initial_capital
        backtester = HistoricalBacktester(engine)

        candle = {
            'timestamp': datetime.utcnow(),
            'open': 2500.0,
            'high': 2501.0,
            'low': 2499.0,
            'close': 2500.0,
            'volume': 100.0
        }

        # Fill price history to 30+ candles
        for i in range(30):
            backtester._close_prices.append(2500.0)

        # Manually execute a signal to test position sizing
        signal = {'direction': 'LONG', 'confidence': 0.6}
        backtester._execute_signal(signal, candle)

        # Position should be created
        assert len(engine.open_positions) == 1

        # Verify position size = (equity * 0.5%) / entry_price
        trade = list(engine.open_positions.values())[0]
        expected_size = (initial_capital * 0.005) / 2500.0
        assert abs(trade['position_size'] - expected_size) < 0.00001

    def test_stop_loss_levels(self):
        """Test stop loss level calculation."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine)

        candle = {
            'timestamp': datetime.utcnow(),
            'open': 2500.0,
            'high': 2501.0,
            'low': 2499.0,
            'close': 2500.0,
            'volume': 100.0
        }

        # Fill price history
        for i in range(30):
            backtester._close_prices.append(2500.0)

        # Execute LONG signal
        signal = {'direction': 'LONG', 'confidence': 0.6}
        backtester._execute_signal(signal, candle)

        trade = list(engine.open_positions.values())[0]

        # LONG stop loss should be below entry
        assert trade['stop_loss'] == 2500.0 * 0.998  # 0.2% below

    def test_take_profit_levels(self):
        """Test take profit level calculation."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine)

        candle = {
            'timestamp': datetime.utcnow(),
            'close': 2500.0,
            'volume': 100.0
        }

        # Fill price history
        for i in range(30):
            backtester._close_prices.append(2500.0)

        # Execute LONG signal
        signal = {'direction': 'LONG', 'confidence': 0.6}
        backtester._execute_signal(signal, candle)

        trade = list(engine.open_positions.values())[0]

        # LONG take profit 1 should be above entry
        assert trade['take_profit_1'] == 2500.0 * 1.0075
        # LONG take profit 2 should be higher
        assert trade['take_profit_2'] == 2500.0 * 1.012

    def test_short_signal_levels(self):
        """Test SHORT signal entry levels."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine)

        candle = {
            'timestamp': datetime.utcnow(),
            'close': 2500.0,
            'volume': 100.0
        }

        # Fill price history
        for i in range(30):
            backtester._close_prices.append(2500.0)

        # Execute SHORT signal
        signal = {'direction': 'SHORT', 'confidence': 0.6}
        backtester._execute_signal(signal, candle)

        trade = list(engine.open_positions.values())[0]

        # SHORT stop loss should be above entry
        assert trade['stop_loss'] == 2500.0 * 1.002  # 0.2% above
        # SHORT take profit 1 should be below entry
        assert trade['take_profit_1'] == 2500.0 * 0.9925

    def test_position_closure(self):
        """Test position closure and P&L calculation."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine)

        # Create a position manually
        trade = {
            'direction': 'LONG',
            'entry_price': 2500.0,
            'entry_time': datetime.utcnow(),
            'position_size': 0.002,
            'stop_loss': 2498.0,
            'take_profit_1': 2520.0,
            'take_profit_2': 2530.0,
            'confidence': 0.6,
            'source': 'phase1_ema'
        }
        engine.open_positions['test_1'] = trade
        engine.last_candle = {'timestamp': datetime.utcnow()}

        # Close position at profit
        backtester._close_position('test_1', 2520.0, 'take_profit')

        # Position should be removed from open positions
        assert 'test_1' not in engine.open_positions

        # Trade should be recorded
        assert len(backtester.trades) == 1

        # P&L should be positive
        recorded_trade = backtester.trades[0]
        expected_pnl = (2520.0 - 2500.0) * 0.002
        assert abs(recorded_trade['pnl'] - expected_pnl) < 0.01

    def test_pnl_calculation_accuracy(self):
        """Test P&L calculation accuracy."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine)

        # Create and close multiple test trades
        test_cases = [
            ('LONG', 2500.0, 2510.0, 0.001, (2510.0 - 2500.0) * 0.001),
            ('LONG', 2500.0, 2490.0, 0.001, (2490.0 - 2500.0) * 0.001),
            ('SHORT', 2500.0, 2490.0, 0.001, (2500.0 - 2490.0) * 0.001),
            ('SHORT', 2500.0, 2510.0, 0.001, (2500.0 - 2510.0) * 0.001),
        ]

        for direction, entry, exit_p, size, expected_pnl in test_cases:
            trade = {
                'direction': direction,
                'entry_price': entry,
                'entry_time': datetime.utcnow(),
                'position_size': size,
                'confidence': 0.6,
                'source': 'phase1_ema'
            }
            engine.open_positions['test'] = trade
            engine.last_candle = {'timestamp': datetime.utcnow()}

            backtester._close_position('test', exit_p, 'test')

            assert len(backtester.trades) > 0
            actual_pnl = backtester.trades[-1]['pnl']
            assert abs(actual_pnl - expected_pnl) < 0.001

    def test_metrics_empty_backtest(self):
        """Test metrics calculation with no trades."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine)

        metrics = backtester._calculate_metrics()

        assert metrics.total_trades == 0
        assert metrics.winning_trades == 0
        assert metrics.losing_trades == 0
        assert metrics.win_rate == 0.0
        assert metrics.total_pnl == 0.0
        assert metrics.final_equity == backtester.start_equity

    def test_metrics_with_trades(self):
        """Test metrics calculation with executed trades."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine)

        # Manually create some closed trades
        now = datetime.utcnow()
        backtester.trades = [
            {
                'pnl': 10.0,
                'duration_sec': 300,
                'entry_price': 2500.0
            },
            {
                'pnl': -5.0,
                'duration_sec': 600,
                'entry_price': 2505.0
            },
            {
                'pnl': 15.0,
                'duration_sec': 450,
                'entry_price': 2510.0
            }
        ]
        backtester.equity_history = [10000.0, 10010.0, 10005.0, 10020.0]

        metrics = backtester._calculate_metrics()

        assert metrics.total_trades == 3
        assert metrics.winning_trades == 2
        assert metrics.losing_trades == 1
        assert metrics.win_rate == 2/3
        assert metrics.total_pnl == 20.0
        assert metrics.best_trade_pnl == 15.0
        assert metrics.worst_trade_pnl == -5.0

    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine)

        # Create equity history with returns
        backtester.equity_history = [
            10000.0, 10010.0, 10005.0, 10015.0, 10020.0,
            10012.0, 10018.0, 10025.0, 10020.0, 10030.0
        ]
        backtester.trades = [
            {'pnl': 10.0, 'duration_sec': 100, 'entry_price': 2500.0},
            {'pnl': -5.0, 'duration_sec': 200, 'entry_price': 2500.0}
        ]

        metrics = backtester._calculate_metrics()

        # Sharpe ratio should be calculated (not None)
        if len(backtester.equity_history) > 1:
            assert metrics.sharpe_ratio is not None

    def test_drawdown_calculation(self):
        """Test max drawdown calculation."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine)

        # Equity that reaches peak then drops
        backtester.equity_history = [
            10000.0, 10100.0, 10150.0,  # Building up
            10000.0, 9950.0, 9900.0,    # Drawdown
            10050.0                      # Recovery
        ]
        backtester.trades = []

        metrics = backtester._calculate_metrics()

        # Max drawdown should be negative
        assert metrics.max_drawdown_pct < 0
        # Should be approximately -0.05 (from 10150 to 9900)
        assert metrics.max_drawdown_pct < -0.01

    def test_backtest_execution(self, sample_candles):
        """Test full backtest execution."""
        engine = MockTradingEngine()
        backtester = HistoricalBacktester(engine, use_julia_agents=False)

        # Run backtest
        metrics = backtester.run_backtest(pd.DataFrame(sample_candles))

        # Verify metrics object is valid
        assert isinstance(metrics, BacktestMetrics)
        assert metrics.total_trades >= 0
        assert 0 <= metrics.win_rate <= 1
        assert metrics.final_equity >= 0
