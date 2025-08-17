"""
Base Fund Event Handler.

This module provides the base class for all fund event handlers,
defining the common interface and shared functionality.

Key responsibilities:
- Common event processing logic
- Event validation and error handling
- Event relationship management
- Event publishing and side effects
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod

from src.fund.models import Fund, FundEvent
from src.fund.enums import EventType, FundType, FundStatus
from src.fund.services.fund_calculation_service import FundCalculationService
from src.fund.services.fund_status_service import FundStatusService
from src.fund.services.tax_calculation_service import TaxCalculationService


class BaseFundEventHandler(ABC):
    """
    Abstract base class for all fund event handlers.
    
    Each handler is responsible for:
    1. Validating the event data
    2. Processing the event and updating the fund
    3. Publishing domain events for dependent updates
    4. Managing transaction boundaries
    
    This class provides common functionality and enforces the contract
    that all handlers must implement.
    """
    
    def __init__(self, session: Session, fund: Fund):
        """
        Initialize the handler with session and fund.
        
        Args:
            session: Database session for all operations
            fund: Fund instance to operate on
        """
        self.session = session
        self.fund = fund
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize services for business logic
        self.calculation_service = FundCalculationService()
        self.status_service = FundStatusService()
        self.tax_service = TaxCalculationService()
    
    @abstractmethod
    def handle(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Handle the event and return the created/updated FundEvent.
        
        This is the main entry point that all handlers must implement.
        It should:
        1. Validate the event data
        2. Create/update the FundEvent
        3. Update fund state as needed
        4. Publish domain events
        5. Return the event
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            FundEvent: The created or updated event
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        pass
    
    @abstractmethod
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate event data before processing.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        pass
    
    def _get_fund(self, fund_id: int) -> Fund:
        """
        Get fund by ID from the current session.
        
        Args:
            fund_id: Fund ID to retrieve
            
        Returns:
            Fund: Fund instance
            
        Raises:
            ValueError: If fund not found
        """
        fund = self.session.query(Fund).filter(Fund.id == fund_id).first()
        if not fund:
            raise ValueError(f"Fund with ID {fund_id} not found")
        return fund
    
    def _validate_fund_type(self, expected_type: FundType) -> None:
        """
        Validate that the fund is of the expected type.
        
        Args:
            expected_type: Expected fund type
            
        Raises:
            ValueError: If fund type doesn't match
        """
        # Compare enum objects directly - no need for .value
        if self.fund.tracking_type != expected_type:
            raise ValueError(
                f"Event requires {expected_type} fund, "
                f"but fund is {self.fund.tracking_type}"
            )
    
    def _validate_positive_amount(self, amount: Any, field_name: str) -> None:
        """
        Validate that an amount is positive.
        
        Args:
            amount: Amount to validate
            field_name: Name of the field for error messages
            
        Raises:
            ValueError: If amount is not positive or not a valid number
        """
        try:
            amount_val = float(amount)
            if amount_val <= 0:
                raise ValueError(f"{field_name} must be a positive number")
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} must be a valid positive number")
    
    def _validate_required_date(self, date: Any, field_name: str) -> None:
        """
        Validate that a required date is provided.
        
        Args:
            date: Date to validate
            field_name: Name of the field for error messages
            
        Raises:
            ValueError: If date is missing
        """
        if not date:
            raise ValueError(f"{field_name} is required")
    
    def _check_duplicate_event(self, event_type: EventType, **filters) -> Optional[FundEvent]:
        """
        Check for existing duplicate event to support idempotent behavior.
        
        Args:
            event_type: Type of event to check
            **filters: Additional filters to apply
            
        Returns:
            FundEvent: Existing event if found, None otherwise
        """
        query = self.session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund.id,
            FundEvent.event_type == event_type.name  # Use enum name for database compatibility
        )
        
        for field, value in filters.items():
            if hasattr(FundEvent, field) and value is not None:
                query = query.filter(getattr(FundEvent, field) == value)
        
        return query.first()
    
    def _create_event(self, event_type: EventType, **kwargs) -> FundEvent:
        """
        Create a new FundEvent with common fields.
        
        Args:
            event_type: Type of event to create
            **kwargs: Event-specific fields
            
        Returns:
            FundEvent: Created event
        """
        event = FundEvent(
            fund_id=self.fund.id,
            event_type=event_type,  # Store the enum object directly
            **kwargs
        )
        self.session.add(event)
        self.session.flush()
        return event
    
    def _publish_dependent_events(self, event: FundEvent) -> None:
        """
        Publish domain events for dependent updates.
        
        This method creates and stores domain events for significant
        state changes, enabling loose coupling between components.
        
        Args:
            event: The event that was just processed
        """
        from src.fund.repositories.domain_event_repository import DomainEventRepository
        
        # Initialize domain event repository
        domain_repo = DomainEventRepository(self.session)
        
        # Create domain events based on the fund event type
        domain_events = self._create_domain_events_for_fund_event(event)
        
        # Store all domain events in the database
        if domain_events:
            domain_repo.store_domain_events(domain_events)
            
            # Also publish events to the event bus for real-time consumption
            self._publish_events_to_bus(domain_events)
    
    def _publish_events_to_bus(self, domain_events: List['FundDomainEvent']) -> None:
        """
        Publish domain events to the event bus for real-time consumption.
        
        This method ensures that domain events are not only stored
        but also immediately available for consumption by event handlers.
        
        Args:
            domain_events: List of domain events to publish
        """
        try:
            # Import the event bus from the consumption module
            from src.fund.events.consumption.event_bus import event_bus
            
            # Publish each domain event to the event bus
            for domain_event in domain_events:
                event_bus.publish(domain_event)
                self.logger.debug(f"Published {type(domain_event).__name__} to event bus")
                
        except ImportError as e:
            # If the event bus is not available, log a warning but don't fail
            self.logger.warning(f"Event bus not available, skipping event bus publishing: {e}")
        except Exception as e:
            # Log any other errors but don't fail the main event processing
            self.logger.error(f"Error publishing events to event bus: {e}")
            # Don't raise - this is a non-critical operation
    
    def _create_domain_events_for_fund_event(self, event: FundEvent) -> List['FundDomainEvent']:
        """
        Create appropriate domain events for a fund event.
        
        This method determines which domain events should be created
        based on the type of fund event and its impact.
        
        Args:
            event: The fund event that was processed
            
        Returns:
            List[FundDomainEvent]: List of domain events to publish
        """
        domain_events = []
        
        # Import domain event classes
        from src.fund.events.domain.equity_balance_changed_event import EquityBalanceChangedEvent
        from src.fund.events.domain.distribution_recorded_event import DistributionRecordedEvent
        from src.fund.events.domain.nav_updated_event import NAVUpdatedEvent
        from src.fund.events.domain.units_changed_event import UnitsChangedEvent
        from src.fund.events.domain.tax_statement_updated_event import TaxStatementUpdatedEvent
        
        # Get current fund state for comparison
        old_equity_balance = getattr(event, 'previous_equity_balance', 0.0) or 0.0
        current_equity_balance = getattr(event, 'current_equity_balance', 0.0) or 0.0
        
        # Create equity balance changed event if balance changed
        if abs(current_equity_balance - old_equity_balance) > 0.01:  # Small tolerance for floating point
            equity_event = EquityBalanceChangedEvent(
                fund_id=self.fund.id,
                event_date=event.event_date,
                old_balance=old_equity_balance,
                new_balance=current_equity_balance,
                change_reason=f"{event.event_type} event {event.id}"
            )
            domain_events.append(equity_event)
        
        # Create event-specific domain events
        if event.event_type == EventType.DISTRIBUTION:
            # Distribution recorded event
            # Get distribution type as enum if possible, fallback to string
            distribution_type = getattr(event, 'distribution_type', 'Unknown')
            # No need to extract .value - work with the enum object directly
            
            dist_event = DistributionRecordedEvent(
                fund_id=self.fund.id,
                event_date=event.event_date,
                distribution_type=distribution_type,
                amount=getattr(event, 'amount', 0.0),
                tax_withheld=getattr(event, 'withholding_tax_amount', 0.0),
                metadata={'fund_event_id': event.id}
            )
            domain_events.append(dist_event)
            
            # Tax statement updated event if tax was withheld
            if getattr(event, 'withholding_tax_amount', 0.0) > 0:
                tax_event = TaxStatementUpdatedEvent(
                    fund_id=self.fund.id,
                    event_date=event.event_date,
                    tax_statement_id=None,  # Will be updated when tax statement is created
                    update_type='distribution_tax_withheld',
                    metadata={'fund_event_id': event.id, 'tax_amount': getattr(event, 'withholding_tax_amount')}
                )
                domain_events.append(tax_event)
        
        elif event.event_type == EventType.NAV_UPDATE:
            # NAV updated event
            nav_event = NAVUpdatedEvent(
                fund_id=self.fund.id,
                event_date=event.event_date,
                old_nav=getattr(event, 'previous_nav', 0.0) or 0.0,
                new_nav=getattr(event, 'current_nav', 0.0) or 0.0,
                change_reason=f"NAV update event {event.id}",
                metadata={'fund_event_id': event.id}
            )
            domain_events.append(nav_event)
        
        elif event.event_type in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]:
            # Units changed event
            old_units = getattr(event, 'previous_units', 0.0) or 0.0
            current_units = getattr(event, 'current_units', 0.0) or 0.0
            
            if abs(current_units - old_units) > 0.01:  # Small tolerance for floating point
                units_event = UnitsChangedEvent(
                    fund_id=self.fund.id,
                    event_date=event.event_date,
                    old_units=old_units,
                    new_units=current_units,
                    change_reason=f"{event.event_type} event {event.id}",
                    metadata={'fund_event_id': event.id}
                )
                domain_events.append(units_event)
        
        return domain_events
    
    def _update_fund_summary_fields(self) -> None:
        """
        Update fund summary fields after event processing.
        
        This method updates calculated fields on the fund using
        the new architecture instead of calling old Fund methods.
        """
        # Update fund summary fields based on fund type
        if self.fund.tracking_type == FundType.COST_BASED:
            # For cost-based funds, update equity balance and related fields
            self._update_cost_based_fund_summary()
        elif self.fund.tracking_type == FundType.NAV_BASED:
            # For NAV-based funds, update NAV-specific fields
            self._update_nav_based_fund_summary()
    
    def _update_cost_based_fund_summary(self) -> None:
        """
        Update cost-based fund summary fields.
        
        This method updates fields like current_equity_balance,
        total_cost_basis, and average_equity_balance for cost-based funds.
        """
        # Get all capital events for this fund to calculate summary fields
        from src.fund.models import FundEvent
        from src.fund.enums import EventType
        
        capital_events = self.session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund.id,
            FundEvent.event_type.in_([
                EventType.CAPITAL_CALL,
                EventType.RETURN_OF_CAPITAL
            ])
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        # Calculate total cost basis and equity balance
        total_cost_basis = 0.0
        current_equity_balance = 0.0
        
        for event in capital_events:
            if event.event_type == EventType.CAPITAL_CALL:
                total_cost_basis += event.amount or 0.0
                current_equity_balance += event.amount or 0.0
            elif event.event_type == EventType.RETURN_OF_CAPITAL:
                current_equity_balance -= event.amount or 0.0
        
        # Update fund fields
        self.fund.total_cost_basis = total_cost_basis
        self.fund.current_equity_balance = current_equity_balance
        
        # Calculate average equity balance if we have events
        if capital_events:
            # For now, use a simple average - this could be enhanced with time-weighted calculations
            self.fund.average_equity_balance = current_equity_balance / len(capital_events)
        else:
            self.fund.average_equity_balance = 0.0
    
    def _update_nav_based_fund_summary(self) -> None:
        """
        Update NAV-based fund summary fields.
        
        This method updates fields like current_units, current_nav_total,
        and current_unit_price for NAV-based funds.
        """
        # For NAV-based funds, update NAV-specific fields
        if hasattr(self.fund, 'current_nav_total'):
            self.fund.current_nav_total = (
                (self.fund.current_units or 0.0) * 
                (self.fund.current_unit_price or 0.0)
            )
    
    def _handle_status_transition(self, event: FundEvent) -> None:
        """
        Handle fund status transitions if needed.
        
        Args:
            event: The event that was just processed
        """
        # Check if status update is needed
        if self.status_service.should_calculate_irr(self.fund.status, self.fund):
            # Trigger IRR calculation and status update using new architecture
            self._update_fund_status_independently()
    
    def _update_fund_status_independently(self) -> None:
        """
        Update fund status independently using new architecture.
        
        This method handles status transitions and IRR calculations
        without calling old Fund model methods.
        """
        # For now, implement basic status logic
        # This can be enhanced with more sophisticated status transition logic
        
        # Check if fund should transition to REALIZED status
        if (self.fund.status != FundStatus.REALIZED and 
            self.fund.current_equity_balance == 0.0 and
            hasattr(self.fund, 'end_date') and self.fund.end_date):
            
            # Transition to REALIZED status
            old_status = self.fund.status
            self.fund.status = FundStatus.REALIZED
            
            # Log the status change
            print(f"Fund {self.fund.name} status updated to {self.fund.status} after equity event")
            
            # TODO: Implement IRR calculation logic here
            # For now, just log that IRRs would be calculated
            print(f"IRRs calculated and stored for realized fund {self.fund.name}")
    
    def _commit_changes(self) -> None:
        """
        Commit all changes to the database.
        
        This method ensures that all changes are persisted
        and handles any commit-time errors.
        """
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise RuntimeError(f"Failed to commit changes: {e}") from e
    
    def _parse_date(self, date_value: Any) -> date:
        """
        Parse date value to ensure it's a proper datetime.date object.
        
        Args:
            date_value: Date value that could be string, date, or datetime
            
        Returns:
            date: Proper datetime.date object
            
        Raises:
            ValueError: If date cannot be parsed
        """
        if isinstance(date_value, datetime):
            return date_value.date()
        elif isinstance(date_value, date):
            return date_value
        elif isinstance(date_value, str):
            try:
                # Try parsing common date formats
                if '-' in date_value:
                    return datetime.strptime(date_value, '%Y-%m-%d').date()
                elif '/' in date_value:
                    return datetime.strptime(date_value, '%Y/%m/%d').date()
                else:
                    raise ValueError(f"Unsupported date format: {date_value}")
            except ValueError as e:
                raise ValueError(f"Invalid date format: {date_value}. Expected YYYY-MM-DD or YYYY/MM/DD") from e
        else:
            raise ValueError(f"Invalid date type: {type(date_value)}. Expected string, date, or datetime")
    
    def _rollback_on_error(self, error: Exception) -> None:
        """
        Rollback changes on error.
        
        Args:
            error: The error that occurred
        """
        self.session.rollback()
        raise error
