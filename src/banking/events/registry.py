"""
Banking Event Handler Registry.

This module provides a centralized registry for all banking event handlers,
enabling automatic registration and discovery of handlers for different event types.

Key responsibilities:
- Handler registration and discovery
- Handler routing by event type
- Handler validation and error handling
- Handler lifecycle management
"""

from typing import Dict, Type, Optional, List, Union, Any
from datetime import datetime
import logging

from src.banking.events.base_handler import BaseBankingEventHandler
from src.banking.models import Bank, BankAccount
from src.banking.events.handlers.bank_created_handler import BankCreatedHandler
from src.banking.events.handlers.bank_updated_handler import BankUpdatedHandler
from src.banking.events.handlers.bank_deleted_handler import BankDeletedHandler
from src.banking.events.handlers.bank_account_created_handler import BankAccountCreatedHandler
from src.banking.events.handlers.bank_account_updated_handler import BankAccountUpdatedHandler
from src.banking.events.handlers.bank_account_deleted_handler import BankAccountDeletedHandler
from src.banking.events.handlers.currency_changed_handler import CurrencyChangedHandler
from src.banking.events.handlers.account_status_changed_handler import AccountStatusChangedHandler


class BankingEventHandlerRegistry:
    """
    Centralized registry for routing banking events to appropriate handlers.
    
    This class implements the Registry pattern to:
    1. Register handlers for each event type
    2. Route events to the correct handler
    3. Support dynamic handler registration
    4. Enable easy testing and mocking
    
    The registry maintains a mapping of event type to handler classes
    and creates handler instances as needed.
    """
    
    def __init__(self):
        """Initialize the registry with default handlers."""
        self._handlers: Dict[str, Type[BaseBankingEventHandler]] = {}
        self._register_default_handlers()
    
    def register_handler(self, event_type: str, handler_class: Type[BaseBankingEventHandler]) -> None:
        """
        Register a handler class for a specific event type.
        
        Args:
            event_type: The event type to register the handler for
            handler_class: The handler class to register
            
        Raises:
            ValueError: If handler_class doesn't inherit from BaseBankingEventHandler
        """
        if not issubclass(handler_class, BaseBankingEventHandler):
            raise ValueError(
                f"Handler class {handler_class.__name__} must inherit from BaseBankingEventHandler"
            )
        
        self._handlers[event_type] = handler_class
    
    def get_handler(self, event_type: str, session, banking_entity: Union[Bank, BankAccount]) -> BaseBankingEventHandler:
        """
        Get a handler instance for the specified event type.
        
        Args:
            event_type: The event type to get a handler for
            session: Database session for the handler
            banking_entity: Bank or BankAccount instance for the handler
            
        Returns:
            BaseBankingEventHandler: Handler instance
            
        Raises:
            ValueError: If no handler is registered for the event type
        """
        handler_class = self._handlers.get(event_type)
        if not handler_class:
            raise ValueError(f"No handler registered for event type: {event_type}")
        
        return handler_class(session, banking_entity)
    
    def handle_event(self, event_data: Dict, session, banking_entity: Union[Bank, BankAccount]) -> Dict[str, Any]:
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
            banking_entity: Bank or BankAccount instance to operate on
            
        Returns:
            Dict[str, Any]: Result data from event processing
            
        Raises:
            ValueError: If event data is invalid or no handler found
            RuntimeError: If event processing fails
        """
        event_type = event_data.get('event_type')
        if not event_type:
            raise ValueError("Event data must contain 'event_type' field")
        
        handler = self.get_handler(event_type, session, banking_entity)
        return handler.handle(event_data)
    
    def get_registered_event_types(self) -> List[str]:
        """
        Get a list of all registered event types.
        
        Returns:
            List[str]: List of registered event type names
        """
        return list(self._handlers.keys())
    
    def is_event_type_registered(self, event_type: str) -> bool:
        """
        Check if an event type is registered.
        
        Args:
            event_type: Event type to check
            
        Returns:
            bool: True if event type is registered, False otherwise
        """
        return event_type in self._handlers
    
    def _register_default_handlers(self) -> None:
        """Register the default set of banking event handlers."""
        self.register_handler('bank_created', BankCreatedHandler)
        self.register_handler('bank_updated', BankUpdatedHandler)
        self.register_handler('bank_deleted', BankDeletedHandler)
        self.register_handler('bank_account_created', BankAccountCreatedHandler)
        self.register_handler('bank_account_updated', BankAccountUpdatedHandler)
        self.register_handler('bank_account_deleted', BankAccountDeletedHandler)
        self.register_handler('currency_changed', CurrencyChangedHandler)
        self.register_handler('account_status_changed', AccountStatusChangedHandler)
    
    def clear_handlers(self) -> None:
        """Clear all registered handlers (useful for testing)."""
        self._handlers.clear()
    
    def __repr__(self) -> str:
        """String representation of the registry."""
        registered_types = ', '.join(self.get_registered_event_types())
        return f"BankingEventHandlerRegistry(registered_types=[{registered_types}])"
