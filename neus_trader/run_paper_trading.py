#!/usr/bin/env python3
"""
Paper Trading Runner

Executes Phase 1 trading signals in real-time using live Binance data.
No real capital at risk - simulated trading only.

Usage:
    python run_paper_trading.py [--symbol ETHUSDT] [--interval 5m] [--duration 7d]
"""

import sys
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict
import json

# Add project root to path
python_core_path = str(Path(__file__).parent / 'python_core')
sys.path.insert(0, python_core_path)

from paper_trading import PaperTradingEngine
from binance_websocket import BinanceWebSocketClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('PaperTradingRunner')


class PaperTradingSession:
    """Manages a paper trading session."""

    def __init__(
        self,
        symbol: str = 'ETHUSDT',
        interval: str = '5m',
        initial_capital: float = 10000.0,
        max_duration_hours: Optional[float] = None
    ):
        """
        Initialize paper trading session.

        Args:
            symbol: Trading pair
            interval: Candle interval
            initial_capital: Simulated starting capital
            max_duration_hours: Maximum session duration (None = unlimited)
        """
        self.symbol = symbol
        self.interval = interval
        self.initial_capital = initial_capital
        self.max_duration_hours = max_duration_hours
        self.logger = logging.getLogger('Session')

        # Initialize components
        self.engine = PaperTradingEngine(
            symbol=symbol,
            initial_capital=initial_capital
        )
        self.ws_client = None

    async def start(self):
        """Start paper trading session."""
        self.logger.info("=" * 70)
        self.logger.info("PAPER TRADING SESSION STARTED")
        self.logger.info("=" * 70)
        self.logger.info(f"Symbol: {self.symbol}")
        self.logger.info(f"Interval: {self.interval}")
        self.logger.info(f"Initial Capital: ${self.initial_capital:.2f}")
        if self.max_duration_hours:
            self.logger.info(f"Max Duration: {self.max_duration_hours} hours")
        self.logger.info(f"Start Time: {datetime.utcnow().isoformat()}")

        # Create WebSocket client with callback
        self.ws_client = BinanceWebSocketClient(
            symbol=self.symbol,
            interval=self.interval,
            callback=self._on_candle
        )

        # Run until max duration or cancelled
        try:
            if self.max_duration_hours:
                await asyncio.wait_for(
                    self.ws_client.run(),
                    timeout=self.max_duration_hours * 3600
                )
            else:
                await self.ws_client.run()
        except asyncio.TimeoutError:
            self.logger.info("Max duration reached, stopping session")
        except KeyboardInterrupt:
            self.logger.info("Session interrupted by user")
        finally:
            await self.stop()

    async def _on_candle(self, candle: Dict):
        """Process new candle from WebSocket."""
        # Execute trade signal
        result = self.engine.process_candle(candle)

        # Log activity
        current_price = candle['close']
        self.logger.info(
            f"Candle: {candle['timestamp'].isoformat()} | "
            f"Price: ${current_price:.2f} | "
            f"Capital: ${self.engine.current_capital:.2f} | "
            f"Positions: {len(self.engine.open_positions)}"
        )

        if result:
            self.logger.info(
                f"✅ Trade executed: {result['direction']} "
                f"{result['position_size']:.4f} @ ${result['entry_price']:.2f}"
            )

    async def stop(self):
        """Stop paper trading session."""
        if self.ws_client:
            await self.ws_client.disconnect()

        # Print final metrics
        metrics = self.engine.get_metrics()

        self.logger.info("=" * 70)
        self.logger.info("PAPER TRADING SESSION SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"Duration: {metrics['duration_sec'] / 3600:.2f} hours")
        self.logger.info(f"Total Trades: {metrics['total_trades']}")
        self.logger.info(f"Winning Trades: {metrics['winning_trades']}")
        self.logger.info(f"Losing Trades: {metrics['losing_trades']}")
        self.logger.info(f"Win Rate: {metrics['win_rate']*100:.1f}%")
        self.logger.info(f"Total P&L: ${metrics['total_pnl']:.2f}")
        self.logger.info(f"P&L %: {metrics['total_pnl_pct']*100:.2f}%")
        self.logger.info(f"Final Capital: ${metrics['current_capital']:.2f}")
        self.logger.info(f"Open Positions: {metrics['open_positions']}")
        self.logger.info(f"Total Signals: {metrics['total_signals']}")

        if metrics['total_trades'] > 0:
            self.logger.info(f"Best Trade: ${metrics['best_trade']:.2f}")
            self.logger.info(f"Worst Trade: ${metrics['worst_trade']:.2f}")
            self.logger.info(f"Avg Trade P&L: ${metrics['avg_trade_pnl']:.2f}")

        self.logger.info("=" * 70)

        # Export session data
        output_file = f"paper_trading_{datetime.utcnow().isoformat()}.json"
        self.engine.export_session(output_file)
        self.logger.info(f"Session exported to {output_file}")


def parse_duration(duration_str: str) -> Optional[float]:
    """Parse duration string to hours."""
    if not duration_str:
        return None

    duration_str = duration_str.lower().strip()

    if duration_str.endswith('h'):
        return float(duration_str[:-1])
    elif duration_str.endswith('d'):
        return float(duration_str[:-1]) * 24
    elif duration_str.endswith('w'):
        return float(duration_str[:-1]) * 24 * 7
    else:
        return float(duration_str)


async def main():
    """Main paper trading runner."""
    parser = argparse.ArgumentParser(
        description='NEUS_TRADER Paper Trading Runner'
    )
    parser.add_argument(
        '--symbol',
        default='ETHUSDT',
        help='Trading pair (default: ETHUSDT)'
    )
    parser.add_argument(
        '--interval',
        default='5m',
        choices=['1m', '5m', '15m', '1h', '4h', '1d'],
        help='Candle interval (default: 5m)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=10000.0,
        help='Initial simulated capital (default: $10000)'
    )
    parser.add_argument(
        '--duration',
        help='Session duration (e.g., 7d, 24h, 1w)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test Binance WebSocket connection only'
    )

    args = parser.parse_args()

    # Test mode
    if args.test:
        logger.info(f"Testing Binance WebSocket connection...")
        await BinanceWebSocketClient.test_connection(args.symbol, args.interval)
        return

    # Parse duration
    max_duration = parse_duration(args.duration) if args.duration else None

    # Start paper trading session
    session = PaperTradingSession(
        symbol=args.symbol,
        interval=args.interval,
        initial_capital=args.capital,
        max_duration_hours=max_duration
    )

    await session.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nPaper trading interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Paper trading failed: {e}", exc_info=True)
        sys.exit(1)
