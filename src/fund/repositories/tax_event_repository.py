"""
Tax Event Repository.

This repository provides data access operations for tax-related fund events
(TAX_PAYMENT, DAILY_RISK_FREE_INTEREST_CHARGE, EOFY_DEBT_COST), implementing 
the repository pattern for clean separation of concerns.

Key responsibilities:
- Tax event CRUD operations
- Tax event querying and filtering
- Tax event aggregations
- Interest charge operations
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.fund.models import FundEvent
from src.fund.enums import EventType, SortOrder, SortFieldFund


class TaxEventRepository:
    """
    Repository for tax event data access operations.
    
    This repository handles all database operations for tax events including
    CRUD operations, bulk operations, and optimized queries for tax event processing.
    It provides a clean interface for business logic components to interact with
    tax event data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the tax event repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def create_tax_payment(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a tax payment event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created tax payment event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.TAX_PAYMENT
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def create_daily_interest_charge(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a daily risk-free interest charge event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created daily interest charge event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def create_eofy_debt_cost(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create an end-of-financial-year debt cost event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created EOFY debt cost event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.EOFY_DEBT_COST
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def get_tax_events(self, fund_id: int, session: Session, 
                      skip: int = 0, limit: int = 100,
                      start_date: Optional[date] = None,
                      end_date: Optional[date] = None,
                      sort_by: SortFieldFund = SortFieldFund.EVENT_DATE,
                      sort_order: SortOrder = SortOrder.ASC) -> List[FundEvent]:
        """
        Get tax events for a specific fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            start_date: Optional start date filter
            end_date: Optional end date filter
            sort_by: Field to sort by
            sort_order: Sort order (ASC or DESC)
            
        Returns:
            List of tax events
        """
        cache_key = f"tax_events:fund:{fund_id}:skip:{skip}:limit:{limit}:start:{start_date}:end:{end_date}:sort:{sort_by.value}:order:{sort_order.value}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build query
        query = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type.in_([EventType.TAX_PAYMENT.value, EventType.DAILY_RISK_FREE_INTEREST_CHARGE.value, EventType.EOFY_DEBT_COST.value])
            )
        )
        
        # Apply date filters
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        # Apply sorting
        if sort_by == SortFieldFund.EVENT_DATE:
            sort_column = FundEvent.event_date
        else:
            sort_column = getattr(FundEvent, sort_by.value)
        if sort_order == SortOrder.DESC:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        events = query.all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_total_tax_payments(self, fund_id: int, session: Session) -> float:
        """
        Get total tax payments for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Total tax payments amount
        """
        cache_key = f"total_tax_payments:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        total = session.query(func.sum(FundEvent.amount)).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.TAX_PAYMENT.value
            )
        ).scalar()
        
        result = float(total) if total else 0.0
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_total_daily_interest_charges(self, fund_id: int, session: Session) -> float:
        """
        Get total daily interest charges for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Total daily interest charges amount
        """
        cache_key = f"total_daily_interest:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        total = session.query(func.sum(FundEvent.amount)).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE.value
            )
        ).scalar()
        
        result = float(total) if total else 0.0
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_daily_interest_charges_by_financial_year(self, fund_id: int, financial_year: int, session: Session) -> float:
        """
        Get total daily interest charges for a specific financial year.
        
        Args:
            fund_id: ID of the fund
            financial_year: Financial year to calculate for
            session: Database session
            
        Returns:
            Total daily interest charges for the financial year
        """
        cache_key = f"daily_interest_fy:fund:{fund_id}:fy:{financial_year}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Calculate financial year date range
        fy_start = date(financial_year, 7, 1)  # July 1st
        fy_end = date(financial_year + 1, 6, 30)  # June 30th next year
        
        # Query database
        total = session.query(func.sum(FundEvent.amount)).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE.value,
                FundEvent.event_date >= fy_start,
                FundEvent.event_date <= fy_end
            )
        ).scalar()
        
        result = float(total) if total else 0.0
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_tax_events_by_type_and_date_range(self, fund_id: int, event_type: EventType, 
                                            start_date: date, end_date: date, session: Session) -> List[FundEvent]:
        """
        Get tax events by type within a date range.
        
        Args:
            fund_id: ID of the fund
            event_type: Type of tax event
            start_date: Start date for the range
            end_date: End date for the range
            session: Database session
            
        Returns:
            List of tax events of the specified type in the date range
        """
        cache_key = f"tax_events_type:fund:{fund_id}:type:{event_type.value}:start:{start_date}:end:{end_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == event_type.value,
                FundEvent.event_date >= start_date,
                FundEvent.event_date <= end_date
            )
        ).order_by(FundEvent.event_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events

    def get_tax_event_by_group_id(self, group_id: int, session: Session) -> FundEvent:
        """
        Get a tax event by group id.
        """
        return session.query(FundEvent).filter(FundEvent.group_id == group_id).filter(FundEvent.event_type == EventType.TAX_PAYMENT.value).first()
    
    def delete_tax_events_by_type(self, fund_id: int, event_type: EventType, session: Session) -> int:
        """
        Delete all tax events of a specific type for a fund.
        
        Args:
            fund_id: ID of the fund
            event_type: Type of tax event to delete
            session: Database session
            
        Returns:
            Number of events deleted
        """
        # Get events to delete
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == event_type.value
            )
        ).all()
        
        # Delete events
        count = 0
        for event in events:
            session.delete(event)
            count += 1
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return count
    
    def _clear_fund_cache(self, fund_id: int) -> None:
        """Clear cache for events by fund."""
        for key in list(self._cache.keys()):
            if f"fund:{fund_id}" in key:
                self._cache.pop(key, None)
    
    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
