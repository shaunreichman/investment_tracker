"""
Fund Event Handler Registry.

This module provides a centralized registry for all fund event handlers,
enabling automatic registration and discovery of handlers for different event types.

Key responsibilities:
- Handler registration and discovery
- Handler routing by event type
- Handler validation and error handling
- Handler lifecycle management
"""

from typing import Dict, Type, Optional, List
from datetime import datetime
import logging

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType
from src.fund.models import FundEvent
from src.fund.events.handlers.capital_call_handler import CapitalCallHandler
from src.fund.events.handlers.return_of_capital_handler import ReturnOfCapitalHandler
from src.fund.events.handlers.distribution_handler import DistributionHandler
from src.fund.events.handlers.nav_update_handler import NAVUpdateHandler
from src.fund.events.handlers.unit_purchase_handler import UnitPurchaseHandler
from src.fund.events.handlers.unit_sale_handler import UnitSaleHandler
from src.fund.events.handlers.tax_payment_handler import TaxPaymentHandler


class FundEventHandlerRegistry:
    """
    Centralized registry for routing fund events to appropriate handlers.
    
    This class implements the Registry pattern to:
    1. Register handlers for each event type
    2. Route events to the correct handler
    3. Support dynamic handler registration
    4. Enable easy testing and mocking
    
    The registry maintains a mapping of EventType to handler classes
    and creates handler instances as needed.
    """
    
    def __init__(self):
        """Initialize the registry with default handlers."""
        self._handlers: Dict[EventType, Type[BaseFundEventHandler]] = {}
        self._register_default_handlers()
    
    def register_handler(self, event_type: EventType, handler_class: Type[BaseFundEventHandler]) -> None:
        """
        Register a handler class for a specific event type.
        
        Args:
            event_type: The event type to register the handler for
            handler_class: The handler class to register
            
        Raises:
            ValueError: If handler_class doesn't inherit from BaseFundEventHandler
        """
        if not issubclass(handler_class, BaseFundEventHandler):
            raise ValueError(
                f"Handler class {handler_class.__name__} must inherit from BaseFundEventHandler"
            )
        
        self._handlers[event_type] = handler_class
    
    def get_handler(self, event_type: EventType, session, fund) -> BaseFundEventHandler:
        """
        Get a handler instance for the specified event type.
        
        Args:
            event_type: The event type to get a handler for
            session: Database session for the handler
            fund: Fund instance for the handler
            
        Returns:
            BaseFundEventHandler: Handler instance
            
        Raises:
            ValueError: If no handler is registered for the event type
        """
        handler_class = self._handlers.get(event_type)
        if not handler_class:
            raise ValueError(f"No handler registered for event type: {event_type}")
        
        return handler_class(session, fund)
    
    def handle_event(self, event_data: Dict, session, fund) -> FundEvent:
        """
        Handle an event by routing it to the appropriate handler.
        
        This is the main entry point for event processing. It:
        1. Extracts the event type from the event data
        2. Gets the appropriate handler
        3. Delegates processing to the handler
        4. Returns the result
        
        Args:
            event_data: Dictionary containing event parameters including 'event_type'
            session: Database session for all operations
            fund: Fund instance to operate on
            
        Returns:
            FundEvent: The created or updated event
            
        Raises:
            ValueError: If event_type is missing or invalid
            RuntimeError: If event processing fails
        """
        # Extract event type from event data
        event_type_raw = event_data.get('event_type')
        if not event_type_raw:
            raise ValueError("event_type is required in event_data")
        
        # Handle both string and enum object inputs
        if isinstance(event_type_raw, EventType):
            event_type = event_type_raw
        else:
            try:
                event_type = EventType.from_string(event_type_raw)
            except ValueError as e:
                raise ValueError(f"Invalid event_type '{event_type_raw}': {e}")
        
        # Get and use the appropriate handler
        handler = self.get_handler(event_type, session, fund)
        return handler.handle(event_data)
    
    def is_handler_registered(self, event_type: EventType) -> bool:
        """
        Check if a handler is registered for the specified event type.
        
        Args:
            event_type: The event type to check
            
        Returns:
            bool: True if a handler is registered, False otherwise
        """
        return event_type in self._handlers
    
    def get_registered_event_types(self) -> list[EventType]:
        """
        Get a list of all registered event types.
        
        Returns:
            list[EventType]: List of registered event types
        """
        return list(self._handlers.keys())
    
    def unregister_handler(self, event_type: EventType) -> None:
        """
        Unregister a handler for the specified event type.
        
        Args:
            event_type: The event type to unregister
            
        Note:
            This is primarily useful for testing. In production,
            handlers should remain registered once set up.
        """
        if event_type in self._handlers:
            del self._handlers[event_type]
    
    def clear_handlers(self) -> None:
        """
        Clear all registered handlers.
        
        Note:
            This is primarily useful for testing. In production,
            handlers should remain registered once set up.
        """
        self._handlers.clear()
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """
        Register the default handlers for all supported event types.
        
        This method registers all implemented handlers for the supported
        event types. It's called during initialization and after clearing
        handlers to ensure all event types have handlers registered.
        """
        # Import handlers here to avoid circular imports
        # from .handlers.capital_call_handler import CapitalCallHandler
        # from .handlers.return_of_capital_handler import ReturnOfCapitalHandler
        # from .handlers.distribution_handler import DistributionHandler
        # from .handlers.nav_update_handler import NAVUpdateHandler
        # from .handlers.unit_purchase_handler import UnitPurchaseHandler
        # from .handlers.unit_sale_handler import UnitSaleHandler
        
        # Register all handlers
        self.register_handler(EventType.CAPITAL_CALL, CapitalCallHandler)
        self.register_handler(EventType.RETURN_OF_CAPITAL, ReturnOfCapitalHandler)
        self.register_handler(EventType.DISTRIBUTION, DistributionHandler)
        self.register_handler(EventType.NAV_UPDATE, NAVUpdateHandler)
        self.register_handler(EventType.UNIT_PURCHASE, UnitPurchaseHandler)
        self.register_handler(EventType.UNIT_SALE, UnitSaleHandler)
        self.register_handler(EventType.TAX_PAYMENT, TaxPaymentHandler)
