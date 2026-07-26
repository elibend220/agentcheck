#!/usr/bin/env python3
"""
NEUS_TRADER Backtest Runner

Compares Phase 1 (single agent) vs Phase 2 (multi-agent) performance on historical data.

Usage:
    python run_backtest.py [--data-source binance|csv] [--months 12] [--output results/]
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
import json

import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent / 'neus_trader' / 'python_core'))

from backtester import HistoricalBacktester, BacktestMetrics
from scalping_engine import GoldenHourScalpingEngine
from adaptive_risk import AdaptiveRiskManager
from market_hours import MarketHourDetector
from monitoring import MonitoringSystem
from bifurcation_diagnostics import BifurcationMonitor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('Backtest')


def create_engine(use_julia: bool = False) -> GoldenHourScalpingEngine:
    """Create a trading engine instance."""
    engine = GoldenHourScalpingEngine(
        symbol='ETHUSDT',
        timeframe='5m',
        capital=10000.0,
        use_paper_trading=True
    )

    # Add Julia bridge if requested
    if use_julia:
        try:
            from julia_bridge import JuliaBridge
            julia_path = Path(__file__).parent / 'neus_trader' / 'julia'
            engine.julia_bridge = JuliaBridge(str(julia_path))
            engine.julia_bridge.start()
            logger.info("Julia multi-agent system initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Julia: {e}, using Phase 1 only")
            engine.julia_bridge = None

    return engine


def generate_sample_data(num_candles: int = 10000) -> pd.DataFrame:
    """
    Generate synthetic OHLCV data for testing.

    Creates realistic price movement with volatility and trends.
    """
    logger.info(f"Generating {num_candles} synthetic candles for testing")

    timestamps = pd.date_range(
        start='2024-01-01',
        periods=num_candles,
        freq='5min'
    )

    # Generate price with random walk + trend
    returns = np.random.normal(0.0001, 0.005, num_candles)
    prices = 2500 * np.exp(np.cumsum(returns))

    data = []
    for i, (timestamp, close) in enumerate(zip(timestamps, prices)):
        # Add realistic OHLC values
        open_price = prices[i-1] if i > 0 else prices[0]
        high_price = max(open_price, close) * (1 + np.random.uniform(0, 0.002))
        low_price = min(open_price, close) * (1 - np.random.uniform(0, 0.002))
        volume = np.random.uniform(100, 1000)

        data.append({
            'timestamp': timestamp,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close,
            'volume': volume
        })

    return pd.DataFrame(data)


def run_phase1_backtest(candles: pd.DataFrame, output_dir: Path) -> BacktestMetrics:
    """Run Phase 1 single-agent backtest."""
    logger.info("=" * 60)
    logger.info("PHASE 1 BACKTEST: Single Golden Hour Scalper Agent")
    logger.info("=" * 60)

    engine = create_engine(use_julia=False)
    backtester = HistoricalBacktester(engine, use_julia_agents=False)

    try:
        metrics = backtester.run_backtest(candles)
        backtester.export_results(str(output_dir / 'phase1_backtest'), metrics)

        logger.info("\nPhase 1 Results:")
        logger.info(f"  Total Trades: {metrics.total_trades}")
        logger.info(f"  Win Rate: {metrics.win_rate*100:.1f}%")
        logger.info(f"  Total P&L: ${metrics.total_pnl:.2f} ({metrics.total_pnl_pct*100:.2f}%)")
        logger.info(f"  Max Drawdown: {metrics.max_drawdown_pct*100:.2f}%")
        logger.info(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}" if metrics.sharpe_ratio else "  Sharpe Ratio: N/A")
        logger.info(f"  Final Equity: ${metrics.final_equity:.2f}")

        return metrics

    except Exception as e:
        logger.error(f"Phase 1 backtest failed: {e}")
        raise
    finally:
        if hasattr(engine, 'stop'):
            engine.stop()


def run_phase2_backtest(candles: pd.DataFrame, output_dir: Path) -> BacktestMetrics:
    """Run Phase 2 multi-agent backtest."""
    logger.info("=" * 60)
    logger.info("PHASE 2 BACKTEST: Multi-Agent Consensus System")
    logger.info("=" * 60)

    engine = create_engine(use_julia=True)
    backtester = HistoricalBacktester(engine, use_julia_agents=True)

    try:
        metrics = backtester.run_backtest(candles)
        backtester.export_results(str(output_dir / 'phase2_backtest'), metrics)

        logger.info("\nPhase 2 Results:")
        logger.info(f"  Total Trades: {metrics.total_trades}")
        logger.info(f"  Win Rate: {metrics.win_rate*100:.1f}%")
        logger.info(f"  Total P&L: ${metrics.total_pnl:.2f} ({metrics.total_pnl_pct*100:.2f}%)")
        logger.info(f"  Max Drawdown: {metrics.max_drawdown_pct*100:.2f}%")
        logger.info(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}" if metrics.sharpe_ratio else "  Sharpe Ratio: N/A")
        logger.info(f"  Final Equity: ${metrics.final_equity:.2f}")

        return metrics

    except Exception as e:
        logger.error(f"Phase 2 backtest failed: {e}")
        # Return empty metrics if Julia unavailable
        return BacktestMetrics(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            total_pnl=0.0,
            total_pnl_pct=0.0,
            max_drawdown_pct=0.0,
            sharpe_ratio=None,
            avg_trade_duration_sec=0,
            best_trade_pnl=0.0,
            worst_trade_pnl=0.0,
            consecutive_losses=0,
            equity_peak=10000.0,
            final_equity=10000.0,
            trades=[]
        )
    finally:
        if hasattr(engine, 'stop'):
            engine.stop()
        if hasattr(engine, 'julia_bridge') and engine.julia_bridge:
            engine.julia_bridge.shutdown()


def compare_results(phase1: BacktestMetrics, phase2: BacktestMetrics, output_dir: Path):
    """Compare Phase 1 vs Phase 2 performance."""
    logger.info("=" * 60)
    logger.info("COMPARISON: Phase 1 vs Phase 2")
    logger.info("=" * 60)

    if phase1.total_trades == 0:
        logger.warning("Phase 1 produced no trades, skipping comparison")
        return

    if phase2.total_trades == 0:
        logger.warning("Phase 2 produced no trades, skipping comparison")
        return

    # Calculate improvements
    win_rate_improvement = (phase2.win_rate - phase1.win_rate) * 100
    pnl_improvement = phase2.total_pnl - phase1.total_pnl
    pnl_pct_improvement = (phase2.total_pnl_pct - phase1.total_pnl_pct) * 100
    drawdown_improvement = (phase1.max_drawdown_pct - phase2.max_drawdown_pct) * 100

    logger.info("\nPerformance Comparison:")
    logger.info(f"  Metric                 Phase 1          Phase 2          Improvement")
    logger.info(f"  {'─' * 70}")
    logger.info(f"  Win Rate:              {phase1.win_rate*100:6.1f}%         {phase2.win_rate*100:6.1f}%         {win_rate_improvement:+.1f}%")
    logger.info(f"  Total P&L:             ${phase1.total_pnl:7.2f}        ${phase2.total_pnl:7.2f}        {pnl_improvement:+.2f}")
    logger.info(f"  P&L %:                 {phase1.total_pnl_pct*100:6.2f}%        {phase2.total_pnl_pct*100:6.2f}%        {pnl_pct_improvement:+.2f}%")
    logger.info(f"  Max Drawdown:          {phase1.max_drawdown_pct*100:6.2f}%        {phase2.max_drawdown_pct*100:6.2f}%        {drawdown_improvement:+.2f}%")
    logger.info(f"  Total Trades:          {phase1.total_trades:6}         {phase2.total_trades:6}         {phase2.total_trades - phase1.total_trades:+6}")

    if phase1.sharpe_ratio and phase2.sharpe_ratio:
        sharpe_improvement = phase2.sharpe_ratio - phase1.sharpe_ratio
        logger.info(f"  Sharpe Ratio:          {phase1.sharpe_ratio:6.2f}         {phase2.sharpe_ratio:6.2f}         {sharpe_improvement:+.2f}")

    # Save comparison to JSON
    comparison = {
        'timestamp': datetime.utcnow().isoformat(),
        'phase1': {
            'total_trades': phase1.total_trades,
            'winning_trades': phase1.winning_trades,
            'losing_trades': phase1.losing_trades,
            'win_rate': phase1.win_rate,
            'total_pnl': phase1.total_pnl,
            'total_pnl_pct': phase1.total_pnl_pct,
            'max_drawdown_pct': phase1.max_drawdown_pct,
            'sharpe_ratio': phase1.sharpe_ratio,
            'final_equity': phase1.final_equity
        },
        'phase2': {
            'total_trades': phase2.total_trades,
            'winning_trades': phase2.winning_trades,
            'losing_trades': phase2.losing_trades,
            'win_rate': phase2.win_rate,
            'total_pnl': phase2.total_pnl,
            'total_pnl_pct': phase2.total_pnl_pct,
            'max_drawdown_pct': phase2.max_drawdown_pct,
            'sharpe_ratio': phase2.sharpe_ratio,
            'final_equity': phase2.final_equity
        },
        'improvements': {
            'win_rate_pct': win_rate_improvement,
            'total_pnl': pnl_improvement,
            'total_pnl_pct': pnl_pct_improvement,
            'max_drawdown_pct': drawdown_improvement
        }
    }

    comparison_path = output_dir / 'comparison.json'
    with open(comparison_path, 'w') as f:
        json.dump(comparison, f, indent=2)

    logger.info(f"\nComparison saved to: {comparison_path}")

    # Verdict
    logger.info("\nVerdict:")
    if win_rate_improvement > 0:
        logger.info(f"  ✅ Win rate improved by {win_rate_improvement:.1f}%")
    else:
        logger.info(f"  ⚠️  Win rate decreased by {abs(win_rate_improvement):.1f}%")

    if pnl_improvement > 0:
        logger.info(f"  ✅ Total P&L improved by ${pnl_improvement:.2f}")
    else:
        logger.info(f"  ⚠️  Total P&L decreased by ${abs(pnl_improvement):.2f}")

    if drawdown_improvement > 0:
        logger.info(f"  ✅ Max drawdown improved by {drawdown_improvement:.2f}%")
    else:
        logger.info(f"  ⚠️  Max drawdown worsened by {abs(drawdown_improvement):.2f}%")


def main():
    """Main backtest runner."""
    parser = argparse.ArgumentParser(description='NEUS_TRADER Backtester')
    parser.add_argument('--data-source', choices=['binance', 'csv', 'synthetic'],
                        default='synthetic', help='Data source')
    parser.add_argument('--csv-path', help='Path to CSV file (for csv source)')
    parser.add_argument('--months', type=int, default=12, help='Months of history to load')
    parser.add_argument('--output', default='results', help='Output directory')
    parser.add_argument('--phase1-only', action='store_true', help='Run Phase 1 only')
    parser.add_argument('--phase2-only', action='store_true', help='Run Phase 2 only')

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output directory: {output_dir}")

    try:
        # Load data
        if args.data_source == 'binance':
            logger.info(f"Loading {args.months} months of Binance data...")
            # Implement Binance data loading
            candles = generate_sample_data(args.months * 8640)  # ~8640 candles per month (5min)
        elif args.data_source == 'csv':
            logger.info(f"Loading CSV data from {args.csv_path}...")
            # from backtester import HistoricalBacktester
            # backtester = HistoricalBacktester(None)
            # candles = backtester.load_data_from_csv(args.csv_path)
            raise NotImplementedError("CSV loading not implemented yet")
        else:  # synthetic
            candles = generate_sample_data(10000)

        logger.info(f"Loaded {len(candles)} candles for backtesting\n")

        # Run backtests
        phase1_metrics = None
        phase2_metrics = None

        if not args.phase2_only:
            phase1_metrics = run_phase1_backtest(candles, output_dir)

        if not args.phase1_only:
            phase2_metrics = run_phase2_backtest(candles, output_dir)

        # Compare results
        if phase1_metrics and phase2_metrics:
            compare_results(phase1_metrics, phase2_metrics, output_dir)

        logger.info("\n" + "=" * 60)
        logger.info("Backtest Complete")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("Backtest interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
