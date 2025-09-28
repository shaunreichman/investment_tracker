"""
Fund Validation Service.
"""

from typing import Dict, List, Any
from sqlalchemy.orm import Session
from src.fund.models import Fund
from src.fund.enums.fund_enums import FundTrackingType
from src.fund.enums.fund_event_enums import EventType
from src.fund.repositories import FundEventRepository, FundTaxStatementRepository, FundRepository


class FundValidationService:
    """
    Fund Validation Service.

    This module provides the FundValidationService class, which handles fund business rule validation.
    The service provides clean separation of concerns for:
    - Fund deletion validation
    - Fund event creation validation
        - Capital call validation
        - Return of capital validation
        - Unit purchase validation
        - Unit sale validation
        - NAV update validation
        - Distribution validation
    - Fund tax statement deletion validation

    The service uses the FundEventRepository and FundTaxStatementRepository to perform CRUD operations.
    """
    
    def __init__(self):
        """
        Initialize the validation service with required repositories.

        Args:
            fund_event_repository: Fund event repository to use. If None, creates a new one.
            fund_tax_statement_repository: Fund tax statement repository to use. If None, creates a new one.
        """
        self.fund_event_repository = FundEventRepository()
        self.fund_tax_statement_repository = FundTaxStatementRepository()
        self.fund_repository = FundRepository()
    
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
        fund_events = self.fund_event_repository.get_fund_events(session, fund_ids=[fund.id])
        if len(fund_events) > 0:
            errors['fund_events'] = [
                f'Cannot delete fund with {len(fund_events)} fund events. '
                f'Fund must have 0 events to be deleted.'
            ]
        
        # BUSINESS RULE: Prevent deletion of funds with tax statements
        tax_statements = self.fund_tax_statement_repository.get_fund_tax_statements(fund_id=fund.id, session=session)
        if len(tax_statements) > 0:
            errors['tax_statements'] = [
                f'Cannot delete fund with {len(tax_statements)} tax statements. '
                f'Fund must have 0 tax statements to be deleted.'
            ]
        
        return errors

    def validate_fund_event_creation(self, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate fund event creation.
        
        Args:
            event_data: Event data
            session: Database session
        """
        event_type = event_data['event_type']
        if event_type == EventType.CAPITAL_CALL:
            return self.validate_capital_call(event_data, session)
        elif event_type == EventType.RETURN_OF_CAPITAL:
            return self.validate_return_of_capital(event_data, session)
        elif event_type == EventType.UNIT_PURCHASE:
            return self.validate_unit_purchase(event_data, session)
        elif event_type == EventType.UNIT_SALE:
            return self.validate_unit_sale(event_data, session)
        elif event_type == EventType.NAV_UPDATE:
            return self.validate_nav_update(event_data, session)
        elif event_type == EventType.DISTRIBUTION:
            return self.validate_distribution(event_data, session)
        else:
            raise ValueError(f"Invalid event type: {event_type}")
    
    def validate_capital_call(self, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate capital call creation.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        # BUSINESS RULE: Capital calls only for cost-based funds
        if event_data['tracking_type'] != FundTrackingType.COST_BASED:
            errors['fund_type'] = ["Capital calls are only applicable for cost-based funds"]
        
        # BUSINESS RULE: Cannot call more than remaining commitment
        fund = self.fund_repository.get_fund_by_id(event_data['fund_id'], session)
        if not fund:
            raise ValueError(f"Fund not found")
        if fund.commitment_amount and event_data['amount'] > fund.commitment_amount:
            errors['amount'] = ["Cannot call more capital than remaining commitment"]
        
        return errors
    
    def validate_return_of_capital(self, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate return of capital creation.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # BUSINESS RULE: Returns only for cost-based funds
        if event_data['tracking_type'] != FundTrackingType.COST_BASED:
            errors['fund_type'] = ["Returns of capital are only applicable for cost-based funds"]

        # BUSINESS RULE: Cannot return more capital than remaining equity
        fund = self.fund_repository.get_fund_by_id(event_data['fund_id'], session)
        if not fund:
            raise ValueError(f"Fund not found")
        if fund.current_equity_balance and event_data['amount'] > fund.current_equity_balance:
            errors['amount'] = ["Cannot return more capital than remaining equity"]
        
        return errors
    
    def validate_unit_purchase(self, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate unit purchase business rules.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}

        # BUSINESS RULE: Unit purchases only for NAV-based funds
        if event_data['tracking_type'] != FundTrackingType.NAV_BASED:
            errors['fund_type'] = ["Unit purchases are only applicable for NAV-based funds"]
        
        return errors
    
    def validate_unit_sale(self, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate unit sale business rules.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}

        # BUSINESS RULE: Unit sales only for NAV-based funds
        if event_data['tracking_type'] != FundTrackingType.NAV_BASED:
            errors['fund_type'] = ["Unit sales are only applicable for NAV-based funds"]
        
        # BUSINESS RULE: Cannot sell more units than available
        fund = self.fund_repository.get_fund_by_id(event_data['fund_id'], session)
        if not fund:
            raise ValueError(f"Fund not found")
        if event_data['units'] > fund.current_units:
            errors['units'] = [f"Insufficient units: trying to sell {event_data['units']} but only {fund.current_units} available"]
        
        return errors
    
    def validate_nav_update(self, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate NAV update business rules.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}

        # BUSINESS RULE: NAV updates only for NAV-based funds
        if event_data['tracking_type'] != FundTrackingType.NAV_BASED:
            errors['fund_type'] = ["NAV updates are only applicable for NAV-based funds"]
        
        return errors
    
    def validate_distribution(self, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate distribution event parameters.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}
    
        # No business logic validation for distributions. The other validation is done in the middleware.
        
        return errors

    def validate_fund_tax_statement_deletion(self, fund_tax_statement_id: int, session: Session) -> Dict[str, List[str]]:
        """
        Validate fund tax statement deletion.
        
        Args:
            fund_tax_statement_id: ID of the fund tax statement to delete
            session: Database session
        """
        errors = {}
        
        # For no we won't do any validation. In the future we could validate that the fund tax statement has no fund events associated with it.
        return errors