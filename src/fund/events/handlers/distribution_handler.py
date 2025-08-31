"""
Distribution Event Handler.

This handler processes distribution events for funds,
updating equity balances and triggering dependent calculations.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, DistributionType, GroupType
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
        
        self._validate_required_date(event_date, 'event_date')
        
        # Validate distribution type
        if not distribution_type:
            raise ValueError("distribution_type is required")
        
        try:
            DistributionType.from_string(distribution_type)
        except ValueError as e:
            raise ValueError(f"Invalid distribution_type: {e}")
        
        # Check if this is a withholding tax distribution based on field presence
        has_withholding_tax_fields = any([
            event_data.get('interest_gross_amount') is not None,
            event_data.get('interest_net_amount') is not None,
            event_data.get('interest_withholding_tax_amount') is not None,
            event_data.get('interest_withholding_tax_rate') is not None
        ])
        
        # Validate withholding tax fields if applicable
        if has_withholding_tax_fields:
            self._validate_withholding_tax_fields(event_data)
        else:
            # For simple distributions, amount is required
            amount = event_data.get('amount')
            if not amount:
                raise ValueError("amount is required for simple distributions")
            
            try:
                amount_val = float(amount)
                if amount_val <= 0:
                    raise ValueError("amount must be positive")
            except (ValueError, TypeError):
                raise ValueError("amount must be a valid positive number")
    
    def _validate_withholding_tax_fields(self, event_data: Dict[str, Any]) -> None:
        """
        Validate withholding tax specific fields with enhanced business rules.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        # Validate that withholding tax is only valid for INTEREST distributions
        distribution_type = event_data.get('distribution_type')
        if distribution_type != DistributionType.INTEREST:
            raise ValueError(f"Withholding tax is only valid for INTEREST distributions, not {distribution_type}")
        
        # Extract new field names
        gross_amount = event_data.get('interest_gross_amount')
        net_amount = event_data.get('interest_net_amount')
        tax_amount = event_data.get('interest_withholding_tax_amount')
        tax_rate = event_data.get('interest_withholding_tax_rate')
        
        # Business Rule 1: Must have exactly one amount type (gross OR net)
        amount_fields = [gross_amount, net_amount]
        provided_amount_fields = sum(1 for field in amount_fields if field is not None)
        
        if provided_amount_fields == 0:
            raise ValueError(
                "For withholding tax distributions, exactly one of the following must be provided: "
                "interest_gross_amount OR interest_net_amount"
            )
        
        if provided_amount_fields > 1:
            raise ValueError(
                "For withholding tax distributions, only one of the following can be provided: "
                "interest_gross_amount OR interest_net_amount (not both)"
            )
        
        # Business Rule 2: Must have exactly one tax type (amount OR rate)
        tax_fields = [tax_amount, tax_rate]
        provided_tax_fields = sum(1 for field in tax_fields if field is not None)
        
        if provided_tax_fields == 0:
            raise ValueError(
                "For withholding tax distributions, exactly one of the following must be provided: "
                "interest_withholding_tax_amount OR interest_withholding_tax_rate"
            )
        
        if provided_tax_fields > 1:
            raise ValueError(
                "For withholding tax distributions, only one of the following can be provided: "
                "interest_withholding_tax_amount OR interest_withholding_tax_rate (not both)"
            )
        
        # Validate numeric values and ranges
        for field_name, value in [
            ('interest_gross_amount', gross_amount),
            ('interest_net_amount', net_amount),
            ('interest_withholding_tax_amount', tax_amount),
            ('interest_withholding_tax_rate', tax_rate)
        ]:
            if value is not None:
                try:
                    float_val = float(value)
                    if field_name == 'interest_withholding_tax_rate':
                        if float_val < 0 or float_val > 100:
                            raise ValueError(f"{field_name} must be between 0% and 100%")
                    else:
                        if float_val <= 0:
                            raise ValueError(f"{field_name} must be positive")
                except (ValueError, TypeError):
                    raise ValueError(f"{field_name} must be a valid number")
        
        # Business Rule 3: Validate logical consistency
        if gross_amount and net_amount and gross_amount <= net_amount:
            raise ValueError("Gross amount must be greater than net amount for withholding tax distributions")
        
        if tax_rate and tax_rate >= 100:
            raise ValueError("Tax rate must be less than 100% for withholding tax distributions")
    
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
        
        # Validate first event business rules
        self._validate_first_event(EventType.DISTRIBUTION)
        
        # Extract parameters
        event_date = self._parse_date(event_data['event_date'])
        distribution_type = event_data['distribution_type']
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        # Check if this is a withholding tax distribution based on field presence
        has_withholding_tax_fields = any([
            event_data.get('interest_gross_amount') is not None,
            event_data.get('interest_net_amount') is not None,
            event_data.get('interest_withholding_tax_amount') is not None,
            event_data.get('interest_withholding_tax_rate') is not None
        ])
        
        # Check for existing duplicate event (idempotent behavior)
        existing_event = self._check_duplicate_distribution(event_data, has_withholding_tax_fields)
        if existing_event:
            # Return existing event without creating duplicate
            return existing_event
        
        # Create distribution event
        if has_withholding_tax_fields:
            event = self._create_withholding_tax_distribution(event_data)
        else:
            event = self._create_simple_distribution(event_data)
        
        # Update fund state
        self._update_fund_after_distribution(event)
        
        # Handle status transitions
        self._handle_status_transition(event)
        
        # Publish domain events
        self._publish_dependent_events(event)
        
        return event
    
    def _check_duplicate_distribution(self, event_data: Dict[str, Any], has_withholding_tax_fields: bool) -> Optional[FundEvent]:
        """
        Check for existing duplicate distribution event.
        
        Args:
            event_data: Dictionary containing event parameters
            has_withholding_tax_fields: Whether this is a withholding tax distribution
            
        Returns:
            FundEvent: Existing event if found, None otherwise
        """
        event_date = self._parse_date(event_data['event_date'])
        distribution_type = event_data['distribution_type']
        reference_number = event_data.get('reference_number')
        
        if has_withholding_tax_fields:
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
            amount = event_data.get('amount')
            return self._check_duplicate_event(
                EventType.DISTRIBUTION,
                event_date=event_date,
                distribution_type=distribution_type,
                amount=amount,
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
        amount = float(event_data['amount'])
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        return self._create_event(
            EventType.DISTRIBUTION,
            event_date=event_date,
            distribution_type=distribution_type,
            amount=amount,
            description=description or f"Distribution: ${amount:,.2f}",
            reference_number=reference_number
        )
    
    def _create_withholding_tax_distribution(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Create a distribution event with withholding tax using enhanced calculation logic.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: Created distribution event
        """
        event_date = self._parse_date(event_data['event_date'])
        distribution_type = event_data['distribution_type']
        gross_amount = event_data.get('interest_gross_amount')
        net_amount = event_data.get('interest_net_amount')
        tax_amount = event_data.get('interest_withholding_tax_amount')
        tax_rate = event_data.get('interest_withholding_tax_rate')
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        # Calculate all missing values using enhanced business logic
        calculated_values = self._calculate_withholding_tax_values(
            gross_amount, net_amount, tax_amount, tax_rate
        )
        
        # Extract calculated values
        final_gross = calculated_values['gross_amount']
        final_net = calculated_values['net_amount']
        final_tax = calculated_values['tax_amount']
        final_rate = calculated_values['tax_rate']
        
        # Create the distribution event with proper grouping
        event = self._create_event(
            EventType.DISTRIBUTION,
            event_date=event_date,
            distribution_type=DistributionType.INTEREST,
            amount=final_gross,
            has_withholding_tax=True,
            tax_withholding=final_tax,
            description=description or f"Interest distribution: ${final_gross:,.2f} (net of ${final_tax:,.2f} withholding tax)",
            reference_number=reference_number
        )
        
        # Create tax payment event with proper grouping
        tax_event = self._create_event(
            EventType.TAX_PAYMENT,
            event_date=event_date,
            tax_payment_type='NON_RESIDENT_INTEREST_WITHHOLDING',
            amount=-final_tax,  # Negative for tax payments (outflow)
            description=f"Withholding tax payment: ${final_tax:,.2f} ({final_rate:.2f}%)",
            reference_number=f"{reference_number}_TAX" if reference_number else None
        )
        
        # Group the events together for reporting
        group_id = self._generate_group_id()
        event.group_id = group_id
        event.group_type = GroupType.INTEREST_WITHHOLDING
        event.group_position = 0
        
        tax_event.group_id = group_id
        tax_event.group_type = GroupType.INTEREST_WITHHOLDING
        tax_event.group_position = 1
        
        # Store both events in the session
        self.session.add(event)
        self.session.add(tax_event)
        
        return event
    
    def _calculate_withholding_tax_values(self, gross_amount: Optional[float], net_amount: Optional[float], 
                                        tax_amount: Optional[float], tax_rate: Optional[float]) -> Dict[str, float]:
        """
        Calculate all withholding tax values from any combination of provided inputs.
        
        This method implements the business logic for calculating missing values
        based on the user's input preferences.
        
        Args:
            gross_amount: Gross interest amount (before tax)
            net_amount: Net interest amount (after tax)
            tax_amount: Withholding tax amount
            tax_rate: Withholding tax rate as percentage
            
        Returns:
            Dictionary containing all calculated values: gross_amount, net_amount, tax_amount, tax_rate
            
        Raises:
            ValueError: If calculation fails or results are invalid
        """
        # Convert all inputs to float, handling None values
        gross = float(gross_amount) if gross_amount is not None else None
        net = float(net_amount) if net_amount is not None else None
        tax = float(tax_amount) if tax_amount is not None else None
        rate = float(tax_rate) if tax_rate is not None else None
        
        # Case 1: Gross + Tax Amount → Calculate Net and Rate
        if gross is not None and tax is not None:
            if gross <= 0:
                raise ValueError("Gross amount must be positive")
            if tax < 0:
                raise ValueError("Tax amount cannot be negative")
            if tax >= gross:
                raise ValueError("Tax amount cannot be greater than or equal to gross amount")
            
            net = gross - tax
            rate = (tax / gross) * 100
            
        # Case 2: Gross + Tax Rate → Calculate Tax Amount and Net
        elif gross is not None and rate is not None:
            if gross <= 0:
                raise ValueError("Gross amount must be positive")
            if rate < 0 or rate >= 100:
                raise ValueError("Tax rate must be between 0% and 100%")
            
            tax = (gross * rate) / 100
            net = gross - tax
            
        # Case 3: Net + Tax Amount → Calculate Gross and Rate
        elif net is not None and tax is not None:
            if net <= 0:
                raise ValueError("Net amount must be positive")
            if tax < 0:
                raise ValueError("Tax amount cannot be negative")
            
            gross = net + tax
            rate = (tax / gross) * 100
            
        # Case 4: Net + Tax Rate → Calculate Gross and Tax Amount
        elif net is not None and rate is not None:
            if net <= 0:
                raise ValueError("Net amount must be positive")
            if rate < 0 or rate >= 100:
                raise ValueError("Tax rate must be between 0% and 100%")
            
            # Net = Gross * (1 - Rate/100)
            # Gross = Net / (1 - Rate/100)
            gross = net / (1 - (rate / 100))
            tax = gross - net
            
        else:
            # This should never happen due to validation, but just in case
            raise ValueError("Invalid combination of withholding tax fields provided")
        
        # Validate final results
        if gross <= 0 or net <= 0 or tax < 0 or rate < 0 or rate >= 100:
            raise ValueError("Calculation produced invalid results")
        
        # Ensure consistency: Gross = Net + Tax
        if abs(gross - (net + tax)) > 0.01:  # Allow for small floating point differences
            raise ValueError("Calculation inconsistency: Gross amount does not equal Net + Tax")
        
        return {
            'gross_amount': round(gross, 2),
            'net_amount': round(net, 2),
            'tax_amount': round(tax, 2),
            'tax_rate': round(rate, 2)
        }
    
    def _generate_group_id(self) -> int:
        """
        Generate a unique group ID for event grouping.
        
        Returns:
            Unique integer group ID
        """
        # Simple implementation - in production, you might want a more sophisticated approach
        import time
        return int(time.time() * 1000)  # Millisecond timestamp as group ID
    
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
        self._update_fund_summary_fields(event)
    
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
