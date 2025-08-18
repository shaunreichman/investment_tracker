"""
Return of Capital Event Handler.

This handler processes return of capital events for cost-based funds,
updating equity balances and triggering dependent calculations.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, FundType
from src.fund.models import FundEvent


class ReturnOfCapitalHandler(BaseFundEventHandler):
    """
    Handler for return of capital events.
    
    This handler processes return of capital events for cost-based funds.
    It validates the event data, creates the event, and updates
    fund state as needed.
    """
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate return of capital event data.
        
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
        Handle a return of capital event.
        
        This method:
        1. Validates the event data
        2. Checks for duplicate events (idempotent behavior)
        3. Creates the return of capital event
        4. Updates fund state
        5. Publishes domain events
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: The created return of capital event
            
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
            EventType.RETURN_OF_CAPITAL,
            event_date=event_date,
            amount=amount,
            reference_number=reference_number
        )
        
        if existing_event:
            # Return existing event without creating duplicate
            return existing_event
        
        # Create new return of capital event
        event = self._create_event(
            EventType.RETURN_OF_CAPITAL,
            event_date=event_date,
            amount=amount,
            description=description or f"Return of capital: ${amount:,.2f}",
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
        Update fund state after a return of capital event.
        
        This method handles the complex logic of updating fund state
        after a capital event, including:
        - Publishing capital chain recalculation events
        - Updating summary fields
        - Maintaining data consistency
        
        Args:
            event: The return of capital event that was created
        """
        # Instead of direct model calls, publish events for loose coupling
        # This replaces: self.fund.recalculate_capital_chain_from(event, session=self.session)
        
        try:
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
                trigger_event_type="RETURN_OF_CAPITAL",
                old_equity_balance=old_equity_balance,
                new_equity_balance=None,  # Will be calculated by event handler
                change_reason=f"Capital chain recalculation after return of capital: ${event.amount:,.2f}",
                metadata={
                    "event_amount": event.amount,
                    "event_description": event.description,
                    "reference_number": event.reference_number
                }
            )
            
            event_bus.publish(capital_event, self.session)
            
            self.logger.info(f"Published capital chain recalculation event for fund {self.fund.id}")
            
        except Exception as e:
            self.logger.error(f"Error publishing capital chain recalculation event: {e}")
            raise
        
        # Update fund summary fields
        self._update_fund_summary_fields()
    
    def _publish_dependent_events(self, event: FundEvent) -> None:
        """
        Publish domain events for dependent updates.
        
        This method creates and stores domain events for significant
        state changes, enabling loose coupling between components.
        
        Args:
            event: The return of capital event that was processed
        """
        # Call the base class implementation which handles all domain event creation
        super()._publish_dependent_events(event)
