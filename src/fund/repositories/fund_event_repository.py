"""
Fund Event Repository.
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.fund.models import FundEvent
from src.fund.enums.fund_event_enums import EventType, DistributionType, TaxPaymentType, GroupType, SortFieldFundEvent
from src.shared.enums.shared_enums import SortOrder


class FundEventRepository:
    """
    Fund Event Repository.

    This repository handles all database operations for fund events including
    CRUD operations, complex queries. It provides
    a clean interface for business logic components to interact with
    fund event data without direct database access.
    """
    def __init__(self):
        """
        Initialize the fund event repository.
        
        Args:
            None
        """
        pass


    ################################################################################
    # Get Fund Event
    ################################################################################
    
    def get_fund_events(self, session: Session,
                        fund_ids: Optional[List[int]] = None,
                        event_types: Optional[List[EventType]] = None,
                        distribution_types: Optional[List[DistributionType]] = None,
                        tax_payment_types: Optional[List[TaxPaymentType]] = None,
                        group_types: Optional[List[GroupType]] = None,
                        start_event_date: Optional[date] = None,
                        end_event_date: Optional[date] = None,
                        sort_by: Optional[SortFieldFundEvent] = SortFieldFundEvent.EVENT_DATE,
                        sort_order: SortOrder = SortOrder.ASC
    ) -> List[FundEvent]:
        """
        Get all fund events.

        Args:
            session: Database session
            fund_ids: Optional list of fund IDs (optional)
            event_types: Optional list of event types to filter by (optional)
            distribution_types: Optional list of distribution types to filter by (optional)
            tax_payment_types: Optional list of tax payment types to filter by (optional)
            group_types: Optional list of group types to filter by (optional)
            start_event_date: Optional start event date to filter by (optional)
            end_event_date: Optional end event date to filter by (optional)
            sort_by: Optional sort field to sort by (optional)
            sort_order: Optional sort order to sort by (optional)

        Returns:
            List of fund events
        """
        # Validate sort field
        if sort_by not in SortFieldFundEvent:
            raise ValueError(f"Invalid sort field: {sort_by}. Must be one of: {[s.value for s in SortFieldFundEvent]}")
        
        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}. Must be one of: {[s.value for s in SortOrder]}")
        
        # Query database
        query = session.query(FundEvent)
        
        if fund_ids:
            query = query.filter(FundEvent.fund_id.in_(fund_ids))
        if event_types:
            event_type_values = [et.value for et in event_types]
            query = query.filter(FundEvent.event_type.in_(event_type_values))
        if distribution_types:
            query = query.filter(FundEvent.distribution_type.in_([dt.value for dt in distribution_types]))
        if tax_payment_types:
            query = query.filter(FundEvent.tax_payment_type.in_([ttp.value for ttp in tax_payment_types]))
        if group_types:
            query = query.filter(FundEvent.group_type.in_([gt.value for gt in group_types]))
        if start_event_date:
            query = query.filter(FundEvent.event_date >= start_event_date)
        if end_event_date:
            query = query.filter(FundEvent.event_date <= end_event_date)
        
        # Apply sorting
        if sort_by == SortFieldFundEvent.EVENT_DATE:
            query = query.order_by(FundEvent.event_date.asc() if sort_order == SortOrder.ASC else FundEvent.event_date.desc())
        elif sort_by == SortFieldFundEvent.EVENT_TYPE:
            query = query.order_by(FundEvent.event_type.asc() if sort_order == SortOrder.ASC else FundEvent.event_type.desc())
        
        events = query.all()
        
        return events
    
    def get_fund_event_by_id(self, event_id: int, session: Session) -> Optional[FundEvent]:
        """
        Get a fund event by its ID.
        
        Args:
            event_id: ID of the event to retrieve
            session: Database session
            
        Returns:
            FundEvent object if found, None otherwise
        """
        # Query database
        fund_event = session.query(FundEvent).filter(FundEvent.id == event_id).first()
        
        return fund_event


    ################################################################################
    # Create Fund Event
    ################################################################################
   
    def create_fund_event(self, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a new fund event.
        
        Args:
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            Created FundEvent object
            
        Raises:
            TypeError: If event_data is not a dictionary
            ValueError: If required fields are missing
        """
        # Create event object
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()  # Get the ID without committing
        
        return event

    ################################################################################
    # Delete Fund Event
    ################################################################################
    
    def delete_fund_event(self, event_id: int, session: Session) -> bool:
        """
        Delete a fund event.
        
        Args:
            event_id: ID of the event to delete
            session: Database session
            
        Returns:
            True if event was deleted, False if not found
        """
        event = self.get_fund_event_by_id(event_id, session)
        if not event:
            return False
        
        # If this event is grouped, delete all events in the same group
        if event.is_grouped and event.group_id:
            # Find all events in the same group
            group_events = session.query(FundEvent).filter(
                FundEvent.group_id == event.group_id
            ).all()
            
            # Delete all events in the group
            for group_event in group_events:
                session.delete(group_event)
        else:
            # Delete just this single event
            session.delete(event)
        
        return True
    
    
    def generate_group_id(self, session: Session) -> int:
        """
        Generate a unique group ID using database sequence for enterprise-grade uniqueness.
        
        This method uses a PostgreSQL sequence to ensure thread-safe, unique group IDs
        for event grouping functionality. The sequence is created via database migration.
        
        Args:
            session: Database session for sequence access
            
        Returns:
            int: Unique group ID from the sequence
            
        Raises:
            RuntimeError: If sequence access fails
        """
        from sqlalchemy import text
        
        try:
            # Get next value from sequence
            result = session.execute(text("SELECT nextval('group_id_seq')"))
            group_id = result.scalar()
            
            # Ensure we stay within PostgreSQL Integer limits
            if group_id > 2147483647:
                # Reset sequence if we're getting close to the limit
                session.execute(text("ALTER SEQUENCE group_id_seq RESTART WITH 1"))
                result = session.execute(text("SELECT nextval('group_id_seq')"))
                group_id = result.scalar()
            
            return group_id
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate group ID: {e}") from e
