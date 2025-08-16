"""
Capital Call Event Handler.

This handler processes capital call events for cost-based funds,
updating equity balances and triggering dependent calculations.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, FundType
from src.fund.models import FundEvent


class CapitalCallHandler(BaseFundEventHandler):
    """
    Handler for capital call events.
    
    This handler processes capital call events for cost-based funds.
    It validates the event data, creates the event, and updates
    fund state as needed.
    """
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate capital call event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        # Validate fund type
        self._validate_fund_type(FundType.COST_BASED)
        
        # Validate required fields
        amount = event_data.get('amount')
        event_date = event_data.get('date')
        
        self._validate_positive_amount(amount, 'amount')
        self._validate_required_date(event_date, 'date')
        
        # Validate amount is numeric
        try:
            float(amount)
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid number")
    
    def handle(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Handle a capital call event.
        
        This method:
        1. Validates the event data
        2. Checks for duplicate events (idempotent behavior)
        3. Creates the capital call event
        4. Updates fund state
        5. Publishes domain events
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: The created capital call event
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        # Validate event data
        self.validate_event(event_data)
        
        # Extract parameters
        amount = float(event_data['amount'])
        event_date = self._parse_date(event_data['date'])
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        # Check for existing duplicate event (idempotent behavior)
        existing_event = self._check_duplicate_event(
            EventType.CAPITAL_CALL,
            event_date=event_date,
            amount=amount,
            reference_number=reference_number
        )
        
        if existing_event:
            # Return existing event without creating duplicate
            return existing_event
        
        # Create new capital call event
        event = self._create_event(
            EventType.CAPITAL_CALL,
            event_date=event_date,
            amount=amount,
            description=description or f"Capital call: ${amount:,.2f}",
            reference_number=reference_number
        )
        
        # Update fund state
        self._update_fund_after_capital_event(event)
        
        # Publish domain events
        self._publish_dependent_events(event)
        
        # Handle status transitions if needed
        self._handle_status_transition(event)
        
        return event
    
    def _update_fund_after_capital_event(self, event: FundEvent) -> None:
        """
        Update fund state after a capital call event.
        
        This method handles the complex logic of updating fund state
        after a capital event, including:
        - Recalculating capital chain
        - Updating summary fields
        - Maintaining data consistency
        
        Args:
            event: The capital call event that was created
        """
        # Update the event's current_equity_balance field
        # This is the key field that needs to be set for cost-based funds
        if self.fund.tracking_type == FundType.COST_BASED:
            # For cost-based funds, equity balance accumulates with capital calls
            # Get the current fund equity balance as the "previous" balance for this event
            previous_balance = self.fund.current_equity_balance or 0.0
            new_balance = previous_balance + event.amount
            
            # Update the event's current_equity_balance
            event.current_equity_balance = new_balance
            
            # Update the fund's current_equity_balance
            self.fund.current_equity_balance = new_balance
            
            # Ensure the fund is tracked by the session and flush changes
            if self.fund not in self.session:
                self.session.add(self.fund)
            self.session.flush()
            
            # Ensure the event's amount field is set
            if event.amount is None:
                event.amount = 0.0
        
        # Update fund summary fields using the new architecture
        self._update_fund_summary_fields()
    
    def _publish_dependent_events(self, event: FundEvent) -> None:
        """
        Publish domain events for dependent updates.
        
        This method creates and stores domain events for significant
        state changes, enabling loose coupling between components.
        
        Args:
            event: The capital call event that was processed
        """
        # Call the base class implementation which handles all domain event creation
        super()._publish_dependent_events(event)
