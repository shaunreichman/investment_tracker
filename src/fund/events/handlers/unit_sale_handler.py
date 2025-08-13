"""
Unit Sale Event Handler.

This module provides the handler for processing unit sale events.
It handles validation, event creation, and fund updates for unit sales.
"""

from typing import Dict, Any
from datetime import date

from ..base_handler import BaseFundEventHandler
from ...enums import EventType, FundType
from ...models import FundEvent


class UnitSaleHandler(BaseFundEventHandler):
    """
    Handler for unit sale events.
    
    This handler processes unit sale events for NAV-based funds.
    It handles validation, event creation, and fund updates for unit sales.
    """
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate unit sale event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        # Validate fund type
        self._validate_fund_type(FundType.NAV_BASED)
        
        # Validate required fields
        units = event_data.get('units')
        price = event_data.get('price')
        event_date = self._parse_date(event_data.get('date')) if event_data.get('date') else None
        
        self._validate_positive_amount(units, 'units')
        self._validate_positive_amount(price, 'price')
        self._validate_required_date(event_date, 'date')
        
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
        
        # Validate that we have enough units to sell
        self._validate_sufficient_units(units)
    
    def _validate_sufficient_units(self, units_to_sell: float) -> None:
        """
        Validate that the fund has sufficient units to sell.
        
        Args:
            units_to_sell: Number of units to sell
            
        Raises:
            ValueError: If insufficient units available
        """
        # Calculate total available units
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
        
        # Check if we have enough units
        if total_units < units_to_sell:
            raise ValueError(
                f"Insufficient units available. "
                f"Requested: {units_to_sell}, Available: {total_units:.2f}"
            )
    
    def handle(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Handle a unit sale event.
        
        This method:
        1. Validates the event data
        2. Checks for duplicate events (idempotent behavior)
        3. Creates the unit sale event
        4. Updates fund state
        5. Publishes domain events
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: The created unit sale event
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        # Validate event data
        self.validate_event(event_data)
        
        # Extract parameters
        units = float(event_data['units'])
        price = float(event_data['price'])
        event_date = self._parse_date(event_data['date'])
        brokerage_fee = float(event_data.get('brokerage_fee', 0.0))
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        # Calculate total amount (brokerage fee reduces the amount)
        amount = (units * price) - brokerage_fee
        
        # Check for existing duplicate event (idempotent behavior)
        existing_event = self._check_duplicate_event(
            EventType.UNIT_SALE,
            event_date=event_date,
            units_sold=units,
            unit_price=price,
            reference_number=reference_number
        )
        
        if existing_event:
            # Return existing event without creating duplicate
            return existing_event
        
        # Create unit sale event
        event = self._create_event(
            EventType.UNIT_SALE,
            event_date=event_date,
            units_sold=units,
            unit_price=price,
            brokerage_fee=brokerage_fee,
            amount=amount,
            description=description or f"Unit sale: {units} units @ ${price:,.2f}",
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
        Update fund state after a unit sale event.
        
        Args:
            event: The unit sale event that was created
        """
        # Use the existing fund method to recalculate capital chain
        # This maintains compatibility with existing logic while
        # providing a clean interface through the handler
        self.fund.recalculate_capital_chain_from(event, session=self.session)
        
        # Update fund summary fields
        self._update_fund_summary_fields()
        
        # Update current units if this is the latest unit event
        self._update_current_units(event)
    
    def _update_current_units(self, event: FundEvent) -> None:
        """
        Update current units on the fund.
        
        Args:
            event: The unit sale event that was created
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
        
        # Update NAV total if current unit price is available
        if hasattr(self.fund, 'current_unit_price') and self.fund.current_unit_price:
            self.fund.current_nav_total = self.fund.current_units * self.fund.current_unit_price
    
    def _publish_dependent_events(self, event: FundEvent) -> None:
        """
        Publish domain events for dependent updates.
        
        This method will be implemented in Phase 4 when we add
        the full domain event system. For now, it's a placeholder
        that maintains the contract.
        
        Args:
            event: The unit sale event that was processed
        """
        # TODO: Implement domain event publishing in Phase 4
        # Examples of events to publish:
        # - UnitsChangedEvent
        # - EquityBalanceChangedEvent
        # - FundSummaryUpdatedEvent
        pass
