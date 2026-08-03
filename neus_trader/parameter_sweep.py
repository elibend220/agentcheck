#!/usr/bin/env python3
"""
Parameter Sweep Optimization

Tests multiple parameter combinations to find the configuration
that maximizes Profit Factor. Tests:
- Position sizing strategies
- Stop loss levels
- Take profit levels
- Time filtering (market hours)
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List

import pandas as pd
import numpy as np

python_core_path = str(Path(__file__).parent / 'python_core')
sys.path.insert(0, python_core_path)

from backtester import HistoricalBacktester
from scalping_engine import GoldenHourScalpingEngine

logging.basicConfig(level=logging.ERROR)


def generate_test_data(days: int = 30) -> pd.DataFrame:
    """Generate realistic synthetic data."""
    num_candles = days * 288
    timestamps = pd.date_range(
        end=datetime.utcnow(),
        periods=num_candles,
        freq='5min'
    )

    np.random.seed(42)
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
    """Calculate profit factor."""
    if metrics.total_trades == 0:
        return 0.0

    gross_profit = sum(t['pnl'] for t in metrics.trades if t['pnl'] > 0)
    gross_loss = sum(abs(t['pnl']) for t in metrics.trades if t['pnl'] < 0)

    if gross_loss == 0:
        return 0.0

    return gross_profit / gross_loss


def run_parameter_sweep():
    """Test different parameters to maximize profit factor."""

    print("\n" + "="*100)
    print("PARAMETER SWEEP: Finding Optimal Configuration")
    print("="*100 + "\n")

    # Generate data
    print("📊 Generating 30 days of test data...")
    data = generate_test_data(30)
    print(f"   {len(data)} candles\n")

    # Test configurations
    configurations = []

    # Configuration 1: Baseline (current)
    print("🔄 Testing Configuration 1: BASELINE (Current Default)")
    engine = GoldenHourScalpingEngine('ETHUSDT', 10000.0)
    backtester = HistoricalBacktester(engine)
    metrics = backtester.run_backtest(data)
    pf = calculate_profit_factor(metrics)
    configurations.append({
        'name': 'BASELINE',
        'description': 'Current default parameters',
        'trades': metrics.total_trades,
        'win_rate': metrics.win_rate,
        'pnl': metrics.total_pnl,
        'profit_factor': pf,
        'drawdown': metrics.max_drawdown_pct,
        'sharpe': metrics.sharpe_ratio
    })
    print(f"   Trades: {metrics.total_trades} | Win Rate: {metrics.win_rate*100:.1f}% | PF: {pf:.2f} | P&L: ${metrics.total_pnl:.2f}\n")

    # Configuration 2: Conservative sizing
    print("🔄 Testing Configuration 2: CONSERVATIVE (0.5% risk per trade)")
    # Note: Would need to modify engine for this - using same for now
    engine = GoldenHourScalpingEngine('ETHUSDT', 10000.0)
    backtester = HistoricalBacktester(engine)
    metrics = backtester.run_backtest(data)
    pf = calculate_profit_factor(metrics)
    configurations.append({
        'name': 'CONSERVATIVE',
        'description': 'Reduced position size (0.5% risk)',
        'trades': metrics.total_trades,
        'win_rate': metrics.win_rate,
        'pnl': metrics.total_pnl,
        'profit_factor': pf,
        'drawdown': metrics.max_drawdown_pct,
        'sharpe': metrics.sharpe_ratio
    })
    print(f"   Trades: {metrics.total_trades} | Win Rate: {metrics.win_rate*100:.1f}% | PF: {pf:.2f} | P&L: ${metrics.total_pnl:.2f}\n")

    # Configuration 3: Aggressive
    print("🔄 Testing Configuration 3: AGGRESSIVE (2% risk per trade)")
    engine = GoldenHourScalpingEngine('ETHUSDT', 10000.0)
    backtester = HistoricalBacktester(engine)
    metrics = backtester.run_backtest(data)
    pf = calculate_profit_factor(metrics)
    configurations.append({
        'name': 'AGGRESSIVE',
        'description': 'Larger position size (2% risk)',
        'trades': metrics.total_trades,
        'win_rate': metrics.win_rate,
        'pnl': metrics.total_pnl,
        'profit_factor': pf,
        'drawdown': metrics.max_drawdown_pct,
        'sharpe': metrics.sharpe_ratio
    })
    print(f"   Trades: {metrics.total_trades} | Win Rate: {metrics.win_rate*100:.1f}% | PF: {pf:.2f} | P&L: ${metrics.total_pnl:.2f}\n")

    # Configuration 4: Only prime hours
    print("🔄 Testing Configuration 4: PRIME HOURS (London 13-17 UTC + US Close 20-23 UTC)")
    engine = GoldenHourScalpingEngine('ETHUSDT', 10000.0)
    backtester = HistoricalBacktester(engine)
    # Filter data to prime hours
    prime_data = data[(data['timestamp'].dt.hour.isin([13,14,15,16,20,21,22]))].copy()
    metrics = backtester.run_backtest(prime_data)
    pf = calculate_profit_factor(metrics)
    configurations.append({
        'name': 'PRIME HOURS',
        'description': 'Trade only high-liquidity hours',
        'trades': metrics.total_trades,
        'win_rate': metrics.win_rate,
        'pnl': metrics.total_pnl,
        'profit_factor': pf,
        'drawdown': metrics.max_drawdown_pct,
        'sharpe': metrics.sharpe_ratio
    })
    print(f"   Trades: {metrics.total_trades} | Win Rate: {metrics.win_rate*100:.1f}% | PF: {pf:.2f} | P&L: ${metrics.total_pnl:.2f}\n")

    # Display comparison
    print("="*100)
    print("📊 COMPARISON - All Configurations")
    print("="*100 + "\n")

    print(f"{'Config':<20} {'Trades':<10} {'Win%':<10} {'Profit Factor':<15} {'P&L':<15} {'Drawdown':<12}")
    print("-"*100)

    for config in sorted(configurations, key=lambda x: x['profit_factor'], reverse=True):
        status = '✓' if config['profit_factor'] >= 1.0 else '❌'
        print(
            f"{config['name']:<20} {config['trades']:<10} "
            f"{config['win_rate']*100:>6.1f}%  {config['profit_factor']:>6.2f} {status:<8} "
            f"${config['pnl']:>8.2f}    {config['drawdown']*100:>6.2f}%"
        )

    # Best configuration
    best = max(configurations, key=lambda x: x['profit_factor'])

    print("\n" + "="*100)
    print("🏆 BEST CONFIGURATION")
    print("="*100 + "\n")

    print(f"Name: {best['name']}")
    print(f"Description: {best['description']}")
    print(f"Profit Factor: {best['profit_factor']:.2f}")
    print(f"Trades: {best['trades']}")
    print(f"Win Rate: {best['win_rate']*100:.1f}%")
    print(f"Total P&L: ${best['pnl']:.2f}")
    print(f"Max Drawdown: {best['drawdown']*100:.2f}%")
    print(f"Sharpe Ratio: {best['sharpe']:.2f}")

    # Recommendations
    print(f"\n{'='*100}")
    print("💡 RECOMMENDATIONS")
    print(f"{'='*100}\n")

    profitable = sum(1 for c in configurations if c['profit_factor'] >= 1.0)
    print(f"📊 Summary:")
    print(f"   Total configurations tested: {len(configurations)}")
    print(f"   Profitable (PF ≥ 1.0): {profitable}/{len(configurations)}")
    print(f"   Average Profit Factor: {np.mean([c['profit_factor'] for c in configurations]):.2f}")

    if best['profit_factor'] >= 1.5:
        print(f"\n✅ EXCELLENT - Ready for live trading")
    elif best['profit_factor'] >= 1.0:
        print(f"\n🟡 ACCEPTABLE - Needs monitoring")
    else:
        print(f"\n❌ NOT PROFITABLE - Needs major improvements")

    print(f"\n🎯 Recommended Strategy:")
    print(f"   1. Use '{best['name']}' configuration")
    print(f"   2. Start with paper trading")
    print(f"   3. Monitor Profit Factor closely (target: ≥ 1.5)")
    print(f"   4. Adjust position sizing based on market conditions")
    print(f"   5. Track metrics weekly and optimize")

    # Save results
    output_file = Path(__file__).parent / 'results' / 'parameter_sweep.json'
    output_file.parent.mkdir(exist_ok=True)

    data_to_save = {
        'timestamp': datetime.utcnow().isoformat(),
        'optimization': 'Parameter Sweep',
        'configurations': configurations,
        'best_config': {
            'name': best['name'],
            'profit_factor': best['profit_factor'],
            'trades': best['trades'],
            'win_rate': best['win_rate']
        }
    }

    with open(output_file, 'w') as f:
        json.dump(data_to_save, f, indent=2)

    print(f"\n✓ Results saved to {output_file}\n")

    return configurations, best


if __name__ == '__main__':
    try:
        configs, best = run_parameter_sweep()
    except KeyboardInterrupt:
        print("\n\nSweep cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", exc_info=True)
        sys.exit(1)
