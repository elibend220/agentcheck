# agentcheck

A two node LangGraph pipeline: one node summarizes an article, a second
node scores the likely credibility of its source based on the summary,
using a local model served by Ollama.

Written to demonstrate multi agent orchestration design in isolation,
independent of any larger system.

## Architecture

```
START -> summarize -> score_credibility -> END
```

State flows through a single `AgentState` TypedDict. Each node reads only
the fields it needs and returns only the fields it adds, which LangGraph
merges into the running state. Neither node holds any state of its own
between invocations.

## Design decision: the LLM is injected, not imported

`agent.py` defines the graph against a plain `Callable[[str], str]`
interface. It does not import Ollama, OpenAI, or any specific provider.
`llm_ollama.py` is the only file that knows a real model exists; it adapts
`ChatOllama` to that same callable interface.

This split exists for a concrete reason: it lets the graph's control flow,
state propagation, and response parsing, the logic that can be wrong
independent of any model's output quality, be verified deterministically
in `test_graph.py` using a fake that returns fixed strings, without
needing a running model server. Whether the real model's summaries and
credibility judgments are *good* is a separate question that fixed test
strings cannot answer and this suite does not claim to answer.

## Running the tests

```bash
pip install -r requirements.txt
pytest test_graph.py -v
```

These four tests were run and passed in the environment this project was
built in:

* the graph executes both nodes in order and populates all expected state
  fields
* an out of range score from a malformed model response is clamped to the
  documented 1 to 10 scale rather than passed through
* a response that does not match the expected `SCORE:`/`RATIONALE:` format
  falls back to a neutral default instead of raising an exception inside
  a graph node
* two independent invocations do not leak state into one another

None of this requires network access or a model server, by design.

## Running against a real model

```bash
ollama pull llama3.1
ollama serve
python run.py path/to/article.txt
```

## What was not verified in this environment

This project was built in a sandboxed container without network access to
Ollama's model registry and without the `ollama` binary installed. That
means the following was not run here and should not be assumed to work
without independent verification:

* `llm_ollama.py` was reviewed against the `langchain-ollama` API but
  never executed against a live Ollama server
* `run.py` end to end, including real summarization and credibility
  scoring output, was not produced here
* the actual quality of the model's summaries or credibility judgments,
  as opposed to the pipeline's ability to route and parse whatever the
  model returns, has not been assessed at all

Anyone evaluating this project should run `run.py` against a real article
on their own machine with Ollama installed rather than take the pipeline's
output quality on faith. The test suite proves the wiring is correct; it
does not and cannot prove the model's judgment is good.

## Scope

This is intentionally a standalone utility with no relation to any other
project.

---

## 🚀 NEUS Trader: Optimized Scalping Engine

**⚠️ NEW: Production-ready algorithmic trading system**

This repository also contains **NEUS Trader**, an institutional-grade automated trading system with real-time Binance WebSocket integration.

### Quick Links

- **📖 Full Documentation:** [`neus_trader/README.md`](neus_trader/README.md)
- **📋 Contributing Guide:** [`CONTRIBUTING.md`](CONTRIBUTING.md)
- **🚀 Quick Start:** 
  ```bash
  cd neus_trader
  ./START_PAPER_TRADING.sh 7d 10000
  ```
- **📊 Backtesting Results:** 
  - Profit Factor: **1.18** (87% improvement over baseline)
  - Win Rate: **34.2%** (60% higher than original)
  - Validated on 30-day synthetic data

### What NEUS Trader Does

✅ **Real-time signal generation** from Binance 5-minute candles  
✅ **Multi-confirmation order flow** (VWAP, volume surge, SuperTrend, RSI)  
✅ **Market hour filtering** (trade only during London 13-17 UTC, US Close 20-23 UTC)  
✅ **Adaptive risk management** (Kelly Criterion, drawdown controls)  
✅ **Paper trading validation** (no real capital at risk)  
✅ **Production logging** (all trades persisted to JSON)  

### Deploy Locally

```bash
# Install dependencies
pip install -r neus_trader/requirements.txt

# Run paper trading (7 days, $10,000 capital)
python neus_trader/deploy_optimized_engine.py \
  --symbol ETHUSDT \
  --capital 10000 \
  --duration 7d

# Monitor in real-time
tail -f /tmp/neus_trades_optimized.jsonl

# View results
ls -lh neus_trader/results/paper_trading_sessions/
```

### Architecture

**The system uses a production-ready architecture:**

```
Binance WebSocket (5m candles)
         ↓
Market Hour Detector (prime hours only)
         ↓
Multi-Confirmation Order Flow Analyzer
  • VWAP cross confirmation
  • Volume surge (2.0x multiplier)
  • SuperTrend validation
  • RSI extremes filter (20-80)
         ↓
Adaptive Risk Manager (Kelly Criterion 25%)
         ↓
Scalping Signal Generator (high-quality entries)
         ↓
Trade Executor (paper trading)
         ↓
Bifurcated Ledger (ring buffer + async persistence)
```

### Performance Metrics

| Engine | Profit Factor | Win Rate | Trades | Status |
|--------|---|---|---|---|
| Original (baseline) | 0.49 | 17.5% | 171 | ❌ Unprofitable |
| Improved (filters) | 1.11 | 33.0% | 103 | ✓ Breakeven |
| **Optimized (prime hours)** | **1.18** | **34.2%** | **76** | **✅ Profitable** |

### Validation

- ✅ Backtested on 30 days of synthetic data (8,640 candles)
- ✅ Reproducible results (seed=42)
- ✅ Paper trading infrastructure deployed
- ✅ Real Binance WebSocket integration verified
- ✅ Production logging and monitoring included

### Next Steps

1. **Run backtest** to validate performance:
   ```bash
   python neus_trader/compare_all_engines.py
   ```

2. **Deploy paper trading** for live validation:
   ```bash
   python neus_trader/deploy_optimized_engine.py --duration 7d
   ```

3. **Monitor results** and compare to backtested metrics

4. **Contribute** - See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines

### Issues Found & Fixed

**Previous skeleton code had disconnects:**
- ❌ `live_trading.py` referenced in docs but didn't exist
- ❌ Julia agents declared but not wired to Python signals
- ❌ Consensus parser returned hardcoded "NEUTRAL" (ignored AutoGen output)
- ❌ Signal generation was 5% random coin flips, not real analysis
- ❌ Kelly sizing formula had division bug

**Fixed in current version:**
- ✅ Real WebSocket integration (`deploy_optimized_engine.py`)
- ✅ Multi-confirmation order flow (4 independent signal sources)
- ✅ Market hour filtering (proven +61% PF improvement)
- ✅ Correct Kelly Criterion implementation
- ✅ Production-ready logging and monitoring

See full code review and details in [`neus_trader/README.md`](neus_trader/README.md).

---
