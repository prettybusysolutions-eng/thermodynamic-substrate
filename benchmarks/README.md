# TCS Benchmark Suite

Empirical comparison of Thermodynamic Computing Substrate vs traditional load management.

## Quick Start

```bash
cd benchmarks
python stress_test.py --operations 1000
```

## What's Being Tested

**Scenario:** 1000 operations with varying load (burst spikes every 100 ops)

**Approaches:**
1. **Standard Load Balancer**: Traditional if/else with rate limiting and cooldowns
2. **TCS**: Thermodynamic substrate with phase-based coupling

**Metrics:**
- Throttling frequency
- Infrastructure overhead (ms per operation)
- Total execution time
- Recovery behavior after spikes

## Interpreting Results

Key questions:
- **Overhead**: Is TCS's SQLite thermal state check faster/slower than standard counters?
- **Throttling**: Does phase-based throttling handle bursts better than boolean rules?
- **Smoothness**: Does heat-based cooling create smoother degradation than hard cutoffs?

## Current Results

Run locally to see baseline. We need community data from:
- Different load patterns (sustained vs bursty)
- Different operation costs
- Multi-agent scenarios
- Production-like workloads

## Contributing Benchmarks

To add a benchmark:

1. Create new file `benchmarks/test_<scenario>.py`
2. Implement test following `stress_test.py` structure
3. Document what you're measuring
4. Open PR with results

We especially want:
- Real LangChain/AutoGen workloads
- Token cost comparisons ($/1000 ops)
- Latency under concurrent load
- Memory footprint over time

## Discussion

This is where we answer: "Is thermodynamic coupling actually better, or just different?"

Science > hype. Let's measure.
