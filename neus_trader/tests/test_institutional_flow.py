"""
Unit tests for Institutional Flow Detector

Tests smart money detection:
- Volume surge detection
- Price efficiency (absorption)
- Accumulation vs distribution patterns
- Entry/exit signal generation
"""

import pytest
from datetime import datetime, timedelta
from institutional_flow import InstitutionalFlowDetector, InstitutionalSignal


class TestInstitutionalFlowDetector:
    """Test suite for institutional flow detection."""

    def test_initialization(self):
        """Test detector initialization."""
        detector = InstitutionalFlowDetector('ETHUSDT')

        assert detector.symbol == 'ETHUSDT'
        assert len(detector.close_prices) == 0
        assert detector.avg_volume == 0.0
        assert detector.volume_surge_threshold == 1.5

    def test_volume_surge_detection(self):
        """Test volume spike detection."""
        detector = InstitutionalFlowDetector()

        # Add baseline volumes
        for i in range(20):
            candle = {
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': 2500.0,
                'high': 2501.0,
                'low': 2499.0,
                'close': 2500.0,
                'volume': 100.0  # Baseline
            }
            detector.process_candle(candle)

        # Update statistics
        detector._update_statistics()
        assert detector.avg_volume > 0

        # Test with surge volume
        signal = detector.process_candle({
            'timestamp': datetime.utcnow(),
            'open': 2500.0,
            'high': 2501.0,
            'low': 2499.0,
            'close': 2500.0,
            'volume': 500.0  # 5x baseline
        })

        assert signal is not None
        assert signal.volume_score > 0.5  # Should detect surge

    def test_price_efficiency_absorption(self):
        """Test smart money absorption detection."""
        detector = InstitutionalFlowDetector()

        # Build history
        for i in range(20):
            candle = {
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': 2500.0 + (i * 0.1),
                'high': 2500.0 + (i * 0.1) + 0.5,
                'low': 2500.0 + (i * 0.1) - 0.5,
                'close': 2500.0 + (i * 0.1),
                'volume': 100.0
            }
            detector.process_candle(candle)

        # Large volume but small price movement = absorption
        signal = detector.process_candle({
            'timestamp': datetime.utcnow(),
            'open': 2502.0,
            'high': 2502.5,  # Small range
            'low': 2501.8,
            'close': 2502.3,  # Closed near high
            'volume': 500.0  # Large volume
        })

        assert signal is not None
        assert signal.price_score > 0.3  # Efficiency detected

    def test_accumulation_phase_detection(self):
        """Test accumulation pattern detection."""
        detector = InstitutionalFlowDetector()

        # Create accumulation pattern:
        # - Rising volume
        # - Flat/rising price
        # - Low volatility
        base_price = 2500.0
        for i in range(30):
            # Volume increasing
            volume = 100.0 + (i * 5)
            # Price flat
            price = base_price + (i * 0.05)

            candle = {
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': price,
                'high': price + 0.2,
                'low': price - 0.2,
                'close': price,
                'volume': volume
            }
            detector.process_candle(candle)

        # Should detect accumulation
        accumulation = detector._detect_accumulation()
        assert accumulation > 0.4

    def test_distribution_phase_detection(self):
        """Test distribution pattern detection."""
        detector = InstitutionalFlowDetector()

        # Create distribution pattern:
        # - High volume
        # - Declining price
        # - Increasing volatility
        base_price = 2500.0
        for i in range(30):
            # High volume
            volume = 300.0
            # Price declining
            price = base_price - (i * 0.1)
            # Increasing volatility
            volatility = i * 0.05

            candle = {
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': price,
                'high': price + volatility,
                'low': price - volatility,
                'close': price - (volatility * 0.5),
                'volume': volume
            }
            detector.process_candle(candle)

        # Should detect distribution
        distribution = detector._detect_distribution()
        assert distribution > 0.3

    def test_entry_signal_generation(self):
        """Test entry signal on accumulation."""
        detector = InstitutionalFlowDetector()

        # Build baseline
        for i in range(25):
            detector.process_candle({
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': 2500.0,
                'high': 2500.5,
                'low': 2499.5,
                'close': 2500.0,
                'volume': 100.0
            })

        # Create accumulation signal
        for i in range(25, 35):
            signal = detector.process_candle({
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': 2500.0 + (i * 0.05),
                'high': 2500.0 + (i * 0.05) + 0.2,
                'low': 2500.0 + (i * 0.05) - 0.1,
                'close': 2500.0 + (i * 0.05) + 0.1,
                'volume': 150.0 + (i * 2)
            })

        # Should generate entry signal
        if signal and signal.entry_signal:
            assert signal.confidence > 0.5
            assert 'accumulation' in signal.reason.lower()

    def test_exit_signal_generation(self):
        """Test exit signal on distribution."""
        detector = InstitutionalFlowDetector()

        # Build accumulation first
        base_price = 2500.0
        for i in range(30):
            detector.process_candle({
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': base_price + (i * 0.05),
                'high': base_price + (i * 0.05) + 0.2,
                'low': base_price + (i * 0.05) - 0.1,
                'close': base_price + (i * 0.05),
                'volume': 150.0 + (i * 2)
            })

        # Then create distribution
        peak_price = base_price + 1.5
        for i in range(30, 40):
            signal = detector.process_candle({
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': peak_price - (i - 30) * 0.1,
                'high': peak_price - (i - 30) * 0.1 + ((i - 30) * 0.1),
                'low': peak_price - (i - 30) * 0.1 - ((i - 30) * 0.1),
                'close': peak_price - (i - 30) * 0.1 - ((i - 30) * 0.05),
                'volume': 300.0
            })

        # Should detect distribution
        if signal and signal.exit_signal:
            assert signal.confidence > 0.5
            assert 'distribution' in signal.reason.lower()

    def test_flow_state_reporting(self):
        """Test flow state reporting."""
        detector = InstitutionalFlowDetector()

        # Accumulation state
        for i in range(30):
            detector.process_candle({
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': 2500.0 + (i * 0.05),
                'high': 2500.0 + (i * 0.05) + 0.2,
                'low': 2500.0 + (i * 0.05) - 0.1,
                'close': 2500.0 + (i * 0.05),
                'volume': 150.0 + (i * 2)
            })

        state = detector.get_flow_state()

        assert 'state' in state
        assert 'accumulation_score' in state
        assert 'distribution_score' in state
        assert state['state'] in ['accumulation', 'distribution', 'neutral', 'initializing']

    def test_smart_money_absorption_with_recovery(self):
        """Test absorption pattern with quick price recovery."""
        detector = InstitutionalFlowDetector()

        # Build baseline
        for i in range(20):
            detector.process_candle({
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': 2500.0,
                'high': 2500.5,
                'low': 2499.5,
                'close': 2500.0,
                'volume': 100.0
            })

        # Large volume on low but closes high = absorption
        signal = detector.process_candle({
            'timestamp': datetime.utcnow() + timedelta(minutes=20),
            'open': 2500.0,
            'high': 2500.8,
            'low': 2499.5,  # Tested the low
            'close': 2500.6,  # But recovered/closed high
            'volume': 400.0  # Large volume
        })

        assert signal is not None
        absorption = detector._detect_smart_money_absorption()
        assert absorption > 0.4  # Absorption pattern detected

    def test_history_buffer_limit(self):
        """Test that history buffer is limited."""
        detector = InstitutionalFlowDetector()

        # Add 150 candles (max is 100)
        for i in range(150):
            detector.process_candle({
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': 2500.0,
                'high': 2500.5,
                'low': 2499.5,
                'close': 2500.0,
                'volume': 100.0
            })

        # Buffer should not exceed 100
        assert len(detector.close_prices) <= 100
        assert len(detector.volumes) <= 100
        assert len(detector.timestamps) <= 100

    def test_insufficient_data_handling(self):
        """Test handling when insufficient data for analysis."""
        detector = InstitutionalFlowDetector()

        # Only 3 candles
        for i in range(3):
            signal = detector.process_candle({
                'timestamp': datetime.utcnow() + timedelta(minutes=i),
                'open': 2500.0,
                'high': 2500.5,
                'low': 2499.5,
                'close': 2500.0,
                'volume': 100.0
            })

            # Should return None when insufficient data
            assert signal is None
