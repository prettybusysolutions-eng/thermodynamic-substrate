"""
Example usage of TCS adapters with popular frameworks
"""
from .decorators import thermal_coupled, langchain_coupled, ThermalContext, get_substrate

# ============================================================================
# Example 1: Drop-in decorator for any function
# ============================================================================

@thermal_coupled(entity_id="gpt4_agent")
def call_openai(prompt: str) -> str:
    """Existing OpenAI call - no changes to code"""
    # import openai
    # return openai.ChatCompletion.create(...)
    return f"Response to: {prompt}"

# ============================================================================
# Example 2: LangChain integration
# ============================================================================

@langchain_coupled(chain_id="research_chain")
def run_langchain_research(query: str):
    """Existing LangChain chain - just add decorator"""
    # from langchain import LLMChain
    # return chain.run(query)
    return f"Research result for: {query}"

# ============================================================================
# Example 3: Context manager for manual control
# ============================================================================

def complex_workflow():
    """Use context manager for fine-grained control"""
    with ThermalContext('workflow_executor') as thermal:
        
        # Check before expensive operation
        if thermal.is_throttled():
            print("System hot - deferring work")
            return None
        
        # Do work
        result = perform_expensive_task()
        return result

def perform_expensive_task():
    return "Task completed"

# ============================================================================
# Example 4: Multi-agent coordination via heat transfer
# ============================================================================

from .decorators import get_substrate

@thermal_coupled(entity_id="agent_1")
def agent_1_task():
    return "Agent 1 result"

@thermal_coupled(entity_id="agent_2")  
def agent_2_task():
    return "Agent 2 result"

def coordinate_agents():
    """Agents automatically balance load via heat transfer"""
    
    # Run tasks
    result_1 = agent_1_task()
    result_2 = agent_2_task()
    
    # Heat automatically transfers between agents
    substrate = get_substrate()
    substrate.heat_transfer('agent_1', 'agent_2')
    
    return result_1, result_2

if __name__ == '__main__':
    print("Running TCS adapter examples...\n")
    
    # Example 1
    print("1. Simple decorated function:")
    for i in range(3):
        result = call_openai(f"Query {i}")
        print(f"   {result}")
    
    # Example 2
    print("\n2. LangChain decorated:")
    result = run_langchain_research("AI safety")
    print(f"   {result}")
    
    # Example 3
    print("\n3. Context manager:")
    result = complex_workflow()
    print(f"   {result}")
    
    # Example 4
    print("\n4. Multi-agent coordination:")
    r1, r2 = coordinate_agents()
    print(f"   Agent 1: {r1}")
    print(f"   Agent 2: {r2}")
    
    # Show system status
    print("\n5. System thermal status:")
    from .decorators import get_system_status
    print(get_system_status())
