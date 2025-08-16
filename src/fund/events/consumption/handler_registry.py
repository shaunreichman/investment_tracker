"""
Event Handler Registry.

This module provides automatic registration of all event handlers
with the event bus to enable real-time event consumption.
"""

import logging
from typing import List, Type

from .event_bus import event_bus
from .base_consumer import EventConsumer
from .handlers.tax_statement_event_handler import TaxStatementEventHandler
from .handlers.company_record_event_handler import CompanyRecordEventHandler

logger = logging.getLogger(__name__)


class EventHandlerRegistry:
    """
    Registry for automatically registering event handlers with the event bus.
    
    This class manages the registration of all event handlers and ensures
    they are properly subscribed to the events they can handle.
    """
    
    def __init__(self):
        """Initialize the event handler registry."""
        self.handlers: List[EventConsumer] = []
        self.registered = False
    
    def register_all_handlers(self) -> None:
        """
        Register all available event handlers with the event bus.
        
        This method creates instances of all event handlers and
        subscribes them to the appropriate event types.
        """
        if self.registered:
            logger.info("Event handlers already registered, skipping registration")
            return
        
        try:
            logger.info("Starting event handler registration...")
            
            # Create and register tax statement event handler
            tax_handler = TaxStatementEventHandler()
            self._register_handler(tax_handler)
            
            # Create and register company record event handler
            company_handler = CompanyRecordEventHandler()
            self._register_handler(company_handler)
            
            self.registered = True
            logger.info(f"Successfully registered {len(self.handlers)} event handlers")
            
        except Exception as e:
            logger.error(f"Error registering event handlers: {e}")
            raise
    
    def _register_handler(self, handler: EventConsumer) -> None:
        """
        Register a single event handler with the event bus.
        
        Args:
            handler: The event handler to register
        """
        try:
            # Subscribe the handler to all event types it can handle
            for event_type in handler.event_types:
                event_bus.subscribe_consumer(event_type, handler)
                logger.debug(f"Registered {handler.name} for {event_type.__name__}")
            
            # Store the handler reference
            self.handlers.append(handler)
            
        except Exception as e:
            logger.error(f"Error registering handler {handler.name}: {e}")
            raise
    
    def get_handler_stats(self) -> dict:
        """
        Get statistics about registered handlers.
        
        Returns:
            Dictionary with handler statistics
        """
        stats = {
            'total_handlers': len(self.handlers),
            'registered': self.registered,
            'handlers': []
        }
        
        for handler in self.handlers:
            handler_stats = {
                'name': handler.name,
                'event_types': [et.__name__ for et in handler.event_types],
                'processed_count': handler.processed_count,
                'enabled': handler.enabled
            }
            stats['handlers'].append(handler_stats)
        
        return stats
    
    def clear_registrations(self) -> None:
        """Clear all event handler registrations."""
        try:
            # Clear all subscriptions from the event bus
            event_bus.clear_subscriptions()
            
            # Clear our handler list
            self.handlers.clear()
            self.registered = False
            
            logger.info("Cleared all event handler registrations")
            
        except Exception as e:
            logger.error(f"Error clearing registrations: {e}")
            raise


# Global instance of the event handler registry
handler_registry = EventHandlerRegistry()


def register_all_handlers() -> None:
    """
    Convenience function to register all event handlers.
    
    This function should be called during system startup to ensure
    all event handlers are registered and ready to consume events.
    """
    handler_registry.register_all_handlers()


def get_handler_stats() -> dict:
    """
    Convenience function to get handler statistics.
    
    Returns:
        Dictionary with handler statistics
    """
    return handler_registry.get_handler_stats()


def clear_registrations() -> None:
    """
    Convenience function to clear all registrations.
    
    This is useful for testing or system shutdown.
    """
    handler_registry.clear_registrations()
