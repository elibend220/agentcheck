#!/usr/bin/env python3
"""
Flow Filter Backtest: EMA + Flow Risk Management

Tests the redesigned approach:
- EMA signals drive entry/exit (unchanged)
- Institutional flow REDUCES position size on distribution
- Institutional flow INCREASES position size on accumulation
"""

import sys
import logging
from pathlib import Path
import json
import pandas as pd

python_core_path = str(Path(__file__).parent / 'python_core')
sys.path.insert(0, python_core_path)

from paper_trading_with_flow_filter import PaperTradingWithFlowFilter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('FlowFilterBacktest')


def load_data():
    """Load realistic historical data."""
    data_file = Path(__file__).parent / 'data' / 'ethusdt_2weeks.csv'
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    logger.info(f"Loaded {len(df)} candles")
    return df


def run_backtest():
    """Run EMA with flow filter risk management."""
    logger.info("\n" + "="*70)
    logger.info("FLOW FILTER BACKTEST: EMA + Flow Risk Management")
    logger.info("="*70)

    data = load_data()

    engine = PaperTradingWithFlowFilter(
        symbol='ETHUSDT',
        initial_capital=10000.0,
        risk_per_trade=0.01,  # 1% base risk
        max_positions=3,
        use_flow_filter=True  # Enable flow filter
    )

    for idx, candle in data.iterrows():
        engine.process_candle(candle.to_dict())

        if (idx + 1) % 500 == 0:
            logger.info(f"Processed {idx+1}/{len(data)} | Capital: ${engine.current_capital:.2f}")

    # Metrics
    total_pnl = engine.current_capital - engine.initial_capital
    win_trades = sum(1 for t in engine.closed_trades if t.pnl and t.pnl > 0)
    total_trades = len(engine.closed_trades)
    win_rate = win_trades / total_trades if total_trades > 0 else 0.0

    logger.info("\n" + "="*70)
    logger.info("RESULTS:")
    logger.info("="*70)
    logger.info(f"Total Trades: {total_trades}")
    logger.info(f"Winning: {win_trades} | Losing: {total_trades - win_trades}")
    logger.info(f"Win Rate: {win_rate*100:.1f}%")
    logger.info(f"Total P&L: ${total_pnl:.2f} ({(total_pnl/engine.initial_capital)*100:.2f}%)")
    logger.info(f"Final Capital: ${engine.current_capital:.2f}")

    if total_trades > 0:
        per_trade = total_pnl / total_trades
        logger.info(f"P&L per Trade: ${per_trade:.2f}")

    # Compare vs baseline (EMA only at 0.01% risk)
    logger.info("\n" + "="*70)
    logger.info("vs Baseline (EMA-only: 27.2% win, +$1.28):")
    logger.info("="*70)

    if total_pnl > 1.28:
        logger.info(f"✓ P&L improved by ${total_pnl - 1.28:.2f}")
    else:
        logger.warning(f"✗ P&L degraded by ${abs(total_pnl - 1.28):.2f}")

    if win_rate > 0.272:
        logger.info(f"✓ Win rate improved by {(win_rate - 0.272)*100:.1f}%")
    elif win_rate < 0.272:
        logger.warning(f"✗ Win rate degraded by {(0.272 - win_rate)*100:.1f}%")

    results = {
        'backtest': 'flow_filter',
        'total_trades': total_trades,
        'win_rate': win_rate,
        'total_pnl': total_pnl,
        'total_pnl_pct': (total_pnl / engine.initial_capital) * 100,
        'final_capital': engine.current_capital
    }

    results_file = Path(__file__).parent / 'results' / 'flow_filter_backtest.json'
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n✓ Results saved to {results_file}")
    return results


if __name__ == '__main__':
    run_backtest()
