#!/usr/bin/env python3
"""
Compare Improved Engine: All Hours vs Prime Hours Only

Tests if restricting to high-liquidity periods (London 13-17 UTC, US Close 20-23 UTC)
improves profitability by filtering out low-quality trading windows.

Hypothesis: Prime hours should show higher win rate and profit factor.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import json

import pandas as pd
import numpy as np

python_core_path = str(Path(__file__).parent / 'python_core')
sys.path.insert(0, python_core_path)

from backtester import HistoricalBacktester
from scalping_engine_improved import GoldenHourScalpingEngineImproved
from market_hours import MarketHourDetector

logging.basicConfig(level=logging.ERROR)


def generate_test_data(days: int = 30) -> pd.DataFrame:
    """Generate consistent test data for both engines"""
    num_candles = days * 288
    timestamps = pd.date_range(
        end=datetime.utcnow(),
        periods=num_candles,
        freq='5min'
    )

    np.random.seed(42)  # Consistent seed
    returns = np.random.normal(0.00005, 0.003, num_candles)
    prices = 2500 * np.exp(np.cumsum(returns))

    volatility = np.ones(num_candles) * 0.003
    for i in range(1000, len(volatility), 500):
        volatility[i:i+200] *= 2.0

    returns = np.random.normal(0.00005, volatility, num_candles)
    prices = 2500 * np.exp(np.cumsum(returns))

    data = []
    for i, (timestamp, close) in enumerate(zip(timestamps, prices)):
        open_price = prices[i-1] if i > 0 else prices[0]
        high = max(open_price, close) * (1 + np.random.uniform(0, 0.002))
        low = min(open_price, close) * (1 - np.random.uniform(0, 0.002))
        volume = np.random.uniform(100, 500)

        data.append({
            'timestamp': timestamp,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })

    return pd.DataFrame(data)


def calculate_profit_factor(metrics) -> float:
    """Calculate profit factor"""
    if metrics.total_trades == 0:
        return 0.0

    gross_profit = sum(t['pnl'] for t in metrics.trades if t['pnl'] > 0)
    gross_loss = sum(abs(t['pnl']) for t in metrics.trades if t['pnl'] < 0)

    if gross_loss == 0:
        return 0.0

    return gross_profit / gross_loss


def is_prime_hour(timestamp) -> bool:
    """Check if timestamp is in prime trading hours"""
    hour = timestamp.hour
    # London 13-17 UTC or US Close 20-23 UTC
    return (13 <= hour < 17) or (20 <= hour < 23)


def run_comparison():
    """Compare improved engine on all hours vs prime hours only"""

    print("\n" + "="*100)
    print("IMPROVED ENGINE: All Hours vs Prime Hours Only")
    print("="*100 + "\n")

    # Generate test data
    print("📊 Generating 30 days of test data...")
    data = generate_test_data(30)
    print(f"   {len(data)} candles\n")

    # Test on ALL HOURS
    print("🔄 Testing IMPROVED Engine - ALL HOURS...")
    print("-"*100)

    engine_all = GoldenHourScalpingEngineImproved('ETHUSDT', 10000.0, min_confidence=0.75)
    backtester_all = HistoricalBacktester(engine_all)
    metrics_all = backtester_all.run_backtest(data)
    pf_all = calculate_profit_factor(metrics_all)

    print(f"   Trades: {metrics_all.total_trades}")
    print(f"   Win Rate: {metrics_all.win_rate*100:.1f}%")
    print(f"   P&L: ${metrics_all.total_pnl:.2f} ({metrics_all.total_pnl_pct*100:.2f}%)")
    print(f"   Profit Factor: {pf_all:.2f}")
    print(f"   Max Drawdown: {metrics_all.max_drawdown_pct*100:.2f}%")
    print(f"   Sharpe Ratio: {metrics_all.sharpe_ratio:.2f}\n")

    # Test on PRIME HOURS ONLY
    print("🔄 Testing IMPROVED Engine - PRIME HOURS ONLY (London 13-17, US Close 20-23 UTC)...")
    print("-"*100)

    prime_data = data[data['timestamp'].apply(is_prime_hour)].copy()
    print(f"   Filtered to {len(prime_data)} candles in prime hours ({len(prime_data)/len(data)*100:.1f}%)")

    engine_prime = GoldenHourScalpingEngineImproved('ETHUSDT', 10000.0, min_confidence=0.75)
    backtester_prime = HistoricalBacktester(engine_prime)
    metrics_prime = backtester_prime.run_backtest(prime_data)
    pf_prime = calculate_profit_factor(metrics_prime)

    print(f"   Trades: {metrics_prime.total_trades}")
    print(f"   Win Rate: {metrics_prime.win_rate*100:.1f}%")
    print(f"   P&L: ${metrics_prime.total_pnl:.2f} ({metrics_prime.total_pnl_pct*100:.2f}%)")
    print(f"   Profit Factor: {pf_prime:.2f}")
    print(f"   Max Drawdown: {metrics_prime.max_drawdown_pct*100:.2f}%")
    sharpe_str = f"{metrics_prime.sharpe_ratio:.2f}" if metrics_prime.sharpe_ratio else "N/A"
    print(f"   Sharpe Ratio: {sharpe_str}\n")

    # Display comparison
    print("="*100)
    print("📊 DETAILED COMPARISON")
    print("="*100 + "\n")

    # Calculate improvements
    trade_reduction = ((metrics_all.total_trades - metrics_prime.total_trades) / metrics_all.total_trades * 100) if metrics_all.total_trades > 0 else 0
    win_rate_change = (metrics_prime.win_rate - metrics_all.win_rate) * 100
    pnl_change = metrics_prime.total_pnl - metrics_all.total_pnl
    pf_improvement = pf_prime - pf_all

    print(f"{'Metric':<25} {'All Hours':<20} {'Prime Hours':<20} {'Change':<25}")
    print("-"*100)
    print(f"{'Total Trades':<25} {metrics_all.total_trades:<20} {metrics_prime.total_trades:<20} {-trade_reduction:+.1f}%")
    print(f"{'Win Rate':<25} {metrics_all.win_rate*100:>6.1f}%          {metrics_prime.win_rate*100:>6.1f}%          {win_rate_change:+.1f}%")
    print(f"{'Profit Factor':<25} {pf_all:>6.2f}            {pf_prime:>6.2f}            {pf_improvement:+.2f}")
    print(f"{'Total P&L':<25} ${metrics_all.total_pnl:>7.2f}          ${metrics_prime.total_pnl:>7.2f}          {pnl_change:+.2f}")
    print(f"{'P&L %':<25} {metrics_all.total_pnl_pct*100:>6.2f}%          {metrics_prime.total_pnl_pct*100:>6.2f}%          {(metrics_prime.total_pnl_pct - metrics_all.total_pnl_pct)*100:+.2f}%")
    print(f"{'Max Drawdown':<25} {metrics_all.max_drawdown_pct*100:>6.2f}%          {metrics_prime.max_drawdown_pct*100:>6.2f}%          {(metrics_prime.max_drawdown_pct - metrics_all.max_drawdown_pct)*100:+.2f}%")
    all_sharpe = metrics_all.sharpe_ratio if metrics_all.sharpe_ratio else 0.0
    prime_sharpe = metrics_prime.sharpe_ratio if metrics_prime.sharpe_ratio else 0.0
    print(f"{'Sharpe Ratio':<25} {all_sharpe:>6.2f}            {prime_sharpe:>6.2f}            {prime_sharpe - all_sharpe:+.2f}")

    # Analysis
    print(f"\n{'='*100}")
    print("🔍 ANALYSIS")
    print(f"{'='*100}\n")

    print(f"📊 Market Hours Impact:")
    print(f"   Prime hours represent {len(prime_data)/len(data)*100:.1f}% of total trading time")
    print(f"   Trade concentration: {metrics_prime.total_trades}/{metrics_all.total_trades} trades ({metrics_prime.total_trades/max(metrics_all.total_trades, 1)*100:.1f}%)\n")

    if win_rate_change > 0:
        print(f"📈 Win Rate: {metrics_prime.win_rate*100:.1f}% (vs {metrics_all.win_rate*100:.1f}%)")
        print(f"   ✓ Improved by {win_rate_change:.1f}% in prime hours\n")
    else:
        print(f"⚠️  Win Rate: {metrics_prime.win_rate*100:.1f}% (vs {metrics_all.win_rate*100:.1f}%)")
        print(f"   Similar performance across all hours\n")

    print(f"💰 Profit Factor: {pf_prime:.2f} (vs {pf_all:.2f})")
    if pf_improvement > 0:
        if pf_prime >= 1.0:
            print(f"   ✓ IMPROVED and now profitable! (+{pf_improvement:.2f})")
        else:
            print(f"   ✓ Improved but still unprofitable (+{pf_improvement:.2f})")
    else:
        print(f"   ⚠ Similar or worse performance")
    print()

    # Verdict
    print(f"{'='*100}")
    print("🎯 VERDICT")
    print(f"{'='*100}\n")

    if pf_prime >= 1.0 and pf_prime > pf_all:
        print(f"✅ PRIME HOURS STRATEGY WORKS")
        print(f"   • Profit Factor improved to {pf_prime:.2f}")
        print(f"   • Focus on high-liquidity windows shows promise")
        print(f"   • Recommended: Apply market hour filtering to live trading")
    elif pf_prime > pf_all:
        print(f"🟡 PRIME HOURS SHOW IMPROVEMENT")
        print(f"   • Profit Factor improved from {pf_all:.2f} to {pf_prime:.2f}")
        print(f"   • Still not fully profitable, but better direction")
        print(f"   • Consider: Tighter entry filters + market hour filtering")
    elif metrics_prime.total_trades > 0 and metrics_prime.win_rate > metrics_all.win_rate:
        print(f"🟡 WIN RATE IMPROVED IN PRIME HOURS")
        print(f"   • Win rate: {metrics_prime.win_rate*100:.1f}% vs {metrics_all.win_rate*100:.1f}%")
        print(f"   • Fewer trades with better quality")
        print(f"   • Exit strategy refinement needed for profitability")
    else:
        print(f"⚠️  MIXED RESULTS")
        print(f"   • Market hour filtering shows modest improvement")
        print(f"   • Current win rate insufficient for profitability")
        print(f"   • Need stronger entry signals or better exits")

    # Save results
    output_file = Path(__file__).parent / 'results' / 'engine_prime_hours_comparison.json'
    output_file.parent.mkdir(exist_ok=True)

    comparison_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'comparison': 'Improved Engine: All Hours vs Prime Hours',
        'all_hours': {
            'trades': metrics_all.total_trades,
            'win_rate': metrics_all.win_rate,
            'pnl': metrics_all.total_pnl,
            'pnl_pct': metrics_all.total_pnl_pct,
            'profit_factor': pf_all,
            'drawdown': metrics_all.max_drawdown_pct,
            'sharpe': metrics_all.sharpe_ratio
        },
        'prime_hours': {
            'trades': metrics_prime.total_trades,
            'win_rate': metrics_prime.win_rate,
            'pnl': metrics_prime.total_pnl,
            'pnl_pct': metrics_prime.total_pnl_pct,
            'profit_factor': pf_prime,
            'drawdown': metrics_prime.max_drawdown_pct,
            'sharpe': metrics_prime.sharpe_ratio
        },
        'improvements': {
            'trade_reduction_pct': -trade_reduction,
            'win_rate_change_pct': win_rate_change,
            'profit_factor_change': pf_improvement,
            'pnl_change': pnl_change
        }
    }

    with open(output_file, 'w') as f:
        json.dump(comparison_data, f, indent=2)

    print(f"\n✓ Comparison saved to {output_file}\n")

    return metrics_all, metrics_prime, pf_all, pf_prime


if __name__ == '__main__':
    try:
        run_comparison()
    except KeyboardInterrupt:
        print("\n\nComparison cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", exc_info=True)
        sys.exit(1)
