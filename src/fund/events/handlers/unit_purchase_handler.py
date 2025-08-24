"""
Unit Purchase Event Handler.

This handler processes unit purchase events for NAV-based funds,
updating unit counts and triggering dependent calculations.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date

logger = logging.getLogger(__name__)

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, FundType
from src.fund.models import FundEvent
from src.fund.services.fund_calculation_service import FundCalculationService


class UnitPurchaseHandler(BaseFundEventHandler):
    """
    Handler for unit purchase events.
    
    This handler processes unit purchase events for NAV-based funds.
    It handles validation, event creation, and fund updates for unit purchases.
    """
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate unit purchase event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        # Validate fund type
        self._validate_fund_type(FundType.NAV_BASED)
        
        # Validate required fields
        units = event_data.get('units_purchased')
        price = event_data.get('unit_price')
        event_date = self._parse_date(event_data.get('event_date')) if event_data.get('event_date') else None
        
        self._validate_positive_amount(units, 'units')
        self._validate_positive_amount(price, 'price')
        self._validate_required_date(event_date, 'event_date')
        
        # Validate units and price are numeric
        try:
            float(units)
            float(price)
        except (ValueError, TypeError):
            raise ValueError("Units and price must be valid numbers")
        
        # Validate brokerage fee if provided
        brokerage_fee = event_data.get('brokerage_fee', 0.0)
        if brokerage_fee is not None:
            try:
                fee = float(brokerage_fee)
                if fee < 0:
                    raise ValueError("Brokerage fee cannot be negative")
            except (ValueError, TypeError):
                raise ValueError("Brokerage fee must be a valid number")
    
    def handle(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Handle a unit purchase event.
        
        This method:
        1. Validates the event data
        2. Checks for duplicate events (idempotent behavior)
        3. Creates the unit purchase event
        4. Updates fund state
        5. Publishes domain events
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: The created unit purchase event
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        # Validate event data
        self.validate_event(event_data)
        
        # Validate first event business rules
        self._validate_first_event(EventType.UNIT_PURCHASE)
        
        # Extract parameters
        units = float(event_data['units_purchased'])
        price = float(event_data['unit_price'])
        event_date = self._parse_date(event_data['event_date'])
        brokerage_fee = float(event_data.get('brokerage_fee', 0.0))
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        # Calculate total amount
        amount = (units * price) + brokerage_fee
        
        # Check for existing duplicate event (idempotent behavior)
        existing_event = self._check_duplicate_event(
            EventType.UNIT_PURCHASE,
            event_date=event_date,
            units_purchased=units,
            unit_price=price,
            reference_number=reference_number
        )
        
        if existing_event:
            # Return existing event without creating duplicate
            return existing_event
        
        # Create unit purchase event
        event = self._create_event(
            EventType.UNIT_PURCHASE,
            event_date=event_date,
            units_purchased=units,
            unit_price=price,
            brokerage_fee=brokerage_fee,
            amount=amount,
            description=description or f"Unit purchase: {units} units @ ${price:,.2f}",
            reference_number=reference_number
        )
        
        # Update fund state
        self._update_fund_after_unit_event(event)
        
        # Publish domain events
        self._publish_dependent_events(event)
        
        # Handle status transitions if needed
        self._handle_status_transition(event)
        
        return event
    
    def _update_fund_after_unit_event(self, event: FundEvent) -> None:
        """
        Update fund state after a unit purchase event.
        
        This method handles the complex logic of updating fund state
        after a capital event, including:
        - Publishing capital chain recalculation events
        - Updating summary fields
        - Maintaining data consistency
        
        Args:
            event: The unit purchase event that was created
        """
        # First, update the event's equity balance fields using the calculation service
        self._update_event_equity_fields(event)
        
        # Then publish the capital chain recalculation event
        self._publish_capital_chain_event(event)
        
        # Finally, update fund summary fields
        self._update_fund_summary_fields(event)
        
        # Update current units if this is the latest unit event
        self._update_current_units(event)
    
    def _update_event_equity_fields(self, event: FundEvent) -> None:
        """
        Update the event's equity balance fields using the calculation service.
        
        This ensures the event has the correct equity balance before publishing
        the capital chain recalculation event.
        
        Args:
            event: The unit purchase event to update
        """
        try:
            # Get all unit events for this fund, ordered by date and ID
            unit_events = self.session.query(FundEvent).filter(
                FundEvent.fund_id == self.fund.id,
                FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
            ).order_by(FundEvent.event_date, FundEvent.id).all()
            
            if not unit_events:
                # This is the first unit event
                event.current_equity_balance = (event.units_purchased or 0.0) * (event.unit_price or 0.0)
                event.units_owned = event.units_purchased or 0.0
                return
            
            # Find the index of this event in the ordered list
            event_index = None
            for i, e in enumerate(unit_events):
                if e.id == event.id:
                    event_index = i
                    break
            
            if event_index is None:
                # Event not found in the list (shouldn't happen)
                logger.warning(f"Event {event.id} not found in unit events list")
                return
            
            # Use the calculation service to calculate equity balance
            calc_service = FundCalculationService()
            calc_service.calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(
                self.fund, unit_events, event_index, self.session
            )
            
            # The calculation service should have updated the event's fields
            logger.debug(f"Updated equity balance fields for event {event.id}")
            
        except Exception as e:
            logger.error(f"Error updating event equity fields: {e}")
            raise
    
    def _publish_capital_chain_event(self, event: FundEvent) -> None:
        """
        Publish capital chain recalculation event.
        
        Args:
            event: The unit purchase event that was created
        """
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
                trigger_event_type="UNIT_PURCHASE",
                old_equity_balance=old_equity_balance,
                new_equity_balance=event.current_equity_balance,
                change_reason=f"Capital chain recalculation after unit purchase: ${event.amount:,.2f}",
                metadata={
                    "event_amount": event.amount,
                    "event_description": event.description,
                    "reference_number": event.reference_number
                }
            )
            
            event_bus.publish(capital_event, self.session)
            
            logger.info(f"Published capital chain recalculation event for fund {self.fund.id}")
            
        except Exception as e:
            logger.error(f"Error publishing capital chain recalculation event: {e}")
            raise
    
    def _update_current_units(self, event: FundEvent) -> None:
        """
        Update current units on the fund.
        
        Args:
            event: The unit purchase event that was created
        """
        # Calculate total units from all unit events
        total_units = 0.0
        
        # Get all unit purchase events
        purchase_events = self.session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund.id,
            FundEvent.event_type == EventType.UNIT_PURCHASE
        ).all()
        
        for purchase_event in purchase_events:
            total_units += purchase_event.units_purchased or 0.0
        
        # Get all unit sale events
        sale_events = self.session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund.id,
            FundEvent.event_type == EventType.UNIT_SALE
        ).all()
        
        for sale_event in sale_events:
            total_units -= sale_event.units_sold or 0.0
        
        # Update fund current units
        self.fund.current_units = max(0.0, total_units)
        
        # Calculate weighted average unit price for NAV-based funds
        if total_units > 0:
            total_cost = 0.0
            
            # Calculate total cost from all unit purchase events
            for purchase_event in purchase_events:
                units = purchase_event.units_purchased or 0.0
                price = purchase_event.unit_price or 0.0
                total_cost += units * price
            
            # Update unit price to weighted average
            self.fund.current_unit_price = total_cost / total_units
            
            # Update NAV total
            self.fund.current_nav_total = self.fund.current_units * self.fund.current_unit_price
    
    def _publish_dependent_events(self, event: FundEvent) -> None:
        """
        Publish domain events for dependent updates.
        
        This method creates and stores domain events for significant
        state changes, enabling loose coupling between components.
        
        Args:
            event: The unit purchase event that was processed
        """
        # Call the base class implementation which handles all domain event creation
        super()._publish_dependent_events(event)
