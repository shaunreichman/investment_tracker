"""
Fund Validation Service.

Provides comprehensive validation for fund operations including deletion validation.
Follows enterprise patterns established in company validation service.
"""

from typing import Dict, List, Optional
from datetime import date
from sqlalchemy.orm import Session
from src.fund.models import Fund
from src.fund.enums import FundStatus, FundType, EventType
from src.fund.repositories import FundEventRepository, TaxStatementRepository, DomainEventRepository, CapitalEventRepository


class FundValidationService:
    """Enterprise-grade validation service for fund operations."""
    
    def __init__(self):
        """Initialize the validation service with required repositories."""
        self.fund_event_repository = FundEventRepository()
        self.tax_statement_repository = TaxStatementRepository()
        self.capital_event_repository = CapitalEventRepository()
        # DomainEventRepository requires session, so we'll create it when needed
    
    def validate_fund_deletion(self, fund: Fund, session: Session) -> Dict[str, List[str]]:
        """
        Validate that the fund can be deleted.
        
        Args:
            fund: Fund to validate for deletion
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # BUSINESS RULE: Only allow deletion if fund has 0 fund events
        fund_events_count = self.fund_event_repository.get_event_count_by_fund(fund.id, session)
        if fund_events_count > 0:
            errors['fund_events'] = [
                f'Cannot delete fund with {fund_events_count} fund events. '
                f'Fund must have 0 events to be deleted.'
            ]
        
        # BUSINESS RULE: Prevent deletion of funds with tax statements
        tax_statements_count = self.tax_statement_repository.get_statement_count_by_fund(fund.id, session)
        if tax_statements_count > 0:
            errors['tax_statements'] = [
                f'Cannot delete fund with {tax_statements_count} tax statements. '
                f'Fund must have 0 tax statements to be deleted.'
            ]
        
        # BUSINESS RULE: Prevent deletion of funds with domain events
        domain_event_repository = DomainEventRepository(session)
        domain_events_count = domain_event_repository.get_event_count_by_fund(fund.id, session)
        if domain_events_count > 0:
            errors['domain_events'] = [
                f'Cannot delete fund with {domain_events_count} domain events. '
                f'Fund must have 0 domain events to be deleted.'
            ]
        
        return errors
    
    def get_deletion_rules(self) -> List[str]:
        """
        Get list of fund deletion business rules.
        
        Returns:
            List of human-readable deletion rules
        """
        return [
            "Fund must have 0 fund events to be deleted",
            "Fund must have 0 tax statements to be deleted", 
            "Fund must have 0 domain events to be deleted"
        ]
    
    def validate_capital_call(self, fund: Fund, amount: float, call_date: date, 
                            reference_number: str = None, session: Session = None) -> Dict[str, List[str]]:
        """
        Validate capital call creation.
        
        Args:
            fund: Fund object
            amount: Capital call amount
            call_date: Date of the capital call
            reference_number: External reference number
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # BUSINESS RULE: Amount must be positive
        if not amount or amount <= 0:
            errors['amount'] = ["Capital call amount must be a positive number"]
        
        # BUSINESS RULE: Call date is required
        if not call_date:
            errors['call_date'] = ["Capital call date is required"]
        
        # BUSINESS RULE: Capital calls only for cost-based funds
        if fund.tracking_type != FundType.COST_BASED:
            errors['fund_type'] = ["Capital calls are only applicable for cost-based funds"]
        
        # BUSINESS RULE: Cannot call more than remaining commitment
        if fund.commitment_amount and amount > fund.get_remaining_commitment():
            errors['amount'] = ["Cannot call more capital than remaining commitment"]
        
        return errors
    
    def validate_return_of_capital(self, fund: Fund, amount: float, return_date: date,
                                 reference_number: str = None, session: Session = None) -> Dict[str, List[str]]:
        """
        Validate return of capital creation.
        
        Args:
            fund: Fund object
            amount: Return amount
            return_date: Date of the return
            reference_number: External reference number
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # BUSINESS RULE: Amount must be positive
        if not amount or amount <= 0:
            errors['amount'] = ["Return amount must be a positive number"]
        
        # BUSINESS RULE: Return date is required
        if not return_date:
            errors['return_date'] = ["Return date is required"]
        
        # BUSINESS RULE: Returns only for cost-based funds
        if fund.tracking_type != FundType.COST_BASED:
            errors['fund_type'] = ["Returns of capital are only applicable for cost-based funds"]
        
        return errors
