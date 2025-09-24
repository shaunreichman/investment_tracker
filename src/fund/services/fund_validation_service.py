"""
Fund Validation Service.

Provides comprehensive validation for fund operations including deletion validation.
Follows enterprise patterns established in company validation service.
"""

from typing import Dict, List, Any
from sqlalchemy.orm import Session
from src.fund.models import Fund
from src.fund.enums.fund_enums import FundTrackingType
from src.fund.enums.fund_event_enums import EventType, DistributionType
from src.fund.repositories import FundEventRepository, FundTaxStatementRepository


class FundValidationService:
    """Enterprise-grade validation service for fund operations."""
    
    def __init__(self):
        """Initialize the validation service with required repositories."""
        self.fund_event_repository = FundEventRepository()
        self.fund_tax_statement_repository = FundTaxStatementRepository()
    
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
        fund_events = self.fund_event_repository.get_fund_events(session, fund.id)
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

        required_fields = ['amount', 'date', 'tracking_type']
        for field in required_fields:
            if field not in event_data:
                errors[field] = [f"{field} is required"]
        
        # BUSINESS RULE: Amount must be positive
        if not event_data['amount'] or event_data['amount'] <= 0:
            errors['amount'] = ["Capital call amount must be a positive number"]
        
        # BUSINESS RULE: Capital calls only for cost-based funds
        if event_data['tracking_type'] != FundTrackingType.COST_BASED:
            errors['fund_type'] = ["Capital calls are only applicable for cost-based funds"]
        
        # BUSINESS RULE: Cannot call more than remaining commitment
        fund = self.fund_repository.get_fund_by_id(event_data['fund_id'], session)
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

        required_fields = ['amount', 'date', 'tracking_type']
        for field in required_fields:
            if field not in event_data:
                errors[field] = [f"{field} is required"]
        
        # BUSINESS RULE: Amount must be positive
        if not event_data['amount'] or event_data['amount'] <= 0:
            errors['amount'] = ["Return amount must be a positive number"]
        
        # BUSINESS RULE: Returns only for cost-based funds
        if event_data['tracking_type'] != FundTrackingType.COST_BASED:
            errors['fund_type'] = ["Returns of capital are only applicable for cost-based funds"]

        # BUSINESS RULE: Cannot return more capital than remaining equity
        fund = self.fund_repository.get_fund_by_id(event_data['fund_id'], session)
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

        required_fields = ['units', 'price', 'date', 'tracking_type']
        for field in required_fields:
            if field not in event_data:
                errors[field] = [f"{field} is required"]
        
        # BUSINESS RULE: Units must be positive
        if event_data['units'] <= 0:
            errors['units'] = ["Units must be a positive number"]
        
        # BUSINESS RULE: Price must be positive
        if event_data['price'] <= 0:
            errors['price'] = ["Unit price must be a positive number"]
        
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

        required_fields = ['units', 'price', 'date', 'tracking_type']
        for field in required_fields:
            if field not in event_data:
                errors[field] = [f"{field} is required"]
                
        # BUSINESS RULE: Units must be positive
        if event_data['units'] <= 0:
            errors['units'] = ["Units must be a positive number"]
        
        # BUSINESS RULE: Price must be positive
        if event_data['price'] <= 0:
            errors['price'] = ["Unit price must be a positive number"]
        
        # BUSINESS RULE: Unit sales only for NAV-based funds
        if event_data['tracking_type'] != FundTrackingType.NAV_BASED:
            errors['fund_type'] = ["Unit sales are only applicable for NAV-based funds"]
        
        # BUSINESS RULE: Cannot sell more units than available
        fund = self.fund_repository.get_fund_by_id(event_data['fund_id'], session)
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

        required_fields = ['nav_per_share', 'date', 'tracking_type']
        for field in required_fields:
            if field not in event_data:
                errors[field] = [f"{field} is required"]

        # BUSINESS RULE: NAV per share must be positive
        if event_data['nav_per_share'] <= 0:
            errors['nav_per_share'] = ["NAV per share must be a positive number"]
        
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
        
        required_fields = ['date', 'distribution_type', 'has_withholding_tax']
        for field in required_fields:
            if field not in event_data:
                errors[field] = [f"{field} is required"]
        
        # BUSINESS RULE: Event date is required
        if not event_data['date']:
            errors['date'] = ["Event date is required"]
        
        # BUSINESS RULE: Distribution type is required
        if not event_data['distribution_type']:
            errors['distribution_type'] = ["Distribution type is required"]
        
        # BUSINESS RULE: Validate withholding tax scenario
        if event_data['has_withholding_tax']:
            # Withholding tax is only valid for INTEREST distributions
            if event_data['distribution_type'] and event_data['distribution_type'] != DistributionType.INTEREST:
                errors['distribution_type'] = ["Withholding tax is only valid for INTEREST distributions"]
            
            # Must have exactly one amount type (gross OR net)
            amount_fields = [event_data['gross_interest_amount'], event_data['net_interest_amount']]
            provided_amount_fields = sum(1 for field in amount_fields if field is not None)
            
            if provided_amount_fields == 0:
                errors['amount'] = ["For withholding tax distributions, exactly one of gross_interest_amount OR net_interest_amount must be provided"]
            elif provided_amount_fields > 1:
                errors['amount'] = ["For withholding tax distributions, only one of gross_interest_amount OR net_interest_amount can be provided (not both)"]
            
            # Must have exactly one tax type (amount OR rate)
            tax_fields = [event_data['withholding_tax_amount'], event_data['withholding_tax_rate']]
            provided_tax_fields = sum(1 for field in tax_fields if field is not None)
            
            if provided_tax_fields == 0:
                errors['tax'] = ["For withholding tax distributions, exactly one of withholding_tax_amount OR withholding_tax_rate must be provided"]
            elif provided_tax_fields > 1:
                errors['tax'] = ["For withholding tax distributions, only one of withholding_tax_amount OR withholding_tax_rate can be provided (not both)"]
            
            # Validate numeric values
            for field_name, value in [
                ('gross_interest_amount', event_data['gross_interest_amount']),
                ('net_interest_amount', event_data['net_interest_amount']),
                ('withholding_tax_amount', event_data['withholding_tax_amount']),
                ('withholding_tax_rate', event_data['withholding_tax_rate'])
            ]:
                if value is not None:
                    try:
                        float_val = float(value)
                        if field_name == 'withholding_tax_rate':
                            if float_val < 0 or float_val > 100:
                                errors[field_name] = [f"{field_name} must be between 0% and 100%"]
                        else:
                            if float_val <= 0:
                                errors[field_name] = [f"{field_name} must be positive"]
                    except (ValueError, TypeError):
                        errors[field_name] = [f"{field_name} must be a valid number"]
            
            # Validate logical consistency
            if event_data['gross_interest_amount'] and event_data['net_interest_amount'] and event_data['gross_interest_amount'] <= event_data['net_interest_amount']:
                errors['amount'] = ["Gross amount must be greater than net amount for withholding tax distributions"]
        else:
            # Simple distribution validation
            if not event_data['distribution_amount']:
                errors['distribution_amount'] = ["Distribution amount is required for simple distributions"]
            elif event_data['distribution_amount'] <= 0:
                errors['distribution_amount'] = ["Distribution amount must be positive"]
            
            # Simple distributions should not have withholding tax fields
            if any([event_data['gross_interest_amount'], event_data['net_interest_amount'], event_data['withholding_tax_amount'], event_data['withholding_tax_rate']]):
                errors['withholding_tax'] = ["Withholding tax fields should not be provided for simple distributions"]
        
        return errors