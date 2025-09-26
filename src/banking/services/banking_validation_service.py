"""
Banking Validation Service.
"""

from sqlalchemy.orm import Session

from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.fund.repositories.fund_event_cash_flow_repository import FundEventCashFlowRepository

class BankingValidationService:
    """
    Service for handling banking business rule validation.

    This module provides the BankingValidationService class, which handles banking business rule validation.
    The service provides clean separation of concerns for:
    - Bank deletion with dependency checking
    - Bank account deletion with dependency checking

    The service uses the BankAccountRepository and FundEventCashFlowRepository to perform CRUD operations.
    """
    
    def __init__(self):
        """
        Initialize the BankingValidationService.
        
        Args:
            bank_account_repository: Bank account repository to use. If None, creates a new one.
            fund_event_cash_flow_repository: Fund event cash flow repository to use. If None, creates a new one.
        """
        self.bank_account_repository = BankAccountRepository()
        self.fund_event_cash_flow_repository = FundEventCashFlowRepository()
    

    # ============================================================================
    # COMPREHENSIVE VALIDATION METHODS
    # ============================================================================

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