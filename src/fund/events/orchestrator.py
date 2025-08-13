"""
Fund Update Orchestrator.

This module provides the orchestrator that coordinates the complete
fund update pipeline. It manages transaction boundaries, error handling,
and coordinates between different components of the event system.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models import Fund, FundEvent
from .registry import FundEventHandlerRegistry
from ..enums import EventType


class FundUpdateOrchestrator:
    """
    Orchestrates the complete fund update pipeline.
    
    This class coordinates:
    1. Event processing through the registry
    2. Transaction boundaries and rollback
    3. Dependent updates and side effects
    4. Error handling and recovery
    
    It serves as the main entry point for all fund event processing
    and ensures that the entire pipeline is executed atomically.
    """
    
    def __init__(self, registry: Optional[FundEventHandlerRegistry] = None):
        """
        Initialize the orchestrator.
        
        Args:
            registry: Event handler registry to use. If None, creates a new one.
        """
        self.registry = registry or FundEventHandlerRegistry()
    
    def process_fund_event(self, event_data: Dict[str, Any], session: Session, fund: Fund) -> FundEvent:
        """
        Process a fund event through the complete pipeline.
        
        This is the main entry point for all fund event processing.
        It coordinates the entire pipeline:
        1. Event validation and routing
        2. Event processing by appropriate handler
        3. Dependent updates and side effects
        4. Transaction management
        
        Args:
            event_data: Dictionary containing event parameters
            session: Database session for all operations
            fund: Fund instance to operate on
            
        Returns:
            FundEvent: The created or updated event
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        try:
            # Step 1: Process the main event through the registry
            event = self.registry.handle_event(event_data, session, fund)
            
            # Step 2: Handle any dependent updates
            self._handle_dependent_updates(event, session)
            
            # Step 3: Commit all changes
            self._commit_changes(session)
            
            return event
            
        except Exception as e:
            # Step 4: Rollback on any error
            self._rollback_on_error(session, e)
            raise
    
    def process_bulk_events(self, events_data: list[Dict[str, Any]], session: Session, fund: Fund) -> list[FundEvent]:
        """
        Process multiple fund events in a single transaction.
        
        This method processes multiple events atomically, ensuring that
        either all events succeed or none do. It's useful for bulk
        operations and maintaining data consistency.
        
        Args:
            events_data: List of event data dictionaries
            session: Database session for all operations
            fund: Fund instance to operate on
            
        Returns:
            list[FundEvent]: List of created/updated events
            
        Raises:
            ValueError: If any event data is invalid
            RuntimeError: If any event processing fails
        """
        if not events_data:
            return []
        
        events = []
        try:
            # Process each event
            for event_data in events_data:
                event = self.registry.handle_event(event_data, session, fund)
                events.append(event)
                
                # Handle dependent updates for this event
                self._handle_dependent_updates(event, session)
            
            # Commit all changes
            self._commit_changes(session)
            
            return events
            
        except Exception as e:
            # Rollback on any error
            self._rollback_on_error(session, e)
            raise
    
    def _handle_dependent_updates(self, event: FundEvent, session: Session) -> None:
        """
        Handle dependent updates triggered by the event.
        
        This method coordinates updates to related entities that
        depend on the fund event. Examples include:
        - Tax statement updates
        - Company record updates
        - Summary field recalculations
        - Status transitions
        
        Args:
            event: The event that was just processed
            session: Database session for all operations
        """
        # TODO: Implement dependent updates in Phase 4
        # For now, this is a placeholder that maintains the contract
        
        # Update fund summary fields if needed
        if hasattr(event.fund, 'update_fund_summary_fields_after_capital_event'):
            # For capital events, update summary fields
            if event.event_type in [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE]:
                event.fund.update_fund_summary_fields_after_capital_event(session=session)
        
        # Handle NAV-specific updates
        if event.event_type == EventType.NAV_UPDATE:
            # Update subsequent NAV events if needed
            if hasattr(event.fund, '_update_subsequent_nav_change_fields'):
                event.fund._update_subsequent_nav_change_fields(event, session)
    
    def _commit_changes(self, session: Session) -> None:
        """
        Commit all changes to the database.
        
        Args:
            session: Database session to commit
            
        Raises:
            RuntimeError: If commit fails
        """
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to commit changes: {e}") from e
    
    def _rollback_on_error(self, session: Session, error: Exception) -> None:
        """
        Rollback changes on error.
        
        Args:
            session: Database session to rollback
            error: The error that occurred
        """
        try:
            session.rollback()
        except Exception as rollback_error:
            # If rollback fails, log it but don't mask the original error
            # In a production system, this would be logged
            pass
        
        # Re-raise the original error
        raise error
    
    def get_registry_status(self) -> Dict[str, Any]:
        """
        Get the current status of the event handler registry.
        
        Returns:
            Dict containing registry status information
        """
        return {
            'registered_event_types': [
                event_type.value for event_type in self.registry.get_registered_event_types()
            ],
            'total_handlers': len(self.registry.get_registered_event_types()),
            'registry_initialized': self.registry is not None
        }
    
    def validate_event_data(self, event_data: Dict[str, Any]) -> bool:
        """
        Validate event data before processing.
        
        This method performs basic validation to catch obvious errors
        before attempting to process the event. It's a lightweight
        validation that doesn't require database access.
        
        Args:
            event_data: Event data to validate
            
        Returns:
            bool: True if validation passes, False otherwise
            
        Raises:
            ValueError: If validation fails with details
        """
        # Check required fields
        required_fields = ['event_type']
        for field in required_fields:
            if field not in event_data or not event_data[field]:
                raise ValueError(f"Required field '{field}' is missing or empty")
        
        # Validate event type
        try:
            EventType.from_string(event_data['event_type'])
        except ValueError as e:
            raise ValueError(f"Invalid event_type: {e}")
        
        # Validate date if present
        if 'date' in event_data and event_data['date']:
            try:
                from datetime import date
                if isinstance(event_data['date'], str):
                    date.fromisoformat(event_data['date'])
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
        # Validate amount if present
        if 'amount' in event_data and event_data['amount'] is not None:
            try:
                amount = float(event_data['amount'])
            except (ValueError, TypeError):
                raise ValueError("Amount must be a valid number")
            
            if amount < 0:
                raise ValueError("Amount cannot be negative")
        
        return True
