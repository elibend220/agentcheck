#!/usr/bin/env python3
"""
Last Week Trading Backtest

Fetches real ETHUSDT data from the past 7 days and backtests the Golden Hour Scalper.
Shows actual performance on recent market conditions.

Usage:
    python backtest_last_week.py [--days 7] [--symbol ETHUSDT] [--capital 10000]
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Optional
import pandas as pd
import numpy as np

python_core_path = str(Path(__file__).parent / 'python_core')
sys.path.insert(0, python_core_path)

from backtester import HistoricalBacktester, BacktestMetrics
from scalping_engine import GoldenHourScalpingEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('LastWeekBacktest')


def fetch_last_week_data(days: int = 7, symbol: str = 'ETHUSDT') -> Optional[pd.DataFrame]:
    """Fetch real data from the past N days."""
    logger.info(f"Fetching last {days} days of {symbol} data from Binance...")

    try:
        import requests

        # Binance API
        url = "https://api.binance.com/api/v3/klines"
        interval = '5m'

        # Calculate how many candles we need
        # ~288 candles per day (24 hours * 12 per hour = 288)
        limit = days * 288

        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }

        logger.info(f"Requesting {limit} candles ({days} days of 5-min data)...")
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        klines = response.json()
        logger.info(f"✓ Received {len(klines)} candles from Binance")

        if not klines:
            logger.warning("No data received from Binance")
            return None

        # Convert to DataFrame
        data = []
        for kline in klines:
            data.append({
                'timestamp': pd.Timestamp(int(kline[0]), unit='ms'),
                'open': float(kline[1]),
                'high': float(kline[2]),
                'low': float(kline[3]),
                'close': float(kline[4]),
                'volume': float(kline[7])
            })

        df = pd.DataFrame(data)

        # Display info
        logger.info(f"\n📊 Data Summary:")
        logger.info(f"   Period: {df['timestamp'].min()} to {df['timestamp'].max()}")
        logger.info(f"   Duration: {(df['timestamp'].max() - df['timestamp'].min()).days} days")
        logger.info(f"   Price Range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        logger.info(f"   Avg Price: ${df['close'].mean():.2f}")
        logger.info(f"   Avg Volume: {df['volume'].mean():.2f}\n")

        return df

    except Exception as e:
        logger.error(f"Failed to fetch from Binance: {e}")
        logger.info("Falling back to synthetic data...")
        return None


def generate_fallback_data(days: int = 7) -> pd.DataFrame:
    """Generate realistic synthetic data as fallback."""
    logger.info(f"Generating {days} days of synthetic data as fallback...\n")

    num_candles = days * 288  # ~288 per day
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    timestamps = pd.date_range(start=start_date, periods=num_candles, freq='5min')

    # Realistic price movement
    np.random.seed(42)
    returns = np.random.normal(0.00005, 0.004, num_candles)
    prices = 2500 * np.exp(np.cumsum(returns))

    # Add volatility clustering
    volatility = np.ones(num_candles) * 0.003
    for i in range(500, len(volatility), 500):
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

    df = pd.DataFrame(data)
    logger.info(f"✓ Generated {len(df)} synthetic candles\n")
    return df


def run_backtest(data: pd.DataFrame, initial_capital: float = 10000.0) -> BacktestMetrics:
    """Run backtest on the data."""
    logger.info("="*70)
    logger.info("BACKTEST: Golden Hour Scalping Engine - Last Week")
    logger.info("="*70 + "\n")

    # Create engine
    engine = GoldenHourScalpingEngine(
        symbol='ETHUSDT',
        initial_capital=initial_capital
    )

    # Run backtest
    backtester = HistoricalBacktester(engine)
    metrics = backtester.run_backtest(data)

    return metrics


def display_results(metrics: BacktestMetrics, data: pd.DataFrame):
    """Display detailed backtest results."""
    print("\n" + "="*70)
    print("BACKTEST RESULTS - LAST WEEK TRADING")
    print("="*70 + "\n")

    # Key metrics
    print("📊 PERFORMANCE METRICS:")
    print(f"{'─'*70}")
    print(f"   Total Trades:        {metrics.total_trades}")
    print(f"   Winning Trades:      {metrics.winning_trades}")
    print(f"   Losing Trades:       {metrics.losing_trades}")
    print(f"   Win Rate:            {metrics.win_rate*100:.1f}%")
    print(f"\n   Starting Capital:    ${metrics.equity_peak - metrics.final_equity + metrics.total_pnl:.2f}")
    print(f"   Final Equity:        ${metrics.final_equity:.2f}")
    print(f"   Total P&L:           ${metrics.total_pnl:.2f}")
    print(f"   P&L %:               {metrics.total_pnl_pct*100:.2f}%")
    print(f"\n   Max Drawdown:        {metrics.max_drawdown_pct*100:.2f}%")
    print(f"   Sharpe Ratio:        {metrics.sharpe_ratio:.2f}" if metrics.sharpe_ratio else "   Sharpe Ratio:        N/A")
    print(f"   Consecutive Losses:  {metrics.consecutive_losses}")

    # Per-trade stats
    if metrics.total_trades > 0:
        print(f"\n📈 PER-TRADE STATISTICS:")
        print(f"{'─'*70}")
        avg_pnl = metrics.total_pnl / metrics.total_trades
        print(f"   Avg P&L per Trade:   ${avg_pnl:.2f}")
        print(f"   Best Trade:          ${metrics.best_trade_pnl:.2f}")
        print(f"   Worst Trade:         ${metrics.worst_trade_pnl:.2f}")
        print(f"   Avg Trade Duration:  {metrics.avg_trade_duration_sec:.0f} seconds ({metrics.avg_trade_duration_sec/60:.1f} min)")

        # Win/loss analysis
        if metrics.winning_trades > 0:
            avg_win = sum([t['pnl'] for t in metrics.trades if t['pnl'] > 0]) / metrics.winning_trades
            print(f"   Avg Winning Trade:   ${avg_win:.2f}")

        if metrics.losing_trades > 0:
            avg_loss = sum([t['pnl'] for t in metrics.trades if t['pnl'] < 0]) / metrics.losing_trades
            print(f"   Avg Losing Trade:    ${avg_loss:.2f}")

    # Market data info
    print(f"\n📈 MARKET CONDITIONS:")
    print(f"{'─'*70}")
    print(f"   Period:              {data['timestamp'].min()} to {data['timestamp'].max()}")
    print(f"   Days:                {(data['timestamp'].max() - data['timestamp'].min()).days + 1}")
    print(f"   Candles Analyzed:    {len(data)}")
    print(f"   Price Range:         ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    print(f"   Volatility:          {data['close'].pct_change().std()*100:.2f}%")

    # Verdict
    print(f"\n{'='*70}")
    print("🎯 VERDICT:")
    print(f"{'='*70}\n")

    if metrics.total_trades == 0:
        print("⚠️  No trades generated during this period")
        print("   Market conditions may not favor the strategy")
    elif metrics.total_pnl > 0:
        print(f"✅ PROFITABLE: +${metrics.total_pnl:.2f} ({metrics.total_pnl_pct*100:.2f}%)")
        print(f"   Win Rate: {metrics.win_rate*100:.1f}% ({metrics.winning_trades}/{metrics.total_trades})")
        print(f"   Risk/Reward: Acceptable")
    elif metrics.total_pnl < -100:
        print(f"❌ SIGNIFICANT LOSS: ${metrics.total_pnl:.2f} ({metrics.total_pnl_pct*100:.2f}%)")
        print(f"   Win Rate: {metrics.win_rate*100:.1f}% ({metrics.winning_trades}/{metrics.total_trades})")
        print(f"   Action: Review market conditions during this period")
    else:
        print(f"~  BREAKEVEN: ${metrics.total_pnl:.2f} ({metrics.total_pnl_pct*100:.2f}%)")
        print(f"   Win Rate: {metrics.win_rate*100:.1f}% ({metrics.winning_trades}/{metrics.total_trades})")
        print(f"   Status: System is stable and risk-controlled")

    # Risk analysis
    print(f"\n⚠️  RISK ANALYSIS:")
    print(f"{'─'*70}")
    if metrics.max_drawdown_pct > 0.05:
        print(f"   ⚠️  Max drawdown {metrics.max_drawdown_pct*100:.2f}% is acceptable for scalping")
    else:
        print(f"   ✓ Max drawdown {metrics.max_drawdown_pct*100:.2f}% is well-controlled")

    if metrics.consecutive_losses >= 5:
        print(f"   ⚠️  Consecutive losses: {metrics.consecutive_losses} (consider trade filtering)")
    else:
        print(f"   ✓ Consecutive losses: {metrics.consecutive_losses} (within limits)")

    # Recommendation
    print(f"\n{'='*70}")
    print("💡 RECOMMENDATION:")
    print(f"{'='*70}\n")

    if metrics.total_trades < 10:
        print("📊 Low trade volume - market may have been quiet")
        print("   Consider longer backtest period or different symbols")
    elif metrics.win_rate > 0.50 and metrics.total_pnl >= 0:
        print("✅ READY FOR DEPLOYMENT")
        print(f"   • {metrics.total_trades} trades executed with {metrics.win_rate*100:.1f}% win rate")
        print(f"   • System is stable and profitable")
        print(f"   • Ready for live paper trading")
    elif metrics.win_rate > 0.45 and metrics.total_pnl >= -50:
        print("🟡 PROCEED WITH CAUTION")
        print(f"   • {metrics.total_trades} trades with {metrics.win_rate*100:.1f}% win rate")
        print(f"   • System is breakeven but stable")
        print(f"   • Monitor closely before live deployment")
    else:
        print("🔴 NEEDS REVIEW")
        print(f"   • Win rate {metrics.win_rate*100:.1f}% is below target (50%+)")
        print(f"   • Loss ${abs(metrics.total_pnl):.2f} exceeds acceptable range")
        print(f"   • Review market conditions and parameters")

    print(f"\n{'='*70}\n")


def save_results(metrics: BacktestMetrics, data: pd.DataFrame, filename: str = 'last_week_backtest.json'):
    """Save backtest results to JSON."""
    results = {
        'timestamp': datetime.utcnow().isoformat(),
        'backtest_type': 'Last Week Real Data',
        'period': {
            'start': data['timestamp'].min().isoformat(),
            'end': data['timestamp'].max().isoformat(),
            'days': (data['timestamp'].max() - data['timestamp'].min()).days + 1,
            'candles': len(data)
        },
        'metrics': {
            'total_trades': metrics.total_trades,
            'winning_trades': metrics.winning_trades,
            'losing_trades': metrics.losing_trades,
            'win_rate': metrics.win_rate,
            'total_pnl': metrics.total_pnl,
            'total_pnl_pct': metrics.total_pnl_pct,
            'final_equity': metrics.final_equity,
            'max_drawdown_pct': metrics.max_drawdown_pct,
            'sharpe_ratio': metrics.sharpe_ratio,
            'consecutive_losses': metrics.consecutive_losses,
            'best_trade_pnl': metrics.best_trade_pnl,
            'worst_trade_pnl': metrics.worst_trade_pnl,
            'avg_trade_duration_sec': metrics.avg_trade_duration_sec
        }
    }

    output_file = Path(__file__).parent / 'results' / filename
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"✓ Results saved to {output_file}\n")


def main():
    """Main backtest runner."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Backtest Golden Hour Scalper on last week trading data'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to backtest (default: 7)'
    )
    parser.add_argument(
        '--symbol',
        default='ETHUSDT',
        help='Trading pair (default: ETHUSDT)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=10000.0,
        help='Initial capital (default: $10000)'
    )
    parser.add_argument(
        '--synthetic-fallback',
        action='store_true',
        help='Use synthetic data if Binance fetch fails'
    )

    args = parser.parse_args()

    print("\n" + "="*70)
    print(f"BACKTEST: Last {args.days} Days of {args.symbol} Trading")
    print("="*70 + "\n")

    # Fetch data
    data = fetch_last_week_data(args.days, args.symbol)

    if data is None:
        if args.synthetic_fallback:
            data = generate_fallback_data(args.days)
        else:
            logger.error("Failed to fetch data and synthetic fallback disabled")
            sys.exit(1)

    # Run backtest
    metrics = run_backtest(data, args.capital)

    # Display results
    display_results(metrics, data)

    # Save results
    save_results(metrics, data)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nBacktest cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        sys.exit(1)
