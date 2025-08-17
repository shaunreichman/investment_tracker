"""
Fund Status Event Handler.

This handler processes fund status update events and performs
dependent updates for other components in the system.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from sqlalchemy.orm import Session

from src.fund.events.consumption.base_consumer import EventConsumer
from src.fund.events.domain import FundStatusUpdateEvent
from src.fund.repositories.fund_repository import FundRepository
from src.fund.models import Fund
from src.fund.enums import FundStatus

logger = logging.getLogger(__name__)


class FundStatusEventHandler(EventConsumer):
    """
    Event handler for fund status update events.
    
    This handler processes fund status update events and
    updates dependent components accordingly.
    """
    
    def __init__(self):
        """Initialize the fund status event handler."""
        super().__init__(
            name="FundStatusEventHandler",
            event_types=[FundStatusUpdateEvent]
        )
        
        logger.info("Initialized FundStatusEventHandler")
    
    def handle_event(self, event: FundStatusUpdateEvent) -> None:
        """
        Handle a fund status update event.
        
        Args:
            event: The fund status update event to handle
        """
        logger.info(f"Processing fund status update for fund {event.fund_id}")
        
        try:
            # Get the fund to determine its current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping status update")
                return
            
            # Update fund status based on the event
            self._update_fund_status(event, fund)
            
            # Publish additional events for dependent updates
            self._publish_dependent_events(event, fund)
            
        except Exception as e:
            logger.error(f"Error handling fund status update event: {e}")
            raise
    
    def _update_fund_status(self, event: FundStatusUpdateEvent, fund: Fund) -> None:
        """
        Update fund status based on the event.
        
        Args:
            event: The fund status update event
            fund: The fund to update
        """
        logger.info(f"Updating fund status for fund {event.fund_id}")
        
        try:
            # Update fund status based on the event
            # This replaces the direct call to fund.status_service.update_status_after_tax_statement()
            
            # Set the new status
            fund.status = event.new_status
            
            # Handle status-specific logic
            if event.new_status == FundStatus.COMPLETED:
                # Fund is completed, trigger final calculations
                self._handle_fund_completion(event, fund)
            elif event.new_status == FundStatus.REALIZED:
                # Fund is realized, trigger IRR calculations
                self._handle_fund_realization(event, fund)
            elif event.new_status == FundStatus.ACTIVE:
                # Fund is active, ensure proper state
                self._handle_fund_active(event, fund)
            
            logger.info(f"Successfully updated fund status to {event.new_status} for fund {event.fund_id}")
            
        except Exception as e:
            logger.error(f"Error updating fund status: {e}")
            raise
    
    def _handle_fund_completion(self, event: FundStatusUpdateEvent, fund: Fund) -> None:
        """
        Handle fund completion status.
        
        Args:
            event: The fund status update event
            fund: The fund that was completed
        """
        try:
            # Handle fund completion logic
            # This could include final calculations, notifications, etc.
            
            logger.info(f"Fund {fund.id} completed, processing final calculations")
            
            # Trigger final IRR calculations if needed
            if hasattr(fund, 'calculate_final_irr'):
                fund.calculate_final_irr()
            
        except Exception as e:
            logger.error(f"Error handling fund completion: {e}")
            raise
    
    def _handle_fund_realization(self, event: FundStatusUpdateEvent, fund: Fund) -> None:
        """
        Handle fund realization status.
        
        Args:
            event: The fund status update event
            fund: The fund that was realized
        """
        try:
            # Handle fund realization logic
            # This could include IRR calculations, tax statement updates, etc.
            
            logger.info(f"Fund {fund.id} realized, processing IRR calculations")
            
            # Trigger IRR calculations if needed
            if hasattr(fund, 'calculate_irr'):
                fund.calculate_irr()
            
        except Exception as e:
            logger.error(f"Error handling fund realization: {e}")
            raise
    
    def _handle_fund_active(self, event: FundStatusUpdateEvent, fund: Fund) -> None:
        """
        Handle fund active status.
        
        Args:
            event: The fund status update event
            fund: The fund that is active
        """
        try:
            # Handle fund active logic
            # This could include validation, state checks, etc.
            
            logger.info(f"Fund {fund.id} is active, ensuring proper state")
            
            # Validate fund state
            self._validate_fund_state(fund)
            
        except Exception as e:
            logger.error(f"Error handling fund active: {e}")
            raise
    
    def _validate_fund_state(self, fund: Fund) -> None:
        """
        Validate fund state for active funds.
        
        Args:
            fund: The fund to validate
        """
        try:
            # Validate that active funds have proper state
            # This could include checks for required fields, etc.
            
            if not fund.start_date:
                logger.warning(f"Active fund {fund.id} missing start date")
            
            if not fund.investment_company_id:
                logger.warning(f"Active fund {fund.id} missing investment company")
            
        except Exception as e:
            logger.error(f"Error validating fund state: {e}")
            raise
    
    def _publish_dependent_events(self, event: FundStatusUpdateEvent, fund: Fund) -> None:
        """
        Publish events for dependent updates.
        
        Args:
            event: The fund status update event
            fund: The fund that was updated
        """
        try:
            # Import domain events
            from src.fund.events.domain import FundSummaryUpdatedEvent
            from src.fund.events.consumption.event_bus import event_bus
            
            # Publish fund summary update event
            summary_event = FundSummaryUpdatedEvent(
                fund_id=event.fund_id,
                event_date=event.event_date,
                summary_type="FUND_STATUS_UPDATED",
                metadata={
                    "old_status": event.old_status,
                    "new_status": event.new_status,
                    "update_reason": event.update_reason,
                    "trigger_event_id": event.trigger_event_id,
                    "trigger_event_type": event.trigger_event_type
                }
            )
            
            event_bus.publish(summary_event, self.session)
            logger.info(f"Published fund summary update event for fund {event.fund_id}")
            
        except Exception as e:
            logger.error(f"Error publishing dependent events: {e}")
            raise
    
    def _get_fund(self, fund_id: int) -> Optional[Fund]:
        """
        Get fund information for the given fund ID.
        
        Args:
            fund_id: ID of the fund to retrieve
            
        Returns:
            Fund object if found, None otherwise
        """
        if not self.session:
            logger.error("No database session available for retrieving fund")
            return None
            
        try:
            # Use the session to query for the fund
            fund = self.session.query(Fund).filter(Fund.id == fund_id).first()
            return fund
            
        except Exception as e:
            logger.error(f"Error retrieving fund {fund_id}: {e}")
            return None
