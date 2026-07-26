# Phase 2 Architecture: Julia Multi-Agent System with Consensus Voting

## Overview

**Objective**: Extend Phase 1's single Golden Hour Scalper with a consensus-based multi-agent system where 5 specialized Julia agents vote on trading decisions, improving signal quality and risk management through ensemble methods.

```
┌────────────────────────────────────────────────────────────────┐
│              React Dashboard (Port 3000)                       │
│         Real-time visualization & control interface           │
└──────────────────┬─────────────────────────────────────────────┘
                   │ REST API + WebSocket
                   ↓
┌────────────────────────────────────────────────────────────────┐
│           FastAPI Backend (Port 8000)                          │
│  - Orchestrates agents, manages consensus voting              │
│  - Exposes agent decisions to frontend                        │
└──────────────────┬─────────────────────────────────────────────┘
                   │ IPC / Stdio
                   ↓
┌────────────────────────────────────────────────────────────────┐
│         Julia Multi-Agent System (Process)                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Momentum Agent   │  │ Mean-Reversion   │                   │
│  │ (Fast trends)    │  │ Agent (Pullbacks)│                   │
│  └──────────────────┘  └──────────────────┘                   │
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Volatility Agent │  │ Arbitrage Agent  │                   │
│  │ (Vol breakouts)  │  │ (Cross-venue)    │                   │
│  └──────────────────┘  └──────────────────┘                   │
│                                                                │
│  ┌──────────────────────────────────────┐                     │
│  │     Risk Management Agent             │                    │
│  │  (Position sizing, circuit breaker)   │                    │
│  └──────────────────────────────────────┘                     │
│                                                                │
│  ┌──────────────────────────────────────┐                     │
│  │  Consensus Voting Engine              │                    │
│  │  - Majority voting (3+ agents agree)  │                    │
│  │  - Confidence weighting               │                    │
│  │  - Dissent tracking for meta-learning │                    │
│  └──────────────────────────────────────┘                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                   │
                   ↓
┌────────────────────────────────────────────────────────────────┐
│      Ring Buffer + Ledger Worker (Bifurcation)                │
│  (In-memory event queue + async persistence)                 │
└────────────────────────────────────────────────────────────────┘
```

## Agent Specifications

### 1. Momentum Agent
**Strategy**: Fast-moving trends identified via EMA crossover and MACD

```julia
struct MomentumAgent
  ema_short::Int              # 9-period
  ema_long::Int               # 21-period
  macd_fast::Int              # 12-period
  macd_slow::Int              # 26-period
  macd_signal::Int            # 9-period
  trend_strength_threshold::Float64  # 0.6
end

function analyze(agent::MomentumAgent, candles::DataFrame) -> Decision
  # Returns: LONG, SHORT, or HOLD
  # Confidence: 0.0 - 1.0 based on MACD divergence
end
```

**Triggers**: When EMA(9) > EMA(21) and MACD > Signal
**Confidence**: 1.0 if trend is strong, 0.5 if weak

### 2. Mean-Reversion Agent
**Strategy**: Identifies overbought/oversold conditions via RSI and Bollinger Bands

```julia
struct MeanReversionAgent
  rsi_period::Int             # 14-period
  rsi_overbought::Float64     # 70
  rsi_oversold::Float64       # 30
  bb_period::Int              # 20-period
  bb_std_dev::Float64         # 2.0
end

function analyze(agent::MeanReversionAgent, candles::DataFrame) -> Decision
  # Returns: LONG (on oversold), SHORT (on overbought), or HOLD
  # Confidence: distance from midline / distance to band
end
```

**Triggers**: When RSI < 30 (LONG) or RSI > 70 (SHORT)
**Confidence**: 1.0 if touching band, 0.5 if near band

### 3. Volatility Agent
**Strategy**: Breakout detection via ATR and Keltner Channels

```julia
struct VolatilityAgent
  atr_period::Int             # 14-period
  kc_period::Int              # 20-period
  breakout_multiplier::Float64 # 1.5
end

function analyze(agent::VolatilityAgent, candles::DataFrame) -> Decision
  # Returns: LONG (upper breakout), SHORT (lower breakout), or HOLD
  # Confidence: 1.0 if strong breakout, 0.5 if weak
end
```

**Triggers**: When price breaks outside Keltner Channels
**Confidence**: Based on breakout magnitude vs ATR

### 4. Arbitrage Agent
**Strategy**: Cross-venue price discrepancies (ETH/USD on different exchanges)

```julia
struct ArbitrageAgent
  venue_1::Symbol             # :binance
  venue_2::Symbol             # :coinbase
  spread_threshold::Float64   # 0.002 (0.2%)
end

function analyze(agent::ArbitrageAgent, prices::Dict) -> Decision
  # Returns: LONG (if venue 1 cheaper), SHORT (if venue 2 cheaper), or HOLD
  # Confidence: spread_pct / spread_threshold
end
```

**Triggers**: When spread > 0.2%
**Confidence**: spread size relative to threshold

### 5. Risk Management Agent
**Strategy**: Position sizing and circuit breaker logic

```julia
struct RiskManagementAgent
  max_position_size::Float64  # USDT
  max_concurrent_positions::Int
  max_drawdown_pct::Float64   # 20%
  max_daily_loss_pct::Float64 # 3%
end

function analyze(agent::RiskManagementAgent, state::EngineState) -> Decision
  # Returns: ALLOW (proceed), REDUCE (smaller position), or DENY (circuit break)
  # Confidence: 1.0 always (binary decision)
end
```

**Triggers**: Always runs before position open
**Confidence**: 1.0 (certain allow/deny), 0.5 (suggest reduction)

## Consensus Voting Mechanism

### Voting Rules

```julia
struct VotingResult
  direction::Symbol           # :LONG, :SHORT, :HOLD
  confidence::Float64         # 0.0 - 1.0
  agent_votes::Dict           # Agent ID => (direction, confidence)
  consensus_strength::Float64 # 0.0 - 1.0
  risk_approved::Bool         # Risk agent approval
end

function consensus_vote(agent_decisions::Vector{Decision}) -> VotingResult
  # 1. Collect votes from all 4 active agents (momentum, mean-reversion, volatility, arbitrage)
  # 2. Risk agent runs independently as gate/filter
  # 3. Majority voting (3+ agents agree = signal)
  # 4. Weighted confidence by agent track record
  # 5. Dissent tracking for meta-learning
  
  vote_counts = count_votes(agent_decisions)
  
  # Require 3+ agents to agree on direction
  if vote_counts[:LONG] >= 3
    return VotingResult(:LONG, mean_confidence(...), ..., true)
  elseif vote_counts[:SHORT] >= 3
    return VotingResult(:SHORT, mean_confidence(...), ..., true)
  else
    return VotingResult(:HOLD, 0.0, ..., false)
  end
end
```

### Confidence Scoring

```julia
function weighted_confidence(votes::Dict, agent_weights::Dict) -> Float64
  # weight = (win_rate - 50%) / 50%  # Range: [-1, 1]
  # confidence = mean(vote_confidence .* agent_weights)
  # return max(0, confidence)
end
```

### Dissent Tracking

```julia
struct DissentRecord
  timestamp::DateTime
  agent_1::Symbol
  agent_2::Symbol
  eventual_outcome::Symbol    # :LONG, :SHORT, :HOLD
  dissent_was_correct::Bool
end

# Use dissent history to identify agent disagreement patterns
# Example: If momentum and mean-reversion disagree, weight risk manager more heavily
```

## Integration Points

### Python Backend ↔ Julia Agents

**Communication**: Stdio-based message passing (JSON)

```python
# Python → Julia
{
  "type": "analyze",
  "timestamp": 1689012345.123,
  "symbol": "ETHUSDT",
  "candles": [...],  # Last 50 candles
  "current_state": {...}
}

# Julia → Python
{
  "type": "decision",
  "decisions": [
    {"agent": "momentum", "direction": "LONG", "confidence": 0.8},
    {"agent": "mean_reversion", "direction": "HOLD", "confidence": 0.5},
    ...
  ],
  "consensus": {
    "direction": "LONG",
    "confidence": 0.75,
    "strength": 0.8,
    "risk_approved": true
  }
}
```

### Event Flow

```
1. Market Update (WebSocket or polling)
   ↓
2. Python Backend: Update candle history
   ↓
3. Python → Julia: Send latest candles + state
   ↓
4. Julia Agents: Analyze in parallel
   ↓
5. Consensus Vote: Aggregate decisions
   ↓
6. Julia → Python: Return consensus decision
   ↓
7. Risk Gate: Risk Management Agent final check
   ↓
8. Trade Execution: Execute if approved
   ↓
9. Event Logging: Ring buffer → Ledger worker
   ↓
10. Frontend: WebSocket update to dashboard
```

## Performance Targets

**Latency**: Julia analysis + consensus should complete within 100ms
- Agent analysis: 20ms (parallel processing)
- Consensus voting: 5ms
- Python overhead: 25ms
- Total: ~50ms (well under 500ms critical path)

**Throughput**: Support 1 decision per candle (every 5-15 seconds in live trading)

**Accuracy**: Consensus votes should improve win rate from 60% (single agent) to 70%+ (ensemble)

## Implementation Roadmap

### Phase 2.1: Julia Agent Framework
- [ ] Julia project setup with dependencies (DataFrames, Indicators, Plots)
- [ ] Base agent interface (abstract Agent)
- [ ] Indicator library wrapper (EMA, RSI, MACD, Bollinger Bands, Keltner, ATR)
- [ ] Single agent implementation (Momentum Agent)
- [ ] Unit tests for agent analysis

### Phase 2.2: Multi-Agent System
- [ ] Implement remaining 4 agents
- [ ] Consensus voting engine
- [ ] Dissent tracking and meta-learning
- [ ] Integration tests

### Phase 2.3: Python-Julia Bridge
- [ ] Stdio message passing protocol
- [ ] Julia process management (spawn/monitor/cleanup)
- [ ] Error handling and reconnection logic
- [ ] Performance profiling

### Phase 2.4: Backend Integration
- [ ] Update FastAPI endpoints to use multi-agent system
- [ ] A/B testing: single vs ensemble agents
- [ ] Dashboard updates for agent voting visualization
- [ ] Live trading activation

## Configuration (julia_agents.yaml)

```yaml
agents:
  momentum:
    enabled: true
    ema_short: 9
    ema_long: 21
    macd_fast: 12
    macd_slow: 26
    macd_signal: 9
    trend_strength_threshold: 0.6
    
  mean_reversion:
    enabled: true
    rsi_period: 14
    rsi_overbought: 70
    rsi_oversold: 30
    bb_period: 20
    bb_std_dev: 2.0
    
  volatility:
    enabled: true
    atr_period: 14
    kc_period: 20
    breakout_multiplier: 1.5
    
  arbitrage:
    enabled: false  # Requires multi-exchange data
    venue_1: binance
    venue_2: coinbase
    spread_threshold: 0.002
    
  risk_management:
    enabled: true
    max_position_size: 1000
    max_concurrent_positions: 3
    max_drawdown_pct: 20.0
    max_daily_loss_pct: 3.0

voting:
  min_agreement: 3  # Require 3+ agents to agree
  confidence_weighting: true
  dissent_tracking: true
  meta_learning_enabled: true
```

## Testing Strategy

### Unit Tests (Julia)
- Agent decision logic (given known inputs, verify outputs)
- Indicator calculations (compare to reference implementations)
- Voting aggregation (verify majority voting logic)

### Integration Tests (Python ↔ Julia)
- Message passing protocol (serialize/deserialize JSON)
- Process lifecycle (spawn, communicate, shutdown)
- Error handling (malformed JSON, agent crashes)

### Backtesting
- Historical data with agent decisions logged
- Verify ensemble outperforms single agent
- Optimize agent weights via dissent analysis

### Live Paper Trading
- Real market data (Binance WebSocket)
- Agent decisions executed in paper mode
- Monitor agent agreement rates
- Validate latency <100ms per decision

## Risk Considerations

**Risk 1**: Agent disagreement leads to no trades
- Mitigation: Default to HOLD when no consensus, rather than random action

**Risk 2**: Correlated agent failures in certain market regimes
- Mitigation: Dissent tracking identifies patterns, allow override via manual mode

**Risk 3**: Julia process crashes during live trading
- Mitigation: Fallback to Phase 1 single agent mode, automatic restart with exponential backoff

**Risk 4**: Latency from Python-Julia IPC exceeds 100ms
- Mitigation: Pre-fork Julia process, use stdio buffering, profile decision latency

## Future Enhancements (Phase 3+)

- **Adaptive Weighting**: Dynamically adjust agent weights based on recent performance
- **Market Regime Detection**: Switch between agent subsets depending on market conditions
- **Natural Language Processing**: Parse news sentiment for additional signal
- **Deep Learning**: Neural network agent for complex pattern recognition
- **Multi-Symbol Trading**: Extend to trade multiple symbols simultaneously
- **Options Trading**: Introduce options agents for volatility arbitrage

---

**Architecture Status**: Design phase complete, ready for Phase 2.1 implementation
**Next Step**: Create Julia project structure and implement Momentum Agent
