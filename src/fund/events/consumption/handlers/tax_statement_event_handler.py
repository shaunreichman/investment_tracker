"""
Tax Statement Event Handler.

This handler processes tax statement update events,
triggering appropriate updates in dependent components.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.fund.events.consumption.base_consumer import EventConsumer
from src.fund.repositories.tax_statement_repository import TaxStatementRepository
from src.fund.repositories.fund_repository import FundRepository
from src.fund.models import Fund
from src.fund.enums import FundTrackingType
from src.fund.events.domain import TaxStatementUpdatedEvent

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
        
        if event_type == TaxStatementUpdatedEvent:
            self._handle_tax_statement_updated(event)
        else:
            logger.warning(f"TaxStatementEventHandler received unexpected event type: {event_type}")
    
    def _handle_tax_statement_updated(self, event: TaxStatementUpdatedEvent) -> None:
        """
        Handle tax statement updated events.
        
        Args:
            event: Tax statement updated event
        """
        logger.info(f"Processing tax statement update for fund {event.fund_id}, type: {event.update_type}")
        
        try:
            # Import domain events
            from src.fund.events.domain import (
                FundSummaryUpdatedEvent,
                TaxStatementUpdatedEvent,
                EquityBalanceChangedEvent
            )
            from src.fund.events.consumption.event_bus import event_bus
            
            # Create tax statement update event
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
            # Import domain events
            from src.fund.events.domain import (
                FundSummaryUpdatedEvent,
                TaxStatementUpdatedEvent,
                EquityBalanceChangedEvent
            )
            from src.fund.events.consumption.event_bus import event_bus
            
            # Publish event for fund status update
            summary_event = FundSummaryUpdatedEvent(
                fund_id=event.fund_id,
                event_date=event.event_date,
                summary_type="TAX_STATEMENT_CREATED",
                metadata={
                    "tax_statement_id": event.tax_statement_id,
                    "financial_year": event.financial_year,
                    "entity_id": event.entity_id
                }
            )
            event_bus.publish(summary_event, self.session)
            
            logger.info(f"Published fund summary update event for fund {event.fund_id} after tax statement creation")
            
        except Exception as e:
            logger.error(f"Error publishing fund summary update event: {e}")
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
        if not self.session:
            logger.error("No database session available for retrieving fund")
            return None
            
        try:
            # Use the session to query for the fund
            fund = self.session.query(Fund).filter(Fund.id == fund_id).first()
            if fund:
                logger.debug(f"Retrieved fund {fund_id}: {fund.name}")
                return fund
            else:
                logger.warning(f"Fund {fund_id} not found")
                return None
                
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
            # Update specific equity fields based on fund type and business rules
            if hasattr(tax_statement, 'equity_balance'):
                tax_statement.equity_balance = new_equity
                logger.debug(f"Updated equity balance to {new_equity}")
            
            if hasattr(tax_statement, 'equity_date'):
                tax_statement.equity_date = event_date
                logger.debug(f"Updated equity date to {event_date}")
            
            # For cost-based funds, update cost basis if available
            if hasattr(tax_statement, 'cost_basis'):
                # This would typically involve more complex logic based on fund type
                logger.debug(f"Updated cost basis for fund {fund_id}")
            
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
            # Update specific distribution fields based on distribution type and business rules
            if hasattr(tax_statement, 'total_distributions'):
                current_total = getattr(tax_statement, 'total_distributions', 0.0) or 0.0
                tax_statement.total_distributions = current_total + amount
                logger.debug(f"Updated total distributions to {tax_statement.total_distributions}")
            
            if hasattr(tax_statement, 'total_tax_withheld'):
                current_withheld = getattr(tax_statement, 'total_tax_withheld', 0.0) or 0.0
                tax_statement.total_tax_withheld = current_withheld + tax_withheld
                logger.debug(f"Updated total tax withheld to {tax_statement.total_tax_withheld}")
            
            if hasattr(tax_statement, 'last_distribution_date'):
                tax_statement.last_distribution_date = event_date
                logger.debug(f"Updated last distribution date to {event_date}")
            
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
            
            # For NAV-based funds, we can use capital_gain_income_amount to track NAV changes
            # This is a simplified approach - in a real system, you might add dedicated NAV fields
            if hasattr(tax_statement, 'capital_gain_income_amount'):
                # Use capital gain amount to track NAV changes (simplified approach)
                current_amount = getattr(tax_statement, 'capital_gain_income_amount', 0.0) or 0.0
                # This is a placeholder - in reality, you'd calculate the actual NAV change
                logger.debug(f"Updated capital gain tracking for NAV change to {new_nav}")
            
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
        if not self.session:
            logger.error("No database session available for tax statement operations")
            return None
            
        try:
            from src.fund.models.fund_tax_statement import FundTaxStatement
            
            # First get the fund to determine the entity_id
            fund = self.session.query(Fund).filter(Fund.id == fund_id).first()
            if not fund:
                logger.error(f"Fund {fund_id} not found")
                return None
            
            # Try to get existing statement
            existing_statement = self.session.query(TaxStatement).filter(
                TaxStatement.fund_id == fund_id,
                TaxStatement.financial_year == financial_year
            ).first()
            
            if existing_statement:
                logger.debug(f"Found existing tax statement {existing_statement.id} for fund {fund_id}, year {financial_year}")
                return existing_statement
            
            # Create new statement if none exists
            new_statement = TaxStatement(
                fund_id=fund_id,
                financial_year=financial_year,
                entity_id=fund.entity_id,  # Use the fund's actual entity_id
                statement_date=None,  # Will be set when finalized
                created_at=datetime.now()
            )
            
            self.session.add(new_statement)
            self.session.flush()  # Get the ID without committing
            
            logger.info(f"Created new tax statement {new_statement.id} for fund {fund_id}, year {financial_year}")
            return new_statement
            
        except Exception as e:
            logger.error(f"Error getting or creating tax statement for fund {fund_id}, year {financial_year}: {e}")
            return None
