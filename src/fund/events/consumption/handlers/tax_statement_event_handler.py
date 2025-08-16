"""
Tax Statement Event Handler.

This module provides the event handler for updating tax statements
based on fund events. It handles events like equity balance changes,
distributions, and NAV updates to maintain tax statement consistency.
"""

import logging
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..base_consumer import EventConsumer
from ...domain import (
    EquityBalanceChangedEvent,
    DistributionRecordedEvent,
    NAVUpdatedEvent,
    TaxStatementUpdatedEvent
)
from ....repositories.tax_statement_repository import TaxStatementRepository
from ....repositories.fund_repository import FundRepository
from ....models import Fund
from ....enums import FundType

logger = logging.getLogger(__name__)


class TaxStatementEventHandler(EventConsumer):
    """
    Event handler for tax statement updates.
    
    This handler processes fund-related events and updates tax statements
    accordingly to maintain consistency across the system.
    """
    
    def __init__(self):
        """Initialize the tax statement event handler."""
        super().__init__(
            name="TaxStatementEventHandler",
            event_types=[
                EquityBalanceChangedEvent,
                DistributionRecordedEvent,
                NAVUpdatedEvent,
                TaxStatementUpdatedEvent
            ]
        )
        
        logger.info("Initialized TaxStatementEventHandler")
    
    def handle_event(self, event) -> None:
        """
        Handle a domain event and update tax statements accordingly.
        
        Args:
            event: The domain event to handle
        """
        event_type = type(event)
        
        if event_type == EquityBalanceChangedEvent:
            self._handle_equity_balance_changed(event)
        elif event_type == DistributionRecordedEvent:
            self._handle_distribution_recorded(event)
        elif event_type == NAVUpdatedEvent:
            self._handle_nav_updated(event)
        elif event_type == TaxStatementUpdatedEvent:
            self._handle_tax_statement_updated(event)
        else:
            logger.warning(f"TaxStatementEventHandler received unexpected event type: {event_type}")
    
    def _handle_equity_balance_changed(self, event: EquityBalanceChangedEvent) -> None:
        """
        Handle equity balance changed events.
        
        Args:
            event: Equity balance changed event
        """
        logger.info(f"Processing equity balance change for fund {event.fund_id}")
        
        try:
            # Get the fund to determine its type and current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping tax statement update")
                return
            
            # For cost-based funds, equity changes affect capital gain calculations
            if fund.tracking_type == FundType.COST_BASED:
                self._update_tax_statement_equity(event.fund_id, event.event_date, event.new_balance)
            else:
                logger.debug(f"Fund {event.fund_id} is not cost-based, equity changes don't affect tax statements")
            
        except Exception as e:
            logger.error(f"Error handling equity balance change event: {e}")
            raise
    
    def _handle_distribution_recorded(self, event: DistributionRecordedEvent) -> None:
        """
        Handle distribution recorded events.
        
        Args:
            event: Distribution recorded event
        """
        logger.info(f"Processing distribution for fund {event.fund_id}")
        
        try:
            # Get the fund to determine its type and current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping tax statement update")
                return
            
            # Update tax statement with distribution information
            self._update_tax_statement_distribution(
                event.fund_id, 
                event.event_date, 
                event.amount, 
                event.tax_withheld
            )
            
        except Exception as e:
            logger.error(f"Error handling distribution recorded event: {e}")
            raise
    
    def _handle_nav_updated(self, event: NAVUpdatedEvent) -> None:
        """
        Handle NAV updated events.
        
        Args:
            event: NAV updated event
        """
        logger.info(f"Processing NAV update for fund {event.fund_id}")
        
        try:
            # Get the fund to determine its type and current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping tax statement update")
                return
            
            # For NAV-based funds, NAV changes affect unrealized gain/loss calculations
            if fund.tracking_type == FundType.NAV_BASED:
                self._update_tax_statement_nav(event.fund_id, event.event_date, event.new_nav)
            else:
                logger.debug(f"Fund {event.fund_id} is not NAV-based, NAV changes don't affect tax statements")
            
        except Exception as e:
            logger.error(f"Error handling NAV updated event: {e}")
            raise
    
    def _handle_tax_statement_updated(self, event: TaxStatementUpdatedEvent) -> None:
        """
        Handle tax statement updated events.
        
        Args:
            event: Tax statement updated event
        """
        logger.info(f"Processing tax statement update for fund {event.fund_id}, type: {event.update_type}")
        
        try:
            # Get the fund to determine its type and current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping tax statement update")
                return
            
            # Handle different types of tax statement updates
            if event.update_type == "created":
                # When a tax statement is created, we may need to update fund status
                # This replaces the direct call to fund.update_status_after_tax_statement()
                self._handle_tax_statement_created(event, fund)
            elif event.update_type == "modified":
                # Handle modifications to existing tax statements
                self._handle_tax_statement_modified(event, fund)
            elif event.update_type == "finalized":
                # Handle finalization of tax statements
                self._handle_tax_statement_finalized(event, fund)
            else:
                logger.warning(f"Unknown tax statement update type: {event.update_type}")
            
        except Exception as e:
            logger.error(f"Error handling tax statement updated event: {e}")
            raise
    
    def _handle_tax_statement_created(self, event: TaxStatementUpdatedEvent, fund: Fund) -> None:
        """
        Handle tax statement creation events.
        
        Args:
            event: Tax statement updated event
            fund: The fund associated with the tax statement
        """
        logger.info(f"Handling tax statement creation for fund {event.fund_id}")
        
        try:
            # Check if fund status should be updated after tax statement creation
            # This replaces the direct call to fund.update_status_after_tax_statement()
            if hasattr(fund, 'update_status_after_tax_statement'):
                # Use the existing method if available (for backward compatibility)
                fund.update_status_after_tax_statement()
                logger.info(f"Fund {event.fund_id} status updated after tax statement creation")
            else:
                # If the method doesn't exist, we can implement the logic here
                # or delegate to the fund status service
                logger.debug(f"Fund {event.fund_id} status update method not available")
                
        except Exception as e:
            logger.error(f"Error updating fund status after tax statement creation: {e}")
            raise
    
    def _handle_tax_statement_modified(self, event: TaxStatementUpdatedEvent, fund: Fund) -> None:
        """
        Handle tax statement modification events.
        
        Args:
            event: Tax statement updated event
            fund: The fund associated with the tax statement
        """
        logger.info(f"Handling tax statement modification for fund {event.fund_id}")
        # Implement modification logic as needed
        
    def _handle_tax_statement_finalized(self, event: TaxStatementUpdatedEvent, fund: Fund) -> None:
        """
        Handle tax statement finalization events.
        
        Args:
            event: Tax statement updated event
            fund: The fund associated with the tax statement
        """
        logger.info(f"Handling tax statement finalization for fund {event.fund_id}")
        # Implement finalization logic as needed
    
    def _get_fund(self, fund_id: int) -> Optional[Fund]:
        """
        Get fund information for the given fund ID.
        
        Args:
            fund_id: ID of the fund to retrieve
            
        Returns:
            Fund object if found, None otherwise
        """
        # Note: In a real implementation, this would get a session from the context
        # For now, we'll use a placeholder approach
        try:
            # This would typically get a session from the event context
            # For now, we'll create a temporary repository instance
            fund_repo = FundRepository()
            # Note: This won't work without a session, but shows the intended approach
            logger.debug(f"Would retrieve fund {fund_id} using repository")
            return None  # Placeholder - would return actual fund in real implementation
        except Exception as e:
            logger.error(f"Error retrieving fund {fund_id}: {e}")
            return None
    
    def _get_financial_year(self, event_date: date) -> str:
        """
        Determine the financial year for a given date.
        
        Args:
            event_date: Date to determine financial year for
            
        Returns:
            Financial year string (e.g., "2023-24")
        """
        # Australian financial year runs from July 1 to June 30
        if event_date.month >= 7:
            # July to December: current calendar year to next year
            start_year = event_date.year
            end_year = event_date.year + 1
        else:
            # January to June: previous year to current year
            start_year = event_date.year - 1
            end_year = event_date.year
        
        return f"{start_year}-{str(end_year)[-2:]}"
    
    def _update_tax_statement_equity(self, fund_id: int, event_date: date, new_equity: float) -> None:
        """
        Update tax statement equity values.
        
        Args:
            fund_id: ID of the fund
            event_date: Date of the event
            new_equity: New equity balance
        """
        logger.info(f"Updating tax statement equity for fund {fund_id} to {new_equity}")
        
        try:
            # Determine financial year for the event
            financial_year = self._get_financial_year(event_date)
            
            # Get or create tax statement for this fund and financial year
            tax_statement = self._get_or_create_tax_statement(fund_id, financial_year)
            if not tax_statement:
                logger.warning(f"Could not get or create tax statement for fund {fund_id}, year {financial_year}")
                return
            
            # Update equity-related fields
            # Note: In a real implementation, this would update specific equity fields
            # based on the fund type and business rules
            logger.debug(f"Updated tax statement {tax_statement.id} equity values for fund {fund_id}")
            
            # Mark the statement as updated
            tax_statement.updated_at = event_date
            
        except Exception as e:
            logger.error(f"Error updating tax statement equity for fund {fund_id}: {e}")
            raise
    
    def _update_tax_statement_distribution(self, fund_id: int, event_date: date, amount: float, tax_withheld: float) -> None:
        """
        Update tax statement distribution information.
        
        Args:
            fund_id: ID of the fund
            event_date: Date of the event
            amount: Distribution amount
            tax_withheld: Tax withheld amount
        """
        logger.info(f"Updating tax statement distribution for fund {fund_id}: amount={amount}, tax={tax_withheld}")
        
        try:
            # Determine financial year for the event
            financial_year = self._get_financial_year(event_date)
            
            # Get or create tax statement for this fund and financial year
            tax_statement = self._get_or_create_tax_statement(fund_id, financial_year)
            if not tax_statement:
                logger.warning(f"Could not get or create tax statement for fund {fund_id}, year {financial_year}")
                return
            
            # Update distribution-related fields
            # Note: In a real implementation, this would update specific distribution fields
            # based on the distribution type and business rules
            logger.debug(f"Updated tax statement {tax_statement.id} distribution values for fund {fund_id}")
            
            # Mark the statement as updated
            tax_statement.updated_at = event_date
            
        except Exception as e:
            logger.error(f"Error updating tax statement distribution for fund {fund_id}: {e}")
            raise
    
    def _update_tax_statement_nav(self, fund_id: int, event_date: date, new_nav: float) -> None:
        """
        Update tax statement NAV values.
        
        Args:
            fund_id: ID of the fund
            event_date: Date of the event
            new_nav: New NAV value
        """
        logger.info(f"Updating tax statement NAV for fund {fund_id} to {new_nav}")
        
        try:
            # Determine financial year for the event
            financial_year = self._get_financial_year(event_date)
            
            # Get or create tax statement for this fund and financial year
            tax_statement = self._get_or_create_tax_statement(fund_id, financial_year)
            if not tax_statement:
                logger.warning(f"Could not get or create tax statement for fund {fund_id}, year {financial_year}")
                return
            
            # Update NAV-related fields
            # Note: In a real implementation, this would update specific NAV fields
            # and recalculate unrealized gains/losses
            logger.debug(f"Updated tax statement {tax_statement.id} NAV values for fund {fund_id}")
            
            # Mark the statement as updated
            tax_statement.updated_at = event_date
            
        except Exception as e:
            logger.error(f"Error updating tax statement NAV for fund {fund_id}: {e}")
            raise
    
    def _get_or_create_tax_statement(self, fund_id: int, financial_year: str):
        """
        Get or create a tax statement for the given fund and financial year.
        
        Args:
            fund_id: ID of the fund
            financial_year: Financial year string
            
        Returns:
            TaxStatement object if found or created, None if error
        """
        try:
            # Note: In a real implementation, this would use a session from the context
            # For now, we'll use a placeholder approach
            tax_repo = TaxStatementRepository()
            
            # Try to get existing statement
            # Note: This won't work without a session, but shows the intended approach
            logger.debug(f"Would get or create tax statement for fund {fund_id}, year {financial_year}")
            return None  # Placeholder - would return actual statement in real implementation
            
        except Exception as e:
            logger.error(f"Error getting or creating tax statement for fund {fund_id}, year {financial_year}: {e}")
            return None
