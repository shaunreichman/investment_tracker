"""
Fund Repository.

This module provides the data access layer for fund operations including
CRUD operations, caching strategies, and optimized queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from decimal import Decimal

from ..models import Fund
from ..enums import FundStatus, FundType, SortOrder, SortField


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
    
    def get_by_investment_company(self, company_id: int, session: Session) -> List[Fund]:
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
        funds = session.query(Fund).filter(Fund.investment_company_id == company_id).all()
        
        # Cache the result
        self._cache[cache_key] = funds
        
        return funds
    
    def get_by_entity(self, entity_id: int, session: Session) -> List[Fund]:
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
        funds = session.query(Fund).filter(Fund.entity_id == entity_id).all()
        
        # Cache the result
        self._cache[cache_key] = funds
        
        return funds
    
    def get_all(self, session: Session, 
                skip: int = 0, 
                limit: int = 100,
                sort_by: SortField = SortField.NAME,
                sort_order: SortOrder = SortOrder.ASC) -> List[Fund]:
        """
        Get all funds with pagination and sorting.
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort_by: Field to sort by
            sort_order: Sort order (ascending or descending)
            
        Returns:
            List of funds with pagination and sorting applied
        """
        query = session.query(Fund)
        
        # Apply sorting
        if sort_by == SortField.NAME:
            query = query.order_by(asc(Fund.name) if sort_order == SortOrder.ASC else desc(Fund.name))
        elif sort_by == SortField.STATUS:
            query = query.order_by(asc(Fund.status) if sort_order == SortOrder.ASC else desc(Fund.status))
        elif sort_by == SortField.CREATED_AT:
            query = query.order_by(asc(Fund.created_at) if sort_order == SortOrder.ASC else desc(Fund.created_at))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
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
    
    def search_funds(self, search_term: str, session: Session) -> List[Fund]:
        """
        Search funds by name or description.
        
        Args:
            search_term: Search term to look for
            session: Database session
            
        Returns:
            List of funds matching the search term
        """
        if not search_term.strip():
            return []
        
        # Query database with search
        funds = session.query(Fund).filter(
            or_(
                Fund.name.ilike(f"%{search_term}%"),
                Fund.description.ilike(f"%{search_term}%")
            )
        ).all()
        
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
    
    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
