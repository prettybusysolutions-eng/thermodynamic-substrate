"""
Zero-friction TCS adapters: Drop-in decorators for existing agent frameworks
No code changes required - just add @thermal_coupled
"""
import functools
import time
from typing import Callable, Optional, Any

from ..core import ThermalSubstrate

# Global substrate instance (singleton pattern)
_global_substrate: Optional[ThermalSubstrate] = None

def get_substrate() -> ThermalSubstrate:
    """Get or create global substrate instance"""
    global _global_substrate
    if _global_substrate is None:
        _global_substrate = ThermalSubstrate('thermal.db')
    return _global_substrate

def thermal_coupled(
    entity_id: Optional[str] = None,
    entity_type: str = 'agent',
    initial_temp: float = 300,
    energy_cost: int = 30
):
    """
    Decorator to add thermodynamic coupling to any function.
    
    Usage:
        @thermal_coupled(entity_id="my_agent")
        def call_llm(prompt):
            return openai.ChatCompletion.create(...)
    
    The function will:
    - Check thermal state before executing
    - Throttle if in plasma phase (>1000K)
    - Use read-only mode if in solid phase (<200K)
    - Generate heat on execution
    - Auto-cool periodically
    """
    def decorator(func: Callable) -> Callable:
        # Use function name as entity_id if not provided
        _entity_id = entity_id or f"{func.__module__}.{func.__name__}"
        
        # Register entity
        substrate = get_substrate()
        substrate.register_entity(_entity_id, entity_type, initial_temp)
        
        call_count = [0]  # Mutable counter for closure
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            substrate = get_substrate()
            
            # Check thermal state
            result = substrate.execute_with_coupling('operation', _entity_id)
            
            call_count[0] += 1
            
            # Apply thermal policy
            if result['throttled']:
                # Plasma state - wait and retry
                time.sleep(0.5)
                print(f"⚠️  {_entity_id} throttled (too hot) - cooling down")
                substrate.cool_down()
                # Retry
                result = substrate.execute_with_coupling('operation', _entity_id)
                if result['throttled']:
                    raise RuntimeError(f"{_entity_id} overheating - cannot execute")
            
            elif result['locked']:
                # Solid state - read-only or cached response
                print(f"❄️  {_entity_id} locked (too cold) - limited execution")
                # Could return cached result here if available
            
            # Execute original function
            try:
                return_value = func(*args, **kwargs)
                
                # Cool down periodically
                if call_count[0] % 10 == 0:
                    substrate.cool_down()
                
                return return_value
            
            except Exception as e:
                # On error, cool down to prevent cascading failures
                substrate.cool_down()
                raise
        
        # Attach substrate access to wrapper
        wrapper._substrate = substrate
        wrapper._entity_id = _entity_id
        
        return wrapper
    
    return decorator

# Framework-specific convenience decorators

def langchain_coupled(chain_id: Optional[str] = None):
    """Decorator specifically for LangChain chains"""
    return thermal_coupled(
        entity_id=chain_id,
        entity_type='langchain_chain',
        energy_cost=50  # Chains tend to be heavier
    )

def autogen_coupled(agent_name: Optional[str] = None):
    """Decorator for AutoGen agents"""
    return thermal_coupled(
        entity_id=agent_name,
        entity_type='autogen_agent',
        energy_cost=40
    )

def crewai_coupled(task_id: Optional[str] = None):
    """Decorator for CrewAI tasks"""
    return thermal_coupled(
        entity_id=task_id,
        entity_type='crewai_task',
        energy_cost=35
    )

# Context manager for manual control

class ThermalContext:
    """
    Context manager for thermal control
    
    Usage:
        with ThermalContext('my_operation') as thermal:
            # Your code here
            if thermal.is_throttled():
                # Handle throttling
                pass
    """
    def __init__(self, entity_id: str, entity_type: str = 'operation'):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.substrate = get_substrate()
        
    def __enter__(self):
        self.substrate.register_entity(self.entity_id, self.entity_type)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.substrate.cool_down()
    
    def check_state(self):
        """Check current thermal state"""
        return self.substrate.execute_with_coupling('check', self.entity_id)
    
    def is_throttled(self) -> bool:
        """Check if currently throttled"""
        state = self.check_state()
        return state.get('throttled', False)
    
    def is_locked(self) -> bool:
        """Check if currently locked"""
        state = self.check_state()
        return state.get('locked', False)

# Monitoring utilities

def get_thermal_status(entity_id: str) -> dict:
    """Get current thermal status of an entity"""
    substrate = get_substrate()
    return substrate.execute_with_coupling('status', entity_id)

def get_system_status() -> str:
    """Get system-wide thermal status prompt"""
    substrate = get_substrate()
    return substrate.get_system_state_prompt()

def reset_thermal_state():
    """Reset all thermal state (for testing)"""
    global _global_substrate
    _global_substrate = None
