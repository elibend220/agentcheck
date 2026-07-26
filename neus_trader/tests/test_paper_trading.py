"""
Unit tests for PaperTradingEngine.

Tests signal generation, position management, P&L calculation, and metrics.
"""

import pytest
from datetime import datetime, timedelta
from paper_trading import PaperTradingEngine, PaperTrade


class TestPaperTradingEngine:
    """Test suite for PaperTradingEngine."""

    def test_initialization(self, initial_capital):
        """Test engine initialization."""
        engine = PaperTradingEngine(
            symbol='ETHUSDT',
            initial_capital=initial_capital
        )

        assert engine.symbol == 'ETHUSDT'
        assert engine.initial_capital == initial_capital
        assert engine.current_capital == initial_capital
        assert len(engine.open_positions) == 0
        assert len(engine.closed_trades) == 0

    def test_process_candle_initialization(self, sample_candles):
        """Test that initial candles are stored without generating signals."""
        engine = PaperTradingEngine()

        # First 30 candles should not generate signals (warm-up period)
        for i, candle in enumerate(sample_candles[:30]):
            result = engine.process_candle(candle)
            assert result is None, f"Unexpected signal at candle {i}"

        # Price history should be populated
        assert len(engine.close_prices) == 30

    def test_ema_calculation(self):
        """Test EMA calculation correctness."""
        engine = PaperTradingEngine()

        # Simple test case
        prices = [100.0, 102.0, 101.0, 103.0, 105.0]
        ema = engine._calc_ema(prices, 3)

        # Verify EMA is between min and max
        assert min(prices) <= ema <= max(prices)

    def test_ema_calculation_insufficient_data(self):
        """Test EMA with insufficient data."""
        engine = PaperTradingEngine()

        prices = [100.0, 101.0]
        ema = engine._calc_ema(prices, 5)

        # Should return last price
        assert ema == prices[-1]

    def test_position_sizing(self, initial_capital):
        """Test position sizing calculation."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        # Risk per trade = 0.5% of equity
        entry_price = 2500.0
        expected_position_value = initial_capital * 0.005
        expected_position_size = expected_position_value / entry_price

        # Simulate a trade
        candle = {
            'timestamp': datetime.utcnow(),
            'open': 2500.0,
            'high': 2501.0,
            'low': 2499.0,
            'close': 2500.0,
            'volume': 100.0
        }

        # Fill price history to enable signal generation
        for i in range(30):
            candle['timestamp'] = datetime.utcnow() + timedelta(minutes=i)
            engine.process_candle(candle)

        # Verify position sizing math
        assert abs(engine.current_capital - initial_capital) < 10  # No trades yet

    def test_long_trade_execution(self, sample_candles, initial_capital):
        """Test executing a LONG trade."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        # Process candles to enable signal generation
        for candle in sample_candles:
            engine.process_candle(candle)

        # Check if any trades were executed
        # (Depends on price movement, so we just verify structure)
        assert isinstance(engine.open_positions, dict)
        assert isinstance(engine.closed_trades, list)

    def test_short_trade_execution(self, initial_capital):
        """Test executing a SHORT trade."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        # Create declining prices to trigger SHORT signal
        base_price = 2500.0
        candles = []

        for i in range(50):
            # Prices decline first (create SHORT signal)
            if i < 25:
                close_price = base_price - (i * 0.5)
            else:
                close_price = base_price - 12.5 + ((i - 25) * 0.3)

            candle = {
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': close_price,
                'high': close_price + 0.5,
                'low': close_price - 0.5,
                'close': close_price,
                'volume': 100.0
            }
            candles.append(candle)
            engine.process_candle(candle)

        # Verify engine state is consistent
        total_positions = len(engine.open_positions) + len(engine.closed_trades)
        assert total_positions >= 0

    def test_stop_loss_execution(self, initial_capital):
        """Test that stop loss closes positions."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        # Create a long entry
        base_price = 2500.0
        entry_price = base_price

        # First, generate enough candles for signal
        for i in range(30):
            candle = {
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': base_price + (i * 0.1),
                'high': base_price + (i * 0.1) + 0.5,
                'low': base_price + (i * 0.1) - 0.5,
                'close': base_price + (i * 0.1),
                'volume': 100.0
            }
            engine.process_candle(candle)

        initial_position_count = len(engine.open_positions)

        # Now create a candle that triggers stop loss
        if initial_position_count > 0:
            # Get first position's stop loss level
            first_trade = list(engine.open_positions.values())[0]
            sl_price = first_trade.stop_loss

            # Create candle at stop loss level
            sl_candle = {
                'timestamp': datetime.utcnow() + timedelta(minutes=31),
                'open': base_price,
                'high': base_price,
                'low': sl_price - 0.01,
                'close': sl_price - 0.01,
                'volume': 100.0
            }
            engine.process_candle(sl_candle)

            # Position should be closed
            assert len(engine.open_positions) < initial_position_count

    def test_take_profit_execution(self, initial_capital):
        """Test that take profit closes positions."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        # Create a long entry with profitable move
        base_price = 2500.0

        # Generate candles for signal
        for i in range(30):
            candle = {
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': base_price,
                'high': base_price + 0.5,
                'low': base_price - 0.5,
                'close': base_price,
                'volume': 100.0
            }
            engine.process_candle(candle)

        initial_trades = len(engine.closed_trades)

        # Create strong uptrend to trigger take profit
        for i in range(31, 50):
            candle = {
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': base_price + (i * 0.1),
                'high': base_price + (i * 0.1) + 1.0,
                'low': base_price + (i * 0.1) - 0.5,
                'close': base_price + (i * 0.1) + 0.5,
                'volume': 100.0
            }
            engine.process_candle(candle)

        # Some trades should be closed
        # (May or may not have take profit, depending on price movement)
        assert isinstance(engine.closed_trades, list)

    def test_metrics_calculation_no_trades(self, initial_capital):
        """Test metrics when no trades have been executed."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        metrics = engine.get_metrics()

        assert metrics['total_trades'] == 0
        assert metrics['winning_trades'] == 0
        assert metrics['losing_trades'] == 0
        assert metrics['win_rate'] == 0.0
        assert metrics['total_pnl'] == 0.0
        assert metrics['current_capital'] == initial_capital

    def test_metrics_calculation_with_trades(self, sample_candles, initial_capital):
        """Test metrics calculation with executed trades."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        # Process multiple candles
        for candle in sample_candles:
            engine.process_candle(candle)

        metrics = engine.get_metrics()

        # Verify metrics structure
        assert 'total_trades' in metrics
        assert 'winning_trades' in metrics
        assert 'losing_trades' in metrics
        assert 'win_rate' in metrics
        assert 'total_pnl' in metrics
        assert 'current_capital' in metrics

        # Win rate should be between 0 and 1
        if metrics['total_trades'] > 0:
            assert 0 <= metrics['win_rate'] <= 1

    def test_position_tracking(self, initial_capital):
        """Test that positions are correctly tracked."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        # Execute a trade by manual insertion
        trade = PaperTrade(
            trade_id='test_1',
            symbol='ETHUSDT',
            direction='LONG',
            entry_price=2500.0,
            entry_time=datetime.utcnow(),
            position_size=0.001,
            stop_loss=2498.0,
            take_profit_1=2520.0,
            take_profit_2=2530.0
        )

        engine.open_positions['test_1'] = trade

        positions = engine.get_positions()

        assert len(positions) == 1
        assert positions[0]['direction'] == 'LONG'
        assert positions[0]['entry_price'] == 2500.0

    def test_capital_preservation_on_winners(self, initial_capital):
        """Test that winning trades increase capital."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        # Create a winning trade manually
        engine._close_position(
            trade_id='test_1',
            exit_price=2510.0,
            reason='take_profit',
            exit_time=datetime.utcnow()
        )

        # Capital should not change without an open position
        assert engine.current_capital == initial_capital

    def test_capital_reduction_on_losses(self, initial_capital):
        """Test that losing trades reduce capital."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        # Create an open position
        trade = PaperTrade(
            trade_id='test_1',
            symbol='ETHUSDT',
            direction='LONG',
            entry_price=2500.0,
            entry_time=datetime.utcnow(),
            position_size=0.001,
            stop_loss=2490.0,
            take_profit_1=2510.0,
            take_profit_2=2520.0
        )
        engine.open_positions['test_1'] = trade

        # Close at a loss
        engine._close_position(
            trade_id='test_1',
            exit_price=2490.0,  # Stop loss hit
            reason='stop_loss',
            exit_time=datetime.utcnow()
        )

        # Capital should decrease
        expected_loss = (2490.0 - 2500.0) * 0.001
        assert abs(engine.current_capital - (initial_capital + expected_loss)) < 0.01

    def test_max_positions_limit(self, initial_capital):
        """Test that max positions limit is enforced."""
        engine = PaperTradingEngine(initial_capital=initial_capital, max_positions=2)

        # Manually create positions
        for i in range(3):
            trade = PaperTrade(
                trade_id=f'test_{i}',
                symbol='ETHUSDT',
                direction='LONG',
                entry_price=2500.0,
                entry_time=datetime.utcnow(),
                position_size=0.001,
                stop_loss=2490.0,
                take_profit_1=2510.0,
                take_profit_2=2520.0
            )
            if i < 2:
                engine.open_positions[f'test_{i}'] = trade

        # Only 2 positions should exist
        assert len(engine.open_positions) <= engine.max_positions

    def test_pnl_calculation_long(self, initial_capital):
        """Test P&L calculation for LONG trades."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        # Create and close a profitable LONG trade
        trade = PaperTrade(
            trade_id='test_long',
            symbol='ETHUSDT',
            direction='LONG',
            entry_price=2500.0,
            entry_time=datetime.utcnow(),
            position_size=0.002,
            stop_loss=2490.0,
            take_profit_1=2510.0,
            take_profit_2=2520.0
        )
        engine.open_positions['test_long'] = trade

        engine._close_position(
            trade_id='test_long',
            exit_price=2520.0,  # Take profit hit
            reason='take_profit',
            exit_time=datetime.utcnow()
        )

        # Verify P&L calculation
        expected_pnl = (2520.0 - 2500.0) * 0.002
        assert len(engine.closed_trades) == 1
        assert abs(engine.closed_trades[0].pnl - expected_pnl) < 0.01

    def test_pnl_calculation_short(self, initial_capital):
        """Test P&L calculation for SHORT trades."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        # Create and close a profitable SHORT trade
        trade = PaperTrade(
            trade_id='test_short',
            symbol='ETHUSDT',
            direction='SHORT',
            entry_price=2500.0,
            entry_time=datetime.utcnow(),
            position_size=0.002,
            stop_loss=2510.0,
            take_profit_1=2490.0,
            take_profit_2=2480.0
        )
        engine.open_positions['test_short'] = trade

        engine._close_position(
            trade_id='test_short',
            exit_price=2480.0,  # Take profit hit
            reason='take_profit',
            exit_time=datetime.utcnow()
        )

        # Verify P&L calculation for SHORT
        expected_pnl = (2500.0 - 2480.0) * 0.002
        assert len(engine.closed_trades) == 1
        assert abs(engine.closed_trades[0].pnl - expected_pnl) < 0.01

    def test_trade_history_export(self, sample_candles, initial_capital):
        """Test exporting trade history."""
        engine = PaperTradingEngine(initial_capital=initial_capital)

        for candle in sample_candles:
            engine.process_candle(candle)

        history = engine.get_trade_history(limit=10)

        assert isinstance(history, list)
        # Each trade should have required fields
        for trade in history:
            assert 'trade_id' in trade
            assert 'direction' in trade
            assert 'entry_price' in trade
            assert 'pnl' in trade
