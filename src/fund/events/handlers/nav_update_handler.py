"""
NAV Update Event Handler.

This module provides the handler for processing NAV update events.
It handles validation, event creation, and fund updates for NAV updates.
"""

from typing import Dict, Any, Optional
from datetime import date

from ..base_handler import BaseFundEventHandler
from ...enums import EventType, FundType
from ...models import FundEvent


class NAVUpdateHandler(BaseFundEventHandler):
    """
    Handler for NAV update events.
    
    This handler processes NAV update events for NAV-based funds.
    It handles validation, event creation, and updates to subsequent
    NAV events to maintain consistency.
    """
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate NAV update event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        # Validate fund type
        self._validate_fund_type(FundType.NAV_BASED)
        
        # Validate required fields
        nav_per_share = event_data.get('nav_per_share')
        event_date = event_data.get('date')
        
        if not nav_per_share:
            raise ValueError("nav_per_share is required")
        
        try:
            nav_value = float(nav_per_share)
            if nav_value <= 0:
                raise ValueError("nav_per_share must be positive")
        except (ValueError, TypeError):
            raise ValueError("nav_per_share must be a valid positive number")
        
        self._validate_required_date(event_date, 'date')
    
    def handle(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Handle a NAV update event.
        
        This method:
        1. Validates the event data
        2. Checks for duplicate events (idempotent behavior)
        3. Creates the NAV update event
        4. Updates fund state
        5. Updates subsequent NAV events if needed
        6. Publishes domain events
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: The created NAV update event
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        # Validate event data
        self.validate_event(event_data)
        
        # Extract parameters
        nav_per_share = float(event_data['nav_per_share'])
        event_date = event_data['date']
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        # Check for existing duplicate event (idempotent behavior)
        existing_event = self._check_duplicate_event(
            EventType.NAV_UPDATE,
            event_date=event_date,
            reference_number=reference_number
        )
        
        if existing_event:
            # Return existing event without creating duplicate
            return existing_event
        
        # Calculate NAV change fields
        previous_nav, nav_change_absolute, nav_change_percentage = self._calculate_nav_change_fields(
            nav_per_share, event_date
        )
        
        # Create NAV update event
        event = self._create_event(
            EventType.NAV_UPDATE,
            event_date=event_date,
            nav_per_share=nav_per_share,
            previous_nav_per_share=previous_nav,
            nav_change_absolute=nav_change_absolute,
            nav_change_percentage=nav_change_percentage,
            description=description or f"NAV update: ${nav_per_share:.4f}",
            reference_number=reference_number
        )
        
        # Update fund state
        self._update_fund_after_nav_event(event)
        
        # Update subsequent NAV events if needed
        self._update_subsequent_nav_events(event)
        
        # Publish domain events
        self._publish_dependent_events(event)
        
        return event
    
    def _calculate_nav_change_fields(self, nav_per_share: float, event_date: date) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate NAV change fields for the event.
        
        Args:
            nav_per_share: New NAV per share
            event_date: Date of the NAV update
            
        Returns:
            tuple: (previous_nav, nav_change_absolute, nav_change_percentage)
        """
        # Get the previous NAV event for this fund
        previous_event = self.session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund.id,
            FundEvent.event_type == EventType.NAV_UPDATE,
            FundEvent.event_date < event_date
        ).order_by(FundEvent.event_date.desc(), FundEvent.id.desc()).first()
        
        if not previous_event:
            # This is the first NAV update
            return None, None, None
        
        previous_nav = previous_event.nav_per_share
        nav_change_absolute = nav_per_share - previous_nav
        nav_change_percentage = (nav_change_absolute / previous_nav) * 100 if previous_nav else 0.0
        
        return previous_nav, nav_change_absolute, nav_change_percentage
    
    def _update_fund_after_nav_event(self, event: FundEvent) -> None:
        """
        Update fund state after a NAV update event.
        
        Args:
            event: The NAV update event that was created
        """
        # Check if this is the latest NAV update event
        latest_event = self.session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund.id,
            FundEvent.event_type == EventType.NAV_UPDATE
        ).order_by(FundEvent.event_date.desc(), FundEvent.id.desc()).first()
        
        if latest_event and latest_event.id == event.id:
            # This is the latest NAV update, update fund fields
            self.fund.current_unit_price = event.nav_per_share
            
            # Update NAV total if units are available
            if hasattr(self.fund, 'current_units') and self.fund.current_units:
                self.fund.current_nav_total = self.fund.current_units * event.nav_per_share
    
    def _update_subsequent_nav_events(self, event: FundEvent) -> None:
        """
        Update subsequent NAV events to maintain consistency.
        
        Args:
            event: The NAV update event that was created
        """
        # Find subsequent NAV events that need their change fields updated
        subsequent_events = self.session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund.id,
            FundEvent.event_type == EventType.NAV_UPDATE,
            FundEvent.event_date > event.event_date
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        for subsequent_event in subsequent_events:
            # Recalculate change fields for this subsequent event
            previous_event = self.session.query(FundEvent).filter(
                FundEvent.fund_id == self.fund.id,
                FundEvent.event_type == EventType.NAV_UPDATE,
                FundEvent.event_date < subsequent_event.event_date
            ).order_by(FundEvent.event_date.desc(), FundEvent.id.desc()).first()
            
            if previous_event:
                # Update the subsequent event's change fields
                nav_change_absolute = subsequent_event.nav_per_share - previous_event.nav_per_share
                nav_change_percentage = (nav_change_absolute / previous_event.nav_per_share) * 100 if previous_event.nav_per_share else 0.0
                
                subsequent_event.previous_nav_per_share = previous_event.nav_per_share
                subsequent_event.nav_change_absolute = nav_change_absolute
                subsequent_event.nav_change_percentage = nav_change_percentage
    
    def _publish_dependent_events(self, event: FundEvent) -> None:
        """
        Publish domain events for dependent updates.
        
        This method will be implemented in Phase 4 when we add
        the full domain event system. For now, it's a placeholder
        that maintains the contract.
        
        Args:
            event: The NAV update event that was processed
        """
        # TODO: Implement domain event publishing in Phase 4
        # Examples of events to publish:
        # - NAVUpdatedEvent
        # - FundSummaryUpdatedEvent
        # - UnitsValueChangedEvent
        pass
