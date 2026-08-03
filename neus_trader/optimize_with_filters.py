#!/usr/bin/env python3
"""
Entry Filter Optimization

Tests different entry signal filtering levels to find the configuration
that maximizes Profit Factor by reducing low-confidence trades.

Hypothesis: Fewer, higher-confidence trades = Better Profit Factor
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

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('FilterOptimizer')


class FilteredScalpingEngine(GoldenHourScalpingEngine):
    """Extended engine with configurable entry filters."""

    def __init__(self, symbol: str, initial_capital: float = 10000.0,
                 confidence_threshold: float = 0.5, max_daily_trades: int = 100):
        super().__init__(symbol, initial_capital)
        self.confidence_threshold = confidence_threshold
        self.max_daily_trades = max_daily_trades
        self.daily_trade_count = 0
        self.last_trade_date = None

    def process_candle(self, candle: dict) -> dict:
        """Process candle with filtering."""
        # Reset daily counter
        current_date = candle['timestamp'].date() if hasattr(candle['timestamp'], 'date') else None
        if current_date and current_date != self.last_trade_date:
            self.daily_trade_count = 0
            self.last_trade_date = current_date

        # Check daily limit
        if self.daily_trade_count >= self.max_daily_trades:
            return None

        # Call parent to get signal
        result = super().process_candle(candle)

        # Apply confidence filter
        if result and 'confidence' in result:
            if result['confidence'] < self.confidence_threshold:
                return None  # Reject low-confidence signal
            self.daily_trade_count += 1

        return result


def generate_test_data(days: int = 30, symbol: str = 'ETHUSDT') -> pd.DataFrame:
    """Generate realistic synthetic data."""
    num_candles = days * 288
    timestamps = pd.date_range(
        end=datetime.utcnow(),
        periods=num_candles,
        freq='5min'
    )

    np.random.seed(hash(symbol) % 2**32)
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
    """Calculate profit factor from metrics."""
    if metrics.total_trades == 0:
        return 0.0

    gross_profit = 0.0
    gross_loss = 0.0

    for trade in metrics.trades:
        pnl = trade.get('pnl', 0)
        if pnl > 0:
            gross_profit += pnl
        else:
            gross_loss += abs(pnl)

    if gross_loss == 0:
        return 0.0

    return gross_profit / gross_loss


def test_filter_levels(data: pd.DataFrame, symbol: str = 'ETHUSDT'):
    """Test different confidence threshold levels."""

    print("\n" + "="*90)
    print("ENTRY FILTER OPTIMIZATION - Testing Confidence Thresholds")
    print("="*90 + "\n")

    print(f"📊 Testing {symbol}")
    print(f"   Data: {len(data)} candles ({(len(data)/288):.1f} days)\n")

    # Test different thresholds
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    results = []

    print(f"{'Threshold':<12} {'Trades':<10} {'Win%':<10} {'P&L':<15} {'Profit Factor':<15} {'Drawdown':<12}")
    print("-"*90)

    for threshold in thresholds:
        # Create filtered engine
        engine = FilteredScalpingEngine(
            symbol=symbol,
            initial_capital=10000.0,
            confidence_threshold=threshold
        )

        # Run backtest
        backtester = HistoricalBacktester(engine)
        metrics = backtester.run_backtest(data)

        # Calculate metrics
        pf = calculate_profit_factor(metrics)
        win_rate = metrics.win_rate if metrics.total_trades > 0 else 0

        result = {
            'threshold': threshold,
            'trades': metrics.total_trades,
            'win_rate': win_rate,
            'pnl': metrics.total_pnl,
            'pnl_pct': metrics.total_pnl_pct,
            'profit_factor': pf,
            'drawdown': metrics.max_drawdown_pct,
            'sharpe': metrics.sharpe_ratio
        }
        results.append(result)

        status = '✓' if pf >= 1.0 else '❌'
        print(
            f"{threshold:<12.1f} {metrics.total_trades:<10} "
            f"{win_rate*100:>6.1f}%  ${metrics.total_pnl:>8.2f}    "
            f"{pf:>6.2f} {status:<8} {metrics.max_drawdown_pct*100:>6.2f}%"
        )

    # Find best performer
    best = max(results, key=lambda x: x['profit_factor'])

    print("\n" + "="*90)
    print("🏆 BEST CONFIGURATION (By Profit Factor)")
    print("="*90 + "\n")

    print(f"Confidence Threshold: {best['threshold']:.1f}")
    print(f"Trades Generated: {best['trades']}")
    print(f"Win Rate: {best['win_rate']*100:.1f}%")
    print(f"Total P&L: ${best['pnl']:.2f} ({best['pnl_pct']*100:.2f}%)")
    print(f"Profit Factor: {best['profit_factor']:.2f}")
    print(f"Max Drawdown: {best['drawdown']*100:.2f}%")
    print(f"Sharpe Ratio: {best['sharpe']:.2f}")

    # Analysis
    print(f"\n{'='*90}")
    print("💡 INSIGHTS")
    print(f"{'='*90}\n")

    # Trend analysis
    pfs = [r['profit_factor'] for r in results]
    trades_by_threshold = [r['trades'] for r in results]

    print(f"📊 Key Findings:")
    print(f"   Profit Factor Range: {min(pfs):.2f} to {max(pfs):.2f}")
    print(f"   Best Threshold: {best['threshold']:.1f}")
    print(f"   Trades at best: {best['trades']} (vs {results[0]['trades']} at 0.3)")
    print(f"   Reduction in trades: {((results[0]['trades'] - best['trades']) / results[0]['trades'] * 100):.1f}%")

    profitable = sum(1 for r in results if r['profit_factor'] >= 1.0)
    print(f"   Configurations with PF ≥ 1.0: {profitable}/{len(results)}")

    print(f"\n💡 Interpretation:")
    if best['profit_factor'] >= 1.5:
        print(f"   ✅ Excellent - Filtering significantly improves profitability")
        print(f"   Strategy: Use threshold {best['threshold']:.1f} for live trading")
    elif best['profit_factor'] >= 1.0:
        print(f"   🟡 Acceptable - Filtering helps but needs close monitoring")
        print(f"   Strategy: Consider threshold {best['threshold']:.1f} with risk limits")
    else:
        print(f"   ❌ Still unprofitable - Filtering alone insufficient")
        print(f"   Strategy: Need additional improvements (better indicators, position sizing)")

    # Save results
    output_file = Path(__file__).parent / 'results' / 'filter_optimization.json'
    output_file.parent.mkdir(exist_ok=True)

    data_to_save = {
        'timestamp': datetime.utcnow().isoformat(),
        'optimization': 'Entry Confidence Filtering',
        'symbol': symbol,
        'results': results,
        'best_config': {
            'threshold': best['threshold'],
            'trades': best['trades'],
            'win_rate': best['win_rate'],
            'profit_factor': best['profit_factor']
        }
    }

    with open(output_file, 'w') as f:
        json.dump(data_to_save, f, indent=2)

    print(f"\n✓ Results saved to {output_file}\n")

    return results, best


def main():
    """Main optimizer."""
    print("\n" + "="*90)
    print("ENTRY FILTER OPTIMIZATION")
    print("Testing different confidence thresholds to improve Profit Factor")
    print("="*90)

    # Generate test data
    print("\n📊 Generating test data...")
    data = generate_test_data(30, 'ETHUSDT')
    print(f"   {len(data)} candles generated\n")

    # Test filters
    results, best = test_filter_levels(data, 'ETHUSDT')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOptimization cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        sys.exit(1)
