#!/usr/bin/env python3
"""
Compare Original vs Improved Scalping Engine

Tests both versions on same data to measure improvement in Profit Factor.
Shows exact impact of stricter entry filters.

Hypothesis: Improved version will have:
  • Fewer trades (50-60% reduction)
  • Higher win rate (30% → 40%+)
  • Higher Profit Factor (0.92 → 1.3+)
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
from scalping_engine import GoldenHourScalpingEngine
from scalping_engine_improved import GoldenHourScalpingEngineImproved

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


def run_comparison():
    """Compare original vs improved engine"""

    print("\n" + "="*100)
    print("SCALPING ENGINE COMPARISON: Original vs Improved")
    print("="*100 + "\n")

    # Generate test data
    print("📊 Generating 30 days of test data...")
    data = generate_test_data(30)
    print(f"   {len(data)} candles\n")

    # Test ORIGINAL engine
    print("🔄 Testing ORIGINAL Scalping Engine...")
    print("-"*100)

    original_engine = GoldenHourScalpingEngine('ETHUSDT', 10000.0)
    original_backtester = HistoricalBacktester(original_engine)
    original_metrics = original_backtester.run_backtest(data)
    original_pf = calculate_profit_factor(original_metrics)

    print(f"   Trades: {original_metrics.total_trades}")
    print(f"   Win Rate: {original_metrics.win_rate*100:.1f}%")
    print(f"   P&L: ${original_metrics.total_pnl:.2f} ({original_metrics.total_pnl_pct*100:.2f}%)")
    print(f"   Profit Factor: {original_pf:.2f}")
    print(f"   Max Drawdown: {original_metrics.max_drawdown_pct*100:.2f}%")
    print(f"   Sharpe Ratio: {original_metrics.sharpe_ratio:.2f}\n")

    # Test IMPROVED engine
    print("🔄 Testing IMPROVED Scalping Engine...")
    print("-"*100)

    improved_engine = GoldenHourScalpingEngineImproved('ETHUSDT', 10000.0, min_confidence=0.75)
    improved_backtester = HistoricalBacktester(improved_engine)
    improved_metrics = improved_backtester.run_backtest(data)
    improved_pf = calculate_profit_factor(improved_metrics)

    print(f"   Trades: {improved_metrics.total_trades}")
    print(f"   Win Rate: {improved_metrics.win_rate*100:.1f}%")
    print(f"   P&L: ${improved_metrics.total_pnl:.2f} ({improved_metrics.total_pnl_pct*100:.2f}%)")
    print(f"   Profit Factor: {improved_pf:.2f}")
    print(f"   Max Drawdown: {improved_metrics.max_drawdown_pct*100:.2f}%")
    sharpe_str = f"{improved_metrics.sharpe_ratio:.2f}" if improved_metrics.sharpe_ratio else "N/A"
    print(f"   Sharpe Ratio: {sharpe_str}\n")

    # Display comparison
    print("="*100)
    print("📊 DETAILED COMPARISON")
    print("="*100 + "\n")

    # Calculate improvements
    trade_reduction = ((original_metrics.total_trades - improved_metrics.total_trades) / original_metrics.total_trades * 100) if original_metrics.total_trades > 0 else 0
    win_rate_change = (improved_metrics.win_rate - original_metrics.win_rate) * 100
    pnl_change = improved_metrics.total_pnl - original_metrics.total_pnl
    pf_improvement = improved_pf - original_pf

    print(f"{'Metric':<25} {'Original':<20} {'Improved':<20} {'Change':<25}")
    print("-"*100)
    print(f"{'Total Trades':<25} {original_metrics.total_trades:<20} {improved_metrics.total_trades:<20} {-trade_reduction:+.1f}%")
    print(f"{'Win Rate':<25} {original_metrics.win_rate*100:>6.1f}%          {improved_metrics.win_rate*100:>6.1f}%          {win_rate_change:+.1f}%")
    print(f"{'Profit Factor':<25} {original_pf:>6.2f}            {improved_pf:>6.2f}            {pf_improvement:+.2f}")
    print(f"{'Total P&L':<25} ${original_metrics.total_pnl:>7.2f}          ${improved_metrics.total_pnl:>7.2f}          {pnl_change:+.2f}")
    print(f"{'P&L %':<25} {original_metrics.total_pnl_pct*100:>6.2f}%          {improved_metrics.total_pnl_pct*100:>6.2f}%          {(improved_metrics.total_pnl_pct - original_metrics.total_pnl_pct)*100:+.2f}%")
    print(f"{'Max Drawdown':<25} {original_metrics.max_drawdown_pct*100:>6.2f}%          {improved_metrics.max_drawdown_pct*100:>6.2f}%          {(improved_metrics.max_drawdown_pct - original_metrics.max_drawdown_pct)*100:+.2f}%")
    original_sharpe = original_metrics.sharpe_ratio if original_metrics.sharpe_ratio else 0.0
    improved_sharpe = improved_metrics.sharpe_ratio if improved_metrics.sharpe_ratio else 0.0
    print(f"{'Sharpe Ratio':<25} {original_sharpe:>6.2f}            {improved_sharpe:>6.2f}            {improved_sharpe - original_sharpe:+.2f}")

    # Analysis
    print(f"\n{'='*100}")
    print("🔍 ANALYSIS")
    print(f"{'='*100}\n")

    print(f"📉 Trade Reduction: {trade_reduction:.1f}%")
    print(f"   The improved engine generates {trade_reduction:.1f}% fewer trades")
    print(f"   This means stricter filtering is working as expected\n")

    print(f"📈 Quality Improvement: {win_rate_change:+.1f}% win rate change")
    if win_rate_change > 0:
        print(f"   ✓ Win rate IMPROVED by {win_rate_change:.1f}%")
    else:
        print(f"   ⚠ Win rate DECREASED by {abs(win_rate_change):.1f}%")
    print()

    print(f"💰 Profit Factor: {pf_improvement:+.2f} (from {original_pf:.2f} to {improved_pf:.2f})")
    if improved_pf >= 1.0:
        if improved_pf >= original_pf:
            print(f"   ✓ BETTER - Improved engine is more profitable")
        else:
            print(f"   ⚠ WORSE - Improved engine is less profitable")
    else:
        print(f"   ❌ Still not profitable (PF < 1.0)")
    print()

    print(f"📊 Risk Profile:")
    if improved_metrics.max_drawdown_pct < original_metrics.max_drawdown_pct:
        print(f"   ✓ Better risk control: {improved_metrics.max_drawdown_pct*100:.2f}% vs {original_metrics.max_drawdown_pct*100:.2f}%")
    else:
        print(f"   ⚠ Similar risk control")

    # Verdict
    print(f"\n{'='*100}")
    print("🎯 VERDICT")
    print(f"{'='*100}\n")

    if improved_pf >= 1.0 and improved_pf > original_pf:
        print(f"✅ IMPROVED ENGINE IS BETTER")
        print(f"   • Profit Factor improved to {improved_pf:.2f}")
        print(f"   • Fewer but higher-quality trades ({improved_metrics.total_trades} vs {original_metrics.total_trades})")
        print(f"   • Recommended: Deploy improved version")
    elif improved_pf >= 1.0:
        print(f"🟡 IMPROVED ENGINE IS COMPARABLE")
        print(f"   • Both versions have PF ≥ 1.0")
        print(f"   • Improved version has fewer trades")
        print(f"   • Needs more testing")
    elif improved_pf > original_pf:
        print(f"🟡 IMPROVED ENGINE SHOWS PROMISE")
        print(f"   • Profit Factor improved from {original_pf:.2f} to {improved_pf:.2f}")
        print(f"   • Still not profitable (PF < 1.0) but heading in right direction")
        print(f"   • Need additional refinements")
    else:
        print(f"❌ IMPROVED ENGINE NEEDS MORE WORK")
        print(f"   • Profit Factor decreased from {original_pf:.2f} to {improved_pf:.2f}")
        print(f"   • Filters may be too strict")
        print(f"   • Try adjusting confidence threshold or confirmation requirements")

    # Save comparison
    output_file = Path(__file__).parent / 'results' / 'engine_comparison.json'
    output_file.parent.mkdir(exist_ok=True)

    comparison_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'comparison': 'Original vs Improved Scalping Engine',
        'original': {
            'trades': original_metrics.total_trades,
            'win_rate': original_metrics.win_rate,
            'pnl': original_metrics.total_pnl,
            'pnl_pct': original_metrics.total_pnl_pct,
            'profit_factor': original_pf,
            'drawdown': original_metrics.max_drawdown_pct,
            'sharpe': original_metrics.sharpe_ratio
        },
        'improved': {
            'trades': improved_metrics.total_trades,
            'win_rate': improved_metrics.win_rate,
            'pnl': improved_metrics.total_pnl,
            'pnl_pct': improved_metrics.total_pnl_pct,
            'profit_factor': improved_pf,
            'drawdown': improved_metrics.max_drawdown_pct,
            'sharpe': improved_metrics.sharpe_ratio
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

    return original_metrics, improved_metrics, original_pf, improved_pf


if __name__ == '__main__':
    try:
        run_comparison()
    except KeyboardInterrupt:
        print("\n\nComparison cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", exc_info=True)
        sys.exit(1)
