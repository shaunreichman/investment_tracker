"""
Banking Validation Service.

This service extracts business rule validation logic from the banking models
to provide clean separation of concerns and improved testability.

Extracted functionality:
- Country code validation (2-letter ISO)
- Currency code validation (3-letter ISO)
- SWIFT/BIC validation
- Uniqueness constraint validation
- Business rule enforcement
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.banking.repositories.bank_repository import BankRepository
from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.entity.repositories.entity_repository import EntityRepository


class BankingValidationService:
    """
    Service for handling banking business rule validation.
    
    This service provides clean separation of concerns for:
    - Country and currency code validation
    - SWIFT/BIC validation
    - Uniqueness constraint validation
    - Business rule enforcement
    """
    
    def __init__(self, bank_repository: Optional[BankRepository] = None, bank_account_repository: Optional[BankAccountRepository] = None, entity_repository: Optional[EntityRepository] = None):
        """
        Initialize the BankingValidationService.
        
        Args:
            bank_repository: Bank repository to use. If None, creates a new one.
            bank_account_repository: Bank account repository to use. If None, creates a new one.
            entity_repository: Entity repository to use. If None, creates a new one.
        """
        self.bank_repository = bank_repository or BankRepository()
        self.bank_account_repository = bank_account_repository or BankAccountRepository()
        self.entity_repository = entity_repository or EntityRepository()
    
    # ============================================================================
    # COMPREHENSIVE VALIDATION METHODS
    # ============================================================================
    
    def validate_bank_data(self, data: Dict[str, Any], session: Session, exclude_id: Optional[int] = None) -> None:
        """
        Validate all bank data comprehensively.
        
        Args:
            data: Bank data dictionary
            session: Database session
            exclude_id: Bank ID to exclude from uniqueness check (for updates)
            
        Raises:
            ValueError: If any validation fails
        """
        # Validate required fields
        if 'name' in data:
            self.validate_bank_name_or_raise(data['name'])
        
        if 'country' in data:
            self.validate_country_code_or_raise(data['country'])
        
        if 'swift_bic' in data:
            self.validate_swift_bic_or_raise(data.get('swift_bic'))
        
        # Validate uniqueness if name and country are provided
        if 'name' in data and 'country' in data:
            self.validate_bank_uniqueness_or_raise(data['name'], data['country'], session, exclude_id)
    
    def validate_bank_account_data(self, data: Dict[str, Any], session: Session, exclude_id: Optional[int] = None) -> None:
        """
        Validate all bank account data comprehensively.
        
        Args:
            data: Bank account data dictionary
            session: Database session
            exclude_id: Account ID to exclude from uniqueness check (for updates)
            
        Raises:
            ValueError: If any validation fails
        """
        # Validate required fields
        if 'entity_id' in data:
            self.validate_entity_exists_or_raise(data['entity_id'], session)
        
        if 'bank_id' in data:
            self.validate_bank_exists_or_raise(data['bank_id'], session)
        
        if 'account_name' in data:
            self.validate_account_name_or_raise(data['account_name'])
        
        if 'account_number' in data:
            self.validate_account_number_or_raise(data['account_number'])
        
        if 'currency' in data:
            self.validate_currency_code_or_raise(data['currency'])
        
        # Validate uniqueness if all required fields are provided
        if all(key in data for key in ['entity_id', 'bank_id', 'account_number']):
            self.validate_bank_account_uniqueness_or_raise(
                data['entity_id'], 
                data['bank_id'], 
                data['account_number'], 
                session, 
                exclude_id
            )


    def validate_bank_deletion(self, bank_id: int, session: Session) -> None:
        """
        Validate bank deletion.
        
        Args:
            bank_id: Bank ID
            session: Database session
        """
        errors = {}
        # Cannot delete bank with dependent bank accounts
        bank_accounts = self.bank_account_repository.get_bank_accounts(session, bank_id=bank_id)
        if bank_accounts:
            errors['bank_accounts'] = ["Cannot delete bank with dependent bank accounts"]
        return errors

    
    def validate_bank_account_deletion(self, bank_account_id: int, session: Session) -> None:
        """
        Validate bank account deletion.
        
        Args:
            bank_account_id: Bank account ID
            session: Database session
        """
        errors = {}
        # Cannot delete bank account with dependent fund event cash flows
        fund_events = self.fund_event_cash_flow_repository.get_fund_event_cash_flows(session, bank_account_id=bank_account_id)
        if fund_events:
            errors['fund_events'] = ["Cannot delete bank account with dependent fund events"]
        return errors