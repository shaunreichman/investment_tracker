"""
Distribution Event Handler.

This handler processes distribution events for funds,
updating equity balances and triggering dependent calculations.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, DistributionType
from src.fund.models import FundEvent


class DistributionHandler(BaseFundEventHandler):
    """
    Handler for distribution events.
    
    This handler processes distribution events for all fund types.
    It handles both simple distributions and complex distributions
    with withholding tax calculations.
    """
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate distribution event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        event_date = event_data.get('event_date')
        distribution_type = event_data.get('distribution_type')
        has_withholding_tax = event_data.get('has_withholding_tax', False)
        
        self._validate_required_date(event_date, 'event_date')
        
        # Validate distribution type
        if not distribution_type:
            raise ValueError("distribution_type is required")
        
        try:
            DistributionType.from_string(distribution_type)
        except ValueError as e:
            raise ValueError(f"Invalid distribution_type: {e}")
        
        # Validate withholding tax fields if applicable
        if has_withholding_tax:
            self._validate_withholding_tax_fields(event_data)
        else:
            # For simple distributions, amount is required
            distribution_amount = event_data.get('distribution_amount')
            if not distribution_amount:
                raise ValueError("distribution_amount is required for simple distributions")
            
            try:
                amount = float(distribution_amount)
                if amount <= 0:
                    raise ValueError("distribution_amount must be positive")
            except (ValueError, TypeError):
                raise ValueError("distribution_amount must be a valid positive number")
    
    def _validate_withholding_tax_fields(self, event_data: Dict[str, Any]) -> None:
        """
        Validate withholding tax specific fields.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        # Validate that withholding tax is only valid for INTEREST distributions
        distribution_type = event_data.get('distribution_type')
        if distribution_type != DistributionType.INTEREST:
            raise ValueError(f"Withholding tax (has_withholding_tax=True) is only valid for INTEREST distributions, not {distribution_type}")
        
        # For withholding tax distributions, we need either gross + tax amount
        # or gross + tax rate, or net + tax amount, or net + tax rate
        gross_amount = event_data.get('gross_interest_amount')
        net_amount = event_data.get('net_interest_amount')
        tax_amount = event_data.get('withholding_tax_amount')
        tax_rate = event_data.get('withholding_tax_rate')
        
        # At least two of these must be provided
        provided_fields = sum(1 for field in [gross_amount, net_amount, tax_amount, tax_rate] if field is not None)
        
        if provided_fields < 2:
            raise ValueError(
                "For withholding tax distributions, at least two of the following must be provided: "
                "gross_interest_amount, net_interest_amount, withholding_tax_amount, withholding_tax_rate"
            )
        
        # Validate numeric values
        for field_name, value in [
            ('gross_interest_amount', gross_amount),
            ('net_interest_amount', net_amount),
            ('withholding_tax_amount', tax_amount),
            ('withholding_tax_rate', tax_rate)
        ]:
            if value is not None:
                try:
                    float_val = float(value)
                    if field_name == 'withholding_tax_rate' and (float_val < 0 or float_val > 100):
                        raise ValueError(f"{field_name} must be between 0 and 100")
                    elif field_name != 'withholding_tax_rate' and float_val < 0:
                        raise ValueError(f"{field_name} cannot be negative")
                except (ValueError, TypeError):
                    raise ValueError(f"{field_name} must be a valid number")
    
    def handle(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Handle a distribution event.
        
        This method:
        1. Validates the event data
        2. Checks for duplicate events (idempotent behavior)
        3. Creates the distribution event
        4. Creates tax event if needed
        5. Updates fund state
        6. Publishes domain events
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: The created distribution event
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        # Validate event data
        self.validate_event(event_data)
        
        # Extract parameters
        event_date = self._parse_date(event_data['event_date'])
        distribution_type = event_data['distribution_type']
        has_withholding_tax = event_data.get('has_withholding_tax', False)
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        # Check for existing duplicate event (idempotent behavior)
        existing_event = self._check_duplicate_distribution(event_data)
        if existing_event:
            # Return existing event without creating duplicate
            return existing_event
        
        # Create distribution event
        if has_withholding_tax:
            event = self._create_withholding_tax_distribution(event_data)
        else:
            event = self._create_simple_distribution(event_data)
        
        # Update fund state
        self._update_fund_after_distribution(event)
        
        # Publish domain events
        self._publish_dependent_events(event)
        
        return event
    
    def _check_duplicate_distribution(self, event_data: Dict[str, Any]) -> Optional[FundEvent]:
        """
        Check for existing duplicate distribution event.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: Existing event if found, None otherwise
        """
        event_date = self._parse_date(event_data['event_date'])
        distribution_type = event_data['distribution_type']
        has_withholding_tax = event_data.get('has_withholding_tax', False)
        reference_number = event_data.get('reference_number')
        
        if has_withholding_tax:
            # For withholding tax distributions, check by date, type, and reference
            return self._check_duplicate_event(
                EventType.DISTRIBUTION,
                event_date=event_date,
                distribution_type=distribution_type,
                reference_number=reference_number,
                has_withholding_tax=True
            )
        else:
            # For simple distributions, check by date, type, amount, and reference
            distribution_amount = event_data.get('distribution_amount')
            return self._check_duplicate_event(
                EventType.DISTRIBUTION,
                event_date=event_date,
                distribution_type=distribution_type,
                amount=distribution_amount,
                reference_number=reference_number
            )
    
    def _create_simple_distribution(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Create a simple distribution event.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: Created distribution event
        """
        event_date = self._parse_date(event_data['event_date'])
        distribution_type = event_data['distribution_type']
        distribution_amount = float(event_data['distribution_amount'])
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        return self._create_event(
            EventType.DISTRIBUTION,
            event_date=event_date,
            distribution_type=distribution_type,
            amount=distribution_amount,
            description=description or f"Distribution: ${distribution_amount:,.2f}",
            reference_number=reference_number
        )
    
    def _create_withholding_tax_distribution(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Create a distribution event with withholding tax.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: Created distribution event
        """
        event_date = self._parse_date(event_data['event_date'])
        distribution_type = event_data['distribution_type']
        gross_amount = event_data.get('gross_interest_amount')
        net_amount = event_data.get('net_interest_amount')
        tax_amount = event_data.get('withholding_tax_amount')
        tax_rate = event_data.get('withholding_tax_rate')
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        # Calculate missing values using tax service
        if gross_amount is not None and tax_amount is not None:
            # We have gross and tax, calculate net
            net_amount = gross_amount - tax_amount
            tax_rate = (tax_amount / gross_amount) * 100 if gross_amount else 0.0
        elif gross_amount is not None and tax_rate is not None:
            # We have gross and rate, calculate tax and net
            tax_amount = (gross_amount * tax_rate) / 100
            net_amount = gross_amount - tax_amount
        elif net_amount is not None and tax_amount is not None:
            # We have net and tax, calculate gross
            gross_amount = net_amount + tax_amount
            tax_rate = (tax_amount / gross_amount) * 100 if gross_amount else 0.0
        elif net_amount is not None and tax_rate is not None:
            # We have net and rate, calculate gross and tax
            gross_amount = net_amount / (1 - (tax_rate / 100))
            tax_amount = gross_amount - net_amount
        
        # Create the distribution event
        # NOTE: Only pass fields that exist in the old FundEvent model
        event = self._create_event(
            EventType.DISTRIBUTION,
            event_date=event_date,
            distribution_type=DistributionType.INTEREST,
            amount=net_amount,
            has_withholding_tax=True,
            description=description or f"Interest distribution: ${net_amount:,.2f} (net)",
            reference_number=reference_number
        )
        
        # Create tax payment event
        # NOTE: Only pass fields that exist in the old FundEvent model
        tax_event = self._create_event(
            EventType.TAX_PAYMENT,
            event_date=event_date,
            amount=tax_amount,
            description=f"Withholding tax: ${tax_amount:,.2f}",
            reference_number=f"{reference_number}_TAX" if reference_number else None
        )
        
        return event
    
    def _update_fund_after_distribution(self, event: FundEvent) -> None:
        """
        Update fund state after a distribution event.
        
        Args:
            event: The distribution event that was created
        """
        # For distributions, we typically don't need to recalculate
        # the entire capital chain, but we may need to update
        # specific fields or trigger other updates
        
        # Update fund summary fields if needed
        self._update_fund_summary_fields()
    
    def _publish_dependent_events(self, event: FundEvent) -> None:
        """
        Publish domain events for dependent updates.
        
        This method creates and stores domain events for significant
        state changes, enabling loose coupling between components.
        
        Args:
            event: The distribution event that was processed
        """
        # Call the base class implementation which handles all domain event creation
        super()._publish_dependent_events(event)
