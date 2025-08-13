"""
Capital Call Event Handler.

This module provides the handler for processing capital call events.
It handles validation, event creation, and fund updates for capital calls.
"""

from typing import Dict, Any
from datetime import date

from ..base_handler import BaseFundEventHandler
from ...enums import EventType, FundType
from ...models import FundEvent


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
        event_date = event_data['date']
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
        # Use the existing fund method to recalculate capital chain
        # This maintains compatibility with existing logic while
        # providing a clean interface through the handler
        self.fund.recalculate_capital_chain_from(event, session=self.session)
        
        # Update fund summary fields
        self._update_fund_summary_fields()
    
    def _publish_dependent_events(self, event: FundEvent) -> None:
        """
        Publish domain events for dependent updates.
        
        This method will be implemented in Phase 4 when we add
        the full domain event system. For now, it's a placeholder
        that maintains the contract.
        
        Args:
            event: The capital call event that was processed
        """
        # TODO: Implement domain event publishing in Phase 4
        # Examples of events to publish:
        # - EquityBalanceChangedEvent
        # - CapitalCallRecordedEvent
        # - FundSummaryUpdatedEvent
        pass
