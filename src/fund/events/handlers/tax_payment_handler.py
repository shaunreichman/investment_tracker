"""
Tax Payment Event Handler.

This handler processes tax payment events for funds,
handling tax-related payments and updates.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, TaxPaymentType
from src.fund.models import FundEvent


class TaxPaymentHandler(BaseFundEventHandler):
    """
    Handler for tax payment events.
    
    This handler processes tax payment events for all fund types.
    It handles validation, event creation, and fund updates for tax payments.
    """
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate tax payment event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        amount = event_data.get('amount')
        event_date = event_data.get('event_date')
        tax_payment_type = event_data.get('tax_payment_type')
        
        self._validate_positive_amount(amount, 'amount')
        self._validate_required_date(event_date, 'event_date')
        
        # Validate tax payment type
        if not tax_payment_type:
            raise ValueError("tax_payment_type is required")
        
        try:
            TaxPaymentType.from_string(tax_payment_type)
        except ValueError as e:
            raise ValueError(f"Invalid tax_payment_type: {e}")
        
        # Validate amount is numeric
        try:
            float(amount)
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid number")
    
    def handle(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Handle a tax payment event.
        
        This method:
        1. Validates the event data
        2. Checks for duplicate events (idempotent behavior)
        3. Creates the tax payment event
        4. Updates fund state
        5. Publishes domain events
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: The created tax payment event
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        # Validate event data
        self.validate_event(event_data)
        
        # Extract parameters
        amount = float(event_data['amount'])
        event_date = self._parse_date(event_data['event_date'])
        tax_payment_type = event_data['tax_payment_type']
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        # Check for existing duplicate event (idempotent behavior)
        existing_event = self._check_duplicate_event(
            EventType.TAX_PAYMENT,
            event_date=event_date,
            amount=amount,
            reference_number=reference_number
        )
        
        if existing_event:
            # Return existing event without creating duplicate
            return existing_event
        
        # Create tax payment event
        event = self._create_event(
            EventType.TAX_PAYMENT,
            event_date=event_date,
            amount=amount,
            tax_payment_type=tax_payment_type,
            description=description or f"Tax payment: ${amount:,.2f}",
            reference_number=reference_number
        )
        
        # Update fund state
        self._update_fund_after_tax_payment(event)
        
        # Publish domain events
        self._publish_dependent_events(event)
        
        return event
    
    def _update_fund_after_tax_payment(self, event: FundEvent) -> None:
        """
        Update fund state after a tax payment event.
        
        Args:
            event: The tax payment event that was created
        """
        # Tax payments typically don't affect equity balance
        # They are income events that reduce tax liability
        # No specific fund state updates needed for tax payments
        
        # Update fund summary fields if needed
        self._update_fund_summary_fields(event)
    
    def _publish_dependent_events(self, event: FundEvent) -> None:
        """
        Publish domain events for dependent updates.
        
        This method creates and stores domain events for significant
        state changes, enabling loose coupling between components.
        
        Args:
            event: The tax payment event that was processed
        """
        # Call the base class implementation which handles all domain event creation
        super()._publish_dependent_events(event)
