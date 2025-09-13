"""
NAV Update Event Handler.

This handler processes NAV update events for NAV-based funds,
updating unit prices and triggering dependent calculations.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, FundType
from src.fund.models import FundEvent
from src.fund.repositories.fund_event_repository import FundEventRepository


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
        event_date = event_data.get('event_date')
        
        if not nav_per_share:
            raise ValueError("nav_per_share is required")
        
        try:
            nav_value = float(nav_per_share)
            if nav_value <= 0:
                raise ValueError("nav_per_share must be positive")
        except (ValueError, TypeError):
            raise ValueError("nav_per_share must be a valid positive number")
        
        self._validate_required_date(event_date, 'event_date')
    
    def handle_create_event(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Handle a NAV update event.
        
        This method:
        1. Gets the existing event (created by service)
        2. Updates fund state
        3. Updates subsequent NAV events if needed
        4. Publishes domain events
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: The NAV update event
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        # Event validation is handled by the service layer
        
        # Extract parameters
        nav_per_share = float(event_data['nav_per_share'])
        event_date = self._parse_date(event_data['event_date'])
        description = event_data.get('description')
        reference_number = event_data.get('reference_number')
        
        # Get the existing event (created by service)
        event_id = event_data.get('event_id')
        if not event_id:
            raise ValueError("event_id is required - event should be created by service first")
        
        # Event already created by service, get it from database
        fund_event_repository = FundEventRepository(self.session)
        event = fund_event_repository.get_event_by_id(event_id)
        if not event:
            raise ValueError(f"Event with id {event_id} not found - event should be created by service first")
        
        # Update fund state (side effects only - no session management)
        self._update_fund_after_nav_event(event)
        
        # Update subsequent NAV events if needed
        self._update_subsequent_nav_events(event)
        
        # Publish domain events
        self._publish_dependent_events(event)
        
        return event

    def handle_delete_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Handle a NAV update event deletion.
        
        Args:
            event_data: Dictionary containing event parameters
        """
        event_id = event_data.get('event_id')
        if not event_id:
            raise ValueError("event_id is required - event should have existed first before deletion")
        
        # We need to confirm the event doesn't exist anymore by calling the repository layer
        fund_event_repository = FundEventRepository(self.session)
        if fund_event_repository.get_event_by_id(event_id):
            raise ValueError(f"Event with id {event_id} still exists - event should have been deleted first")
        
        return True
    
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
        
        This method creates and stores domain events for significant
        state changes, enabling loose coupling between components.
        
        Args:
            event: The NAV update event that was processed
        """
        # Call the base class implementation which handles all domain event creation
        super()._publish_dependent_events(event)
