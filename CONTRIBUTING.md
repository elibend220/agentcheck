# Contributing to NEUS Trader

Thank you for your interest in contributing to NEUS Trader! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Performance Considerations](#performance-considerations)
- [Trading-Specific Guidelines](#trading-specific-guidelines)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and professional in all interactions
- Focus on the code, not the person
- Welcome diverse perspectives and approaches
- Report any Code of Conduct violations to the maintainers

## Getting Started

### Prerequisites

- **Python 3.9+**
- **Git** for version control
- **pip** for package management
- **Virtual environment** (recommended: `venv` or `conda`)

### Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/agentcheck.git
cd agentcheck

# Add upstream remote for syncing
git remote add upstream https://github.com/elibend220/agentcheck.git

# Fetch the latest upstream changes
git fetch upstream
```

## Development Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r neus_trader/requirements.txt

# Development dependencies
pip install pytest black flake8 mypy
```

### 3. Create Feature Branch

```bash
git fetch upstream
git checkout -b feature/your-feature-name upstream/main
```

**Branch naming conventions:**
- `feature/` - New features (e.g., `feature/volatility-adjustment`)
- `fix/` - Bug fixes (e.g., `fix/websocket-timeout`)
- `docs/` - Documentation updates (e.g., `docs/api-guide`)
- `test/` - Test improvements (e.g., `test/backtest-coverage`)
- `perf/` - Performance improvements (e.g., `perf/event-buffer-optimization`)

## Making Changes

### File Structure

The project is organized as:

```
agentcheck/
├── neus_trader/                          # Main trading system
│   ├── python_core/                      # Core trading engines
│   │   ├── scalping_engine.py           # Original engine (baseline)
│   │   ├── scalping_engine_improved.py  # Improved filters
│   │   ├── scalping_engine_optimized.py # Optimized (prime hours)
│   │   ├── order_flow_improved.py       # Multi-confirmation analyzer
│   │   ├── market_hours.py              # Market session detector
│   │   ├── adaptive_risk.py             # Risk management
│   │   ├── backtester.py                # Backtesting framework
│   │   └── [other core modules]
│   ├── deploy_optimized_engine.py        # Production deployment
│   ├── compare_*.py                      # Comparison/validation scripts
│   ├── results/                          # Session logs and metrics
│   ├── tests/                            # Unit tests
│   └── README.md                         # System documentation
├── CONTRIBUTING.md                       # This file
├── requirements.txt                      # Project dependencies
└── [other files]
```

### What to Change

**Good candidates for contribution:**

✅ **Bug fixes** - Fix broken functionality with failing tests included  
✅ **Performance improvements** - Optimize existing code (benchmarks required)  
✅ **New signal confirmations** - Add multi-confirmation sources with backtesting  
✅ **Market hours** - Add new trading sessions with historical data  
✅ **Risk management** - Improve position sizing or drawdown protection  
✅ **Documentation** - Clarify existing docs, add examples, improve README  
✅ **Test coverage** - Add tests for existing functionality  

**Avoid:**

❌ Style-only changes without substance  
❌ Renaming variables across the codebase without testing  
❌ Adding untested features or experimental code  
❌ Changing core logic without backtesting  

## Testing

### Run Existing Tests

```bash
# Unit tests
pytest neus_trader/tests/ -v

# With coverage
pytest neus_trader/tests/ --cov=neus_trader --cov-report=html
```

### Run Backtests

```bash
# Full engine comparison (Original → Improved → Optimized)
python neus_trader/compare_all_engines.py

# Market hour filtering impact
python neus_trader/compare_engines_prime_hours.py

# Original vs Improved comparison
python neus_trader/compare_engines.py
```

### Add Tests for New Features

Create tests in `neus_trader/tests/test_*.py`:

```python
import pytest
from neus_trader.python_core.your_module import YourClass

def test_basic_functionality():
    """Test basic behavior"""
    obj = YourClass()
    assert obj.method() == expected_value

def test_edge_case():
    """Test edge case handling"""
    obj = YourClass(edge_value=True)
    assert obj.method() == expected_edge_value
```

### Backtest New Features

If your change affects signal generation or position sizing, provide backtesting results:

```python
# Create a minimal script showing before/after performance
python -c "
from neus_trader.python_core.backtester import HistoricalBacktester
from neus_trader.python_core.your_new_engine import YourNewEngine

engine = YourNewEngine()
backtester = HistoricalBacktester(engine)
metrics = backtester.run_backtest(test_data)
print(f'Profit Factor: {metrics.profit_factor}')
print(f'Win Rate: {metrics.win_rate}')
"
```

## Submitting Changes

### Before Committing

```bash
# Format code
black neus_trader/

# Lint
flake8 neus_trader/

# Type check (optional)
mypy neus_trader/python_core/

# Run tests
pytest neus_trader/tests/ -v
```

### Commit Message Format

Write clear, descriptive commit messages:

```
Brief summary (50 chars max)

Detailed explanation of what changed and why.
- Point 1
- Point 2
- Point 3

Related to: #issue_number (if applicable)
Backtesting: PF improved from 0.90 → 0.95 (+5.6%)
```

**Examples:**

```
Add RSI confirmation to order flow analyzer

Extend order_flow_improved.py to require RSI not in extremes (20-80).
Reduces false signals during overbought/oversold conditions.

Backtesting shows:
- Win rate: 30.0% → 31.5% (+1.5%)
- Profit factor: 1.11 → 1.14 (+2.7%)
- Trade reduction: 103 → 89 (-13.6%)

Related to: #3
```

### Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create PR on GitHub with:
# - Clear title (50 chars max)
# - Description of changes
# - Backtesting results (if applicable)
# - Screenshots/logs (if applicable)
# - Link to related issues
```

**PR Title Format:**
```
[CATEGORY] Brief description

Categories:
- [FEATURE] New capability
- [FIX] Bug fix
- [PERF] Performance improvement
- [TEST] Test coverage
- [DOCS] Documentation
```

**PR Description Template:**
```markdown
## Summary
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests pass
- [ ] Backtesting results: PF 0.90 → 0.95 (+5.6%)
- [ ] Manual testing (describe)

## Checklist
- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
```

## Coding Standards

### Python Style

Follow PEP 8 with Black formatter:

```bash
black neus_trader/ --line-length 100
```

### Naming Conventions

- **Classes:** `PascalCase` (e.g., `OrderFlowAnalyzer`)
- **Functions:** `snake_case` (e.g., `analyze_order_flow`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MIN_CONFIDENCE`)
- **Private:** Leading underscore (e.g., `_internal_method`)

### Type Hints

Use type hints for clarity:

```python
from typing import Dict, List, Optional, Tuple
from datetime import datetime

def on_candle(
    self,
    timestamp: datetime,
    open_price: float,
    high: float,
    low: float,
    close: float,
    volume: float,
    atr: float = 0.0
) -> Optional[ScalpingSignal]:
    """Process incoming candle with market hour filtering."""
    pass
```

### Docstrings

Keep docstrings brief and practical:

```python
def get_signal_quality(self, confirmations: int) -> str:
    """Return signal quality based on confirmation count."""
    if confirmations >= 3:
        return "HIGH"
    elif confirmations == 2:
        return "MEDIUM"
    return "LOW"
```

**Don't write:**
```python
def get_signal_quality(self, confirmations: int) -> str:
    """
    This method determines the quality level of a trading signal
    based on the number of technical confirmations it has received.
    Signals with 3 or more confirmations are considered high quality.
    Signals with exactly 2 confirmations are medium quality.
    Signals with fewer than 2 confirmations are low quality.
    
    Args:
        confirmations (int): The number of technical confirmations
        
    Returns:
        str: A string representing the signal quality level
    """
```

## Performance Considerations

### Latency Requirements

The system targets sub-millisecond latency for the critical path:

- **Candle processing:** < 5ms (5-minute intervals allow buffer)
- **Signal generation:** < 50ms
- **Trade execution:** < 500ms total
- **Event buffering:** < 1μs per enqueue operation

### Optimization Guidelines

**DO:**
- Use efficient data structures (dict, set for O(1) lookups)
- Batch operations where possible (e.g., ledger worker batches)
- Cache calculations that don't change frequently
- Use numpy for numerical operations on arrays
- Profile before optimizing (measure first)

**DON'T:**
- Create unnecessary objects in tight loops
- Use nested loops where vectorization is possible
- Make expensive function calls repeatedly (cache results)
- Block on I/O in critical path (use async/threading)

### Profiling

```bash
# Profile a backtest
python -m cProfile -s cumulative neus_trader/compare_all_engines.py | head -20

# For specific functions
import cProfile
import pstats
from io import StringIO

pr = cProfile.Profile()
pr.enable()
# ... code to profile ...
pr.disable()

s = StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(10)
print(s.getvalue())
```

## Trading-Specific Guidelines

### Backtesting Requirements

Any change affecting trading logic must include backtesting:

```python
# Minimum 30-day backtest
data = generate_test_data(days=30)  # 8,640 candles

# Compare before/after
old_engine = GoldenHourScalpingEngine()
new_engine = YourImprovedEngine()

old_metrics = HistoricalBacktester(old_engine).run_backtest(data)
new_metrics = HistoricalBacktester(new_engine).run_backtest(data)

# Report key metrics
pf_change = new_metrics.profit_factor - old_metrics.profit_factor
wr_change = (new_metrics.win_rate - old_metrics.win_rate) * 100

print(f"PF: {old_metrics.profit_factor:.2f} → {new_metrics.profit_factor:.2f} ({pf_change:+.2f})")
print(f"WR: {old_metrics.win_rate*100:.1f}% → {new_metrics.win_rate*100:.1f}% ({wr_change:+.1f}%)")
```

### Signal Quality Metrics

When adding new signal sources, report:

- **Confirmation rate:** What % of signals include this confirmation?
- **Impact on quality:** Does it filter out false signals?
- **Win rate by quality:** Separate stats for HIGH/MEDIUM/LOW signals
- **Timing:** Does it add significant latency?

### Market Hours

Market hour changes require validation:

```python
# Test on historical data spanning different sessions
# Document win rates for each market session
# Provide data showing liquidity/spread conditions

# Example:
# London (13-17 UTC): 65% win rate, avg 0.5% spread
# US Close (20-23 UTC): 60% win rate, avg 0.3% spread
# Asian (00-08 UTC): 35% win rate, avg 1.2% spread (skip this)
```

### Risk Management

Changes to risk controls must:

- [ ] Preserve drawdown limits (target: -10% max)
- [ ] Maintain position sizing (Kelly Criterion 25% fraction)
- [ ] Document any circuit breaker changes
- [ ] Backtest under adverse conditions (high volatility, losing streaks)

## Common Contribution Patterns

### Adding a New Signal Confirmation

```python
# 1. Add method to order_flow_improved.py
def _check_your_confirmation(self) -> bool:
    """Check your new signal confirmation."""
    return your_condition

# 2. Include in analyze_order_flow()
signals = [
    self._check_vwap_cross(),
    self._check_volume_surge(),
    self._check_supertrend(),
    self._check_your_confirmation(),  # Add here
]

# 3. Backtest
python compare_all_engines.py  # Should show improvement

# 4. Document in README
# "## Signal Confirmations"
# Add description of your confirmation
```

### Optimizing Market Hours

```python
# 1. Update python_core/market_hours.py
PRIME_WINDOWS = [
    TradingWindow("Tokyo", "08:00", "12:00"),  # Add new session
    TradingWindow("London", "13:00", "17:00"),
    TradingWindow("US Close", "20:00", "23:00"),
]

# 2. Backtest to prove it works
python compare_engines_prime_hours.py

# 3. Document in README with historical data
```

### Improving Risk Management

```python
# 1. Modify python_core/adaptive_risk.py
# Change position sizing, stop loss, etc.

# 2. Backtest to ensure drawdown stays within limits
python compare_all_engines.py

# 3. Add unit tests for edge cases
# pytest neus_trader/tests/test_adaptive_risk.py -v
```

## Getting Help

### Questions?

- **Documentation:** Check `neus_trader/README.md` and `DEPLOYMENT_GUIDE.md`
- **Issues:** Search for similar issues before opening a new one
- **Discussions:** Use GitHub Discussions for questions
- **Maintainers:** Reach out via issues with `[QUESTION]` tag

### Code Review

When your PR is reviewed:

- Be open to feedback
- Explain your reasoning if disagreeing
- Update your branch with suggestions
- Don't take feedback personally—it's about the code

### Helpful Resources

- **Backtesting Framework:** See `python_core/backtester.py`
- **Architecture:** See `BIFURCATION_ARCHITECTURE.md`
- **Deployment:** See `DEPLOYMENT_GUIDE.md`
- **Signal Analysis:** See `compare_all_engines.py` for examples

## Recognition

Contributors will be recognized in:

- Release notes for their PRs
- README contributors section
- Commit history with their GitHub profile

Thank you for contributing to NEUS Trader! 🚀

---

**Questions?** Open an issue or reach out via GitHub Discussions.
