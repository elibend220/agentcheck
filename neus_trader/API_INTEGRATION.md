# NEUS_TRADER API Integration Guide

## Overview

The NEUS_TRADER system has complete real-time API integration with Binance for live market data analysis and trading signal generation.

```
┌─────────────────────────────────────────────────────────────┐
│              Binance Real-Time WebSocket                     │
│              (Live OHLCV Candle Data Stream)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ WSS://stream.binance.com:9443/ws
                       │
                       ↓
┌──────────────────────────────────────────────────────────────┐
│              Paper Trading Engine                             │
│         (Golden Hour Scalping Strategy)                       │
│                                                               │
│  • Real-time signal processing                               │
│  • Adaptive risk management                                  │
│  • Position management                                       │
│  • Trade execution (simulated)                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                      │
│                                                               │
│  REST API Endpoints                WebSocket                 │
│  • /health                         • /ws/market-updates      │
│  • /api/status                                               │
│  • /api/market-state                                         │
│  • /api/positions                                            │
│  • /api/performance                                          │
│  • /api/risk-parameters                                      │
│  • /api/alerts                                               │
│  • /api/diagnostics                                          │
│  • /api/agent-decisions (Phase 2)                            │
│  • /api/agent-stats (Phase 2)                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────────────┐
│              React Dashboard (Port 3000)                      │
│                                                               │
│  • Real-time status monitoring                               │
│  • Position visualization                                    │
│  • Trade history                                             │
│  • Performance metrics                                       │
│  • Risk management controls                                  │
│  • Agent decision display (Phase 2)                          │
└──────────────────────────────────────────────────────────────┘
```

## Real-Time Data Flow

### 1. Binance WebSocket Stream (Live Market Data)

**Connection Details:**
- **URL**: `wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}`
- **Example**: `wss://stream.binance.com:9443/ws/ethusdt@kline_5m`
- **Data Type**: OHLCV candle data (Open, High, Low, Close, Volume)
- **Update Frequency**: Every 5 minutes (configurable)
- **No Authentication**: Public market data stream (no API key needed)

**Data Structure Received:**
```json
{
  "e": "kline",
  "E": 1234567890123,
  "s": "ETHUSDT",
  "k": {
    "t": 1234567890000,
    "T": 1234567950000,
    "s": "ETHUSDT",
    "i": "5m",
    "f": 100,
    "L": 200,
    "o": "2500.50",
    "c": "2510.25",
    "h": "2515.00",
    "l": "2495.75",
    "v": "12345.67",
    "n": 101,
    "x": true,
    "q": "30925678.50",
    "V": "6789.12",
    "Q": "17012345.25",
    "B": "0"
  }
}
```

**Parsed Format (Python):**
```python
{
    'timestamp': datetime,      # Candle close time
    'open': float,              # Opening price
    'high': float,              # Highest price in candle
    'low': float,               # Lowest price in candle
    'close': float,             # Closing price
    'volume': float             # Volume in base asset
}
```

### 2. Paper Trading Engine Processing

**Engine Pipeline:**
```
Candle Data
    ↓
[Technical Indicators]
  • SuperTrend (RSI-based)
  • VROC (Volume Rate of Change)
  • RSI (Relative Strength Index)
    ↓
[Signal Generation]
  • Entry signals (LONG/SHORT/HOLD)
  • Confidence scoring
  • Multi-confirmation checks
    ↓
[Risk Management]
  • Dynamic position sizing
  • Stop loss placement
  • Take profit levels
  • Max position limits
    ↓
[Position Execution]
  • Entry order (simulated)
  • Position tracking
  • P&L calculation
  • Exit on SL/TP (simulated)
    ↓
[Trade Recording]
  • Ring buffer (fast)
  • Background worker (async logging)
  • JSON export
```

### 3. API Backend (FastAPI)

**HTTP REST Endpoints:**

#### Health Check
```
GET /health
Response: {"status": "healthy", "timestamp": "2026-08-03T16:47:53Z"}
```

#### Engine Status
```
GET /api/status
Response:
{
    "symbol": "ETHUSDT",
    "is_running": true,
    "capital": 10000.0,
    "equity": 10050.25,
    "drawdown_pct": -0.5,
    "open_positions": 2,
    "total_trades": 15,
    "win_rate": 0.605,
    "timestamp": "2026-08-03T16:47:53Z"
}
```

#### Market State
```
GET /api/market-state
Response:
{
    "session": "London",
    "is_trading_active": true,
    "is_prime_hour": true,
    "expected_win_rate": 0.65,
    "volatility_factor": 1.2,
    "liquidity": 0.95,
    "hours_until_prime": 0
}
```

#### Open Positions
```
GET /api/positions
Response:
[
    {
        "symbol": "ETHUSDT",
        "direction": "LONG",
        "entry_price": 2500.50,
        "current_price": 2510.25,
        "position_size": 1.0,
        "unrealized_pnl": 9.75,
        "unrealized_pnl_pct": 0.0039,
        "stop_loss": 2475.00,
        "take_profit": 2550.00
    }
]
```

#### Performance Metrics
```
GET /api/performance
Response:
{
    "capital": 10000.0,
    "equity_peak": 10250.50,
    "drawdown_pct": 2.5,
    "win_rate": 0.605,
    "consecutive_losses": 2,
    "total_trades": 15,
    "trades_profitable": 9,
    "total_pnl": 250.50,
    "sharpe_ratio": 1.25
}
```

#### Risk Parameters
```
GET /api/risk-parameters
Response:
{
    "position_size": 0.01,
    "risk_per_trade": 100.0,
    "kelly_fraction": 0.25,
    "stop_loss_pct": 2.0,
    "take_profit_pct": 3.0,
    "max_positions": 3,
    "daily_loss_limit": 300.0
}
```

#### System Alerts
```
GET /api/alerts?minutes=60
Response:
[
    {
        "level": "warning",
        "title": "Consecutive Losses",
        "message": "3 consecutive losing trades detected",
        "timestamp": "2026-08-03T16:30:00Z"
    },
    {
        "level": "info",
        "title": "Prime Hour Active",
        "message": "London trading session: 65% expected win rate",
        "timestamp": "2026-08-03T16:47:00Z"
    }
]
```

#### System Diagnostics
```
GET /api/diagnostics
Response:
{
    "ring_buffer": {
        "size": 345,
        "max_size": 10000,
        "enqueues": 8923,
        "dequeues": 8578,
        "dropped": 0
    },
    "worker_stats": {
        "batches_processed": 429,
        "avg_batch_size": 20,
        "total_trades_logged": 8578
    },
    "bifurcation_monitor": {
        "total_calls": 8923,
        "enqueues": 8923,
        "dropped": 0
    }
}
```

**WebSocket (Real-Time Updates):**
```
WS /ws/market-updates
Sends status updates every 1 second
Same data structure as GET /api/status
```

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

**Start complete system with one command:**
```bash
cd /home/user/agentcheck/neus_trader
python deploy_live_system.py --symbol ETHUSDT --capital 10000
```

**What it does:**
1. Checks all dependencies (websockets, fastapi, pandas, etc.)
2. Tests Binance WebSocket connection
3. Starts Paper Trading Engine (live market data)
4. Starts FastAPI Backend (port 8000)
5. Starts React Dashboard (port 3000)
6. Displays live monitoring interface

**Output:**
```
======================================================================
NEUS_TRADER LIVE SYSTEM DEPLOYMENT
======================================================================

📊 System Configuration:
   Trading Pair: ETHUSDT
   Initial Capital: $10000.00
   Candle Interval: 5m
   Data Source: Binance Real-Time WebSocket
   Mode: PAPER TRADING (no real capital)

⚙️  Components Starting:
   ✓ Phase 1: Golden Hour Scalping Engine
   ✓ Binance Live Market Data (WSS)
   ✓ FastAPI Backend (Port 8000)
   ✓ React Dashboard (Port 3000)
   ✓ Real-Time Monitoring & Analytics
```

### Method 2: Component-by-Component

**Terminal 1 - Paper Trading:**
```bash
python run_paper_trading.py --symbol ETHUSDT --capital 10000
```

**Terminal 2 - API Server:**
```bash
python python_core/api_server.py
```

**Terminal 3 - Dashboard (if available):**
```bash
cd dashboard && npm start
```

**Terminal 4 - Monitor API:**
```bash
watch -n 1 'curl -s http://localhost:8000/api/status | jq .'
```

### Method 3: Docker (Future)

```bash
docker-compose up -d
# Binance WebSocket → Engine → API → Dashboard
```

## Testing the Integration

### Test 1: Binance Connection
```bash
python -c "
import asyncio
from python_core.binance_websocket import BinanceWebSocketClient
asyncio.run(BinanceWebSocketClient.test_connection('ETHUSDT', '5m'))
"
```

### Test 2: API Health Check
```bash
curl http://localhost:8000/health
```

### Test 3: Get Current Status
```bash
curl http://localhost:8000/api/status | jq .
```

### Test 4: Monitor Live Updates (Every 5 seconds)
```bash
while true; do
  clear
  echo "=== NEUS_TRADER Status ==="
  curl -s http://localhost:8000/api/status | jq '.capital, .equity, .total_trades, .win_rate'
  sleep 5
done
```

### Test 5: WebSocket Connection
```bash
wscat -c ws://localhost:8000/ws/market-updates
```

## Performance Optimization

### Bifurcation Architecture (I/O Decoupling)

Problem: Trade logging was blocking critical path (60ms latency)

Solution:
- **Ring Buffer**: In-memory FIFO queue (max 10,000 events, <1μs enqueue)
- **Ledger Worker**: Background thread batching trades (50 events per 2ms)
- **Result**: ~20x latency improvement (60ms → 3ms per cycle)

### Data Flow Latency

```
Binance Stream → Engine → Ring Buffer → API Response
      100ms       5-10ms      <1μs       10-50ms
                  └──────────────────┘
                  Critical path: ~15ms
                  (bounded by candle interval)
```

## Configuration

### Market Hours Optimization

System automatically optimizes trading during high-win-rate sessions:

```
Session     | Timezone | Hours    | Expected Win Rate | Status
────────────────────────────────────────────────────────────────
London      | UTC      | 13-17    | 65%              | ✓ Optimal
US Close    | UTC      | 20-23    | 60%              | ✓ Good
Asia Open   | UTC      | 22-06    | 50%              | ✓ Normal
US Morning  | UTC      | 13-21    | 55%              | ✓ Normal
```

### Risk Parameters (Tuned via Backtesting)

```yaml
# From 30-day historical optimization
position_size: 1.0%                 # Kelly fraction
risk_per_trade: $100 (1% capital)   # Max loss per trade
stop_loss: 2.0%                     # Below entry
take_profit: 3.0%                   # Above entry
max_positions: 3                    # Concurrent positions
daily_loss_limit: 3%                # Circuit breaker
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'websockets'"
**Solution:**
```bash
pip install websockets>=11.0.0
```

### Issue: "Connection refused: localhost:8000"
**Solution:**
1. Verify API server started: `python python_core/api_server.py`
2. Check if port 8000 is in use: `lsof -i :8000`
3. Use different port: `python api_server.py --port 8001`

### Issue: "Binance WebSocket connection failed"
**Solution:**
1. Check internet connection: `ping stream.binance.com`
2. Check proxy settings (if behind corporate proxy)
3. Try different interval: `--interval 1m` or `--interval 15m`
4. Binance API status: https://www.binance.com/en/support/announcement/c-48

### Issue: "No candles received from Binance"
**Solution:**
1. Verify symbol is correct (e.g., 'ETHUSDT', not 'ETHUSD')
2. Check Binance supports the interval (1m, 5m, 15m, 1h, 4h, 1d)
3. Ensure Binance server is running: `curl https://api.binance.com/api/v3/time`

## Security Notes

### What's Safe
- ✓ Paper trading (no real capital)
- ✓ Public Binance market data (no authentication needed)
- ✓ Simulated position tracking
- ✓ Local-only API (localhost:8000)

### What's NOT Implemented Yet
- ✗ Real order execution (Future Phase 3)
- ✗ API authentication/authorization
- ✗ Encrypted storage of credentials
- ✗ Production deployment (Kubernetes, etc.)

### For Production Deployment
Before using with real capital:
1. Implement API key management (encrypted storage)
2. Add authentication to API endpoints
3. Use HTTPS instead of HTTP
4. Deploy behind reverse proxy (nginx, etc.)
5. Add rate limiting
6. Implement audit logging
7. Add circuit breakers for risk control
8. Set up monitoring/alerting

## Next Steps

1. **Test the connection:** Run `deploy_live_system.py`
2. **Monitor live trading:** Visit `http://localhost:3000`
3. **Check API status:** `curl http://localhost:8000/api/status`
4. **Analyze results:** Review paper trading performance
5. **Optimize parameters:** Adjust based on market conditions
6. **Plan Phase 3:** Real order execution with Binance API

## Documentation Links

- **Binance API**: https://binance-docs.github.io/apidocs/
- **WebSocket Streams**: https://binance-docs.github.io/apidocs/spot/c_index
- **Kline (Candle) Data**: https://binance-docs.github.io/apidocs/#kline-candlestick-streams
- **FastAPI**: https://fastapi.tiangolo.com/
- **WebSocket Protocol**: https://tools.ietf.org/html/rfc6455

---

**Status**: Production-ready for paper trading
**Last Updated**: 2026-08-03
**System Version**: NEUS_TRADER v2.0 (Phase 1 + Phase 2)
