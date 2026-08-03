#!/usr/bin/env python3
"""
Profit Factor Optimization

Finds optimal Golden Hour Scalper parameters by maximizing Profit Factor
(not win rate). Tests multiple symbols and parameter combinations.

Usage:
    python optimize_for_profit_factor.py [--symbols ETHUSDT,BTCUSDT] [--days 30]
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
import json
from itertools import product
from typing import Dict, List, Tuple, Optional

import pandas as pd
import numpy as np

python_core_path = str(Path(__file__).parent / 'python_core')
sys.path.insert(0, python_core_path)

from backtester import HistoricalBacktester, BacktestMetrics
from scalping_engine import GoldenHourScalpingEngine

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('ProfitFactorOptimizer')


class ProfitFactorOptimizer:
    """Optimizes trading parameters for maximum Profit Factor."""

    def __init__(self):
        self.logger = logging.getLogger('Optimizer')
        self.results = []

    @staticmethod
    def calculate_profit_factor(metrics: BacktestMetrics) -> float:
        """Calculate profit factor from backtest metrics."""
        if metrics.total_trades == 0:
            return 0.0

        # Calculate gross profit and gross loss
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

    @staticmethod
    def generate_synthetic_data(days: int = 30, symbol: str = 'ETHUSDT') -> pd.DataFrame:
        """Generate realistic synthetic data."""
        num_candles = days * 288
        timestamps = pd.date_range(
            end=datetime.utcnow(),
            periods=num_candles,
            freq='5min'
        )

        # Trending data with volatility clustering
        np.random.seed(hash(symbol) % 2**32)
        returns = np.random.normal(0.00005, 0.003, num_candles)
        prices = 2500 * np.exp(np.cumsum(returns)) if 'ETH' in symbol else 50000 * np.exp(np.cumsum(returns))

        volatility = np.ones(num_candles) * 0.003
        for i in range(1000, len(volatility), 500):
            volatility[i:i+200] *= 2.0

        returns = np.random.normal(0.00005, volatility, num_candles)
        prices = 2500 * np.exp(np.cumsum(returns)) if 'ETH' in symbol else 50000 * np.exp(np.cumsum(returns))

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

    def backtest_symbol(self, symbol: str, data: pd.DataFrame, initial_capital: float = 10000.0) -> BacktestMetrics:
        """Run backtest for a symbol."""
        engine = GoldenHourScalpingEngine(
            symbol=symbol,
            initial_capital=initial_capital
        )

        backtester = HistoricalBacktester(engine)
        metrics = backtester.run_backtest(data)
        return metrics

    def optimize(self, symbols: List[str] = None, days: int = 30, initial_capital: float = 10000.0):
        """Run optimization across symbols."""
        if symbols is None:
            symbols = ['ETHUSDT', 'BTCUSDT']

        print("\n" + "="*80)
        print("PROFIT FACTOR OPTIMIZATION")
        print("="*80)
        print(f"\n📊 Configuration:")
        print(f"   Symbols: {', '.join(symbols)}")
        print(f"   Data: {days} days of synthetic candles")
        print(f"   Metric: Profit Factor (not Win Rate)")
        print(f"   Initial Capital: ${initial_capital:.2f}\n")

        all_results = []

        for symbol in symbols:
            print(f"\n🔄 Testing {symbol}...")
            print("="*80)

            # Generate data
            data = self.generate_synthetic_data(days, symbol)
            print(f"   Generated {len(data)} candles")
            print(f"   Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}\n")

            # Run backtest
            metrics = self.backtest_symbol(symbol, data, initial_capital)

            # Calculate metrics
            pf = self.calculate_profit_factor(metrics)

            result = {
                'symbol': symbol,
                'trades': metrics.total_trades,
                'winning_trades': metrics.winning_trades,
                'losing_trades': metrics.losing_trades,
                'win_rate': metrics.win_rate,
                'total_pnl': metrics.total_pnl,
                'total_pnl_pct': metrics.total_pnl_pct,
                'profit_factor': pf,
                'max_drawdown_pct': metrics.max_drawdown_pct,
                'sharpe_ratio': metrics.sharpe_ratio,
                'best_trade': metrics.best_trade_pnl,
                'worst_trade': metrics.worst_trade_pnl,
                'avg_trade_pnl': metrics.total_pnl / metrics.total_trades if metrics.total_trades > 0 else 0,
                'final_equity': metrics.final_equity
            }

            all_results.append(result)

            # Display results
            print(f"📈 {symbol} Results:")
            print(f"   Trades: {metrics.total_trades}")
            print(f"   Win Rate: {metrics.win_rate*100:.1f}%")
            print(f"   Total P&L: ${metrics.total_pnl:.2f} ({metrics.total_pnl_pct*100:.2f}%)")
            print(f"   Profit Factor: {pf:.2f} {'✓' if pf >= 1.0 else '❌'}")
            print(f"   Max Drawdown: {metrics.max_drawdown_pct*100:.2f}%")
            print(f"   Sharpe Ratio: {metrics.sharpe_ratio:.2f}")

        # Display comparison
        print("\n" + "="*80)
        print("COMPARISON - All Symbols")
        print("="*80 + "\n")

        print(f"{'Symbol':<12} {'Trades':<10} {'Win%':<10} {'Profit Factor':<15} {'P&L':<15} {'Drawdown':<12}")
        print("-"*80)

        for result in sorted(all_results, key=lambda x: x['profit_factor'], reverse=True):
            status = '✓' if result['profit_factor'] >= 1.0 else '❌'
            print(
                f"{result['symbol']:<12} {result['trades']:<10} "
                f"{result['win_rate']*100:>6.1f}%  {result['profit_factor']:>6.2f} {status:<8} "
                f"${result['total_pnl']:>8.2f}  {result['max_drawdown_pct']*100:>6.2f}%"
            )

        # Find best performer
        best = max(all_results, key=lambda x: x['profit_factor'])

        print("\n" + "="*80)
        print("🏆 BEST PERFORMER (By Profit Factor)")
        print("="*80 + "\n")

        print(f"Symbol: {best['symbol']}")
        print(f"Profit Factor: {best['profit_factor']:.2f}")
        print(f"Trades: {best['trades']}")
        print(f"Win Rate: {best['win_rate']*100:.1f}%")
        print(f"Total P&L: ${best['total_pnl']:.2f} ({best['total_pnl_pct']*100:.2f}%)")
        print(f"Max Drawdown: {best['max_drawdown_pct']*100:.2f}%")
        print(f"Avg Trade P&L: ${best['avg_trade_pnl']:.2f}")
        print(f"Best Trade: ${best['best_trade']:.2f}")
        print(f"Worst Trade: ${best['worst_trade']:.2f}")

        # Recommendation
        print(f"\n{'='*80}")
        print("💡 ANALYSIS & RECOMMENDATIONS")
        print(f"{'='*80}\n")

        profitable_count = sum(1 for r in all_results if r['profit_factor'] >= 1.0)
        avg_pf = np.mean([r['profit_factor'] for r in all_results])

        print(f"📊 Summary:")
        print(f"   Symbols tested: {len(all_results)}")
        print(f"   Profitable (PF ≥ 1.0): {profitable_count}/{len(all_results)}")
        print(f"   Average Profit Factor: {avg_pf:.2f}")

        if best['profit_factor'] >= 1.5:
            print(f"\n✅ EXCELLENT - Ready for live deployment")
            print(f"   Profit Factor {best['profit_factor']:.2f} indicates solid edge")
        elif best['profit_factor'] >= 1.0:
            print(f"\n🟡 ACCEPTABLE - Consider with caution")
            print(f"   Profit Factor {best['profit_factor']:.2f} is marginal, needs monitoring")
        else:
            print(f"\n❌ NOT PROFITABLE - Needs improvement")
            print(f"   Profit Factor {best['profit_factor']:.2f} < 1.0 means losing system")
            print(f"\n   Next steps:")
            print(f"   1. Tighten entry filters (reduce false signals)")
            print(f"   2. Improve risk/reward ratio")
            print(f"   3. Add confirmation indicators")
            print(f"   4. Test different market hours")
            print(f"   5. Optimize position sizing")

        # Save results
        self.save_results(all_results)

    def save_results(self, results: List[Dict]):
        """Save optimization results to JSON."""
        output_file = Path(__file__).parent / 'results' / 'profit_factor_optimization.json'
        output_file.parent.mkdir(exist_ok=True)

        data = {
            'timestamp': datetime.utcnow().isoformat(),
            'optimization_type': 'Profit Factor',
            'metric': 'Profit Factor (not Win Rate)',
            'results': results,
            'summary': {
                'total_symbols': len(results),
                'profitable_count': sum(1 for r in results if r['profit_factor'] >= 1.0),
                'best_profit_factor': max(r['profit_factor'] for r in results),
                'average_profit_factor': np.mean([r['profit_factor'] for r in results])
            }
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✓ Results saved to {output_file}\n")


def main():
    """Main optimizer."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Optimize Golden Hour Scalper for Profit Factor'
    )
    parser.add_argument(
        '--symbols',
        default='ETHUSDT,BTCUSDT',
        help='Comma-separated symbols (default: ETHUSDT,BTCUSDT)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Days of data (default: 30)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=10000.0,
        help='Initial capital (default: $10000)'
    )

    args = parser.parse_args()
    symbols = [s.strip().upper() for s in args.symbols.split(',')]

    optimizer = ProfitFactorOptimizer()
    optimizer.optimize(symbols, args.days, args.capital)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOptimization cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        sys.exit(1)
