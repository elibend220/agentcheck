#!/usr/bin/env python3
"""
Deploy Optimized Scalping Engine to Paper Trading

Deploys the optimized engine with:
- Market hour filtering (London 13-17 UTC, US Close 20-23 UTC)
- Improved order flow analysis (2+ confirmations)
- RSI filtering (avoid overbought/oversold)
- Position sizing by signal quality
- Real-time Binance WebSocket streaming

Expected Performance:
- Profit Factor: 1.28+ (backtested)
- Win Rate: 33.3%
- Only trades during prime hours (profitable windows)

Usage:
    python deploy_optimized_engine.py --symbol ETHUSDT --capital 10000 --duration 7d
"""

import sys
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict
import json

python_core_path = str(Path(__file__).parent / 'python_core')
sys.path.insert(0, python_core_path)

from scalping_engine_optimized import GoldenHourScalpingEngineOptimized
from binance_websocket import BinanceWebSocketClient
from market_hours import MarketHourDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('DeployOptimized')


class OptimizedEnginePaperTrading:
    """Paper trading session for optimized scalping engine."""

    def __init__(
        self,
        symbol: str = 'ETHUSDT',
        initial_capital: float = 10000.0,
        session_id: str = "optimized",
        max_duration_hours: Optional[float] = None
    ):
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.session_id = session_id
        self.max_duration_hours = max_duration_hours
        self.logger = logging.getLogger('OptimizedSession')

        # Initialize optimized engine with prime hours filtering
        self.engine = GoldenHourScalpingEngineOptimized(
            symbol=symbol,
            initial_capital=initial_capital,
            session_id=session_id,
            min_confidence=0.75,
            prime_hours_only=True  # KEY: Only trade during prime hours
        )

        self.market_hours = MarketHourDetector()
        self.ws_client = None
        self.session_start = datetime.utcnow()
        self.session_end = None
        self.stats = {
            'total_candles': 0,
            'signals_generated': 0,
            'trades_executed': 0,
            'prime_hour_candles': 0,
            'off_hour_candles': 0,
            'pnl': 0.0
        }

    async def start_paper_trading(self):
        """Start paper trading session."""
        self.logger.info("=" * 80)
        self.logger.info("🚀 OPTIMIZED ENGINE PAPER TRADING SESSION STARTED")
        self.logger.info("=" * 80)
        self.logger.info(f"Symbol: {self.symbol}")
        self.logger.info(f"Initial Capital: ${self.initial_capital:.2f}")
        self.logger.info(f"Session ID: {self.session_id}")
        self.logger.info(f"Prime Hours Only: ✓ ENABLED")
        self.logger.info(f"Min Confidence: 0.75")
        self.logger.info(f"Start Time: {self.session_start.isoformat()}")
        if self.max_duration_hours:
            self.logger.info(f"Max Duration: {self.max_duration_hours} hours")
        self.logger.info("-" * 80)

        try:
            # Start the optimized engine
            self.engine.start()

            # Set up candle callback
            async def on_candle(candle_data: Dict):
                await self._process_candle(candle_data)

            # Connect to Binance WebSocket
            self.logger.info(f"📡 Connecting to Binance WebSocket for {self.symbol}...")
            self.ws_client = BinanceWebSocketClient(
                symbol=self.symbol,
                interval='5m',
                callback=on_candle
            )

            self.logger.info("✓ Connected! Waiting for candle data...")
            self.logger.info("-" * 80)

            # Create tasks for WebSocket and duration timeout
            tasks = []

            # Task 1: Run WebSocket
            ws_task = asyncio.create_task(self.ws_client.run())
            tasks.append(ws_task)

            # Task 2: Timeout after max_duration_hours (if specified)
            if self.max_duration_hours:
                timeout_task = asyncio.create_task(
                    asyncio.sleep(self.max_duration_hours * 3600)
                )
                tasks.append(timeout_task)

                # Wait for either timeout or WebSocket to finish
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )

                # Cancel remaining tasks
                for task in pending:
                    task.cancel()
            else:
                # Run indefinitely until interrupted
                await ws_task

        except KeyboardInterrupt:
            self.logger.info("\n\n⏹️  Session interrupted by user")
        except Exception as e:
            self.logger.error(f"❌ Error during paper trading: {e}", exc_info=True)
        finally:
            await self.shutdown()

    async def _process_candle(self, candle_data: Dict):
        """Process incoming candle from WebSocket."""
        try:
            timestamp = datetime.fromtimestamp(candle_data['timestamp'] / 1000)
            open_price = float(candle_data['open'])
            high = float(candle_data['high'])
            low = float(candle_data['low'])
            close = float(candle_data['close'])
            volume = float(candle_data['volume'])

            self.stats['total_candles'] += 1

            # Track prime vs off-prime hours
            is_prime = self.market_hours.is_prime_trading_hour(timestamp)
            if is_prime:
                self.stats['prime_hour_candles'] += 1
            else:
                self.stats['off_hour_candles'] += 1

            # Process candle through optimized engine
            signal = self.engine.on_candle(
                timestamp=timestamp,
                open_price=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
                atr=0.0
            )

            if signal:
                self.stats['signals_generated'] += 1
                self.stats['trades_executed'] += 1

                # Log the trade signal
                self.logger.info(
                    f"📊 SIGNAL: {signal.direction:5} @ ${close:.2f} | "
                    f"Quality: {signal.signal_quality:6} | "
                    f"Conf: {signal.confidence:.1%} | "
                    f"Size: ${signal.position_size:.2f}"
                )

                # Execute trade
                self.engine.execute_scalp_trade(signal)

            # Update position tracking
            self.engine.on_position_update(close, timestamp)

            # Log stats every 288 candles (1 day of 5-min data)
            if self.stats['total_candles'] % 288 == 0:
                self._log_session_stats()

        except Exception as e:
            self.logger.error(f"Error processing candle: {e}", exc_info=True)

    def _log_session_stats(self):
        """Log current session statistics."""
        elapsed = datetime.utcnow() - self.session_start
        hours_elapsed = elapsed.total_seconds() / 3600

        status = self.engine.get_system_status()

        self.logger.info("-" * 80)
        self.logger.info(f"📈 SESSION STATS (after {hours_elapsed:.1f} hours)")
        self.logger.info("-" * 80)
        self.logger.info(f"Total Candles: {self.stats['total_candles']}")
        self.logger.info(f"Prime Hours: {self.stats['prime_hour_candles']} ({self.stats['prime_hour_candles']/max(self.stats['total_candles'], 1)*100:.1f}%)")
        self.logger.info(f"Off-Hours: {self.stats['off_hour_candles']} ({self.stats['off_hour_candles']/max(self.stats['total_candles'], 1)*100:.1f}%)")
        self.logger.info(f"Signals Generated: {self.stats['signals_generated']}")
        self.logger.info(f"Trades Executed: {self.stats['trades_executed']}")
        self.logger.info(f"Open Positions: {status.get('open_positions', 0)}")
        self.logger.info(f"High Quality Signals: {status.get('high_quality_signals', 0)}")
        self.logger.info(f"Signal Rejection Rate: {status.get('rejection_rate', 0)*100:.1f}%")
        self.logger.info(f"Volatility Estimate: {status.get('volatility_estimate', 0):.2f}%")
        self.logger.info("-" * 80)

    async def shutdown(self):
        """Shutdown paper trading session."""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("🛑 SHUTTING DOWN OPTIMIZED ENGINE")
        self.logger.info("=" * 80)

        # Stop the engine
        self.engine.stop()

        # Close WebSocket
        if self.ws_client:
            await self.ws_client.disconnect()
            self.logger.info("✓ WebSocket closed")

        # Final stats
        self.session_end = datetime.utcnow()
        duration = self.session_end - self.session_start
        self.logger.info(f"Session Duration: {duration}")
        self.logger.info(f"Total Candles Processed: {self.stats['total_candles']}")
        self.logger.info(f"Signals Generated: {self.stats['signals_generated']}")
        self.logger.info(f"Trades Executed: {self.stats['trades_executed']}")
        self.logger.info(f"Prime Hour Signals: {self.stats.get('prime_hour_trades', 0)}")

        # Get final status
        status = self.engine.get_system_status()
        self.logger.info(f"Open Positions: {status.get('open_positions', 0)}")
        self.logger.info(f"High Quality Signals: {status.get('high_quality_signals', 0)}")

        # Save session log
        self._save_session_log()

        self.logger.info("=" * 80)
        self.logger.info("✓ Session ended")
        self.logger.info("=" * 80)

    def _save_session_log(self):
        """Save session statistics to file."""
        output_dir = Path(__file__).parent / 'results' / 'paper_trading_sessions'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().isoformat().replace(':', '-')
        log_file = output_dir / f"optimized_engine_{timestamp}.json"

        session_data = {
            'session_id': self.session_id,
            'symbol': self.symbol,
            'initial_capital': self.initial_capital,
            'start_time': self.session_start.isoformat(),
            'end_time': self.session_end.isoformat() if self.session_end else None,
            'duration_seconds': (self.session_end - self.session_start).total_seconds() if self.session_end else None,
            'stats': self.stats,
            'engine_config': {
                'prime_hours_only': True,
                'min_confidence': 0.75,
                'lookback_periods': 50
            }
        }

        with open(log_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        self.logger.info(f"✓ Session log saved to {log_file}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Deploy Optimized Scalping Engine to Paper Trading'
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
        help='Initial simulated capital (default: 10000)'
    )
    parser.add_argument(
        '--duration',
        default=None,
        help='Session duration (e.g., 1h, 7d, 30d) - None for unlimited'
    )
    parser.add_argument(
        '--session-id',
        default='optimized',
        help='Session identifier for logging'
    )

    args = parser.parse_args()

    # Parse duration
    max_duration_hours = None
    if args.duration:
        duration_str = args.duration.lower()
        if 'h' in duration_str:
            max_duration_hours = float(duration_str.replace('h', ''))
        elif 'd' in duration_str:
            max_duration_hours = float(duration_str.replace('d', '')) * 24

    # Create and start paper trading session
    session = OptimizedEnginePaperTrading(
        symbol=args.symbol,
        initial_capital=args.capital,
        session_id=args.session_id,
        max_duration_hours=max_duration_hours
    )

    await session.start_paper_trading()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\n⏹️  Deployment cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
