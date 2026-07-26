"""
Binance WebSocket Client

Real-time streaming of OHLCV data from Binance for paper trading.
Supports multiple timeframes and symbols.
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Optional, Callable, Dict
from dataclasses import dataclass

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

logger = logging.getLogger(__name__)


@dataclass
class Candle:
    """OHLCV candle data."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }


class BinanceWebSocketClient:
    """
    Real-time Binance WebSocket client for OHLCV data.

    Features:
    - Live kline (candlestick) streaming
    - Support for multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d)
    - Automatic reconnection on disconnect
    - Graceful shutdown
    """

    def __init__(
        self,
        symbol: str = 'ETHUSDT',
        interval: str = '5m',
        callback: Optional[Callable] = None
    ):
        """
        Initialize Binance WebSocket client.

        Args:
            symbol: Trading pair (e.g., 'ETHUSDT', 'BTCUSDT')
            interval: Candle interval (1m, 5m, 15m, 1h, 4h, 1d)
            callback: Async function to call on each candle close
        """
        if not HAS_WEBSOCKETS:
            raise ImportError(
                "websockets library required: pip install websockets"
            )

        self.symbol = symbol.lower()
        self.interval = interval
        self.callback = callback
        self.logger = logging.getLogger('BinanceWS')
        self.is_running = False
        self.ws = None

        # Binance WebSocket base URLs
        self.stream_url = (
            f"wss://stream.binance.com:9443/ws/"
            f"{self.symbol}@kline_{self.interval}"
        )

        self.logger.info(
            f"BinanceWebSocketClient initialized: {symbol} {interval}"
        )

    async def connect(self):
        """Connect to Binance WebSocket stream."""
        self.is_running = True
        retry_count = 0
        max_retries = 10

        while self.is_running and retry_count < max_retries:
            try:
                self.logger.info(f"Connecting to {self.stream_url}")

                async with websockets.connect(self.stream_url) as ws:
                    self.ws = ws
                    self.logger.info("Connected to Binance WebSocket")
                    retry_count = 0  # Reset retry count on success

                    async for message in ws:
                        if not self.is_running:
                            break

                        try:
                            await self._process_message(message)
                        except Exception as e:
                            self.logger.error(
                                f"Error processing message: {e}",
                                exc_info=True
                            )

            except asyncio.CancelledError:
                self.logger.info("Connection cancelled")
                break
            except Exception as e:
                retry_count += 1
                wait_time = min(2 ** retry_count, 60)
                self.logger.warning(
                    f"WebSocket error (retry {retry_count}/{max_retries}): {e}"
                )
                if retry_count < max_retries:
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error("Max retries exceeded, stopping stream")
                    self.is_running = False

    async def _process_message(self, message: str):
        """Process WebSocket message."""
        data = json.loads(message)

        # Extract kline data
        if 'k' not in data:
            return

        kline = data['k']

        # Only process closed candles
        if not kline['x']:
            return

        # Create candle object
        candle = Candle(
            timestamp=datetime.fromtimestamp(kline['T'] / 1000),
            open=float(kline['o']),
            high=float(kline['h']),
            low=float(kline['l']),
            close=float(kline['c']),
            volume=float(kline['v'])
        )

        # Call callback if provided
        if self.callback:
            await self.callback(candle.to_dict())

    async def disconnect(self):
        """Disconnect from WebSocket stream."""
        self.logger.info("Disconnecting from Binance WebSocket")
        self.is_running = False

        if self.ws:
            await self.ws.close()

    async def run(self):
        """Run the WebSocket client (blocking)."""
        await self.connect()

    @staticmethod
    async def test_connection(symbol: str = 'ETHUSDT', interval: str = '5m'):
        """Test Binance WebSocket connection."""
        print(f"Testing connection to {symbol} {interval}...")

        received_candles = 0

        async def on_candle(candle: Dict):
            nonlocal received_candles
            received_candles += 1
            timestamp = datetime.fromisoformat(
                candle['timestamp'].isoformat()
                if not isinstance(candle['timestamp'], str)
                else candle['timestamp']
            )
            print(
                f"[{timestamp.strftime('%H:%M:%S')}] "
                f"{symbol} {interval} - "
                f"Close: ${candle['close']:.2f} "
                f"Volume: {candle['volume']:.2f}"
            )

            if received_candles >= 3:
                return False  # Stop after 3 candles

        client = BinanceWebSocketClient(symbol, interval, on_candle)

        try:
            await asyncio.wait_for(client.run(), timeout=120)
        except asyncio.TimeoutError:
            await client.disconnect()
            print(f"Received {received_candles} candles")


if __name__ == '__main__':
    # Test connection
    asyncio.run(BinanceWebSocketClient.test_connection())
