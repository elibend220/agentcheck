---
name: Performance Improvement
about: Suggest performance optimization
title: "[PERF] Brief description of optimization"
labels: performance
assignees: ''
---

## Current Performance

Describe the current bottleneck or performance issue.

```
Current latency: X ms
Current throughput: Y events/sec
Profiling hotspot: function_name()
```

## Proposed Optimization

Describe the proposed optimization approach.

## Expected Improvement

Quantify the expected improvement:

```
Target latency: X ms (from Y ms)
Improvement: Z% reduction
CPU usage reduction: N%
Memory usage reduction: N%
```

## Implementation Approach

Describe how the optimization would be implemented.

```python
# Pseudocode of the optimization
def optimized_function():
    pass
```

## Trade-offs

Any trade-offs or side effects?

- Trade-off 1
- Trade-off 2

## Profiling Results

If available, include profiling data:

```
Function                  Time (ms)  Calls
_______________________________________
function_name()           50.2       10000
another_function()        25.1       5000
```

## Testing Plan

How will the optimization be validated?

- [ ] Unit tests pass
- [ ] Latency benchmarks show improvement
- [ ] Memory usage stays within limits
- [ ] Backtesting results unchanged or improved

## Related Issues

Link to related issues or PRs.

## Additional Context

Any other context or implementation notes?
