"""
Capital Call Event Handler.

This handler processes capital call events for cost-based funds,
updating equity balance and triggering dependent calculations.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date

logger = logging.getLogger(__name__)

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, FundType
from src.fund.models import FundEvent
from src.fund.repositories.fund_event_repository import FundEventRepository

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
        event_date = event_data.get('event_date')
        
        self._validate_positive_amount(amount, 'amount')
        self._validate_required_date(event_date, 'event_date')
        
        # Validate amount is numeric
        try:
            float(amount)
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid number")
    
    def handle_create_event(self, event_data: Dict[str, Any]) -> FundEvent:
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
        # Event validation is handled by the service layer
        
        # Extract parameters
        amount = float(event_data['amount'])
        event_date = self._parse_date(event_data['event_date'])
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        # Get the existing event (created by service)
        event_id = event_data.get('event_id')
        if not event_id:
            raise ValueError("event_id is required - event should be created by service first")
        
        # Event already created by service, get it from database using the repository layer
        fund_event_repository = FundEventRepository(self.session)
        event = fund_event_repository.get_event_by_id(event_id)
        if not event:
            raise ValueError(f"Event with id {event_id} not found - event should be created by service first")
        
        # Update fund state
        self._update_fund_after_capital_event(event)
        
        # Publish domain events
        self._publish_dependent_events(event)
        
        # Handle status transitions if needed
        self._handle_status_transition(event)
        
        return event

    def handle_delete_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Handle a capital call event deletion.
        
        Args:
            event_data: Dictionary containing event parameters

        Returns:
            bool: True if the event was deleted successfully

        Raises:
            ValueError: If event data is invalid
        """
        event_id = event_data.get('event_id')
        if not event_id:
            raise ValueError("event_id is required - event should have existed first before deletion")
        
        fund_event_repository = FundEventRepository(self.session)
        if fund_event_repository.get_event_by_id(event_id):
            raise ValueError(f"Event with id {event_id} still exists - event should have been deleted first")
        
        return True
    
    def _update_fund_after_capital_event(self, event: FundEvent) -> None:
        """
        Update fund state after a capital call event.
        
        This method handles the complex logic of updating fund state
        after a capital event, including:
        - Publishing capital chain recalculation events
        - Updating summary fields
        - Maintaining data consistency
        
        Args:
            event: The capital call event that was created
        """
        # First, update the event's equity balance fields using the calculation service
        self._update_event_equity_fields(event)
        
        # Then publish the capital chain recalculation event
        self._publish_capital_chain_event(event)
        
        # Finally, update fund summary fields
        self._update_fund_summary_fields(event)
    
    def _update_event_equity_fields(self, event: FundEvent) -> None:
        """
        Update the event's equity balance fields using the calculation service.
        
        This ensures the event has the correct equity balance before publishing
        the capital chain recalculation event.
        
        Args:
            event: The capital call event to update
        """
        # Get all capital events for this fund, ordered by date and ID
        capital_events = self.session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund.id,
            FundEvent.event_type.in_([EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL])
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        if not capital_events:
            # This is the first capital event
            event.current_equity_balance = event.amount or 0.0
            return
        
        # Find the index of this event in the ordered list
        event_index = None
        for i, e in enumerate(capital_events):
            if e.id == event.id:
                event_index = i
                break
        
        if event_index is None:
            # Event not found in the list (shouldn't happen)
            return
        
        # Use the new FundEquityService to update equity fields efficiently
        from src.fund.services.fund_equity_service import FundEquityService
        equity_service = FundEquityService(self.session)
        equity_service.update_fund_equity_fields(self.fund)
    
    def _publish_capital_chain_event(self, event: FundEvent) -> None:
        """
        Publish capital chain recalculation event.
        
        Args:
            event: The capital call event that was created
        """
        # Publish capital chain recalculation event
        from src.fund.events.domain import CapitalChainRecalculatedEvent
        from src.fund.events.consumption.event_bus import event_bus
        
        # Get old equity balance before the event
        old_equity_balance = self.fund.current_equity_balance
        
        # Publish capital chain recalculation event
        capital_event = CapitalChainRecalculatedEvent(
            fund_id=self.fund.id,
            event_date=event.event_date,
            trigger_event_id=event.id,
            trigger_event_type="CAPITAL_CALL",
            old_equity_balance=old_equity_balance,
            new_equity_balance=event.current_equity_balance,
            change_reason=f"Capital chain recalculation after capital call: ${event.amount:,.2f}",
            metadata={
                "event_amount": event.amount,
                "event_description": event.description,
                "reference_number": event.reference_number
            }
        )
        
        event_bus.publish(capital_event, self.session)
    
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
