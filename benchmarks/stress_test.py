"""
TCS vs Standard Load Management: Empirical Benchmark
Compares thermodynamic substrate against traditional approaches
"""
import time
import sqlite3
import json
import random
from dataclasses import dataclass
from typing import List, Dict
import sys
import os

# Support both installed package and running from source tree
try:
    from thermal_substrate import ThermalSubstrate
except ModuleNotFoundError:
    # Running from source tree
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from thermal_substrate import ThermalSubstrate

@dataclass
class BenchmarkResult:
    approach: str
    total_operations: int
    throttled_count: int
    failed_count: int
    total_time: float
    avg_latency: float
    peak_load: int
    recovery_time: float
    overhead_ms: float

class StandardLoadBalancer:
    """Traditional if/else load management"""
    def __init__(self):
        self.request_count = 0
        self.last_minute_requests = []
        self.threshold = 50  # requests per minute
        self.cooldown_until = 0
        
    def execute(self, operation_cost: int):
        current_time = time.time()
        
        # Measure overhead
        start = time.perf_counter()
        
        # Remove old requests
        self.last_minute_requests = [
            t for t in self.last_minute_requests 
            if current_time - t < 60
        ]
        
        # Check if in cooldown
        if current_time < self.cooldown_until:
            overhead = (time.perf_counter() - start) * 1000
            return {'throttled': True, 'overhead_ms': overhead}
        
        # Check rate limit
        if len(self.last_minute_requests) >= self.threshold:
            self.cooldown_until = current_time + 5  # 5 second cooldown
            overhead = (time.perf_counter() - start) * 1000
            return {'throttled': True, 'overhead_ms': overhead}
        
        # Execute
        self.last_minute_requests.append(current_time)
        self.request_count += 1
        
        overhead = (time.perf_counter() - start) * 1000
        return {'throttled': False, 'overhead_ms': overhead}

class TCSLoadBalancer:
    """Thermodynamic substrate load management"""
    def __init__(self):
        self.tcs = ThermalSubstrate(':memory:')
        self.tcs.register_entity('agent', 'agent', initial_temp=300)
        self.operation_count = 0
        
    def execute(self, operation_cost: int):
        start = time.perf_counter()
        
        # Execute with thermal coupling
        result = self.tcs.execute_with_coupling('operation', 'agent')
        
        overhead = (time.perf_counter() - start) * 1000
        
        self.operation_count += 1
        
        # Cool down periodically
        if self.operation_count % 10 == 0:
            self.tcs.cool_down()
        
        return {
            'throttled': result.get('throttled', False),
            'overhead_ms': overhead,
            'temperature': result.get('phase_coefficient', 0) * 500
        }

def run_stress_test(balancer, name: str, n_operations: int = 1000) -> BenchmarkResult:
    """Run stress test with varying load patterns"""
    
    print(f"\n{'='*60}")
    print(f"Running {name}")
    print(f"{'='*60}")
    
    throttled = 0
    failed = 0
    latencies = []
    overheads = []
    temperatures = []
    
    start_time = time.time()
    
    # Simulate varying load patterns
    for i in range(n_operations):
        # Burst pattern: spike every 100 operations
        if i % 100 < 20:
            operation_cost = random.randint(50, 100)  # High cost
        else:
            operation_cost = random.randint(10, 30)   # Normal cost
        
        op_start = time.perf_counter()
        result = balancer.execute(operation_cost)
        op_time = (time.perf_counter() - op_start) * 1000
        
        latencies.append(op_time)
        overheads.append(result['overhead_ms'])
        
        if result['throttled']:
            throttled += 1
        
        if 'temperature' in result:
            temperatures.append(result['temperature'])
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            avg_overhead = sum(overheads[-100:]) / 100
            print(f"  [{i+1}/{n_operations}] "
                  f"Throttled: {throttled} | "
                  f"Avg overhead: {avg_overhead:.3f}ms")
            
            if temperatures:
                avg_temp = sum(temperatures[-100:]) / len(temperatures[-100:])
                print(f"    Temperature: {avg_temp:.0f}K")
    
    total_time = time.time() - start_time
    
    return BenchmarkResult(
        approach=name,
        total_operations=n_operations,
        throttled_count=throttled,
        failed_count=failed,
        total_time=total_time,
        avg_latency=sum(latencies) / len(latencies),
        peak_load=max(latencies),
        recovery_time=0,  # TODO: measure recovery after spike
        overhead_ms=sum(overheads) / len(overheads)
    )

def print_results(results: List[BenchmarkResult]):
    """Print comparative results"""
    print(f"\n{'='*60}")
    print("BENCHMARK RESULTS")
    print(f"{'='*60}\n")
    
    for r in results:
        print(f"{r.approach}:")
        print(f"  Total operations:    {r.total_operations}")
        print(f"  Throttled:           {r.throttled_count} ({r.throttled_count/r.total_operations*100:.1f}%)")
        print(f"  Failed:              {r.failed_count}")
        print(f"  Total time:          {r.total_time:.2f}s")
        print(f"  Avg latency:         {r.avg_latency:.3f}ms")
        print(f"  Infrastructure overhead: {r.overhead_ms:.3f}ms")
        print()
    
    # Comparative analysis
    if len(results) == 2:
        standard, tcs = results
        
        print("COMPARATIVE ANALYSIS:")
        
        if standard.throttled_count > 0:
            throttle_diff = ((tcs.throttled_count - standard.throttled_count) / 
                            standard.throttled_count * 100)
            print(f"  Throttling:   {throttle_diff:+.1f}% (TCS vs Standard)")
        else:
            print(f"  Throttling:   TCS: {tcs.throttled_count}, Standard: {standard.throttled_count}")
        
        if standard.overhead_ms > 0:
            overhead_diff = ((tcs.overhead_ms - standard.overhead_ms) / 
                            standard.overhead_ms * 100)
            print(f"  Overhead:     {overhead_diff:+.1f}% (TCS vs Standard)")
        else:
            print(f"  Overhead:     TCS: {tcs.overhead_ms:.3f}ms, Standard: {standard.overhead_ms:.3f}ms")
        
        if standard.total_time > 0:
            time_diff = ((tcs.total_time - standard.total_time) / 
                        standard.total_time * 100)
            print(f"  Total time:   {time_diff:+.1f}% (TCS vs Standard)")
        else:
            print(f"  Total time:   TCS: {tcs.total_time:.2f}s, Standard: {standard.total_time:.2f}s")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='TCS Benchmark Suite')
    parser.add_argument('--operations', type=int, default=1000,
                       help='Number of operations to run')
    args = parser.parse_args()
    
    results = []
    
    # Run standard approach
    standard = StandardLoadBalancer()
    results.append(run_stress_test(standard, "Standard Load Balancer", args.operations))
    
    # Run TCS approach
    tcs = TCSLoadBalancer()
    results.append(run_stress_test(tcs, "Thermodynamic Substrate", args.operations))
    
    # Print comparison
    print_results(results)
    
    # Save to JSON
    with open('benchmark_results.json', 'w') as f:
        json.dump([vars(r) for r in results], f, indent=2)
    
    print("\n✓ Results saved to benchmark_results.json")
