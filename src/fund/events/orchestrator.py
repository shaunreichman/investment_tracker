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
        # Update fund summary fields if needed
        if event.event_type in [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE]:
            # Instead of calling fund method directly, publish a domain event
            # This enables loose coupling and allows other components to react
            from .domain import FundSummaryUpdatedEvent
            from .consumption.event_bus import event_bus
            
            summary_event = FundSummaryUpdatedEvent(
                fund_id=event.fund_id,
                event_date=event.event_date,
                summary_type="CAPITAL_EVENT_PROCESSED",
                metadata={
                    "original_event_id": event.id,
                    "original_event_type": event.event_type.value,
                    "amount": event.amount
                }
            )
            event_bus.publish(summary_event)
        
        # Handle NAV-specific updates
        if event.event_type == EventType.NAV_UPDATE:
            # Update subsequent NAV events if needed
            if hasattr(event.fund, '_update_subsequent_nav_change_fields'):
                event.fund._update_subsequent_nav_change_fields(event, session)
        
        # Trigger domain event processing for dependent components
        self._process_domain_events_for_dependent_updates(event, session)
    
    def _process_domain_events_for_dependent_updates(self, event: FundEvent, session: Session) -> None:
        """
        Process domain events to trigger updates in dependent components.
        
        This method looks at the domain events that were published and
        triggers appropriate updates in other components that need to react.
        
        Args:
            event: The fund event that was processed
            session: Database session for all operations
        """
        from ..repositories.domain_event_repository import DomainEventRepository
        
        # Get the domain events that were published for this fund event
        domain_repo = DomainEventRepository(session)
        
        # Get recent domain events for this fund (last 5 minutes to catch the ones we just published)
        from datetime import datetime, timedelta
        recent_cutoff = datetime.now() - timedelta(minutes=5)
        
        recent_events = domain_repo.get_by_date_range(
            start_date=recent_cutoff.date(),
            end_date=datetime.now().date(),
            fund_id=event.fund_id
        )
        
        # Process each domain event to trigger dependent updates
        for domain_event in recent_events:
            self._trigger_dependent_component_updates(domain_event, session)
    
    def _trigger_dependent_component_updates(self, domain_event, session: Session) -> None:
        """
        Trigger updates in dependent components based on domain events.
        
        Args:
            domain_event: The domain event that occurred
            session: Database session for all operations
        """
        # Import domain event types
        from ..enums import DomainEventType
        
        if domain_event.event_type == DomainEventType.EQUITY_BALANCE_CHANGED:
            # Trigger tax statement updates if needed
            self._update_tax_statements_for_equity_change(domain_event, session)
            
        elif domain_event.event_type == DomainEventType.DISTRIBUTION_RECORDED:
            # Trigger company record updates for distributions
            self._update_company_records_for_distribution(domain_event, session)
            
        elif domain_event.event_type == DomainEventType.NAV_UPDATED:
            # Trigger unit value recalculations
            self._update_unit_values_for_nav_change(domain_event, session)
    
    def _update_tax_statements_for_equity_change(self, domain_event, session: Session) -> None:
        """
        Update tax statements when equity balance changes.
        
        Args:
            domain_event: The equity balance changed event
            session: Database session for all operations
        """
        # This would trigger tax statement recalculations
        # For now, we'll implement this in Phase 4 when we add full tax integration
        pass
    
    def _update_company_records_for_distribution(self, domain_event, session: Session) -> None:
        """
        Update company records when distributions are recorded.
        
        Args:
            domain_event: The distribution recorded event
            session: Database session for all operations
        """
        # This would trigger company record updates
        # For now, we'll implement this in Phase 4 when we add full company integration
        pass
    
    def _update_unit_values_for_nav_change(self, domain_event, session: Session) -> None:
        """
        Update unit values when NAV changes.
        
        Args:
            domain_event: The NAV updated event
            session: Database session for all operations
        """
        # This would trigger unit value recalculations
        # For now, we'll implement this in Phase 4 when we add full NAV integration
        pass
    
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
                event_type for event_type in self.registry.get_registered_event_types()
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
        event_type_raw = event_data['event_type']
        if isinstance(event_type_raw, EventType):
            # Already a valid enum object
            pass
        else:
            try:
                EventType.from_string(event_type_raw)
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
