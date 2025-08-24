"""
Banking Update Orchestrator.

This module provides the main orchestrator for banking updates,
coordinating the complete update pipeline for banking events.

Key responsibilities:
- Event routing and handler selection
- Update pipeline coordination
- Error handling and rollback
- Domain event publishing
"""

from typing import Dict, Any, Optional, List, Union
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
import logging

from src.banking.models import Bank, BankAccount
from src.banking.events.registry import BankingEventHandlerRegistry
from src.banking.events.cross_module_registry import CrossModuleEventRegistry


class BankingUpdateOrchestrator:
    """
    Orchestrates the complete banking update pipeline.
    
    This class coordinates:
    1. Event processing through the registry
    2. Transaction boundaries and rollback
    3. Dependent updates and side effects
    4. Error handling and recovery
    
    It serves as the main entry point for all banking event processing
    and ensures that the entire pipeline is executed atomically.
    """
    
    def __init__(self, registry: Optional[BankingEventHandlerRegistry] = None):
        """
        Initialize the orchestrator.
        
        Args:
            registry: Event handler registry to use. If None, creates a new one.
        """
        self.registry = registry or BankingEventHandlerRegistry()
        self.cross_module_registry = CrossModuleEventRegistry()
        self.logger = logging.getLogger(__name__)
    
    def process_banking_event(self, event_data: Dict[str, Any], session: Session, banking_entity: Union[Bank, BankAccount]) -> Dict[str, Any]:
        """
        Process a banking event through the complete pipeline.
        
        This is the main entry point for all banking event processing.
        It coordinates the entire pipeline:
        1. Event validation and routing
        2. Event processing by appropriate handler
        3. Dependent updates and side effects
        
        Note: Transaction management is handled by the calling layer.
        This method focuses purely on business logic orchestration.
        
        Args:
            event_data: Dictionary containing event parameters
            session: Database session for all operations
            banking_entity: Bank or BankAccount instance to operate on
            
        Returns:
            Dict[str, Any]: Result data from event processing
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        # Step 1: Process the main event through the registry
        result = self.registry.handle_event(event_data, session, banking_entity)
        
        # Step 2: Handle any dependent updates
        self._handle_dependent_updates(result, session, banking_entity)
        
        return result
    
    def process_bulk_events(self, events_data: list[Dict[str, Any]], session: Session, banking_entity: Union[Bank, BankAccount]) -> list[Dict[str, Any]]:
        """
        Process multiple banking events in a single transaction.
        
        This method processes multiple events atomically, ensuring that
        either all events succeed or none do. It's useful for bulk
        operations and maintaining data consistency.
        
        Note: Transaction management is handled by the calling layer.
        This method focuses purely on business logic orchestration.
        
        Args:
            events_data: List of event data dictionaries
            session: Database session for all operations
            banking_entity: Bank or BankAccount instance to operate on
            
        Returns:
            list[Dict[str, Any]]: List of results from event processing
            
        Raises:
            ValueError: If any event data is invalid
            RuntimeError: If any event processing fails
        """
        results = []
        
        # Process each event
        for event_data in events_data:
            result = self.registry.handle_event(event_data, session, banking_entity)
            results.append(result)
        
        # Handle dependent updates for all events
        self._handle_bulk_dependent_updates(results, session, banking_entity)
        
        return results
    
    def _handle_dependent_updates(self, event_result: Dict[str, Any], session: Session, banking_entity: Union[Bank, BankAccount]) -> None:
        """
        Handle dependent updates after event processing.
        
        This method coordinates any updates that need to happen
        in other parts of the system as a result of banking changes.
        
        Args:
            event_result: Result from event processing
            session: Database session for all operations
            banking_entity: Bank or BankAccount instance that was processed
        """
        try:
            # Extract event type and entity information
            event_type = event_result.get('event_type', 'unknown')
            entity_type = 'bank' if isinstance(banking_entity, Bank) else 'bank_account'
            
            self.logger.info(f"Handling dependent updates for {event_type} on {entity_type} {banking_entity.id}")
            
            # Handle different types of dependent updates based on event type
            if event_type == 'bank_created':
                self._handle_bank_created_dependencies(event_result, session, banking_entity)
            elif event_type == 'bank_account_created':
                self._handle_account_created_dependencies(event_result, session, banking_entity)
            elif event_type == 'bank_account_deleted':
                self._handle_account_deleted_dependencies(event_result, session, banking_entity)
            elif event_type == 'currency_changed':
                self._handle_currency_change_dependencies(event_result, session, banking_entity)
            elif event_type == 'account_status_changed':
                self._handle_status_change_dependencies(event_result, session, banking_entity)
            
        except Exception as e:
            self.logger.error(f"Error handling dependent updates: {str(e)}")
            raise RuntimeError(f"Failed to handle dependent updates: {str(e)}") from e
    
    def _handle_bulk_dependent_updates(self, event_results: list[Dict[str, Any]], session: Session, banking_entity: Union[Bank, BankAccount]) -> None:
        """
        Handle dependent updates for bulk event processing.
        
        Args:
            event_results: List of results from event processing
            session: Database session for all operations
            banking_entity: Bank or BankAccount instance that was processed
        """
        try:
            for event_result in event_results:
                self._handle_dependent_updates(event_result, session, banking_entity)
        except Exception as e:
            self.logger.error(f"Error handling bulk dependent updates: {str(e)}")
            raise RuntimeError(f"Failed to handle bulk dependent updates: {str(e)}") from e
    
    def _handle_bank_created_dependencies(self, event_result: Dict[str, Any], session: Session, bank: Bank) -> None:
        """
        Handle dependencies for bank creation.
        
        Args:
            event_result: Result from bank creation event
            session: Database session for all operations
            bank: Bank instance that was created
        """
        # TODO: Implement bank creation dependencies
        # - Update banking summary data
        # - Notify other systems of new bank
        self.logger.info(f"Bank {bank.id} created - handling dependencies")
    
    def _handle_account_deleted_dependencies(self, event_result: Dict[str, Any], session: Session, account: BankAccount) -> None:
        """
        Handle dependencies for account deletion.
        
        Args:
            event_result: Result from account deletion event
            session: Database session for all operations
            account: BankAccount instance that was deleted
        """
        try:
            # Create and route account deletion event to cross-module handlers
            from src.banking.events.domain.bank_account_deleted_event import BankAccountDeletedEvent
            
            event = BankAccountDeletedEvent(
                account_id=account.id,
                entity_id=account.entity_id,
                bank_id=account.bank_id,
                account_name=account.account_name,
                account_number=account.account_number,
                currency=account.currency
            )
            
            # Route to cross-module handlers
            cross_module_results = self.cross_module_registry.route_event(event, session)
            
            self.logger.info(
                f"Bank account {account.id} deleted - cross-module dependencies handled: "
                f"{cross_module_results['handlers_executed']} handlers executed"
            )
            
            # Log any warnings or errors
            if cross_module_results['warnings']:
                for warning in cross_module_results['warnings']:
                    self.logger.warning(f"Cross-module warning: {warning}")
            
            if cross_module_results['errors']:
                for error in cross_module_results['errors']:
                    self.logger.error(f"Cross-module error: {error}")
                    
        except Exception as e:
            self.logger.error(f"Failed to handle account deletion dependencies: {str(e)}")
            # Don't fail the main operation for dependency issues

    def _handle_account_created_dependencies(self, event_result: Dict[str, Any], session: Session, account: BankAccount) -> None:
        """
        Handle dependencies for account creation.
        
        Args:
            event_result: Result from account creation event
            session: Database session for all operations
            account: BankAccount instance that was created
        """
        try:
            # Create and route account creation event to cross-module handlers
            from src.banking.events.domain.bank_account_created_event import BankAccountCreatedEvent
            
            event = BankAccountCreatedEvent(
                account_id=account.id,
                entity_id=account.entity_id,
                bank_id=account.bank_id,
                account_name=account.account_name,
                account_number=account.account_number,
                currency=account.currency,
                is_active=account.is_active
            )
            
            # Route to cross-module handlers
            cross_module_results = self.cross_module_registry.route_event(event, session)
            
            self.logger.info(
                f"Bank account {account.id} created - cross-module dependencies handled: "
                f"{cross_module_results['handlers_executed']} handlers executed"
            )
            
            # Log any warnings or errors
            if cross_module_results['warnings']:
                for warning in cross_module_results['warnings']:
                    self.logger.warning(f"Cross-module warning: {warning}")
            
            if cross_module_results['errors']:
                for error in cross_module_results['errors']:
                    self.logger.error(f"Cross-module error: {error}")
                    
        except Exception as e:
            self.logger.error(f"Failed to handle account creation dependencies: {str(e)}")
            # Don't fail the main operation for dependency issues
    
    def _handle_currency_change_dependencies(self, event_result: Dict[str, Any], session: Session, account: BankAccount) -> None:
        """
        Handle dependencies for currency changes.
        
        Args:
            event_result: Result from currency change event
            session: Database session for all operations
            account: BankAccount instance whose currency changed
        """
        try:
            # Create and route currency change event to cross-module handlers
            from src.banking.events.domain.currency_changed_event import CurrencyChangedEvent
            
            event = CurrencyChangedEvent(
                account_id=account.id,
                entity_id=account.entity_id,
                bank_id=account.bank_id,
                old_currency=event_result.get('old_currency', 'Unknown'),
                new_currency=account.currency
            )
            
            # Route to cross-module handlers
            cross_module_results = self.cross_module_registry.route_event(event, session)
            
            self.logger.info(
                f"Currency changed for account {account.id} - cross-module dependencies handled: "
                f"{cross_module_results['handlers_executed']} handlers executed"
            )
            
            # Log any warnings or errors
            if cross_module_results['warnings']:
                for warning in cross_module_results['warnings']:
                    self.logger.warning(f"Cross-module warning: {warning}")
            
            if cross_module_results['errors']:
                for error in cross_module_results['errors']:
                    self.logger.error(f"Cross-module error: {error}")
                    
        except Exception as e:
            self.logger.error(f"Failed to handle currency change dependencies: {str(e)}")
            # Don't fail the main operation for dependency issues
    
    def _handle_status_change_dependencies(self, event_result: Dict[str, Any], session: Session, account: BankAccount) -> None:
        """
        Handle dependencies for status changes.
        
        Args:
            event_result: Result from status change event
            session: Database session for all operations
            account: BankAccount instance whose status changed
        """
        try:
            # Create and route status change event to cross-module handlers
            from src.banking.events.domain.account_status_changed_event import AccountStatusChangedEvent
            
            event = AccountStatusChangedEvent(
                account_id=account.id,
                entity_id=account.entity_id,
                bank_id=account.bank_id,
                old_status=event_result.get('old_status', True),
                new_status=account.is_active
            )
            
            # Route to cross-module handlers
            cross_module_results = self.cross_module_registry.route_event(event, session)
            
            self.logger.info(
                f"Status changed for account {account.id} - cross-module dependencies handled: "
                f"{cross_module_results['handlers_executed']} handlers executed"
            )
            
            # Log any warnings or errors
            if cross_module_results['warnings']:
                for warning in cross_module_results['warnings']:
                    self.logger.warning(f"Cross-module warning: {warning}")
            
            if cross_module_results['errors']:
                for error in cross_module_results['errors']:
                    self.logger.error(f"Cross-module error: {error}")
                    
        except Exception as e:
            self.logger.error(f"Failed to handle status change dependencies: {str(e)}")
            # Don't fail the main operation for dependency issues
    
    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get information about the event handler registry.
        
        Returns:
            Dict[str, Any]: Registry information including registered event types
        """
        return {
            'registered_event_types': self.registry.get_registered_event_types(),
            'total_handlers': len(self.registry.get_registered_event_types()),
            'orchestrator_class': self.__class__.__name__
        }
