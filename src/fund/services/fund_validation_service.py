"""
Fund Validation Service.

Provides comprehensive validation for fund operations including deletion validation.
Follows enterprise patterns established in company validation service.
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from src.fund.models import Fund
from src.fund.enums import FundStatus


class FundValidationService:
    """Enterprise-grade validation service for fund operations."""
    
    def __init__(self):
        """Initialize the validation service."""
        pass
    
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
        fund_events_count = len(fund.fund_events)
        if fund_events_count > 0:
            errors['fund_events'] = [
                f'Cannot delete fund with {fund_events_count} fund events. '
                f'Fund must have 0 events to be deleted.'
            ]
        
        # BUSINESS RULE: Prevent deletion of funds with tax statements
        tax_statements_count = len(fund.tax_statements)
        if tax_statements_count > 0:
            errors['tax_statements'] = [
                f'Cannot delete fund with {tax_statements_count} tax statements. '
                f'Fund must have 0 tax statements to be deleted.'
            ]
        
        # BUSINESS RULE: Prevent deletion of funds with domain events
        domain_events_count = len(fund.domain_events)
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
