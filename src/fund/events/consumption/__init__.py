"""
Event Consumption System.

This module provides the event consumption architecture that enables
true loose coupling between components through domain events.

Components:
- EventBus: Centralized event routing and subscription system
- EventConsumer: Base class for all event consumers
- EventHandlers: Specific handlers for different event types
- AsyncProcessor: Background processing for heavy calculations
- HandlerRegistry: Automatic registration of all event handlers
"""

from src.fund.events.consumption.base_consumer import EventConsumer
from src.fund.events.consumption.handler_registry import EventHandlerRegistry, register_all_handlers, get_handler_stats, clear_registrations

__all__ = [
    'EventConsumer', 
    'AsyncEventProcessor',
    'EventHandlerRegistry',
    'register_all_handlers',
    'get_handler_stats',
    'clear_registrations'
]
