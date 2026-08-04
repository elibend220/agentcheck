---
name: Backtesting Request
about: Request backtesting of a trading change
title: "[BACKTEST] Brief description of change"
labels: backtest
assignees: ''
---

## Change Description

Describe the trading change to be backtested.

## Change Type

- [ ] Signal confirmation (new filter/source)
- [ ] Market hours (new trading session)
- [ ] Risk management (position sizing, stops)
- [ ] Entry logic (order flow change)
- [ ] Position management (exit rules)

## Code Changes

Describe or link to the code changes:

```python
# Example code change
def new_confirmation():
    return condition
```

## Baseline Metrics (Current)

Current performance to compare against:

```
Engine: Original/Improved/Optimized
Profit Factor: 1.18
Win Rate: 34.2%
Total Trades: 76
P&L: $2.01
Max Drawdown: -0.03%
Sharpe Ratio: 1.42
```

## Expected Outcome

What improvement do you expect?

```
Expected Profit Factor: 1.25+ (improvement: +5.9%)
Expected Win Rate: 35%+ (improvement: +0.8%)
Expected Trade Reduction: None expected / -10% (filtering)
Expected Drawdown: Similar or better
```

## Test Parameters

- Backtesting period: 30 days (default) / Custom
- Asset: ETHUSDT / Other
- Data: Synthetic (seed=42) / Historical
- Timeframe: 5-minute candles

## Acceptance Criteria

- [ ] Profit Factor improves or maintains baseline
- [ ] Win Rate improves or maintains baseline
- [ ] Drawdown stays within limits (-10% max)
- [ ] No new edge cases or errors introduced
- [ ] Documentation updated if improvement confirmed

## Additional Notes

Any other context or special considerations?

## Related PR

Link to PR with code changes (if available).
