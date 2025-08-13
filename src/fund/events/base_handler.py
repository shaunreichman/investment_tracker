"""
Base Fund Event Handler.

This module provides the abstract base class for all fund event handlers.
Each handler is responsible for processing a specific event type and publishing
domain events for dependent updates.
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Optional, Any, Dict, List
from sqlalchemy.orm import Session

from ..models import Fund, FundEvent
from ..enums import EventType, FundType
from ..services.fund_calculation_service import FundCalculationService
from ..services.fund_status_service import FundStatusService
from ..services.tax_calculation_service import TaxCalculationService


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
        # Compare values since we might have different enum classes (old vs new)
        if self.fund.tracking_type.value != expected_type.value:
            raise ValueError(
                f"Event requires {expected_type.value} fund, "
                f"but fund is {self.fund.tracking_type.value}"
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
            event_type=event_type.name,  # Use enum name for database compatibility
            **kwargs
        )
        self.session.add(event)
        self.session.flush()
        return event
    
    def _publish_dependent_events(self, event: FundEvent) -> None:
        """
        Publish domain events for dependent updates.
        
        This method will be implemented in Phase 4 when we add
        the full domain event system. For now, it's a placeholder
        that maintains the contract.
        
        Args:
            event: The event that was just processed
        """
        # TODO: Implement domain event publishing in Phase 4
        pass
    
    def _update_fund_summary_fields(self) -> None:
        """
        Update fund summary fields after event processing.
        
        This method delegates to the appropriate service methods
        to update calculated fields on the fund.
        """
        # Update fund summary fields based on fund type
        if self.fund.tracking_type == FundType.COST_BASED:
            self.fund.update_fund_summary_fields_after_capital_event(session=self.session)
        elif self.fund.tracking_type == FundType.NAV_BASED:
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
            # Trigger IRR calculation and status update
            self.fund.update_status_after_equity_event(session=self.session)
    
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
        if isinstance(date_value, date):
            return date_value
        elif isinstance(date_value, datetime):
            return date_value.date()
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
