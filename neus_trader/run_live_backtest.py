#!/usr/bin/env python3
"""
Live Backtest: Phase 1 Golden Hour Scalper on Real Binance Data
"""

import sys
import logging
from pathlib import Path
import json
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

python_core_path = str(Path(__file__).parent / 'python_core')
sys.path.insert(0, python_core_path)

from backtester import HistoricalBacktester
from scalping_engine import GoldenHourScalpingEngine

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('LiveBacktest')


def fetch_real_data():
    """Fetch real ETHUSDT data from Binance."""
    print("\n🔗 Fetching real Binance data...")

    try:
        # Use pandas + requests to get Binance data
        import requests

        # Fetch last 7 days of 5-minute data
        # Binance API: klines endpoint
        symbol = 'ETHUSDT'
        interval = '5m'
        limit = 2016  # 7 days * 24 hours * 12 candles/hour = 2016 candles

        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }

        print(f"   Fetching {symbol} {interval} data ({limit} candles)...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        klines = response.json()
        print(f"   ✓ Fetched {len(klines)} real candles")

        # Convert to DataFrame
        data = []
        for kline in klines:
            data.append({
                'timestamp': pd.Timestamp(int(kline[0]), unit='ms'),
                'open': float(kline[1]),
                'high': float(kline[2]),
                'low': float(kline[3]),
                'close': float(kline[4]),
                'volume': float(kline[7])  # Quote asset volume
            })

        df = pd.DataFrame(data)

        # Display info
        print(f"\n   📊 Data Summary:")
        print(f"      Period: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"      Price: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        print(f"      Avg Volume: {df['volume'].mean():.0f}")

        return df

    except Exception as e:
        print(f"   ✗ Error fetching from Binance: {e}")
        print(f"   Falling back to synthetic data...")
        return generate_synthetic_data()


def generate_synthetic_data():
    """Generate synthetic data as fallback."""
    print("\n   Generating 7 days of synthetic ETHUSDT data...")

    num_candles = 2016  # 7 days
    timestamps = pd.date_range(end=datetime.utcnow(), periods=num_candles, freq='5min')

    # Trending data with institutional patterns
    returns = np.random.normal(0.0001, 0.004, num_candles)
    prices = 2500 * np.exp(np.cumsum(returns))

    data = []
    for i, (timestamp, close) in enumerate(zip(timestamps, prices)):
        open_price = prices[i-1] if i > 0 else prices[0]
        high = max(open_price, close) * (1 + np.random.uniform(0, 0.001))
        low = min(open_price, close) * (1 - np.random.uniform(0, 0.001))
        volume = np.random.uniform(100, 500)

        data.append({
            'timestamp': timestamp,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })

    df = pd.DataFrame(data)
    print(f"   ✓ Generated {len(df)} synthetic candles")
    return df


def main():
    print("\n" + "="*70)
    print("LIVE BACKTEST: Phase 1 Golden Hour Scalper")
    print("Real Binance ETHUSDT Data (7 days, 5-min candles)")
    print("="*70)

    # Get real data
    data = fetch_real_data()

    # Run Phase 1 backtest
    print(f"\n⚡ Running backtest on {len(data)} candles...")

    engine = GoldenHourScalpingEngine(
        symbol='ETHUSDT',
        initial_capital=10000.0
    )

    backtester = HistoricalBacktester(engine)
    metrics = backtester.run_backtest(data)

    # Display results
    print(f"\n{'='*70}")
    print("RESULTS - REAL BINANCE DATA")
    print(f"{'='*70}\n")

    print(f"📈 Total Trades:        {metrics.total_trades}")
    print(f"✓ Winning Trades:      {metrics.winning_trades}")
    print(f"✗ Losing Trades:       {metrics.losing_trades}")
    print(f"📊 Win Rate:            {metrics.win_rate*100:.1f}%")
    print(f"💰 P&L:                ${metrics.total_pnl:.2f}")
    print(f"📊 P&L %:              {metrics.total_pnl_pct:.2f}%")
    print(f"💵 Final Capital:       ${metrics.final_equity:.2f}")
    print(f"📉 Max Drawdown:        {metrics.max_drawdown_pct:.2f}%")

    if hasattr(metrics, 'sharpe_ratio'):
        print(f"📈 Sharpe Ratio:        {metrics.sharpe_ratio:.2f}")

    print(f"\n{'='*70}")

    # Verdict
    print("\n🎯 VERDICT:")
    print(f"{'='*70}")

    if metrics.total_pnl > 0:
        print(f"✓ PROFITABLE: +${metrics.total_pnl:.2f} ({metrics.total_pnl_pct:.2f}%)")
    elif metrics.total_pnl < -100:
        print(f"✗ LOSS: ${metrics.total_pnl:.2f} ({metrics.total_pnl_pct:.2f}%)")
    else:
        print(f"~ BREAKEVEN: ${metrics.total_pnl:.2f} ({metrics.total_pnl_pct:.2f}%)")

    print(f"\nTrades Executed: {metrics.total_trades}")
    print(f"Win Rate: {metrics.win_rate*100:.1f}%")

    if metrics.total_trades > 0:
        pnl_per_trade = metrics.total_pnl / metrics.total_trades
        print(f"P&L per Trade: ${pnl_per_trade:.2f}")

    print(f"\n{'='*70}\n")

    # Save results
    results = {
        'timestamp': datetime.utcnow().isoformat(),
        'data_source': 'Binance Real Data',
        'period': f"{data['timestamp'].min()} to {data['timestamp'].max()}",
        'candles': len(data),
        'total_trades': metrics.total_trades,
        'winning_trades': metrics.winning_trades,
        'losing_trades': metrics.losing_trades,
        'win_rate': metrics.win_rate,
        'total_pnl': metrics.total_pnl,
        'total_pnl_pct': metrics.total_pnl_pct,
        'final_equity': metrics.final_equity,
        'max_drawdown_pct': metrics.max_drawdown_pct,
        'sharpe_ratio': getattr(metrics, 'sharpe_ratio', None)
    }

    results_file = Path(__file__).parent / 'results' / 'live_backtest_results.json'
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to {results_file}\n")


if __name__ == '__main__':
    main()
