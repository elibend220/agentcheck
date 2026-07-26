"""
Trading Engine API Server (FastAPI)
Provides REST API for frontend dashboard and external integrations.
Decouples trading logic from presentation layer.

Phase 2: Multi-agent decision support via Julia bridge.
Falls back to Phase 1 (single agent) if Julia unavailable.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio
from pathlib import Path

from scalping_engine import GoldenHourScalpingEngine, ScalpingSignal
from adaptive_risk import AdaptiveRiskManager
from market_hours import MarketHourDetector
from bifurcation_diagnostics import BifurcationMonitor
from monitoring import MonitoringSystem
from julia_bridge import JuliaBridge, JuliaDecision


# ============================================================================
# API Request/Response Models (Pydantic)
# ============================================================================

class EngineStatusResponse(BaseModel):
    """Trading engine status"""
    symbol: str
    is_running: bool
    capital: float
    equity: float
    drawdown_pct: float
    open_positions: int
    total_trades: int
    win_rate: float
    timestamp: str


class SignalResponse(BaseModel):
    """Trading signal"""
    direction: str
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    position_size: float
    confidence: float
    timestamp: str


class TradeResponse(BaseModel):
    """Completed trade"""
    direction: str
    entry_price: float
    exit_price: float
    position_size: float
    pnl: float
    pnl_pct: float
    exit_reason: str
    duration_sec: int


class PositionResponse(BaseModel):
    """Open position"""
    symbol: str
    direction: str
    entry_price: float
    current_price: float
    position_size: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    stop_loss: float
    take_profit: float


class MarketStateResponse(BaseModel):
    """Market session state"""
    session: str
    is_trading_active: bool
    is_prime_hour: bool
    expected_win_rate: float
    volatility_factor: float
    liquidity: float
    hours_until_prime: int


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics"""
    capital: float
    equity_peak: float
    drawdown_pct: float
    win_rate: float
    consecutive_losses: int
    total_trades: int
    trades_profitable: int
    total_pnl: float
    sharpe_ratio: Optional[float] = None


class RiskParametersResponse(BaseModel):
    """Current risk parameters"""
    position_size: float
    risk_per_trade: float
    kelly_fraction: float
    stop_loss_pct: float
    take_profit_pct: float
    max_positions: int
    daily_loss_limit: float


class AlertResponse(BaseModel):
    """System alert"""
    level: str
    title: str
    message: str
    timestamp: str


class AgentVoteResponse(BaseModel):
    """Individual agent decision"""
    agent_id: str
    direction: str
    confidence: float
    reasoning: str


class AgentDecisionResponse(BaseModel):
    """Multi-agent consensus decision"""
    direction: str
    confidence: float
    consensus_strength: float
    risk_approved: bool
    agent_votes: List[AgentVoteResponse]
    timestamp: str


class AgentStatsResponse(BaseModel):
    """Agent system statistics"""
    is_julia_running: bool
    decisions_processed: int
    avg_latency_ms: float
    max_latency_ms: float
    error_count: int
    agent_weights: Dict[str, float]


# ============================================================================
# FastAPI Application
# ============================================================================

class TradingAPIServer:
    """
    REST API server for NEUS_TRADER trading engine.
    Provides complete separation between trading logic and presentation.
    """

    def __init__(self, engine: GoldenHourScalpingEngine, host: str = "0.0.0.0", port: int = 8000):
        self.logger = logging.getLogger("TradingAPIServer")
        self.engine = engine
        self.host = host
        self.port = port

        # FastAPI app
        self.app = FastAPI(
            title="NEUS_TRADER API",
            description="High-frequency scalping engine REST API with multi-agent consensus",
            version="2.0.0"
        )

        # CORS middleware for frontend
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production: specify exact origin
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # WebSocket connections
        self.websocket_clients: List[WebSocket] = []

        # Diagnostics
        self.bifurcation_monitor = BifurcationMonitor()

        # Phase 2: Julia multi-agent bridge (optional)
        julia_path = Path(__file__).parent.parent / "julia"
        self.julia_bridge = JuliaBridge(str(julia_path))
        self.use_julia_agents = False

        # Try to start Julia agents (graceful fallback if unavailable)
        try:
            if self.julia_bridge.start():
                self.use_julia_agents = True
                self.logger.info("Julia multi-agent system started (Phase 2 enabled)")
            else:
                self.logger.warning("Julia multi-agent system failed to start, using Phase 1 single agent")
        except Exception as e:
            self.logger.warning(f"Julia multi-agent system unavailable: {e}, using Phase 1 single agent")

        # Register routes
        self._register_routes()

        self.logger.info(f"Trading API Server initialized: {host}:{port} (Julia: {self.use_julia_agents})")

    def _register_routes(self):
        """Register all API routes"""

        # Health check
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

        # Engine status
        @self.app.get("/api/status", response_model=EngineStatusResponse)
        async def get_status():
            metrics = self.engine.risk_manager.get_metrics()
            return EngineStatusResponse(
                symbol=self.engine.symbol,
                is_running=self.engine.is_running,
                capital=metrics['capital'],
                equity=metrics['capital'],
                drawdown_pct=metrics['drawdown_pct'],
                open_positions=len(self.engine.open_positions),
                total_trades=metrics['total_trades'],
                win_rate=metrics.get('win_rate', 0.5),
                timestamp=datetime.utcnow().isoformat()
            )

        # Market state
        @self.app.get("/api/market-state", response_model=MarketStateResponse)
        async def get_market_state():
            state = self.engine.market_hours.get_market_state()
            return MarketStateResponse(
                session=state['session'],
                is_trading_active=state['is_trading_active'],
                is_prime_hour=state['is_prime_hour'],
                expected_win_rate=state['expected_win_rate'],
                volatility_factor=state['volatility_factor'],
                liquidity=state['liquidity'],
                hours_until_prime=state['hours_until_prime']
            )

        # Risk parameters
        @self.app.get("/api/risk-parameters", response_model=RiskParametersResponse)
        async def get_risk_parameters():
            params = self.engine.risk_manager.get_risk_parameters(
                self.engine.volatility_estimate
            )
            return RiskParametersResponse(
                position_size=params.position_size,
                risk_per_trade=params.risk_per_trade,
                kelly_fraction=params.kelly_fraction,
                stop_loss_pct=params.stop_loss_pct,
                take_profit_pct=params.take_profit_pct,
                max_positions=params.max_positions,
                daily_loss_limit=params.daily_loss_limit
            )

        # Performance metrics
        @self.app.get("/api/performance", response_model=PerformanceMetricsResponse)
        async def get_performance():
            metrics = self.engine.risk_manager.get_metrics()
            return PerformanceMetricsResponse(
                capital=metrics['capital'],
                equity_peak=metrics['equity_peak'],
                drawdown_pct=metrics['drawdown_pct'],
                win_rate=metrics.get('win_rate', 0.0),
                consecutive_losses=metrics['consecutive_losses'],
                total_trades=metrics['total_trades'],
                trades_profitable=metrics['trades_profitable'],
                total_pnl=metrics['total_pnl']
            )

        # Open positions
        @self.app.get("/api/positions")
        async def get_positions() -> List[PositionResponse]:
            positions = []
            current_price = self.engine.last_candle['close'] if self.engine.last_candle else 0.0

            for trade_id, position in self.engine.open_positions.items():
                if position['direction'] == "LONG":
                    unrealized_pnl = (current_price - position['entry_price']) * position['position_size']
                    unrealized_pnl_pct = (current_price - position['entry_price']) / position['entry_price']
                else:
                    unrealized_pnl = (position['entry_price'] - current_price) * position['position_size']
                    unrealized_pnl_pct = (position['entry_price'] - current_price) / position['entry_price']

                positions.append(PositionResponse(
                    symbol=self.engine.symbol,
                    direction=position['direction'],
                    entry_price=position['entry_price'],
                    current_price=current_price,
                    position_size=position['position_size'],
                    unrealized_pnl=unrealized_pnl,
                    unrealized_pnl_pct=unrealized_pnl_pct,
                    stop_loss=position['stop_loss'],
                    take_profit=position['tp2']
                ))

            return positions

        # Alerts
        @self.app.get("/api/alerts")
        async def get_alerts(minutes: int = 60) -> List[AlertResponse]:
            alerts = self.engine.monitor.get_recent_alerts(minutes=minutes)
            return [
                AlertResponse(
                    level=alert.level.value,
                    title=alert.title,
                    message=alert.message,
                    timestamp=alert.timestamp.isoformat()
                )
                for alert in alerts
            ]

        # Start trading
        @self.app.post("/api/start")
        async def start_trading():
            if self.engine.is_running:
                raise HTTPException(status_code=400, detail="Engine already running")
            self.engine.start()
            return {"status": "started", "timestamp": datetime.utcnow().isoformat()}

        # Stop trading
        @self.app.post("/api/stop")
        async def stop_trading():
            if not self.engine.is_running:
                raise HTTPException(status_code=400, detail="Engine not running")
            self.engine.stop()
            return {"status": "stopped", "timestamp": datetime.utcnow().isoformat()}

        # Diagnostics
        @self.app.get("/api/diagnostics")
        async def get_diagnostics():
            return {
                "ring_buffer": self.engine.ring_buffer.stats(),
                "worker_stats": self.engine.ledger_worker.get_stats(),
                "bifurcation_monitor": {
                    "total_calls": self.bifurcation_monitor.metrics['total_critical_path_calls'],
                    "enqueues": self.bifurcation_monitor.metrics['total_ring_buffer_enqueues'],
                    "dropped": self.bifurcation_monitor.metrics['ring_buffer_drop_count']
                }
            }

        # Phase 2: Agent decisions
        @self.app.get("/api/agent-decisions", response_model=Optional[AgentDecisionResponse])
        async def get_agent_decisions():
            """Get latest multi-agent consensus decision."""
            if not self.use_julia_agents:
                return None

            # Prepare data for Julia
            candles_data = self._prepare_candles_for_julia()
            engine_state_data = self._prepare_engine_state_for_julia()
            prices_data = self._prepare_prices_for_julia()

            # Get decision from Julia
            decision = self.julia_bridge.send_decision_request(
                candles_data, engine_state_data, prices_data
            )

            if not decision:
                return None

            # Convert to response format
            agent_votes = []
            for agent_id, vote in decision.agent_votes.items():
                agent_votes.append(AgentVoteResponse(
                    agent_id=agent_id,
                    direction=vote.get('direction', 'HOLD'),
                    confidence=vote.get('confidence', 0.0),
                    reasoning=vote.get('reasoning', '')
                ))

            return AgentDecisionResponse(
                direction=decision.direction,
                confidence=decision.confidence,
                consensus_strength=decision.consensus_strength,
                risk_approved=decision.risk_approved,
                agent_votes=agent_votes,
                timestamp=decision.timestamp
            )

        # Phase 2: Agent statistics
        @self.app.get("/api/agent-stats", response_model=AgentStatsResponse)
        async def get_agent_stats():
            """Get multi-agent system statistics."""
            if not self.use_julia_agents:
                stats = {
                    'is_julia_running': False,
                    'decisions_processed': 0,
                    'avg_latency_ms': 0.0,
                    'max_latency_ms': 0.0,
                    'error_count': 0,
                    'agent_weights': {}
                }
            else:
                julia_stats = self.julia_bridge.get_stats()
                stats = {
                    'is_julia_running': julia_stats.get('is_running', False),
                    'decisions_processed': julia_stats.get('decisions_processed', 0),
                    'avg_latency_ms': julia_stats.get('avg_latency_ms', 0.0),
                    'max_latency_ms': julia_stats.get('max_latency_ms', 0.0),
                    'error_count': julia_stats.get('errors', 0),
                    'agent_weights': {}
                }

            return AgentStatsResponse(**stats)

        # WebSocket for real-time updates
        @self.app.websocket("/ws/market-updates")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.websocket_clients.append(websocket)

            try:
                while True:
                    # Send status updates every second
                    data = await self.get_status()
                    await websocket.send_json(data.dict())
                    await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
            finally:
                self.websocket_clients.remove(websocket)

        self.logger.info("API routes registered")

    def _prepare_candles_for_julia(self) -> List[Dict]:
        """Prepare recent candles for Julia agent analysis."""
        candles = []
        # Use last 50 candles from engine history (if available)
        # For now, return minimal data structure
        if self.engine.last_candle:
            candles.append({
                'timestamp': datetime.utcnow().isoformat(),
                'open': self.engine.last_candle.get('open', 0.0),
                'high': self.engine.last_candle.get('high', 0.0),
                'low': self.engine.last_candle.get('low', 0.0),
                'close': self.engine.last_candle.get('close', 0.0),
                'volume': self.engine.last_candle.get('volume', 0.0)
            })
        return candles

    def _prepare_engine_state_for_julia(self) -> Dict:
        """Prepare current engine state for Julia agent analysis."""
        metrics = self.engine.risk_manager.get_metrics()
        return {
            'symbol': self.engine.symbol,
            'current_price': self.engine.last_candle.get('close', 0.0) if self.engine.last_candle else 0.0,
            'capital': metrics.get('capital', 0.0),
            'equity': metrics.get('capital', 0.0),
            'drawdown_pct': metrics.get('drawdown_pct', 0.0),
            'open_positions': len(self.engine.open_positions),
            'total_trades': metrics.get('total_trades', 0),
            'win_rate': metrics.get('win_rate', 0.5),
            'last_trade_pnl': 0.0,
            'is_running': self.engine.is_running
        }

    def _prepare_prices_for_julia(self) -> Dict[str, float]:
        """Prepare multi-venue prices for arbitrage agent (placeholder)."""
        # In production, would fetch prices from multiple exchanges
        current_price = self.engine.last_candle.get('close', 0.0) if self.engine.last_candle else 0.0
        return {
            'binance': current_price,
            'coinbase': current_price
        }

    async def broadcast_update(self, data: Dict):
        """Broadcast update to all connected WebSocket clients"""
        disconnected = []
        for client in self.websocket_clients:
            try:
                await client.send_json(data)
            except Exception as e:
                self.logger.error(f"Failed to send to client: {e}")
                disconnected.append(client)

        for client in disconnected:
            self.websocket_clients.remove(client)

    def run(self):
        """Start API server"""
        import uvicorn

        self.logger.info(f"Starting API server on {self.host}:{self.port}")
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )


# ============================================================================
# Standalone Usage
# ============================================================================

if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s"
    )

    # Create engine
    engine = GoldenHourScalpingEngine(
        symbol="ETHUSDT",
        initial_capital=10000.0
    )

    # Create and run API server
    api_server = TradingAPIServer(engine, host="0.0.0.0", port=8000)
    api_server.run()
