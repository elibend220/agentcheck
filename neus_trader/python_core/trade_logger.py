"""
PostgreSQL Trade Logging System
Persistent logging of all trading activity for analysis and compliance.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class TradeLogger:
    """
    Logs trades to PostgreSQL with fallback to JSON files.
    Enables real-time trade analysis and compliance reporting.
    """

    def __init__(
        self,
        db_host: str = "localhost",
        db_name: str = "neus_trader",
        db_user: str = "trader",
        db_password: str = "secure_password",
        fallback_file: str = "/tmp/trades.jsonl"
    ):
        self.logger = logging.getLogger("TradeLogger")
        self.connection = None
        self.fallback_file = fallback_file
        self.use_fallback = False

        if not PSYCOPG2_AVAILABLE:
            self.logger.warning("psycopg2 not installed, using JSON fallback")
            self.use_fallback = True
            return

        try:
            self.connection = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password
            )
            self.logger.info(f"Connected to PostgreSQL: {db_host}/{db_name}")
            self._initialize_schema()
        except psycopg2.Error as e:
            self.logger.warning(f"PostgreSQL connection failed: {e}, using JSON fallback")
            self.use_fallback = True

    def _initialize_schema(self):
        """Create tables if they don't exist"""
        if not self.connection:
            return

        try:
            with self.connection.cursor() as cur:
                # Trades table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS trades (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT NOW(),
                        symbol VARCHAR(20),
                        direction VARCHAR(10),
                        entry_price FLOAT,
                        exit_price FLOAT,
                        position_size FLOAT,
                        pnl FLOAT,
                        pnl_pct FLOAT,
                        stop_loss FLOAT,
                        take_profit FLOAT,
                        exit_reason VARCHAR(50),
                        agent_id VARCHAR(50),
                        session_id VARCHAR(100),
                        metadata JSONB
                    )
                """)

                # Performance metrics table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS performance_snapshots (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT NOW(),
                        capital FLOAT,
                        drawdown_pct FLOAT,
                        win_rate FLOAT,
                        total_trades INT,
                        session_id VARCHAR(100),
                        market_session VARCHAR(50),
                        metadata JSONB
                    )
                """)

                # Signals table for analysis
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS signals (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT NOW(),
                        symbol VARCHAR(20),
                        signal_type VARCHAR(50),
                        direction VARCHAR(10),
                        confidence FLOAT,
                        agent_id VARCHAR(50),
                        session_id VARCHAR(100),
                        metadata JSONB
                    )
                """)

                self.connection.commit()
                self.logger.info("Database schema initialized")

        except psycopg2.Error as e:
            self.logger.error(f"Schema initialization failed: {e}")
            self.use_fallback = True

    def log_trade(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        exit_price: float,
        position_size: float,
        pnl: float,
        pnl_pct: float,
        stop_loss: float,
        take_profit: float,
        exit_reason: str = "manual",
        agent_id: str = "system",
        session_id: str = "default",
        metadata: Dict = None
    ) -> bool:
        """Log completed trade"""
        if metadata is None:
            metadata = {}

        if self.use_fallback:
            return self._log_trade_json(
                symbol, direction, entry_price, exit_price, position_size,
                pnl, pnl_pct, stop_loss, take_profit, exit_reason, agent_id, session_id, metadata
            )

        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO trades
                    (symbol, direction, entry_price, exit_price, position_size, pnl, pnl_pct,
                     stop_loss, take_profit, exit_reason, agent_id, session_id, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    symbol, direction, entry_price, exit_price, position_size, pnl, pnl_pct,
                    stop_loss, take_profit, exit_reason, agent_id, session_id, json.dumps(metadata)
                ))

            self.connection.commit()
            self.logger.debug(f"Logged trade: {symbol} {direction} PnL={pnl:.2f}")
            return True

        except psycopg2.Error as e:
            self.logger.error(f"Failed to log trade: {e}")
            return self._log_trade_json(
                symbol, direction, entry_price, exit_price, position_size,
                pnl, pnl_pct, stop_loss, take_profit, exit_reason, agent_id, session_id, metadata
            )

    def _log_trade_json(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        exit_price: float,
        position_size: float,
        pnl: float,
        pnl_pct: float,
        stop_loss: float,
        take_profit: float,
        exit_reason: str,
        agent_id: str,
        session_id: str,
        metadata: Dict
    ) -> bool:
        """Log trade to JSON file (fallback)"""
        try:
            trade_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'symbol': symbol,
                'direction': direction,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'position_size': position_size,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'exit_reason': exit_reason,
                'agent_id': agent_id,
                'session_id': session_id,
                'metadata': metadata
            }

            with open(self.fallback_file, 'a') as f:
                f.write(json.dumps(trade_record) + '\n')

            self.logger.debug(f"Logged trade to JSON: {symbol} {direction}")
            return True

        except Exception as e:
            self.logger.error(f"JSON trade logging failed: {e}")
            return False

    def log_performance(
        self,
        capital: float,
        drawdown_pct: float,
        win_rate: float,
        total_trades: int,
        session_id: str = "default",
        market_session: str = "unknown",
        metadata: Dict = None
    ) -> bool:
        """Log performance snapshot"""
        if metadata is None:
            metadata = {}

        if self.use_fallback:
            return self._log_performance_json(capital, drawdown_pct, win_rate, total_trades, session_id, market_session, metadata)

        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO performance_snapshots
                    (capital, drawdown_pct, win_rate, total_trades, session_id, market_session, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    capital, drawdown_pct, win_rate, total_trades, session_id, market_session,
                    json.dumps(metadata)
                ))

            self.connection.commit()
            return True

        except psycopg2.Error as e:
            self.logger.error(f"Failed to log performance: {e}")
            return self._log_performance_json(capital, drawdown_pct, win_rate, total_trades, session_id, market_session, metadata)

    def _log_performance_json(
        self,
        capital: float,
        drawdown_pct: float,
        win_rate: float,
        total_trades: int,
        session_id: str,
        market_session: str,
        metadata: Dict
    ) -> bool:
        """Log performance to JSON (fallback)"""
        try:
            perf_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'capital': capital,
                'drawdown_pct': drawdown_pct,
                'win_rate': win_rate,
                'total_trades': total_trades,
                'session_id': session_id,
                'market_session': market_session,
                'metadata': metadata
            }

            perf_file = self.fallback_file.replace('.jsonl', '_perf.jsonl')
            with open(perf_file, 'a') as f:
                f.write(json.dumps(perf_record) + '\n')

            return True
        except Exception as e:
            self.logger.error(f"JSON performance logging failed: {e}")
            return False

    def log_signal(
        self,
        symbol: str,
        signal_type: str,
        direction: str,
        confidence: float,
        agent_id: str = "system",
        session_id: str = "default",
        metadata: Dict = None
    ) -> bool:
        """Log signal generation"""
        if metadata is None:
            metadata = {}

        if self.use_fallback:
            return self._log_signal_json(symbol, signal_type, direction, confidence, agent_id, session_id, metadata)

        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO signals
                    (symbol, signal_type, direction, confidence, agent_id, session_id, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    symbol, signal_type, direction, confidence, agent_id, session_id,
                    json.dumps(metadata)
                ))

            self.connection.commit()
            return True

        except psycopg2.Error as e:
            self.logger.error(f"Failed to log signal: {e}")
            return self._log_signal_json(symbol, signal_type, direction, confidence, agent_id, session_id, metadata)

    def _log_signal_json(
        self,
        symbol: str,
        signal_type: str,
        direction: str,
        confidence: float,
        agent_id: str,
        session_id: str,
        metadata: Dict
    ) -> bool:
        """Log signal to JSON (fallback)"""
        try:
            signal_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'symbol': symbol,
                'signal_type': signal_type,
                'direction': direction,
                'confidence': confidence,
                'agent_id': agent_id,
                'session_id': session_id,
                'metadata': metadata
            }

            signal_file = self.fallback_file.replace('.jsonl', '_signals.jsonl')
            with open(signal_file, 'a') as f:
                f.write(json.dumps(signal_record) + '\n')

            return True
        except Exception as e:
            self.logger.error(f"JSON signal logging failed: {e}")
            return False

    def get_trade_history(self, limit: int = 100, session_id: str = None) -> List[Dict]:
        """Retrieve trade history"""
        if not self.connection:
            return self._read_trades_json(limit)

        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cur:
                if session_id:
                    cur.execute("""
                        SELECT * FROM trades WHERE session_id = %s
                        ORDER BY timestamp DESC LIMIT %s
                    """, (session_id, limit))
                else:
                    cur.execute("""
                        SELECT * FROM trades
                        ORDER BY timestamp DESC LIMIT %s
                    """, (limit,))

                return cur.fetchall() or []

        except psycopg2.Error as e:
            self.logger.error(f"Failed to retrieve trades: {e}")
            return self._read_trades_json(limit)

    def _read_trades_json(self, limit: int) -> List[Dict]:
        """Read trades from JSON (fallback)"""
        try:
            trades = []
            with open(self.fallback_file, 'r') as f:
                for line in f:
                    if line.strip():
                        trades.append(json.loads(line))

            return trades[-limit:] if limit else trades

        except Exception as e:
            self.logger.error(f"Failed to read trades from JSON: {e}")
            return []

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")

    def __del__(self):
        """Ensure connection is closed"""
        self.close()
