# TCS Adapters: Zero-Friction Integration

Drop-in decorators for adding thermodynamic coupling to existing code.

## Philosophy

**Zero adoption friction.** No rewriting your stack. Just add a decorator.

## Usage

### Basic Decorator

```python
from thermal_substrate.adapters import thermal_coupled

@thermal_coupled(entity_id="gpt4_agent")
def call_llm(prompt: str):
    # Your existing code - unchanged
    return openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

# Now automatically coupled to thermal substrate
result = call_llm("Hello")
```

### LangChain

```python
from thermal_substrate.adapters import langchain_coupled

@langchain_coupled(chain_id="research_chain")
def run_research(query: str):
    # Existing LangChain code
    return chain.run(query)
```

### AutoGen

```python
from thermal_substrate.adapters import autogen_coupled

@autogen_coupled(agent_name="coder_agent")
def autogen_task(task):
    # Existing AutoGen agent
    return agent.run(task)
```

### Manual Control (Context Manager)

```python
from thermal_substrate.adapters import ThermalContext

with ThermalContext('my_operation') as thermal:
    if thermal.is_throttled():
        print("Too hot - deferring work")
        return
    
    result = expensive_operation()
```

## What It Does

The decorator:
1. Registers your function as a thermal entity
2. Checks thermal state before execution
3. Throttles if >1000K (plasma phase)
4. Locks writes if <200K (solid phase)
5. Generates heat on execution
6. Auto-cools periodically

## Monitoring

```python
from thermal_substrate.adapters import get_thermal_status, get_system_status

# Check specific entity
status = get_thermal_status("gpt4_agent")
print(status)

# Get system prompt
prompt = get_system_status()
print(prompt)  # Shows temperature, phase, entropy
```

## Examples

See `examples.py` for complete working examples with:
- OpenAI API calls
- LangChain chains
- Multi-agent coordination
- Heat transfer patterns

## Testing Your Integration

```bash
python examples.py
```

Should run without errors and show thermal state changes.

## Contributing

Found a pattern that doesn't work? Open an issue.
Built an adapter for another framework? Submit a PR.

Goal: Make thermal coupling available everywhere, not just new projects.
