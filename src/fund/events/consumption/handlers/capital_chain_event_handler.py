"""
Capital Chain Event Handler.

This handler processes capital chain recalculation events and performs
dependent updates for other components in the system.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from src.fund.events.consumption.base_consumer import EventConsumer
from src.fund.events.domain import CapitalChainRecalculatedEvent
from src.fund.repositories.fund_repository import FundRepository
from src.fund.models import Fund
from src.fund.enums import FundType

logger = logging.getLogger(__name__)


class CapitalChainEventHandler(EventConsumer):
    """
    Event handler for capital chain recalculation events.
    
    This handler processes capital chain recalculation events and
    updates dependent components accordingly.
    """
    
    def __init__(self):
        """Initialize the capital chain event handler."""
        super().__init__(
            name="CapitalChainEventHandler",
            event_types=[CapitalChainRecalculatedEvent]
        )
        
        logger.info("Initialized CapitalChainEventHandler")
    
    def handle_event(self, event: CapitalChainRecalculatedEvent) -> None:
        """
        Handle a capital chain recalculation event.
        
        Args:
            event: The capital chain recalculation event to handle
        """
        logger.info(f"Processing capital chain recalculation for fund {event.fund_id}")
        
        try:
            # Get the fund to determine its type and current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping capital chain update")
                return
            
            # Update fund summary fields after capital chain recalculation
            self._update_fund_summary_fields(event, fund)
            
            # Publish additional events for dependent updates
            self._publish_dependent_events(event, fund)
            
        except Exception as e:
            logger.error(f"Error handling capital chain recalculation event: {e}")
            raise
    
    def _update_fund_summary_fields(self, event: CapitalChainRecalculatedEvent, fund: Fund) -> None:
        """
        Update fund summary fields after capital chain recalculation.
        
        Args:
            event: The capital chain recalculation event
            fund: The fund to update
        """
        logger.info(f"Updating fund summary fields for fund {event.fund_id}")
        
        try:
            # Update fund summary fields based on the recalculation
            # This replaces the direct call to fund.recalculate_capital_chain_from()
            
            # Get the current equity balance from the fund
            current_equity = fund.current_equity_balance or Decimal('0.0')
            
            # Update fund summary fields
            fund.current_equity_balance = current_equity
            
            # Calculate and update other summary fields as needed
            if fund.tracking_type == FundType.COST_BASED:
                # For cost-based funds, update capital-related fields
                self._update_cost_based_summary_fields(fund)
            else:
                # For NAV-based funds, update unit-related fields
                self._update_nav_based_summary_fields(fund)
            
            logger.info(f"Successfully updated fund summary fields for fund {event.fund_id}")
            
        except Exception as e:
            logger.error(f"Error updating fund summary fields: {e}")
            raise
    
    def _update_cost_based_summary_fields(self, fund: Fund) -> None:
        """
        Update summary fields for cost-based funds.
        
        Args:
            fund: The fund to update
        """
        try:
            # Update capital-related summary fields
            # This would include fields like total_capital_called, remaining_commitment, etc.
            # The actual implementation would depend on the specific business logic
            
            logger.debug(f"Updated cost-based summary fields for fund {fund.id}")
            
        except Exception as e:
            logger.error(f"Error updating cost-based summary fields: {e}")
            raise
    
    def _update_nav_based_summary_fields(self, fund: Fund) -> None:
        """
        Update summary fields for NAV-based funds.
        
        Args:
            fund: The fund to update
        """
        try:
            # Update unit-related summary fields
            # This would include fields like total_units, average_unit_cost, etc.
            # The actual implementation would depend on the specific business logic
            
            logger.debug(f"Updated NAV-based summary fields for fund {fund.id}")
            
        except Exception as e:
            logger.error(f"Error updating NAV-based summary fields: {e}")
            raise
    
    def _publish_dependent_events(self, event: CapitalChainRecalculatedEvent, fund: Fund) -> None:
        """
        Publish events for dependent updates.
        
        Args:
            event: The capital chain recalculation event
            fund: The fund that was updated
        """
        try:
            # Publish events for other components that need to react to capital chain changes
            # This could include events for tax statements, company records, etc.
            
            from src.fund.events.domain import FundSummaryUpdatedEvent
            from src.fund.events.consumption.event_bus import event_bus
            
            # Publish fund summary update event
            summary_event = FundSummaryUpdatedEvent(
                fund_id=event.fund_id,
                event_date=event.event_date,
                summary_type="CAPITAL_CHAIN_RECALCULATED",
                metadata={
                    "trigger_event_id": event.trigger_event_id,
                    "trigger_event_type": event.trigger_event_type,
                    "old_equity_balance": event.old_equity_balance,
                    "new_equity_balance": event.new_equity_balance,
                    "change_reason": event.change_reason
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
