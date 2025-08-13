"""
Fund Service.

This module provides the service layer for fund operations, coordinating
between the API layer, business logic services, and data access layer.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from decimal import Decimal

from ..repositories import FundRepository, FundEventRepository, TaxStatementRepository
from ..events.orchestrator import FundUpdateOrchestrator
from ..events.registry import FundEventHandlerRegistry
from ..enums import FundStatus, FundType, EventType


class FundService:
    """
    Service layer for fund operations.
    
    This service coordinates between the API layer, business logic services,
    and data access layer. It provides a clean interface for handling
    fund-related business operations.
    
    Attributes:
        fund_repository (FundRepository): Repository for fund data access
        fund_event_repository (FundEventRepository): Repository for fund event data access
        tax_statement_repository (TaxStatementRepository): Repository for tax statement data access
        orchestrator (FundUpdateOrchestrator): Orchestrator for fund update operations
        registry (FundEventHandlerRegistry): Registry for event handlers
    """
    
    def __init__(self):
        """Initialize the fund service with all required components."""
        self.fund_repository = FundRepository()
        self.fund_event_repository = FundEventRepository()
        self.tax_statement_repository = TaxStatementRepository()
        self.orchestrator = FundUpdateOrchestrator()
        self.registry = FundEventHandlerRegistry()
    
    def create_fund(self, fund_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
        """
        Create a new fund.
        
        Args:
            fund_data: Dictionary containing fund data
            session: Database session
            
        Returns:
            Dictionary containing the created fund information
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = ['name', 'entity_id', 'investment_company_id']
        for field in required_fields:
            if field not in fund_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Create the fund
        fund = self.fund_repository.create(fund_data, session)
        
        # Return fund information
        return {
            'id': fund.id,
            'name': fund.name,
            'status': fund.status.value if fund.status else None,
            'fund_type': fund.fund_type.value if fund.fund_type else None,
            'entity_id': fund.entity_id,
            'investment_company_id': fund.investment_company_id,
            'created_at': fund.created_at.isoformat() if fund.created_at else None
        }
    
    def update_fund(self, fund_id: int, fund_data: Dict[str, Any], 
                   session: Session) -> Optional[Dict[str, Any]]:
        """
        Update an existing fund.
        
        Args:
            fund_id: ID of the fund to update
            fund_data: Dictionary containing updated fund data
            session: Database session
            
        Returns:
            Dictionary containing the updated fund information, or None if not found
        """
        # Update the fund
        fund = self.fund_repository.update(fund_id, fund_data, session)
        if not fund:
            return None
        
        # Return updated fund information
        return {
            'id': fund.id,
            'name': fund.name,
            'status': fund.status.value if fund.status else None,
            'fund_type': fund.fund_type.value if fund.fund_type else None,
            'entity_id': fund.entity_id,
            'investment_company_id': fund.investment_company_id,
            'updated_at': fund.updated_at.isoformat() if fund.updated_at else None
        }
    
    def delete_fund(self, fund_id: int, session: Session) -> bool:
        """
        Delete a fund.
        
        Args:
            fund_id: ID of the fund to delete
            session: Database session
            
        Returns:
            True if fund was deleted, False if not found
        """
        return self.fund_repository.delete(fund_id, session)
    
    def get_fund(self, fund_id: int, session: Session) -> Optional[Dict[str, Any]]:
        """
        Get a fund by its ID.
        
        Args:
            fund_id: ID of the fund to retrieve
            session: Database session
            
        Returns:
            Dictionary containing fund information, or None if not found
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return None
        
        return {
            'id': fund.id,
            'name': fund.name,
            'status': fund.status.value if fund.status else None,
            'fund_type': fund.fund_type.value if fund.fund_type else None,
            'entity_id': fund.entity_id,
            'investment_company_id': fund.investment_company_id,
            'description': fund.description,
            'created_at': fund.created_at.isoformat() if fund.created_at else None,
            'updated_at': fund.updated_at.isoformat() if fund.updated_at else None
        }
    
    def get_funds(self, session: Session, 
                  skip: int = 0, 
                  limit: int = 100,
                  status: Optional[FundStatus] = None,
                  fund_type: Optional[FundType] = None,
                  search: Optional[str] = None) -> Dict[str, Any]:
        """
        Get funds with filtering, pagination, and search.
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional fund status filter
            fund_type: Optional fund type filter
            search: Optional search term
            
        Returns:
            Dictionary containing funds and pagination information
        """
        funds = []
        
        if search:
            # Use search functionality
            funds = self.fund_repository.search_funds(search, session)
        elif status:
            # Filter by status
            funds = self.fund_repository.get_funds_by_status(status, session)
        elif fund_type:
            # Filter by fund type
            funds = self.fund_repository.get_funds_by_type(fund_type, session)
        else:
            # Get all funds with pagination
            funds = self.fund_repository.get_all(session, skip, limit)
        
        # Convert to dictionaries
        fund_list = []
        for fund in funds:
            fund_list.append({
                'id': fund.id,
                'name': fund.name,
                'status': fund.status.value if fund.status else None,
                'fund_type': fund.fund_type.value if fund.fund_type else None,
                'entity_id': fund.entity_id,
                'investment_company_id': fund.investment_company_id,
                'created_at': fund.created_at.isoformat() if fund.created_at else None
            })
        
        return {
            'funds': fund_list,
            'total': len(fund_list),
            'skip': skip,
            'limit': limit
        }
    
    def add_fund_event(self, fund_id: int, event_data: Dict[str, Any], 
                      session: Session) -> Dict[str, Any]:
        """
        Add a fund event using the event handler system.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            Dictionary containing the created event information
            
        Raises:
            ValueError: If required fields are missing
            RuntimeError: If event processing fails
        """
        # Validate required fields
        required_fields = ['event_type', 'event_date', 'amount']
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Add fund_id to event data
        event_data['fund_id'] = fund_id
        
        # Process the event through the orchestrator
        try:
            result = self.orchestrator.process_fund_event(event_data, session)
            
            # Return event information
            return {
                'id': result.get('event_id'),
                'fund_id': fund_id,
                'event_type': event_data['event_type'],
                'event_date': event_data['event_date'].isoformat() if hasattr(event_data['event_date'], 'isoformat') else str(event_data['event_date']),
                'amount': str(event_data['amount']),
                'status': 'processed'
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to process fund event: {str(e)}")
    
    def update_fund_event(self, fund_id: int, event_id: int, 
                         event_data: Dict[str, Any], session: Session) -> Optional[Dict[str, Any]]:
        """
        Update a fund event.
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event to update
            event_data: Dictionary containing updated event data
            session: Database session
            
        Returns:
            Dictionary containing the updated event information, or None if not found
        """
        # Update the event
        event = self.fund_event_repository.update(event_id, event_data, session)
        if not event:
            return None
        
        # Return updated event information
        return {
            'id': event.id,
            'fund_id': event.fund_id,
            'event_type': event.event_type,
            'event_date': event.event_date.isoformat() if event.event_date else None,
            'amount': str(event.amount) if event.amount else None,
            'updated_at': event.updated_at.isoformat() if event.updated_at else None
        }
    
    def delete_fund_event(self, fund_id: int, event_id: int, session: Session) -> bool:
        """
        Delete a fund event.
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event to delete
            session: Database session
            
        Returns:
            True if event was deleted, False if not found
        """
        return self.fund_event_repository.delete(event_id, session)
    
    def get_fund_events(self, fund_id: int, session: Session,
                       skip: int = 0, 
                       limit: int = 100,
                       event_types: Optional[List[EventType]] = None) -> Dict[str, Any]:
        """
        Get events for a specific fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            event_types: Optional list of event types to filter by
            
        Returns:
            Dictionary containing events and pagination information
        """
        events = self.fund_event_repository.get_by_fund(
            fund_id, session, event_types, skip, limit
        )
        
        # Convert to dictionaries
        event_list = []
        for event in events:
            event_list.append({
                'id': event.id,
                'fund_id': event.fund_id,
                'event_type': event.event_type,
                'event_date': event.event_date.isoformat() if event.event_date else None,
                'amount': str(event.amount) if event.amount else None,
                'created_at': event.created_at.isoformat() if event.created_at else None
            })
        
        return {
            'events': event_list,
            'total': len(event_list),
            'skip': skip,
            'limit': limit
        }
    
    def get_fund_summary(self, fund_id: int, session: Session) -> Optional[Dict[str, Any]]:
        """
        Get a comprehensive summary of a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Dictionary containing fund summary information, or None if not found
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return None
        
        # Get event count
        event_count = self.fund_event_repository.get_event_count_by_fund(fund_id, session)
        
        # Get tax statement count
        tax_statement_count = self.tax_statement_repository.get_statement_count_by_fund(fund_id, session)
        
        return {
            'id': fund.id,
            'name': fund.name,
            'status': fund.status.value if fund.status else None,
            'fund_type': fund.fund_type.value if fund.fund_type else None,
            'entity_id': fund.entity_id,
            'investment_company_id': fund.investment_company_id,
            'event_count': event_count,
            'tax_statement_count': tax_statement_count,
            'created_at': fund.created_at.isoformat() if fund.created_at else None,
            'updated_at': fund.updated_at.isoformat() if fund.updated_at else None
        }
    
    def get_fund_metrics(self, fund_id: int, session: Session) -> Optional[Dict[str, Any]]:
        """
        Get performance metrics for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Dictionary containing fund metrics, or None if not found
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return None
        
        # Get recent events for metrics calculation
        recent_events = self.fund_event_repository.get_by_fund(
            fund_id, session, limit=50
        )
        
        # Calculate basic metrics (this would be enhanced with actual business logic)
        total_events = len(recent_events)
        capital_events = [e for e in recent_events if e.event_type in [EventType.CAPITAL_CALL.value, EventType.RETURN_OF_CAPITAL.value]]
        distribution_events = [e for e in recent_events if e.event_type == EventType.DISTRIBUTION.value]
        
        return {
            'fund_id': fund_id,
            'total_events': total_events,
            'capital_events': len(capital_events),
            'distribution_events': len(distribution_events),
            'last_event_date': recent_events[-1].event_date.isoformat() if recent_events else None,
            'status': fund.status.value if fund.status else None
        }
