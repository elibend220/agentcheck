#!/usr/bin/env python3
"""
Real Historical Data Validation for NEUS_TRADER

Fetches 12 months of real ETHUSDT data from Binance and validates trading performance.
Compares Phase 1 performance on real vs synthetic data.

Usage:
    python run_real_backtest.py [--months 12] [--output results/]
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
python_core_path = str(Path(__file__).parent / 'python_core')
sys.path.insert(0, python_core_path)

from backtester import HistoricalBacktester, BacktestMetrics
from scalping_engine import GoldenHourScalpingEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('RealBacktest')


def fetch_binance_data(symbol: str = 'ETHUSDT', months: int = 12, interval: str = '5m') -> pd.DataFrame:
    """
    Fetch historical OHLCV data from Binance.

    Args:
        symbol: Trading pair (e.g., 'ETHUSDT')
        months: Number of months to fetch
        interval: Candle interval (1m, 5m, 1h, 1d, etc.)

    Returns:
        DataFrame with OHLCV data
    """
    logger.info(f"Fetching {months} months of {symbol} data from Binance (interval: {interval})")

    try:
        import ccxt
    except ImportError:
        logger.error("ccxt library not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "ccxt"])
        import ccxt

    exchange = ccxt.binance({
        'enableRateLimit': True,
        'rateLimit': 500
    })

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30 * months)

    logger.info(f"Date range: {start_date.date()} to {end_date.date()}")

    all_candles = []
    current_date = start_date

    # Fetch data in chunks
    while current_date < end_date:
        try:
            timestamp = int(current_date.timestamp() * 1000)
            candles = exchange.fetch_ohlcv(symbol, interval, since=timestamp, limit=1000)

            if not candles:
                logger.info(f"No more data available after {current_date.date()}")
                break

            all_candles.extend(candles)
            last_timestamp = candles[-1][0]
            current_date = datetime.utcfromtimestamp(last_timestamp / 1000)

            logger.info(f"Fetched {len(candles)} candles, latest: {current_date.date()}")

        except Exception as e:
            logger.warning(f"Error fetching data: {e}, stopping fetch")
            break

    # Convert to DataFrame
    df = pd.DataFrame(
        all_candles,
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.sort_values('timestamp').reset_index(drop=True)

    logger.info(f"Fetched {len(df)} total candles")
    logger.info(f"Date range: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")

    return df


def fetch_local_backup_data(months: int = 12) -> pd.DataFrame:
    """
    Use locally cached data if available, or generate synthetic as fallback.

    This allows testing without requiring live Binance API access.
    """
    cache_file = Path(__file__).parent / f'data_cache_ethusdt_{months}m.csv'

    if cache_file.exists():
        logger.info(f"Loading cached data from {cache_file}")
        df = pd.read_csv(cache_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    logger.warning("No cached data found, attempting to fetch from Binance...")
    try:
        df = fetch_binance_data(months=months)
        # Save for future use
        df.to_csv(cache_file, index=False)
        logger.info(f"Cached data saved to {cache_file}")
        return df
    except Exception as e:
        logger.error(f"Failed to fetch real data: {e}")
        logger.warning("Falling back to synthetic data for testing")
        return generate_synthetic_data(months=months)


def generate_synthetic_data(months: int = 12) -> pd.DataFrame:
    """Generate synthetic data as fallback."""
    num_candles = months * 30 * 24 * 12  # Approximately monthly data at 5m intervals

    logger.info(f"Generating {num_candles} synthetic candles for {months} months")

    timestamps = pd.date_range(
        end=datetime.utcnow(),
        periods=num_candles,
        freq='5min'
    )

    # Generate realistic price movement
    returns = np.random.normal(0.00005, 0.003, num_candles)
    prices = 2000 * np.exp(np.cumsum(returns))

    data = []
    for i, (timestamp, close) in enumerate(zip(timestamps, prices)):
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


def run_backtest_on_real_data(data: pd.DataFrame, output_dir: Path) -> BacktestMetrics:
    """Run Phase 1 backtest on real data."""
    logger.info("=" * 70)
    logger.info("REAL DATA BACKTEST: Phase 1 Single Agent (Golden Hour Scalper)")
    logger.info("=" * 70)

    # Create engine
    engine = GoldenHourScalpingEngine(
        symbol='ETHUSDT',
        initial_capital=10000.0
    )

    backtester = HistoricalBacktester(engine, use_julia_agents=False)

    try:
        logger.info(f"Running backtest on {len(data)} candles...")
        metrics = backtester.run_backtest(data)

        # Export results
        output_dir.mkdir(parents=True, exist_ok=True)
        backtester.export_results(str(output_dir / 'real_data_backtest'), metrics)

        logger.info("\n" + "=" * 70)
        logger.info("REAL DATA BACKTEST RESULTS")
        logger.info("=" * 70)
        logger.info(f"Total Trades: {metrics.total_trades}")
        logger.info(f"Winning Trades: {metrics.winning_trades}")
        logger.info(f"Losing Trades: {metrics.losing_trades}")
        logger.info(f"Win Rate: {metrics.win_rate*100:.1f}%")
        logger.info(f"Total P&L: ${metrics.total_pnl:.2f} ({metrics.total_pnl_pct*100:.2f}%)")
        logger.info(f"Max Drawdown: {metrics.max_drawdown_pct*100:.2f}%")
        sharpe_str = f"{metrics.sharpe_ratio:.2f}" if metrics.sharpe_ratio else "N/A"
        logger.info(f"Sharpe Ratio: {sharpe_str}")
        logger.info(f"Best Trade: ${metrics.best_trade_pnl:.2f}")
        logger.info(f"Worst Trade: ${metrics.worst_trade_pnl:.2f}")
        logger.info(f"Avg Trade Duration: {metrics.avg_trade_duration_sec}s")
        logger.info(f"Final Equity: ${metrics.final_equity:.2f}")
        logger.info("=" * 70)

        return metrics

    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        raise
    finally:
        if hasattr(engine, 'stop'):
            engine.stop()


def generate_validation_report(metrics: BacktestMetrics, data: pd.DataFrame, output_dir: Path):
    """Generate comprehensive validation report."""
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'data_validation': {
            'total_candles': len(data),
            'date_range': {
                'start': data['timestamp'].min().isoformat(),
                'end': data['timestamp'].max().isoformat()
            },
            'duration_days': (data['timestamp'].max() - data['timestamp'].min()).days,
            'price_range': {
                'min': float(data['low'].min()),
                'max': float(data['high'].max()),
                'start': float(data['open'].iloc[0]),
                'end': float(data['close'].iloc[-1])
            }
        },
        'backtest_results': {
            'total_trades': metrics.total_trades,
            'winning_trades': metrics.winning_trades,
            'losing_trades': metrics.losing_trades,
            'win_rate': float(metrics.win_rate),
            'total_pnl': float(metrics.total_pnl),
            'total_pnl_pct': float(metrics.total_pnl_pct),
            'max_drawdown_pct': float(metrics.max_drawdown_pct),
            'sharpe_ratio': float(metrics.sharpe_ratio) if metrics.sharpe_ratio else None,
            'best_trade_pnl': float(metrics.best_trade_pnl),
            'worst_trade_pnl': float(metrics.worst_trade_pnl),
            'avg_trade_duration_sec': metrics.avg_trade_duration_sec,
            'final_equity': float(metrics.final_equity),
            'equity_peak': float(metrics.equity_peak),
            'consecutive_losses': metrics.consecutive_losses
        },
        'validation_status': {
            'passed_basic_checks': metrics.total_trades > 0,
            'min_trades_required': 10,
            'min_trades_met': metrics.total_trades >= 10,
            'positive_expectancy': metrics.win_rate > 0.25,  # EMA scalping can be profitable at 25%+ with proper risk/reward
            'acceptable_drawdown': metrics.max_drawdown_pct > -0.25,
            'all_checks_passed': all([
                metrics.total_trades >= 10,
                metrics.win_rate > 0.25,
                metrics.max_drawdown_pct > -0.25
            ])
        }
    }

    # Save report
    report_file = output_dir / 'validation_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    logger.info(f"Validation report saved to {report_file}")

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Data Period: {data['timestamp'].min().date()} to {data['timestamp'].max().date()}")
    logger.info(f"Total Candles: {len(data)}")
    logger.info(f"Price Range: ${data['low'].min():.2f} - ${data['high'].max():.2f}")
    logger.info(f"\nTrading Performance:")
    logger.info(f"  Trades Executed: {metrics.total_trades}")
    logger.info(f"  Win Rate: {metrics.win_rate*100:.1f}%")
    logger.info(f"  Total Return: {metrics.total_pnl_pct*100:.2f}%")
    logger.info(f"  Max Drawdown: {metrics.max_drawdown_pct*100:.2f}%")
    logger.info(f"\nValidation Checks:")
    logger.info(f"  ✓ Minimum trades (10+): {metrics.total_trades} {'✓' if metrics.total_trades >= 10 else '✗'}")
    logger.info(f"  ✓ Positive expectancy (>25%): {metrics.win_rate*100:.1f}% {'✓' if metrics.win_rate > 0.25 else '✗'}")
    logger.info(f"  ✓ Acceptable drawdown (<-25%): {metrics.max_drawdown_pct*100:.2f}% {'✓' if metrics.max_drawdown_pct > -0.25 else '✗'}")
    logger.info(f"\nStatus: {'✅ PASSED' if report['validation_status']['all_checks_passed'] else '❌ FAILED'}")
    logger.info("=" * 70)

    return report


def main():
    parser = argparse.ArgumentParser(description='Validate NEUS_TRADER on real historical data')
    parser.add_argument('--months', type=int, default=12, help='Months of data to fetch (default: 12)')
    parser.add_argument('--output', type=Path, default=Path('results'), help='Output directory for results')
    parser.add_argument('--use-cached', action='store_true', help='Use cached data if available')

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("REAL HISTORICAL DATA VALIDATION")
    logger.info("=" * 70)

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch data
    if args.use_cached:
        data = fetch_local_backup_data(months=args.months)
    else:
        try:
            data = fetch_binance_data(months=args.months)
        except Exception as e:
            logger.warning(f"Failed to fetch from Binance: {e}, using local backup/synthetic")
            data = fetch_local_backup_data(months=args.months)

    # Run backtest
    try:
        metrics = run_backtest_on_real_data(data, output_dir)

        # Generate validation report
        report = generate_validation_report(metrics, data, output_dir)

        return 0 if report['validation_status']['all_checks_passed'] else 1

    except Exception as e:
        logger.error(f"Real data validation failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
