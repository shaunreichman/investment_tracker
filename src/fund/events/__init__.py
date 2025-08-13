"""
Fund Events Module.

This module provides the event-driven architecture for fund updates.
It separates concerns by moving complex update logic from models into dedicated handlers.

Core Components:
- BaseFundEventHandler: Abstract base class for all event handlers
- FundEventHandlerRegistry: Centralized routing system for events
- FundUpdateOrchestrator: Coordinates complete update pipeline
- Specific handlers for each event type
- Domain event system for loose coupling
"""

from .base_handler import BaseFundEventHandler
from .registry import FundEventHandlerRegistry
from .orchestrator import FundUpdateOrchestrator

__all__ = [
    'BaseFundEventHandler',
    'FundEventHandlerRegistry', 
    'FundUpdateOrchestrator',
]
