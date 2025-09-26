"""
Domain Event Repository.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from src.fund.models import DomainFundEvent
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import EventOperation, SortOrder
from src.fund.enums.domain_fund_event_enums import SortFieldDomainFundEvent


class DomainFundEventRepository:
    """
    Domain Fund Event Repository.

    This repository handles all database operations for domain fund events including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    domain fund event data without direct database access.
    """
    
    def __init__(self):
        """
        Initialize the repository.
        
        Args:
            None
        """
        pass

    ################################################################################
    # Get Domain Fund Event
    ################################################################################

    def get_domain_fund_events(self, session: Session,
                fund_id: Optional[int] = None,
                event_type: Optional[EventType] = None,
                event_operation: Optional[EventOperation] = None,
                fund_event_id: Optional[int] = None,
                sort_by: Optional[SortFieldDomainFundEvent] = SortFieldDomainFundEvent.TIMESTAMP,
                sort_order: Optional[SortOrder] = SortOrder.ASC
    ) -> List[DomainFundEvent]:
        """
        Get all domain fund events.
        
        Args:
            session: Database session
            fund_id: ID of the fund to filter by (optional)
            event_type: Event type to filter by (optional)
            event_operation: Event operation to filter by (optional)
            fund_event_id: ID of the fund event to filter by (optional)
            sort_by: Field to sort by (optional)
            sort_order: Sort order (ascending or descending) (optional)

        Returns:
            List of domain fund events
        """
        # Validate sort field
        if sort_by not in SortFieldDomainFundEvent:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        query = session.query(DomainFundEvent)
        
        if fund_id:
            query = query.filter(DomainFundEvent.fund_id == fund_id)
        if event_type:
            query = query.filter(DomainFundEvent.event_type == event_type)
        if event_operation:
            query = query.filter(DomainFundEvent.event_operation == event_operation)
        if fund_event_id:
            query = query.filter(DomainFundEvent.fund_event_id == fund_event_id)
        
        if sort_by == SortFieldDomainFundEvent.TIMESTAMP:
            query = query.order_by(DomainFundEvent.timestamp.asc() if sort_order == SortOrder.ASC else DomainFundEvent.timestamp.desc())
        elif sort_by == SortFieldDomainFundEvent.EVENT_TYPE:
            query = query.order_by(DomainFundEvent.event_type.asc() if sort_order == SortOrder.ASC else DomainFundEvent.event_type.desc())
        elif sort_by == SortFieldDomainFundEvent.EVENT_OPERATION:
            query = query.order_by(DomainFundEvent.event_operation.asc() if sort_order == SortOrder.ASC else DomainFundEvent.event_operation.desc())
        elif sort_by == SortFieldDomainFundEvent.FUND_EVENT_ID:
            query = query.order_by(DomainFundEvent.fund_event_id.asc() if sort_order == SortOrder.ASC else DomainFundEvent.fund_event_id.desc())
        
        domain_fund_events = query.all()
        
        return domain_fund_events

    def get_domain_fund_event_by_id(self, domain_fund_event_id: int, session: Session) -> DomainFundEvent:
        """
        Get a domain fund event by its ID.
        
        Args:
            domain_fund_event_id: ID of the domain fund event to retrieve
            session: Database session
            
        Returns:
            DomainFundEvent object if found, None otherwise
        """
        domain_fund_event = session.query(DomainFundEvent).filter(DomainFundEvent.id == domain_fund_event_id).first()
        return domain_fund_event


    ################################################################################
    # Create Domain Fund Event
    ################################################################################

    def create_domain_fund_event(self, fund_id: int, event_type: EventType, event_operation: EventOperation, fund_event_id: int, event_data: Dict[str, Any], session: Session) -> DomainFundEvent:
        """
        Create a domain fund event in the database.
        
        Args:
            fund_id: Fund ID
            event_type: Event type
            event_operation: Event operation
            fund_event_id: Fund event ID
            event_data: Event data
            session: Session
        """
        db_event = DomainFundEvent(
            fund_id=fund_id,
            event_type=event_type,
            event_operation=event_operation,
            fund_event_id=fund_event_id,
            event_data=event_data
        )
        session.add(db_event)
        session.flush()
        return db_event


    ################################################################################
    # Delete Domain Fund Event
    ################################################################################

    def delete_domain_fund_event(self, domain_fund_event_id: int, session: Session) -> bool:
        """
        Delete a domain fund event from the database.
        """
        domain_fund_event = self.get_domain_fund_event_by_id(domain_fund_event_id, session)
        if not domain_fund_event:
            return False
        
        session.delete(domain_fund_event)
        session.flush()
        return True
    