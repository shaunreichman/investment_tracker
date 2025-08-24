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
    
    def get_handler(self, event_type: CompanyDomainEventType, session, company: InvestmentCompany, **kwargs) -> BaseCompanyEventHandler:
        """
        Get a handler instance for the specified event type.
        
        This method intelligently creates handler instances by:
        1. Checking the handler's constructor signature
        2. Passing only the required arguments
        3. Supporting handlers with different constructor patterns
        
        Args:
            event_type: The event type to get a handler for
            session: Database session for the handler
            company: Company instance for the handler
            **kwargs: Additional context data (e.g., contact, portfolio) for handlers that need it
            
        Returns:
            BaseCompanyEventHandler: Handler instance
            
        Raises:
            ValueError: If no handler is registered for the event type
        """
        handler_class = self._handlers.get(event_type)
        if not handler_class:
            raise ValueError(f"No handler registered for event type: {event_type}")
        
        # Smart handler creation based on constructor signature
        return self._create_handler_instance(handler_class, session, company, **kwargs)
    
    def _create_handler_instance(self, handler_class, session, company: InvestmentCompany, **kwargs) -> BaseCompanyEventHandler:
        """
        Create a handler instance with the appropriate constructor arguments.
        
        This method inspects the handler's constructor and passes only the required arguments,
        supporting handlers with different constructor signatures.
        
        Args:
            handler_class: The handler class to instantiate
            session: Database session for the handler
            company: Company instance for the handler
            **kwargs: Additional context data
            
        Returns:
            BaseCompanyEventHandler: Properly instantiated handler
        """
        import inspect
        
        # Get the constructor signature
        sig = inspect.signature(handler_class.__init__)
        params = list(sig.parameters.keys())
        
        # Remove 'self' from parameters
        if 'self' in params:
            params.remove('self')
        
        # Build arguments dict based on what the handler needs
        args = {}
        
        # Always pass session and company if the handler expects them
        if 'session' in params:
            args['session'] = session
        if 'company' in params:
            args['company'] = company
        
        # Pass additional context if the handler expects it
        for param in params:
            if param in kwargs and param not in ['session', 'company']:
                args[param] = kwargs[param]
        
        # Create and return the handler instance
        return handler_class(**args)
    
    def get_operation_handler(self, operation_type: CompanyOperationType, session, company: InvestmentCompany, **kwargs) -> BaseCompanyEventHandler:
        """
        Get a handler instance for the specified operation type.
        
        Args:
            operation_type: The operation type to get a handler for
            session: Database session for the handler
            company: Company instance for the handler
            **kwargs: Additional context data for handlers that need it
            
        Returns:
            BaseCompanyEventHandler: Handler instance
            
        Raises:
            ValueError: If no handler is registered for the operation type
        """
        handler_class = self._operation_handlers.get(operation_type)
        if not handler_class:
            raise ValueError(f"No handler registered for operation type: {operation_type}")
        
        # Use the same smart handler creation logic
        return self._create_handler_instance(handler_class, session, company, **kwargs)
    
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
        
        # Extract additional context data for handlers that need it
        context_kwargs = {}
        
        # Extract contact_id if present and create contact object
        if 'contact_id' in event_data:
            from src.investment_company.models import Contact
            contact = session.query(Contact).filter(Contact.id == event_data['contact_id']).first()
            if contact:
                context_kwargs['contact'] = contact
        
        # Extract portfolio_id if present and create portfolio object
        if 'portfolio_id' in event_data:
            # Note: Portfolio model would need to be imported and implemented
            # For now, we'll skip this until the model is available
            pass
        
        handler = self.get_handler(event_type, session, company, **context_kwargs)
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
            from .handlers.contact_updated_handler import ContactUpdatedHandler
            from .handlers.company_updated_handler import CompanyUpdatedHandler
            from .handlers.company_deleted_handler import CompanyDeletedHandler
            from .handlers.portfolio_updated_handler import PortfolioUpdatedHandler
            
            # Register event handlers
            self.register_handler(CompanyDomainEventType.COMPANY_CREATED, CompanyCreatedHandler)
            self.register_handler(CompanyDomainEventType.CONTACT_ADDED, ContactAddedHandler)
            self.register_handler(CompanyDomainEventType.CONTACT_UPDATED, ContactUpdatedHandler)
            self.register_handler(CompanyDomainEventType.COMPANY_UPDATED, CompanyUpdatedHandler)
            self.register_handler(CompanyDomainEventType.COMPANY_DELETED, CompanyDeletedHandler)
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
