"""
Pytest configuration and shared fixtures for NEUS_TRADER tests.
"""

import sys
import pytest
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'python_core'))


@pytest.fixture
def sample_candles():
    """Generate sample OHLCV candle data for testing."""
    timestamps = pd.date_range(
        start='2024-01-01',
        periods=100,
        freq='5min'
    )

    # Generate realistic price movement
    returns = np.random.normal(0.0001, 0.005, 100)
    prices = 2500 * np.exp(np.cumsum(returns))

    candles = []
    for i, (ts, close) in enumerate(zip(timestamps, prices)):
        open_price = prices[i-1] if i > 0 else prices[0]
        high_price = max(open_price, close) * (1 + np.random.uniform(0, 0.002))
        low_price = min(open_price, close) * (1 - np.random.uniform(0, 0.002))
        volume = np.random.uniform(100, 1000)

        candles.append({
            'timestamp': ts,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close,
            'volume': volume
        })

    return candles


@pytest.fixture
def ema_test_prices():
    """Simple price series for EMA testing."""
    return [
        100.0, 101.0, 102.0, 101.5, 103.0,
        104.0, 103.5, 105.0, 106.0, 105.5
    ]


@pytest.fixture
def initial_capital():
    """Standard initial capital for testing."""
    return 10000.0


@pytest.fixture
def risk_per_trade():
    """Standard risk per trade."""
    return 0.005  # 0.5%
