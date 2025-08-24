"""
Cross-Module Event Registry for Banking System.

This registry routes banking events to handlers in other modules,
enabling cross-module integration and data consistency.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import logging

from src.banking.events.domain.base_event import BankingDomainEvent
from src.banking.events.domain.bank_account_deleted_event import BankAccountDeletedEvent
from src.banking.events.domain.bank_account_created_event import BankAccountCreatedEvent
from src.banking.events.domain.bank_account_updated_event import BankAccountUpdatedEvent
from src.banking.events.domain.currency_changed_event import CurrencyChangedEvent
from src.banking.events.domain.account_status_changed_event import AccountStatusChangedEvent


class CrossModuleEventRegistry:
    """
    Registry for routing banking events to handlers in other modules.
    
    This class coordinates the processing of banking events across
    multiple modules to ensure data consistency and proper integration.
    """
    
    def __init__(self):
        """Initialize the cross-module event registry."""
        self.logger = logging.getLogger(__name__)
        self._fund_handlers = {}
        self._entity_handlers = {}
        self._investment_company_handlers = {}
        
        # Initialize handlers from other modules
        self._initialize_handlers()
    
    def _initialize_handlers(self):
        """Initialize handlers from other modules."""
        try:
            # Initialize fund system handlers
            from src.fund.events.handlers.banking_integration_handler import BankingIntegrationHandler
            self._fund_handlers = {
                'bank_account_deleted': BankingIntegrationHandler().handle_bank_account_deleted,
                'currency_changed': BankingIntegrationHandler().handle_bank_account_currency_changed,
                'account_status_changed': BankingIntegrationHandler().handle_bank_account_status_changed,
            }
            self.logger.info("Fund system banking handlers initialized successfully")
        except ImportError as e:
            self.logger.warning(f"Could not initialize fund system handlers: {e}")
        
        try:
            # Initialize entity system handlers
            from src.entity.events.banking_integration_handler import EntityBankingIntegrationHandler
            self._entity_handlers = {
                'bank_account_created': EntityBankingIntegrationHandler().handle_bank_account_created,
                'bank_account_deleted': EntityBankingIntegrationHandler().handle_bank_account_deleted,
                'currency_changed': EntityBankingIntegrationHandler().handle_bank_account_currency_changed,
                'account_status_changed': EntityBankingIntegrationHandler().handle_bank_account_status_changed,
            }
            self.logger.info("Entity system banking handlers initialized successfully")
        except ImportError as e:
            self.logger.warning(f"Could not initialize entity system handlers: {e}")
        
        try:
            # Initialize investment company handlers (if they exist)
            # This is a placeholder for future implementation
            self._investment_company_handlers = {}
            self.logger.info("Investment company banking handlers initialized (placeholder)")
        except ImportError as e:
            self.logger.warning(f"Could not initialize investment company handlers: {e}")
    
    def route_event(self, event: BankingDomainEvent, session: Session) -> Dict[str, Any]:
        """
        Route a banking event to appropriate handlers in other modules.
        
        Args:
            event: Banking domain event to route
            session: Database session for operations
            
        Returns:
            Dict containing results from all handlers
        """
        try:
            results = {
                'event_type': type(event).__name__,
                'handlers_executed': [],
                'results': {},
                'warnings': [],
                'errors': []
            }
            
            # Determine event type and route accordingly
            if isinstance(event, BankAccountDeletedEvent):
                self._route_bank_account_deleted(event, session, results)
            elif isinstance(event, BankAccountCreatedEvent):
                self._route_bank_account_created(event, session, results)
            elif isinstance(event, BankAccountUpdatedEvent):
                self._route_bank_account_updated(event, session, results)
            elif isinstance(event, CurrencyChangedEvent):
                self._route_currency_changed(event, session, results)
            elif isinstance(event, AccountStatusChangedEvent):
                self._route_account_status_changed(event, session, results)
            else:
                self.logger.warning(f"Unknown event type: {type(event).__name__}")
                return results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error routing event {type(event).__name__}: {str(e)}")
            return {
                'event_type': type(event).__name__,
                'handlers_executed': [],
                'results': {},
                'warnings': [],
                'errors': [f"Event routing failed: {str(e)}"]
            }
    
    def _route_bank_account_deleted(self, event: BankAccountDeletedEvent, session: Session, results: Dict[str, Any]):
        """Route bank account deletion events."""
        # Route to fund system (check for active cash flows)
        if 'bank_account_deleted' in self._fund_handlers:
            try:
                fund_result = self._fund_handlers['bank_account_deleted'](event, session)
                results['results']['fund_system'] = fund_result
                results['handlers_executed'].append('fund_system')
                
                if 'warnings' in fund_result:
                    results['warnings'].extend(fund_result['warnings'])
                    
            except Exception as e:
                error_msg = f"Fund system handler failed: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
        
        # Route to entity system (update banking status)
        if 'bank_account_deleted' in self._entity_handlers:
            try:
                entity_result = self._entity_handlers['bank_account_deleted'](event, session)
                results['results']['entity_system'] = entity_result
                results['handlers_executed'].append('entity_system')
                
                if 'warnings' in entity_result:
                    results['warnings'].extend(entity_result['warnings'])
                    
            except Exception as e:
                error_msg = f"Entity system handler failed: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
    
    def _route_bank_account_created(self, event: BankAccountCreatedEvent, session: Session, results: Dict[str, Any]):
        """Route bank account creation events."""
        # Route to entity system (update banking status)
        if 'bank_account_created' in self._entity_handlers:
            try:
                entity_result = self._entity_handlers['bank_account_created'](event, session)
                results['results']['entity_system'] = entity_result
                results['handlers_executed'].append('entity_system')
                
                if 'warnings' in entity_result:
                    results['warnings'].extend(entity_result['warnings'])
                    
            except Exception as e:
                error_msg = f"Entity system handler failed: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
    
    def _route_bank_account_updated(self, event: BankAccountUpdatedEvent, session: Session, results: Dict[str, Any]):
        """Route bank account update events."""
        # Route to entity system (update banking status)
        if 'bank_account_updated' in self._entity_handlers:
            try:
                entity_result = self._entity_handlers['bank_account_updated'](event, session)
                results['results']['entity_system'] = entity_result
                results['handlers_executed'].append('entity_system')
                
                if 'warnings' in entity_result:
                    results['warnings'].extend(entity_result['warnings'])
                    
            except Exception as e:
                error_msg = f"Entity system handler failed: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
    
    def _route_currency_changed(self, event: CurrencyChangedEvent, session: Session, results: Dict[str, Any]):
        """Route currency change events."""
        # Route to fund system (check for currency mismatches)
        if 'currency_changed' in self._fund_handlers:
            try:
                fund_result = self._fund_handlers['currency_changed'](event, session)
                results['results']['fund_system'] = fund_result
                results['handlers_executed'].append('fund_system')
                
                if 'warnings' in fund_result:
                    results['warnings'].extend(fund_result['warnings'])
                    
            except Exception as e:
                error_msg = f"Fund system handler failed: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
        
        # Route to entity system (update currency profile)
        if 'currency_changed' in self._entity_handlers:
            try:
                entity_result = self._entity_handlers['currency_changed'](event, session)
                results['results']['entity_system'] = entity_result
                results['handlers_executed'].append('entity_system')
                
                if 'warnings' in entity_result:
                    results['warnings'].extend(entity_result['warnings'])
                    
            except Exception as e:
                error_msg = f"Entity system handler failed: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
    
    def _route_account_status_changed(self, event: AccountStatusChangedEvent, session: Session, results: Dict[str, Any]):
        """Route account status change events."""
        # Route to fund system (check for active cash flows)
        if 'account_status_changed' in self._fund_handlers:
            try:
                fund_result = self._fund_handlers['account_status_changed'](event, session)
                results['results']['fund_system'] = fund_result
                results['handlers_executed'].append('fund_system')
                
                if 'warnings' in fund_result:
                    results['warnings'].extend(fund_result['warnings'])
                    
            except Exception as e:
                error_msg = f"Fund system handler failed: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
        
        # Route to entity system (update banking status)
        if 'account_status_changed' in self._entity_handlers:
            try:
                entity_result = self._entity_handlers['account_status_changed'](event, session)
                results['results']['entity_system'] = entity_result
                results['handlers_executed'].append('entity_system')
                
                if 'warnings' in entity_result:
                    results['warnings'].extend(entity_result['warnings'])
                    
            except Exception as e:
                error_msg = f"Entity system handler failed: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
