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
    
    def validate_unit_purchase(self, fund: 'Fund', units: float, price: float, 
                              purchase_date: date, reference_number: str = None, 
                              session: Session = None) -> Dict[str, List[str]]:
        """
        Validate unit purchase business rules.
        
        Args:
            fund: The fund to validate against
            units: Number of units to purchase
            price: Price per unit
            purchase_date: Date of the purchase
            reference_number: External reference number
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}
        
        # BUSINESS RULE: Units must be positive
        if not units or units <= 0:
            errors['units'] = ["Units must be a positive number"]
        
        # BUSINESS RULE: Price must be positive
        if not price or price <= 0:
            errors['price'] = ["Unit price must be a positive number"]
        
        # BUSINESS RULE: Purchase date is required
        if not purchase_date:
            errors['purchase_date'] = ["Purchase date is required"]
        
        # BUSINESS RULE: Unit purchases only for NAV-based funds
        if fund.tracking_type != FundType.NAV_BASED:
            errors['fund_type'] = ["Unit purchases are only applicable for NAV-based funds"]
        
        return errors
    
    def validate_unit_sale(self, fund: 'Fund', units: float, price: float, 
                          sale_date: date, reference_number: str = None, 
                          session: Session = None) -> Dict[str, List[str]]:
        """
        Validate unit sale business rules.
        
        Args:
            fund: The fund to validate against
            units: Number of units to sell
            price: Price per unit
            sale_date: Date of the sale
            reference_number: External reference number
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}
        
        # BUSINESS RULE: Units must be positive
        if not units or units <= 0:
            errors['units'] = ["Units must be a positive number"]
        
        # BUSINESS RULE: Price must be positive
        if not price or price <= 0:
            errors['price'] = ["Unit price must be a positive number"]
        
        # BUSINESS RULE: Sale date is required
        if not sale_date:
            errors['sale_date'] = ["Sale date is required"]
        
        # BUSINESS RULE: Unit sales only for NAV-based funds
        if fund.tracking_type != FundType.NAV_BASED:
            errors['fund_type'] = ["Unit sales are only applicable for NAV-based funds"]
        
        # BUSINESS RULE: Cannot sell more units than available
        if units > fund.current_units:
            errors['units'] = [f"Insufficient units: trying to sell {units} but only {fund.current_units} available"]
        
        return errors
    
    def validate_nav_update(self, fund: 'Fund', nav_per_share: float, update_date: date, 
                           reference_number: str = None, session: Session = None) -> Dict[str, List[str]]:
        """
        Validate NAV update business rules.
        
        Args:
            fund: The fund to validate against
            nav_per_share: NAV per share value
            update_date: Date of the NAV update
            reference_number: External reference number
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}
        
        # BUSINESS RULE: NAV per share must be positive
        if not nav_per_share or nav_per_share <= 0:
            errors['nav_per_share'] = ["NAV per share must be a positive number"]
        
        # BUSINESS RULE: Update date is required
        if not update_date:
            errors['update_date'] = ["Update date is required"]
        
        # BUSINESS RULE: NAV updates only for NAV-based funds
        if fund.tracking_type != FundType.NAV_BASED:
            errors['fund_type'] = ["NAV updates are only applicable for NAV-based funds"]
        
        # BUSINESS RULE: No duplicate NAV events on same date
        if session:
            duplicate_event = self._check_duplicate_nav_event(fund, nav_per_share, update_date, reference_number, session)
            if duplicate_event:
                errors['duplicate'] = [f"NAV update already exists for {update_date}"]
        
        return errors
    
    def _check_duplicate_nav_event(self, fund: 'Fund', nav_per_share: float, date: date, 
                                  reference_number: str, session: Session) -> Optional['FundEvent']:
        """
        Check for existing NAV update event on the same date.
        
        Args:
            fund: The fund object
            nav_per_share: NAV per share value (not used in check)
            date: Date of the NAV update
            reference_number: External reference number (not used in check)
            session: Database session
            
        Returns:
            FundEvent: Existing event if found on same date, None otherwise
        """
        from src.fund.enums import EventType
        from src.fund.repositories import FundEventRepository
        
        # Use business repository (not query repository) for validation
        event_repo = FundEventRepository()
        existing_events = event_repo.get_by_fund_and_types(fund.id, [EventType.NAV_UPDATE], session)
        
        # Check if any NAV event exists on the same date
        for event in existing_events:
            if event.event_date == date:
                return event
        
        return None
    
    def validate_distribution(self, fund: 'Fund', event_date: date, distribution_type: 'DistributionType',
                            distribution_amount: float = None, has_withholding_tax: bool = False,
                            gross_interest_amount: float = None, net_interest_amount: float = None,
                            withholding_tax_amount: float = None, withholding_tax_rate: float = None,
                            reference_number: str = None, session: Session = None) -> Dict[str, List[str]]:
        """
        Validate distribution event parameters.
        
        Args:
            fund: The fund object
            event_date: Distribution date
            distribution_type: Type of distribution
            distribution_amount: Simple distribution amount (when has_withholding_tax=False)
            has_withholding_tax: Whether this distribution has withholding tax
            gross_interest_amount: Gross interest amount (when has_withholding_tax=True)
            net_interest_amount: Net interest amount (when has_withholding_tax=True)
            withholding_tax_amount: Tax amount withheld (when has_withholding_tax=True)
            withholding_tax_rate: Tax rate percentage (when has_withholding_tax=True)
            reference_number: External reference number
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}
        
        # BUSINESS RULE: Event date is required
        if not event_date:
            errors['event_date'] = ["Event date is required"]
        
        # BUSINESS RULE: Distribution type is required
        if not distribution_type:
            errors['distribution_type'] = ["Distribution type is required"]
        
        # BUSINESS RULE: Validate distribution type
        if distribution_type:
            try:
                from src.fund.enums import DistributionType
                if not isinstance(distribution_type, DistributionType):
                    DistributionType.from_string(str(distribution_type))
            except (ValueError, AttributeError):
                errors['distribution_type'] = ["Invalid distribution_type"]
        
        # BUSINESS RULE: Validate withholding tax scenario
        if has_withholding_tax:
            # Withholding tax is only valid for INTEREST distributions
            if distribution_type and distribution_type != DistributionType.INTEREST:
                errors['distribution_type'] = ["Withholding tax is only valid for INTEREST distributions"]
            
            # Must have exactly one amount type (gross OR net)
            amount_fields = [gross_interest_amount, net_interest_amount]
            provided_amount_fields = sum(1 for field in amount_fields if field is not None)
            
            if provided_amount_fields == 0:
                errors['amount'] = ["For withholding tax distributions, exactly one of gross_interest_amount OR net_interest_amount must be provided"]
            elif provided_amount_fields > 1:
                errors['amount'] = ["For withholding tax distributions, only one of gross_interest_amount OR net_interest_amount can be provided (not both)"]
            
            # Must have exactly one tax type (amount OR rate)
            tax_fields = [withholding_tax_amount, withholding_tax_rate]
            provided_tax_fields = sum(1 for field in tax_fields if field is not None)
            
            if provided_tax_fields == 0:
                errors['tax'] = ["For withholding tax distributions, exactly one of withholding_tax_amount OR withholding_tax_rate must be provided"]
            elif provided_tax_fields > 1:
                errors['tax'] = ["For withholding tax distributions, only one of withholding_tax_amount OR withholding_tax_rate can be provided (not both)"]
            
            # Validate numeric values
            for field_name, value in [
                ('gross_interest_amount', gross_interest_amount),
                ('net_interest_amount', net_interest_amount),
                ('withholding_tax_amount', withholding_tax_amount),
                ('withholding_tax_rate', withholding_tax_rate)
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
            if gross_interest_amount and net_interest_amount and gross_interest_amount <= net_interest_amount:
                errors['amount'] = ["Gross amount must be greater than net amount for withholding tax distributions"]
        else:
            # Simple distribution validation
            if not distribution_amount:
                errors['distribution_amount'] = ["Distribution amount is required for simple distributions"]
            elif distribution_amount <= 0:
                errors['distribution_amount'] = ["Distribution amount must be positive"]
            
            # Simple distributions should not have withholding tax fields
            if any([gross_interest_amount, net_interest_amount, withholding_tax_amount, withholding_tax_rate]):
                errors['withholding_tax'] = ["Withholding tax fields should not be provided for simple distributions"]
        
        return errors