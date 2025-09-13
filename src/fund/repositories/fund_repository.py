"""
Fund Repository.

This repository provides data access operations for Fund entities,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Fund CRUD operations
- Fund querying and filtering
- Fund relationship management
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.fund.models import Fund
from src.fund.enums import FundStatus, FundType, SortOrder, SortField


class FundRepository:
    """
    Repository for fund data access operations.
    
    This repository handles all database operations for funds including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    fund data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the fund repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def get_by_id(self, fund_id: int, session: Session) -> Optional[Fund]:
        """
        Get a fund by its ID.
        
        Args:
            fund_id: ID of the fund to retrieve
            session: Database session
            
        Returns:
            Fund object if found, None otherwise
        """
        cache_key = f"fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        fund = session.query(Fund).filter(Fund.id == fund_id).first()
        
        # Cache the result
        if fund:
            self._cache[cache_key] = fund
        
        return fund
    
    def get_by_investment_company(self, company_id: int, session: Session,
                                  sort_by: SortField = SortField.START_DATE,
                                  sort_order: SortOrder = SortOrder.ASC) -> List[Fund]:
        """
        Get all funds for a specific investment company.
        
        Args:
            company_id: ID of the investment company
            session: Database session
            
        Returns:
            List of funds associated with the company
        """
        cache_key = f"funds:company:{company_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        query = session.query(Fund).filter(Fund.investment_company_id == company_id)

        # Apply sorting
        if sort_by == SortField.NAME:
            query = query.order_by(Fund.name.asc() if sort_order == SortOrder.ASC else Fund.name.desc())
        elif sort_by == SortField.STATUS:
            query = query.order_by(Fund.status.asc() if sort_order == SortOrder.ASC else Fund.status.desc())
        elif sort_by == SortField.CREATED_AT:
            query = query.order_by(Fund.created_at.asc() if sort_order == SortOrder.ASC else Fund.created_at.desc())
        elif sort_by == SortField.START_DATE:
            query = query.order_by(Fund.start_date.asc() if sort_order == SortOrder.ASC else Fund.start_date.desc())

        funds = query.all()
        # Cache the result
        self._cache[cache_key] = funds
        
        return funds
    
    def get_by_entity(self, entity_id: int, session: Session,
                      sort_by: SortField = SortField.START_DATE,
                      sort_order: SortOrder = SortOrder.ASC) -> List[Fund]:
        """
        Get all funds for a specific entity.
        
        Args:
            entity_id: ID of the entity
            session: Database session
            
        Returns:
            List of funds associated with the entity
        """
        cache_key = f"funds:entity:{entity_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        query = session.query(Fund).filter(Fund.entity_id == entity_id)

        # Apply sorting
        if sort_by == SortField.NAME:
            query = query.order_by(Fund.name.asc() if sort_order == SortOrder.ASC else Fund.name.desc())
        elif sort_by == SortField.STATUS:
            query = query.order_by(Fund.status.asc() if sort_order == SortOrder.ASC else Fund.status.desc())
        elif sort_by == SortField.CREATED_AT:
            query = query.order_by(Fund.created_at.asc() if sort_order == SortOrder.ASC else Fund.created_at.desc())
        elif sort_by == SortField.START_DATE:
            query = query.order_by(Fund.start_date.asc() if sort_order == SortOrder.ASC else Fund.start_date.desc())

        funds = query.all()
        # Cache the result
        self._cache[cache_key] = funds
        
        return funds
    
    def get_all_funds(self, session: Session, 
                sort_by: SortField = SortField.START_DATE,
                sort_order: SortOrder = SortOrder.ASC) -> List[Fund]:
        """
        Get all funds with optional sorting.
        
        Args:
            session: Database session
            sort_by: Field to sort by
            sort_order: Sort order (ascending or descending)
            
        Returns:
            List of funds with optional sorting applied
        """
        query = session.query(Fund)
        
        # Apply sorting
        if sort_by == SortField.NAME:
            query = query.order_by(Fund.name.asc() if sort_order == SortOrder.ASC else Fund.name.desc())
        elif sort_by == SortField.STATUS:
            query = query.order_by(Fund.status.asc() if sort_order == SortOrder.ASC else Fund.status.desc())
        elif sort_by == SortField.CREATED_AT:
            query = query.order_by(Fund.created_at.asc() if sort_order == SortOrder.ASC else Fund.created_at.desc())
        elif sort_by == SortField.START_DATE:
            query = query.order_by(Fund.start_date.asc() if sort_order == SortOrder.ASC else Fund.start_date.desc())
        
        return query.all()
    
    def create(self, fund_data: Dict[str, Any], session: Session) -> Fund:
        """
        Create a new fund.
        
        Args:
            fund_data: Dictionary containing fund data
            session: Database session
            
        Returns:
            Created fund object
            
        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        required_fields = ['name', 'entity_id', 'investment_company_id']
        for field in required_fields:
            if field not in fund_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Create fund object
        fund = Fund(**fund_data)
        session.add(fund)
        session.flush()  # Get the ID without committing
        
        # Clear relevant caches
        self._clear_company_cache(fund_data.get('investment_company_id'))
        self._clear_entity_cache(fund_data.get('entity_id'))
        
        return fund
    
    def update(self, fund_id: int, fund_data: Dict[str, Any], session: Session) -> Optional[Fund]:
        """
        Update an existing fund.
        
        Args:
            fund_id: ID of the fund to update
            fund_data: Dictionary containing updated fund data
            session: Database session
            
        Returns:
            Updated fund object if found, None otherwise
        """
        fund = self.get_by_id(fund_id, session)
        if not fund:
            return None
        
        # Update fields
        for key, value in fund_data.items():
            if hasattr(fund, key):
                setattr(fund, key, value)
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        self._clear_company_cache(fund.investment_company_id)
        self._clear_entity_cache(fund.entity_id)
        
        session.flush()
        return fund
    
    def delete(self, fund_id: int, session: Session) -> bool:
        """
        Delete a fund.
        
        Args:
            fund_id: ID of the fund to delete
            session: Database session
            
        Returns:
            True if fund was deleted, False if not found
        """
        fund = self.get_by_id(fund_id, session)
        if not fund:
            return False
        
        # Store IDs for cache clearing
        company_id = fund.investment_company_id
        entity_id = fund.entity_id
        
        # Delete the fund
        session.delete(fund)
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        self._clear_company_cache(company_id)
        self._clear_entity_cache(entity_id)
        
        return True
    
    def get_funds_by_status(self, status: FundStatus, session: Session) -> List[Fund]:
        """
        Get all funds with a specific status.
        
        Args:
            status: Fund status to filter by
            session: Database session
            
        Returns:
            List of funds with the specified status
        """
        cache_key = f"funds:status:{status.value}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        funds = session.query(Fund).filter(Fund.status == status).all()
        
        # Cache the result
        self._cache[cache_key] = funds
        
        return funds
    
    def get_funds_by_type(self, fund_type: FundType, session: Session) -> List[Fund]:
        """
        Get all funds of a specific type.
        
        Args:
            fund_type: Fund type to filter by
            session: Database session
            
        Returns:
            List of funds of the specified type
        """
        cache_key = f"funds:type:{fund_type.value}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        funds = session.query(Fund).filter(Fund.fund_type == fund_type).all()
        
        # Cache the result
        self._cache[cache_key] = funds
        
        return funds
    
    def _clear_fund_cache(self, fund_id: int) -> None:
        """Clear cache for a specific fund."""
        cache_key = f"fund:{fund_id}"
        self._cache.pop(cache_key, None)
    
    def _clear_company_cache(self, company_id: Optional[int]) -> None:
        """Clear cache for funds by company."""
        if company_id:
            cache_key = f"funds:company:{company_id}"
            self._cache.pop(cache_key, None)
    
    def _clear_entity_cache(self, entity_id: Optional[int]) -> None:
        """Clear cache for funds by entity."""
        if entity_id:
            cache_key = f"funds:entity:{entity_id}"
            self._cache.pop(cache_key, None)
    
    def get_fund_with_events(self, fund_id: int, session: Session) -> Optional[Fund]:
        """
        Get a fund with its events loaded.
        
        Args:
            fund_id: ID of the fund to retrieve
            session: Database session
            
        Returns:
            Fund object with events loaded if found, None otherwise
        """
        cache_key = f"fund_with_events:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with events loaded
        fund = session.query(Fund).filter(Fund.id == fund_id).first()
        
        if fund:
            # Load events to ensure they're available
            _ = fund.fund_events
        
        # Cache the result
        if fund:
            self._cache[cache_key] = fund
        
        return fund
    
    def get_funds_by_equity_balance(self, min_balance: float, max_balance: float, 
                                   session: Session) -> List[Fund]:
        """
        Get funds filtered by equity balance range.
        
        Args:
            min_balance: Minimum equity balance
            max_balance: Maximum equity balance
            session: Database session
            
        Returns:
            List of funds within the equity balance range
        """
        cache_key = f"funds:equity:{min_balance}:{max_balance}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        funds = session.query(Fund).filter(
            and_(
                Fund.current_equity_balance >= min_balance,
                Fund.current_equity_balance <= max_balance
            )
        ).all()
        
        # Cache the result
        self._cache[cache_key] = funds
        
        return funds
    
    def get_funds_by_status_and_equity(self, status: FundStatus, 
                                      equity_threshold: float, 
                                      session: Session) -> List[Fund]:
        """
        Get funds by status with equity balance above threshold.
        
        Args:
            status: Fund status to filter by
            equity_threshold: Minimum equity balance threshold
            session: Database session
            
        Returns:
            List of funds matching the criteria
        """
        cache_key = f"funds:status:{status.value}:equity:{equity_threshold}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        funds = session.query(Fund).filter(
            and_(
                Fund.status == status,
                Fund.current_equity_balance >= equity_threshold
            )
        ).all()
        
        # Cache the result
        self._cache[cache_key] = funds
        
        return funds

    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
