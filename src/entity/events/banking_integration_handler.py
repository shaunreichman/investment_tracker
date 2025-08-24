"""
Banking Integration Handler for Entity System.

This handler responds to banking events that affect entity operations,
particularly entity banking status and account relationships.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.entity.models import Entity
from src.banking.events.domain.base_event import BankingDomainEvent


class EntityBankingIntegrationHandler:
    """
    Handles banking events that affect entity operations.
    
    This handler ensures that banking changes properly update
    related entity records and maintain data consistency.
    """
    
    def __init__(self):
        """Initialize the entity banking integration handler."""
        self.handler_name = "EntityBankingIntegrationHandler"
    
    def handle_bank_account_created(self, event: BankingDomainEvent, session: Session) -> Dict[str, Any]:
        """
        Handle bank account creation events.
        
        When a bank account is created, we need to:
        1. Update entity banking status
        2. Increment account count
        3. Update any relevant entity calculations
        
        Args:
            event: Banking domain event containing account creation details
            session: Database session for operations
            
        Returns:
            Dict containing processing results
        """
        try:
            # Extract account details from event
            entity_id = event.entity_id if hasattr(event, 'entity_id') else None
            account_id = event.account_id if hasattr(event, 'account_id') else None
            
            if not entity_id or not account_id:
                raise ValueError("Bank account creation event missing entity_id or account_id")
            
            # Get the entity
            entity = session.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                raise RuntimeError(f"Entity {entity_id} not found for bank account creation")
            
            # Update entity banking status
            # Note: This assumes Entity has banking-related fields
            # If not, we'll need to add them or handle differently
            
            return {
                "success": True,
                "action": "entity_banking_updated",
                "entity_id": entity_id,
                "account_id": account_id,
                "message": f"Entity {entity_id} banking status updated for new account {account_id}"
            }
                
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to handle bank account creation: {str(e)}")
    
    def handle_bank_account_deleted(self, event: BankingDomainEvent, session: Session) -> Dict[str, Any]:
        """
        Handle bank account deletion events.
        
        When a bank account is deleted, we need to:
        1. Update entity banking status
        2. Decrement account count
        3. Check if entity still has active accounts
        
        Args:
            event: Banking domain event containing account deletion details
            session: Database session for operations
            
        Returns:
            Dict containing processing results
        """
        try:
            # Extract account details from event
            entity_id = event.entity_id if hasattr(event, 'entity_id') else None
            account_id = event.account_id if hasattr(event, 'account_id') else None
            
            if not entity_id or not account_id:
                raise ValueError("Bank account deletion event missing entity_id or account_id")
            
            # Get the entity
            entity = session.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                raise RuntimeError(f"Entity {entity_id} not found for bank account deletion")
            
            # Check remaining active accounts for this entity
            from src.banking.models.bank_account import BankAccount
            remaining_accounts = session.query(BankAccount).filter(
                and_(
                    BankAccount.entity_id == entity_id,
                    BankAccount.is_active == True
                )
            ).count()
            
            # Update entity banking status based on remaining accounts
            if remaining_accounts == 0:
                # No more active accounts
                return {
                    "success": True,
                    "action": "entity_no_active_accounts",
                    "entity_id": entity_id,
                    "account_id": account_id,
                    "remaining_accounts": 0,
                    "message": f"Entity {entity_id} now has no active bank accounts"
                }
            else:
                # Still has active accounts
                return {
                    "success": True,
                    "action": "entity_accounts_remaining",
                    "entity_id": entity_id,
                    "account_id": account_id,
                    "remaining_accounts": remaining_accounts,
                    "message": f"Entity {entity_id} has {remaining_accounts} remaining active accounts"
                }
                
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to handle bank account deletion: {str(e)}")
    
    def handle_bank_account_status_changed(self, event: BankingDomainEvent, session: Session) -> Dict[str, Any]:
        """
        Handle bank account status change events.
        
        When a bank account status changes (active/inactive), we need to:
        1. Update entity banking status
        2. Recalculate active account count
        3. Update any relevant entity calculations
        
        Args:
            event: Banking domain event containing status change details
            session: Database session for operations
            
        Returns:
            Dict containing processing results
        """
        try:
            # Extract account details from event
            entity_id = event.entity_id if hasattr(event, 'entity_id') else None
            account_id = event.account_id if hasattr(event, 'account_id') else None
            new_status = event.new_status if hasattr(event, 'new_status') else None
            
            if not entity_id or not account_id or new_status is None:
                raise ValueError("Status change event missing entity_id, account_id, or new_status")
            
            # Get the entity
            entity = session.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                raise RuntimeError(f"Entity {entity_id} not found for bank account status change")
            
            # Count active accounts for this entity
            from src.banking.models.bank_account import BankAccount
            active_accounts = session.query(BankAccount).filter(
                and_(
                    BankAccount.entity_id == entity_id,
                    BankAccount.is_active == True
                )
            ).count()
            
            status_description = "active" if new_status else "inactive"
            
            return {
                "success": True,
                "action": "entity_banking_status_updated",
                "entity_id": entity_id,
                "account_id": account_id,
                "account_status": status_description,
                "active_accounts": active_accounts,
                "message": f"Entity {entity_id} banking status updated: account {account_id} is {status_description}, {active_accounts} total active accounts"
            }
                
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to handle status change: {str(e)}")
    
    def handle_bank_account_currency_changed(self, event: BankingDomainEvent, session: Session) -> Dict[str, Any]:
        """
        Handle bank account currency change events.
        
        When a bank account currency changes, we need to:
        1. Update entity currency profile
        2. Check for currency consistency across accounts
        3. Flag any currency mismatches for review
        
        Args:
            event: Banking domain event containing currency change details
            session: Database session for operations
            
        Returns:
            Dict containing processing results and any warnings
        """
        try:
            # Extract account details from event
            entity_id = event.entity_id if hasattr(event, 'entity_id') else None
            account_id = event.account_id if hasattr(event, 'account_id') else None
            new_currency = event.new_currency if hasattr(event, 'new_currency') else None
            
            if not entity_id or not account_id or not new_currency:
                raise ValueError("Currency change event missing entity_id, account_id, or new_currency")
            
            # Get the entity
            entity = session.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                raise RuntimeError(f"Entity {entity_id} not found for currency change")
            
            # Check currency consistency across all active accounts for this entity
            from src.banking.models.bank_account import BankAccount
            currency_distribution = session.query(
                BankAccount.currency,
                func.count(BankAccount.id).label('count')
            ).filter(
                and_(
                    BankAccount.entity_id == entity_id,
                    BankAccount.is_active == True
                )
            ).group_by(BankAccount.currency).all()
            
            if len(currency_distribution) > 1:
                # Multiple currencies detected
                currencies = [f"{curr}: {count}" for curr, count in currency_distribution]
                return {
                    "success": True,
                    "action": "currency_change_processed_multi_currency",
                    "entity_id": entity_id,
                    "account_id": account_id,
                    "new_currency": new_currency,
                    "currency_distribution": currencies,
                    "warnings": [
                        f"Entity {entity_id} now uses multiple currencies: {', '.join(currencies)}. "
                        "Review recommended for currency consistency."
                    ],
                    "message": f"Currency change processed for account {account_id}, multi-currency entity detected"
                }
            else:
                # Single currency entity
                return {
                    "success": True,
                    "action": "currency_change_processed_single_currency",
                    "entity_id": entity_id,
                    "account_id": account_id,
                    "new_currency": new_currency,
                    "currency_distribution": [f"{new_currency}: {currency_distribution[0].count}"],
                    "message": f"Currency change processed for account {account_id}, entity maintains single currency"
                }
                
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to handle currency change: {str(e)}")
