# Thermodynamic Computing Substrate (TCS)

A non-von Neumann runtime abstraction where execution behavior emerges from simulated thermodynamic laws rather than boolean logic.

## Overview

TCS introduces computational physics to AI runtime systems. Every entity (file, process, operation) has temperature, entropy, and phase state that mathematically couple to execution parameters.

## Key Features

- **Mathematical Coupling**: Phase coefficients directly modify execution (not if/else)
- **Heat Transfer**: Inter-entity thermal conductivity for autonomous workload distribution
- **Self-Regulation**: System maintains equilibrium without external control
- **Thermal Reflection**: AI adapts behavior based on environment it creates
- **Phase Transitions**: Execution characteristics change with thermal state

## Quick Start

```python
from thermal_substrate import ThermalSubstrate

# Initialize
tcs = ThermalSubstrate('thermal.db')

# Register entity
tcs.register_entity('my_process', 'operation', initial_temp=300)

# Execute with thermal coupling
result = tcs.execute_with_coupling('compute', 'my_process')

# Heat transfers automatically between interacting entities
tcs.heat_transfer('process_a', 'process_b')

# Get thermal state for AI reflection
state = tcs.get_system_state_prompt()
```

## Installation

```bash
pip install thermodynamic-substrate
```

Or from source:
```bash
git clone https://github.com/prettybusysolutions-eng/thermodynamic-substrate
cd thermodynamic-substrate
pip install -e .
```

## Use Cases

### Autonomous Cost Control
Hot operations (>1000K) automatically throttle, preventing runaway compute costs.

### Load Balancing
Heat transfer naturally distributes workload across entities.

### Agent Coordination
Multi-agent systems self-regulate through shared thermal environment.

### Resource Management
Frozen entities (<100K) automatically prune, freeing resources.

## Documentation

- [Integration Guide](docs/INTEGRATION.md)
- [Academic Abstract](docs/ACADEMIC_ABSTRACT.md)

## Architecture

```
┌─────────────────────────────────────┐
│         AI Agent / Runtime          │
└──────────────┬──────────────────────┘
               │ Operations
               ▼
┌─────────────────────────────────────┐
│   Thermodynamic Substrate (DB)      │
│  ┌─────────┐      ┌─────────┐      │
│  │Entity A │──────│Entity B │      │
│  │  800K   │ Heat │  300K   │      │
│  └─────────┘Transfer└────────┘      │
└──────────────┬──────────────────────┘
               │ Phase Changes
               ▼
┌─────────────────────────────────────┐
│    Emergent System Behavior         │
│  (Throttling / Pruning / Balance)   │
└─────────────────────────────────────┘
```

## Performance

This is currently best framed as an experimental runtime and research prototype.

Stress test highlights:
- Initial: 397K average
- Peak: 968K (stayed below 1000K throttle)
- Final: 548K (self-regulated)
- Zero manual intervention required

Current benchmark tradeoffs for small operations:
- Overhead: +950.8%
- Total time: +532.5%

That overhead is expected at small scales where thermal bookkeeping dominates. TCS is not claiming production performance superiority yet; it is exploring whether physics-inspired coupling can unlock better load management under more realistic agent workloads.

## License

MIT License - see LICENSE file

## Citation

```bibtex
@software{thermodynamic_substrate_2026,
  title={Thermodynamic Computing Substrate: A Non-Von Neumann Runtime for AI Systems},
  author={[Authors]},
  year={2026},
  url={https://github.com/prettybusysolutions-eng/thermodynamic-substrate}
}
```

## Contributing

Contributions welcome! Please:
- Open an issue for bugs or feature requests
- Submit PRs for improvements
- Add tests for new features
- Follow existing code style

## Status

✅ Working implementation  
✅ Tested and validated  
✅ Experimental / research-stage  
✅ Open source  

---

**A new kind of computer. One that runs on computational friction.**
