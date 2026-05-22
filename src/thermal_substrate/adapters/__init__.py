"""
TCS Adapters - Zero-friction integration decorators
"""

from .decorators import (
    thermal_coupled,
    langchain_coupled,
    autogen_coupled,
    crewai_coupled,
    ThermalContext,
    get_thermal_status,
    get_system_status,
    reset_thermal_state
)

__all__ = [
    'thermal_coupled',
    'langchain_coupled',
    'autogen_coupled',
    'crewai_coupled',
    'ThermalContext',
    'get_thermal_status',
    'get_system_status',
    'reset_thermal_state',
]
