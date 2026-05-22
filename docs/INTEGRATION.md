# Production Integration Guide

## Overview

Integrating TCS into production AI systems for autonomous cost control and self-regulation.

## Architecture Patterns

### Pattern 1: AI Agent Wrapper

Wrap existing AI agent with thermal substrate:

```python
from thermal_substrate import ThermalSubstrate

class ThermalAIAgent:
    def __init__(self, agent, db_path='thermal.db'):
        self.agent = agent
        self.thermal = ThermalSubstrate(db_path)
        self.thermal.register_entity('agent', 'ai_process')
    
    def execute(self, task):
        # Get thermal state
        state = self.thermal.get_system_state_prompt()
        
        # Inject into agent context
        context = f"{state}\n\nTask: {task}"
        
        # Execute with coupling
        result = self.thermal.execute_with_coupling('inference', 'agent')
        
        if result['throttled']:
            # Plasma state - use cheaper operations
            response = self.agent.execute_lite(context)
        elif result['locked']:
            # Solid state - read-only operations
            response = self.agent.read_only(context)
        else:
            # Normal execution
            response = self.agent.execute(context)
        
        return response
```

### Pattern 2: Multi-Agent Coordination

Agents share thermal environment:

```python
thermal = ThermalSubstrate('shared_thermal.db')

# Register multiple agents
agents = ['agent_1', 'agent_2', 'agent_3']
for agent_id in agents:
    thermal.register_entity(agent_id, 'agent')

# Agents interact
thermal.execute_with_coupling('task_a', 'agent_1')
thermal.execute_with_coupling('task_b', 'agent_2')

# Heat transfers between interacting agents
thermal.heat_transfer('agent_1', 'agent_2')

# System self-regulates
thermal.cool_down()
```

### Pattern 3: Cost Control Gateway

API gateway with thermal regulation:

```python
class ThermalAPIGateway:
    def __init__(self):
        self.thermal = ThermalSubstrate()
        self.thermal.register_entity('api_endpoint', 'gateway')
    
    def handle_request(self, request):
        # Check thermal state
        result = self.thermal.execute_with_coupling(
            'api_call', 
            'api_endpoint'
        )
        
        if result['throttled']:
            # Return cached response or 429
            return self.throttled_response()
        
        # Execute normally
        response = self.process_request(request)
        
        # High-cost operations heat the system
        if request.is_expensive():
            # Heat transfer to endpoint
            pass
        
        return response
```

## Deployment Configurations

### Development
```python
thermal = ThermalSubstrate('dev_thermal.db')
thermal.register_entity('dev_agent', 'agent', initial_temp=300)
```

### Production
```python
# Persistent database
thermal = ThermalSubstrate('/var/lib/tcs/thermal.db')

# Lower initial temp for conservative behavior
thermal.register_entity('prod_agent', 'agent', initial_temp=250)

# Background cooling process
import threading
def cooling_loop():
    while True:
        thermal.cool_down()
        time.sleep(10)

threading.Thread(target=cooling_loop, daemon=True).start()
```

### Multi-Instance
```python
# Shared database across instances
thermal = ThermalSubstrate('redis://thermal-state')  # Custom backend

# Each instance registers
import socket
instance_id = f"agent_{socket.gethostname()}"
thermal.register_entity(instance_id, 'distributed_agent')
```

## Monitoring

### Metrics to Track

```python
def get_thermal_metrics(thermal):
    cursor = thermal.db.execute('''
        SELECT 
            AVG(temperature) as avg_temp,
            MAX(temperature) as max_temp,
            AVG(entropy) as avg_entropy,
            COUNT(*) as entity_count
        FROM thermal_entities
    ''')
    
    return cursor.fetchone()

# Prometheus export
from prometheus_client import Gauge

temp_gauge = Gauge('tcs_temperature', 'System temperature')
entropy_gauge = Gauge('tcs_entropy', 'System entropy')

def update_metrics():
    avg_temp, max_temp, avg_entropy, count = get_thermal_metrics(thermal)
    temp_gauge.set(avg_temp)
    entropy_gauge.set(avg_entropy)
```

### Alerting

```python
def check_thermal_health(thermal):
    avg_temp, max_temp, _, _ = get_thermal_metrics(thermal)
    
    if max_temp > 1000:
        alert("System in plasma state - throttling active")
    elif avg_temp > 700:
        warn("System temperature elevated - monitor load")
    elif avg_temp < 150:
        info("System cool - consider warming up")
```

## Cost Control Examples

### Token Budget Management

```python
class TokenBudgetController:
    def __init__(self, max_tokens_per_minute=10000):
        self.thermal = ThermalSubstrate()
        self.thermal.register_entity('token_budget', 'budget')
        self.max_tokens = max_tokens_per_minute
    
    def check_budget(self, requested_tokens):
        result = self.thermal.execute_with_coupling(
            'token_request',
            'token_budget'
        )
        
        # Hot system = high usage, reduce allocation
        if result['phase_coefficient'] > 1.5:
            allowed = int(requested_tokens * 0.5)  # 50% reduction
        elif result['phase_coefficient'] > 1.0:
            allowed = int(requested_tokens * 0.75)  # 25% reduction
        else:
            allowed = requested_tokens
        
        # Heat proportional to tokens used
        heat = allowed / 100
        current_temp = result['phase_coefficient'] * 500
        new_temp = current_temp + heat
        
        return min(allowed, self.max_tokens)
```

### Compute Resource Throttling

```python
class ComputeThrottle:
    def __init__(self):
        self.thermal = ThermalSubstrate()
        self.thermal.register_entity('compute', 'resource')
    
    def allocate_compute(self, task_complexity):
        result = self.thermal.execute_with_coupling('compute', 'compute')
        
        if result['throttled']:
            # Plasma - minimum resources
            return {'cpu': 1, 'memory': '512MB', 'timeout': 30}
        elif result['phase'] == 'gas':
            # Gas - reduced resources
            return {'cpu': 2, 'memory': '1GB', 'timeout': 60}
        else:
            # Normal allocation
            return {'cpu': 4, 'memory': '2GB', 'timeout': 120}
```

## Best Practices

### 1. Register All Entities
```python
# Register every component that generates load
thermal.register_entity('database', 'resource')
thermal.register_entity('cache', 'resource')
thermal.register_entity('api', 'endpoint')
thermal.register_entity('agent', 'ai')
```

### 2. Enable Heat Transfer
```python
# Connect related entities
def on_database_access(agent_id):
    thermal.heat_transfer(agent_id, 'database')

def on_api_call(agent_id):
    thermal.heat_transfer(agent_id, 'api')
```

### 3. Inject Thermal State
```python
# Always include thermal context in AI prompts
state = thermal.get_system_state_prompt()
prompt = f"{state}\n\n{user_prompt}"
```

### 4. Monitor Phase Transitions
```python
# Log phase changes for analysis
def on_phase_change(entity_id, old_phase, new_phase):
    logger.info(f"{entity_id}: {old_phase} → {new_phase}")
    metrics.increment(f"phase_transition.{new_phase}")
```

### 5. Background Cooling
```python
# Always run cooling process
def cooling_daemon():
    while True:
        thermal.cool_down()
        time.sleep(10)
```

## Troubleshooting

### System Too Hot
- Reduce operation frequency
- Increase cooling rate
- Distribute load across entities
- Check for runaway processes

### System Too Cold
- Increase initial temperatures
- Reduce cooling rate
- Generate warming operations
- Check for frozen entities

### Oscillations
- Adjust conductivity (lower = more stable)
- Increase thermal mass (slower changes)
- Tune decay rates

## Migration Path

### Existing System → TCS

1. **Wrap existing components**
   ```python
   thermal_wrapped = ThermalWrapper(existing_agent)
   ```

2. **Add monitoring**
   ```python
   log_thermal_metrics()
   ```

3. **Enable throttling**
   ```python
   if result['throttled']:
       use_lite_mode()
   ```

4. **Inject context**
   ```python
   prompt += thermal.get_system_state_prompt()
   ```

5. **Full deployment**
   ```python
   migrate_to_thermal_substrate()
   ```

---

**Production ready. Deploy with confidence.**
