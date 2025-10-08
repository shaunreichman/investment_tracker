"""
Banking Validation Service.
"""

from sqlalchemy.orm import Session
from datetime import date
from typing import Dict, Any

from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.banking.repositories.bank_account_balance_repository import BankAccountBalanceRepository
from src.fund.repositories.fund_event_cash_flow_repository import FundEventCashFlowRepository
from src.shared.calculators.last_day_of_the_month_calculator import LastDayOfTheMonthCalculator

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
            bank_account_balance_repository: Bank account balance repository to use. If None, creates a new one.
            fund_event_cash_flow_repository: Fund event cash flow repository to use. If None, creates a new one.
            last_day_of_the_month_calculator: Last day of the month calculator to use. If None, creates a new one.
        """
        self.bank_account_repository = BankAccountRepository()
        self.bank_account_balance_repository = BankAccountBalanceRepository()
        self.fund_event_cash_flow_repository = FundEventCashFlowRepository()
        self.last_day_of_the_month_calculator = LastDayOfTheMonthCalculator()

    # ============================================================================
    # COMPREHENSIVE VALIDATION METHODS
    # ============================================================================

    def validate_bank_deletion(self, bank_id: int, session: Session) -> Dict[str, list]:
        """
        Validate bank deletion.
        
        Args:
            bank_id: Bank ID
            session: Database session

        Returns:
            Dict containing validation errors, empty if no errors
        """
        errors = {}
        # Cannot delete bank with dependent bank accounts
        bank_accounts = self.bank_account_repository.get_bank_accounts(session, bank_ids=[bank_id])
        if bank_accounts:
            errors['bank_accounts'] = ["Cannot delete bank with dependent bank accounts"]
        return errors

    
    def validate_bank_account_deletion(self, bank_account_id: int, session: Session) -> Dict[str, list]:
        """
        Validate bank account deletion.
        
        Args:
            bank_account_id: Bank account ID
            session: Database session

        Returns:
            Dict containing validation errors, empty if no errors
        """
        errors = {}
        # Cannot delete bank account with dependent fund event cash flows
        fund_events = self.fund_event_cash_flow_repository.get_fund_event_cash_flows(session, bank_account_ids=[bank_account_id])
        if fund_events:
            errors['fund_events'] = ["Cannot delete bank account with dependent fund events"]

        # Cannot delete bank account with dependent bank account balances
        bank_account_balances = self.bank_account_balance_repository.get_bank_account_balances(session, bank_account_ids=[bank_account_id])
        if bank_account_balances:
            errors['bank_account_balances'] = ["Cannot delete bank account with dependent bank account balances"]

        return errors

    def validate_bank_account_balance_creation(self, bank_account_id: int, bank_account_balance_data: Dict[str, Any], session: Session) -> Dict[str, list]:
        """
        Validate bank account balance creation.
        
        Args:
            bank_account_id: Bank account ID
            bank_account_balance_data: Bank account balance data
            session: Database session
            
        Returns:
            Dict containing validation errors, empty if no errors
        """
        errors = {}

        # Validate the bank account exists
        bank_account = self.bank_account_repository.get_bank_account_by_id(bank_account_id, session)
        if not bank_account:
            errors['bank_account'] = [f"Bank account with ID {bank_account_id} not found"]
        
        # Validate the balance date is the last day of any month
        if 'date' not in bank_account_balance_data:
            errors['date'] = ["Bank account balance date is required"]
        else:
            balance_date = bank_account_balance_data['date']
            if isinstance(balance_date, str):
                balance_date = date.fromisoformat(balance_date)
            
            if not self.last_day_of_the_month_calculator.is_last_day_of_the_month(balance_date):
                errors['date'] = ["Bank account balance date must be the last day of the month"]
            else:
                # Only check uniqueness if date is valid
                # Validate the balance is unique for the bank account and date
                bank_account_balances = self.bank_account_balance_repository.get_bank_account_balances(
                    session, bank_account_ids=[bank_account_id], start_date=balance_date, end_date=balance_date
                )
                if bank_account_balances:
                    errors['bank_account_balances'] = ["Bank account balance must be unique for the bank account and date"]
        
        # Validate the currency is the same as the bank account
        if 'currency' not in bank_account_balance_data:
            errors['currency'] = ["Bank account balance currency is required"]
        else:
            # Only validate currency if bank account exists
            if bank_account and bank_account_balance_data['currency'] != bank_account.currency:
                errors['currency'] = ["Bank account balance currency must be the same as the bank account currency"]

        return errors