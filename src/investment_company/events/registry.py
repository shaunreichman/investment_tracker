"""
Company Event Handler Registry.

This module provides a centralized registry for all company event handlers,
enabling automatic registration and discovery of handlers for different event types.

Key responsibilities:
- Handler registration and discovery
- Handler routing by event type
- Handler validation and error handling
- Handler lifecycle management
"""

from typing import Dict, Type, Optional, List, Any
from datetime import datetime
import logging

from src.investment_company.events.base_handler import BaseCompanyEventHandler
from src.investment_company.enums import CompanyDomainEventType, CompanyOperationType
from src.investment_company.models import InvestmentCompany


class CompanyEventHandlerRegistry:
    """
    Centralized registry for routing company events to appropriate handlers.
    
    This class implements the Registry pattern to:
    1. Register handlers for each event type
    2. Route events to the correct handler
    3. Support dynamic handler registration
    4. Enable easy testing and mocking
    
    The registry maintains a mapping of CompanyDomainEventType to handler classes
    and creates handler instances as needed.
    """
    
    def __init__(self):
        """Initialize the registry with default handlers."""
        self.logger = logging.getLogger(__name__)
        self._handlers: Dict[CompanyDomainEventType, Type[BaseCompanyEventHandler]] = {}
        self._operation_handlers: Dict[CompanyOperationType, Type[BaseCompanyEventHandler]] = {}
        self._register_default_handlers()
    
    def register_handler(self, event_type: CompanyDomainEventType, handler_class: Type[BaseCompanyEventHandler]) -> None:
        """
        Register a handler class for a specific event type.
        
        Args:
            event_type: The event type to register the handler for
            handler_class: The handler class to register
            
        Raises:
            ValueError: If handler_class doesn't inherit from BaseCompanyEventHandler
        """
        if not issubclass(handler_class, BaseCompanyEventHandler):
            raise ValueError(
                f"Handler class {handler_class.__name__} must inherit from BaseCompanyEventHandler"
            )
        
        self._handlers[event_type] = handler_class
        logging.info(f"Registered handler {handler_class.__name__} for event type {event_type}")
    
    def register_operation_handler(self, operation_type: CompanyOperationType, handler_class: Type[BaseCompanyEventHandler]) -> None:
        """
        Register a handler class for a specific operation type.
        
        Args:
            operation_type: The operation type to register the handler for
            handler_class: The handler class to register
            
        Raises:
            ValueError: If handler_class doesn't inherit from BaseCompanyEventHandler
        """
        if not issubclass(handler_class, BaseCompanyEventHandler):
            raise ValueError(
                f"Handler class {handler_class.__name__} must inherit from BaseCompanyEventHandler"
            )
        
        self._operation_handlers[operation_type] = handler_class
        logging.info(f"Registered handler {handler_class.__name__} for operation type {operation_type}")
    
    def get_handler(self, event_type: CompanyDomainEventType, session, company: InvestmentCompany) -> BaseCompanyEventHandler:
        """
        Get a handler instance for the specified event type.
        
        Args:
            event_type: The event type to get a handler for
            session: Database session for the handler
            company: Company instance for the handler
            
        Returns:
            BaseCompanyEventHandler: Handler instance
            
        Raises:
            ValueError: If no handler is registered for the event type
        """
        handler_class = self._handlers.get(event_type)
        if not handler_class:
            raise ValueError(f"No handler registered for event type: {event_type}")
        
        return handler_class(session, company)
    
    def get_operation_handler(self, operation_type: CompanyOperationType, session, company: InvestmentCompany) -> BaseCompanyEventHandler:
        """
        Get a handler instance for the specified operation type.
        
        Args:
            operation_type: The operation type to get a handler for
            session: Database session for the handler
            company: Company instance for the handler
            
        Returns:
            BaseCompanyEventHandler: Handler instance
            
        Raises:
            ValueError: If no handler is registered for the operation type
        """
        handler_class = self._operation_handlers.get(operation_type)
        if not handler_class:
            raise ValueError(f"No handler registered for operation type: {operation_type}")
        
        return handler_class(session, company)
    
    def handle_event(self, event_data: Dict, session, company: InvestmentCompany) -> Any:
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
            company: Company instance for the handler
            
        Returns:
            Any: Result from the event handler
            
        Raises:
            ValueError: If event data is invalid or no handler is found
            RuntimeError: If event processing fails
        """
        if 'event_type' not in event_data:
            raise ValueError("Event data must contain 'event_type' field")
        
        try:
            event_type = CompanyDomainEventType(event_data['event_type'])
        except ValueError:
            raise ValueError(f"Invalid event type: {event_data['event_type']}")
        
        handler = self.get_handler(event_type, session, company)
        return handler.handle(event_data)
    
    def handle_operation(self, operation_data: Dict, session, company: InvestmentCompany) -> Any:
        """
        Handle an operation by routing it to the appropriate handler.
        
        This is the main entry point for operation processing. It:
        1. Extracts the operation type from the operation data
        2. Gets the appropriate handler
        3. Delegates processing to the handler
        4. Returns the result
        
        Args:
            operation_data: Dictionary containing operation parameters including 'operation_type'
            session: Database session for all operations
            company: Company instance for the handler
            
        Returns:
            Any: Result from the operation handler
            
        Raises:
            ValueError: If operation data is invalid or no handler is found
            RuntimeError: If operation processing fails
        """
        if 'operation_type' not in operation_data:
            raise ValueError("Operation data must contain 'operation_type' field")
        
        try:
            operation_type = CompanyOperationType(operation_data['operation_type'])
        except ValueError:
            raise ValueError(f"Invalid operation type: {operation_data['operation_type']}")
        
        handler = self.get_operation_handler(operation_type, session, company)
        return handler.handle(operation_data)
    
    def _register_default_handlers(self) -> None:
        """
        Register default handlers for all event types.
        
        This method registers the specific handlers for each event type
        to enable automatic event routing.
        """
        try:
            from .handlers.company_created_handler import CompanyCreatedHandler
            from .handlers.contact_added_handler import ContactAddedHandler
            from .handlers.portfolio_updated_handler import PortfolioUpdatedHandler
            
            # Register event handlers
            self.register_handler(CompanyDomainEventType.COMPANY_CREATED, CompanyCreatedHandler)
            self.register_handler(CompanyDomainEventType.CONTACT_ADDED, ContactAddedHandler)
            self.register_handler(CompanyDomainEventType.PORTFOLIO_UPDATED, PortfolioUpdatedHandler)
            
            self.logger.info("Successfully registered all default event handlers")
            
        except ImportError as error:
            self.logger.warning(f"Failed to register some handlers: {error}")
        except Exception as error:
            self.logger.error(f"Error registering handlers: {error}")
    
    def get_registered_event_types(self) -> List[CompanyDomainEventType]:
        """
        Get list of all registered event types.
        
        Returns:
            List[CompanyDomainEventType]: List of registered event types
        """
        return list(self._handlers.keys())
    
    def get_registered_operation_types(self) -> List[CompanyOperationType]:
        """
        Get list of all registered operation types.
        
        Returns:
            List[CompanyOperationType]: List of registered operation types
        """
        return list(self._operation_handlers.keys())
    
    def is_event_type_registered(self, event_type: CompanyDomainEventType) -> bool:
        """
        Check if an event type has a registered handler.
        
        Args:
            event_type: Event type to check
            
        Returns:
            bool: True if handler is registered, False otherwise
        """
        return event_type in self._handlers
    
    def is_operation_type_registered(self, operation_type: CompanyOperationType) -> bool:
        """
        Check if an operation type has a registered handler.
        
        Args:
            operation_type: Operation type to check
            
        Returns:
            bool: True if handler is registered, False otherwise
        """
        return operation_type in self._operation_handlers
