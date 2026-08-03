#!/usr/bin/env python3
"""
Real Data Backtest: EMA vs EMA + Institutional Flow

Tests on 2 weeks of realistic ETHUSDT data with:
- Trend phases
- Mean reversion
- Institutional order blocks
- Realistic volume patterns
"""

import sys
import logging
from pathlib import Path
import json
import pandas as pd

# Add to path
python_core_path = str(Path(__file__).parent / 'python_core')
sys.path.insert(0, python_core_path)

from paper_trading import PaperTradingEngine
from paper_trading_enhanced import EnhancedPaperTradingEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('RealDataBacktest')


def load_data():
    """Load realistic historical data."""
    logger.info("Loading historical ETHUSDT data...")

    data_file = Path(__file__).parent / 'data' / 'ethusdt_2weeks.csv'

    if not data_file.exists():
        logger.error(f"Data file not found: {data_file}")
        raise FileNotFoundError(f"Data file not found: {data_file}")

    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    logger.info(f"Loaded {len(df)} candles from {df['timestamp'].min()} to {df['timestamp'].max()}")
    logger.info(f"Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    logger.info(f"Volume range: {df['volume'].min():.0f} - {df['volume'].max():.0f}")

    return df


def run_traditional_backtest(data: pd.DataFrame) -> dict:
    """Run traditional EMA-only strategy."""
    logger.info("\n" + "="*70)
    logger.info("TRADITIONAL BACKTEST: EMA(9/21) only")
    logger.info("="*70)

    engine = PaperTradingEngine(
        symbol='ETHUSDT',
        initial_capital=10000.0,
        risk_per_trade=0.01,  # Increased to 1% for meaningful position sizes
        max_positions=3
    )

    for idx, candle in data.iterrows():
        engine.process_candle(candle.to_dict())

        if (idx + 1) % 500 == 0:
            logger.info(f"Processed {idx+1}/{len(data)} candles | Capital: ${engine.current_capital:.2f}")

    # Calculate metrics
    total_pnl = engine.current_capital - engine.initial_capital
    win_trades = sum(1 for t in engine.closed_trades if t.pnl and t.pnl > 0)
    total_trades = len(engine.closed_trades)
    win_rate = win_trades / total_trades if total_trades > 0 else 0.0

    metrics = {
        'strategy': 'EMA_ONLY',
        'total_trades': total_trades,
        'winning_trades': win_trades,
        'losing_trades': total_trades - win_trades,
        'win_rate': win_rate,
        'total_pnl': total_pnl,
        'total_pnl_pct': (total_pnl / engine.initial_capital) * 100,
        'final_capital': engine.current_capital,
    }

    logger.info(f"Total Trades: {metrics['total_trades']}")
    logger.info(f"Win Rate: {metrics['win_rate']*100:.1f}%")
    logger.info(f"Total P&L: ${metrics['total_pnl']:.2f} ({metrics['total_pnl_pct']:.2f}%)")
    logger.info(f"Final Capital: ${metrics['final_capital']:.2f}")

    return metrics


def run_enhanced_backtest(data: pd.DataFrame) -> dict:
    """Run EMA + Institutional Flow strategy."""
    logger.info("\n" + "="*70)
    logger.info("ENHANCED BACKTEST: EMA(9/21) + Institutional Flow")
    logger.info("="*70)

    engine = EnhancedPaperTradingEngine(
        symbol='ETHUSDT',
        initial_capital=10000.0,
        risk_per_trade=0.01,  # Increased to 1% for meaningful position sizes
        max_positions=3,
        use_institutional_flow=True
    )

    for idx, candle in data.iterrows():
        engine.process_candle(candle.to_dict())

        if (idx + 1) % 500 == 0:
            logger.info(f"Processed {idx+1}/{len(data)} candles | Capital: ${engine.current_capital:.2f}")

    # Calculate metrics
    total_pnl = engine.current_capital - engine.initial_capital
    win_trades = sum(1 for t in engine.closed_trades if t.pnl and t.pnl > 0)
    total_trades = len(engine.closed_trades)
    win_rate = win_trades / total_trades if total_trades > 0 else 0.0

    signal_stats = engine.get_signal_statistics()

    metrics = {
        'strategy': 'EMA_FLOW',
        'total_trades': total_trades,
        'winning_trades': win_trades,
        'losing_trades': total_trades - win_trades,
        'win_rate': win_rate,
        'total_pnl': total_pnl,
        'total_pnl_pct': (total_pnl / engine.initial_capital) * 100,
        'final_capital': engine.current_capital,
        'signal_stats': {
            'ema_only': signal_stats['ema_only'],
            'ema_flow_combined': signal_stats['ema_flow_combined'],
            'flow_only': signal_stats['flow_only']
        }
    }

    logger.info(f"Total Trades: {metrics['total_trades']}")
    logger.info(f"Win Rate: {metrics['win_rate']*100:.1f}%")
    logger.info(f"Total P&L: ${metrics['total_pnl']:.2f} ({metrics['total_pnl_pct']:.2f}%)")
    logger.info(f"Final Capital: ${metrics['final_capital']:.2f}")
    logger.info(f"\nSignal Breakdown:")
    logger.info(f"  EMA only: {metrics['signal_stats']['ema_only']}")
    logger.info(f"  EMA + Flow combined: {metrics['signal_stats']['ema_flow_combined']}")
    logger.info(f"  Flow only: {metrics['signal_stats']['flow_only']}")

    return metrics


def compare_results(traditional: dict, enhanced: dict):
    """Compare results."""
    logger.info("\n" + "="*70)
    logger.info("COMPARISON: Traditional vs Enhanced")
    logger.info("="*70)

    logger.info(f"\n{'Metric':<30} {'EMA Only':<20} {'EMA + Flow':<20} {'Improvement':<15}")
    logger.info("-" * 85)

    # Trade count
    trade_diff = enhanced['total_trades'] - traditional['total_trades']
    trade_diff_pct = (trade_diff / traditional['total_trades']) * 100 if traditional['total_trades'] > 0 else 0
    logger.info(
        f"{'Total Trades':<30} {traditional['total_trades']:<20} "
        f"{enhanced['total_trades']:<20} {trade_diff_pct:+.1f}%"
    )

    # Win rate
    win_rate_improvement = (enhanced['win_rate'] - traditional['win_rate']) * 100
    logger.info(
        f"{'Win Rate':<30} {traditional['win_rate']*100:>18.1f}% "
        f"{enhanced['win_rate']*100:>18.1f}% {win_rate_improvement:+.1f}%"
    )

    # P&L
    pnl_diff = enhanced['total_pnl'] - traditional['total_pnl']
    logger.info(
        f"{'Total P&L ($)':<30} ${traditional['total_pnl']:>17.2f} "
        f"${enhanced['total_pnl']:>17.2f} ${pnl_diff:+.2f}"
    )

    # P&L %
    pnl_pct_diff = enhanced['total_pnl_pct'] - traditional['total_pnl_pct']
    logger.info(
        f"{'Total P&L (%)':<30} {traditional['total_pnl_pct']:>18.2f}% "
        f"{enhanced['total_pnl_pct']:>18.2f}% {pnl_pct_diff:+.2f}%"
    )

    # Efficiency
    traditional_per_trade = traditional['total_pnl'] / traditional['total_trades'] if traditional['total_trades'] > 0 else 0
    enhanced_per_trade = enhanced['total_pnl'] / enhanced['total_trades'] if enhanced['total_trades'] > 0 else 0
    efficiency_diff = enhanced_per_trade - traditional_per_trade

    logger.info(
        f"{'P&L per Trade':<30} ${traditional_per_trade:>17.4f} "
        f"${enhanced_per_trade:>17.4f} ${efficiency_diff:+.4f}"
    )

    # Summary
    logger.info("\n" + "="*70)
    logger.info("FINDINGS:")
    logger.info("="*70)

    if enhanced['total_trades'] < traditional['total_trades']:
        reduction = 100 * (1 - enhanced['total_trades']/traditional['total_trades'])
        logger.info(f"✓ Reduced signals by {reduction:.1f}%")

    if enhanced['win_rate'] > traditional['win_rate']:
        improvement = (enhanced['win_rate'] - traditional['win_rate']) * 100
        logger.info(f"✓ Improved win rate by {improvement:.1f}%")
    elif enhanced['win_rate'] < traditional['win_rate']:
        degradation = (traditional['win_rate'] - enhanced['win_rate']) * 100
        logger.warning(f"✗ Win rate degraded by {degradation:.1f}%")

    if enhanced['total_pnl'] > traditional['total_pnl']:
        logger.info(f"✓ Improved P&L by ${pnl_diff:.2f}")
    else:
        logger.warning(f"✗ P&L degraded by ${abs(pnl_diff):.2f}")

    # Save results
    results = {
        'data_period': f"2 weeks (4,032 candles)",
        'traditional': traditional,
        'enhanced': enhanced,
        'comparison': {
            'trade_reduction_pct': trade_diff_pct,
            'win_rate_improvement_pct': win_rate_improvement,
            'pnl_improvement_usd': pnl_diff,
            'pnl_improvement_pct': pnl_pct_diff,
            'efficiency_improvement': efficiency_diff
        }
    }

    results_file = Path(__file__).parent / 'results' / 'real_data_backtest.json'
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\nResults saved to {results_file}")
    return results


def main():
    logger.info("="*70)
    logger.info("Real Data Backtest: EMA vs EMA + Institutional Flow")
    logger.info("="*70)

    # Load data
    data = load_data()

    # Run backtests
    logger.info("\nRunning traditional backtest...")
    traditional = run_traditional_backtest(data)

    logger.info("\nRunning enhanced backtest...")
    enhanced = run_enhanced_backtest(data)

    # Compare
    compare_results(traditional, enhanced)

    logger.info("\n✅ Backtest complete!")


if __name__ == '__main__':
    main()
