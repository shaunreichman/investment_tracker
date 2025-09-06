"""
Tax Statement Repository.

This repository provides data access operations for tax statements,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Tax statement CRUD operations
- Statement querying and filtering
- Statement relationship management
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, asc, desc

from src.tax.models import TaxStatement
from src.fund.enums import SortOrder


class TaxStatementRepository:
    """
    Repository for tax statement data access operations.
    
    This repository handles all database operations for tax statements including
    CRUD operations, efficient querying, and caching strategies. It provides
    a clean interface for business logic components to interact with
    tax statement data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the tax statement repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def get_by_id(self, statement_id: int, session: Session) -> Optional[TaxStatement]:
        """
        Get a tax statement by its ID.
        
        Args:
            statement_id: ID of the tax statement to retrieve
            session: Database session
            
        Returns:
            TaxStatement object if found, None otherwise
        """
        cache_key = f"tax_statement:{statement_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        statement = session.query(TaxStatement).filter(TaxStatement.id == statement_id).first()
        
        # Cache the result
        if statement:
            self._cache[cache_key] = statement
        
        return statement
    
    def get_by_fund_and_year(self, fund_id: int, financial_year: str, 
                            session: Session) -> Optional[TaxStatement]:
        """
        Get a tax statement for a specific fund and financial year.
        
        Args:
            fund_id: ID of the fund
            financial_year: Financial year (e.g., '2023-24')
            session: Database session
            
        Returns:
            TaxStatement object if found, None otherwise
        """
        cache_key = f"tax_statement:fund:{fund_id}:year:{financial_year}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        statement = session.query(TaxStatement).filter(
            and_(
                TaxStatement.fund_id == fund_id,
                TaxStatement.financial_year == financial_year
            )
        ).first()
        
        # Cache the result
        if statement:
            self._cache[cache_key] = statement
        
        return statement
    
    def get_by_entity_and_year(self, entity_id: int, financial_year: str, 
                              session: Session) -> List[TaxStatement]:
        """
        Get all tax statements for a specific entity and financial year.
        
        Args:
            entity_id: ID of the entity
            financial_year: Financial year (e.g., '2023-24')
            session: Database session
            
        Returns:
            List of TaxStatement objects for the entity and year
        """
        cache_key = f"tax_statements:entity:{entity_id}:year:{financial_year}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        statements = session.query(TaxStatement).filter(
            and_(
                TaxStatement.entity_id == entity_id,
                TaxStatement.financial_year == financial_year
            )
        ).all()
        
        # Cache the result
        self._cache[cache_key] = statements
        
        return statements
    
    def get_by_fund(self, fund_id: int, session: Session,
                    skip: int = 0,
                    limit: int = 100,
                    sort_order: SortOrder = SortOrder.DESC) -> List[TaxStatement]:
        """
        Get all tax statements for a specific fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort_order: Sort order (SortOrder.ASC or SortOrder.DESC)
            
        Returns:
            List of TaxStatement objects for the fund
        """
        cache_key = f"tax_statements:fund:{fund_id}:skip:{skip}:limit:{limit}:sort:{sort_order}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build query
        query = session.query(TaxStatement).filter(TaxStatement.fund_id == fund_id)
        
        # Apply sorting
        if sort_order == SortOrder.ASC:
            query = query.order_by(asc(TaxStatement.financial_year), asc(TaxStatement.id))
        else:
            query = query.order_by(desc(TaxStatement.financial_year), desc(TaxStatement.id))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        statements = query.all()
        
        # Cache the result
        self._cache[cache_key] = statements
        
        return statements
    
    def get_by_entity(self, entity_id: int, session: Session,
                     skip: int = 0,
                     limit: int = 100,
                     sort_order: SortOrder = SortOrder.DESC) -> List[TaxStatement]:
        """
        Get all tax statements for a specific entity.
        
        Args:
            entity_id: ID of the entity
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort_order: Sort order (SortOrder.ASC or SortOrder.DESC)
            
        Returns:
            List of TaxStatement objects for the entity
        """
        cache_key = f"tax_statements:entity:{entity_id}:skip:{skip}:limit:{limit}:sort:{sort_order}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build query
        query = session.query(TaxStatement).filter(TaxStatement.entity_id == entity_id)
        
        # Apply sorting
        if sort_order == SortOrder.ASC:
            query = query.order_by(asc(TaxStatement.financial_year), asc(TaxStatement.id))
        else:
            query = query.order_by(desc(TaxStatement.financial_year), desc(TaxStatement.id))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        statements = query.all()
        
        # Cache the result
        self._cache[cache_key] = statements
        
        return statements
    
    def create(self, statement_data: Dict[str, Any], session: Session) -> TaxStatement:
        """
        Create a new tax statement.
        
        Args:
            statement_data: Dictionary containing tax statement data
            session: Database session
            
        Returns:
            Created TaxStatement object
            
        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        required_fields = ['fund_id', 'entity_id', 'financial_year']
        for field in required_fields:
            if field not in statement_data or statement_data[field] is None:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Create tax statement object
        statement = TaxStatement(**statement_data)
        session.add(statement)
        session.flush()  # Get the ID without committing
        
        # Clear relevant caches
        self._clear_fund_cache(statement_data.get('fund_id'))
        self._clear_entity_cache(statement_data.get('entity_id'))
        self._clear_year_cache(statement_data.get('financial_year'))
        
        return statement
    
    def update(self, statement_id: int, statement_data: Dict[str, Any], 
              session: Session) -> Optional[TaxStatement]:
        """
        Update an existing tax statement.
        
        Args:
            statement_id: ID of the tax statement to update
            statement_data: Dictionary containing updated tax statement data
            session: Database session
            
        Returns:
            Updated TaxStatement object if found, None otherwise
        """
        statement = self.get_by_id(statement_id, session)
        if not statement:
            return None
        
        # Store old values for cache clearing
        old_fund_id = statement.fund_id
        old_entity_id = statement.entity_id
        old_financial_year = statement.financial_year
        
        # Update fields
        for key, value in statement_data.items():
            if hasattr(statement, key):
                setattr(statement, key, value)
        
        # Clear relevant caches
        self._clear_fund_cache(old_fund_id)
        self._clear_entity_cache(old_entity_id)
        self._clear_year_cache(old_financial_year)
        
        # Clear caches for new values
        self._clear_fund_cache(statement.fund_id)
        self._clear_entity_cache(statement.entity_id)
        self._clear_year_cache(statement.financial_year)
        
        session.flush()
        return statement
    
    def delete(self, statement_id: int, session: Session) -> bool:
        """
        Delete a tax statement.
        
        Args:
            statement_id: ID of the tax statement to delete
            session: Database session
            
        Returns:
            True if tax statement was deleted, False if not found
        """
        statement = self.get_by_id(statement_id, session)
        if not statement:
            return False
        
        # Store values for cache clearing
        fund_id = statement.fund_id
        entity_id = statement.entity_id
        financial_year = statement.financial_year
        
        # Delete the tax statement
        session.delete(statement)
        
        # Clear relevant caches
        self._clear_statement_cache(statement_id)
        self._clear_fund_cache(fund_id)
        self._clear_entity_cache(entity_id)
        self._clear_year_cache(financial_year)
        
        return True
    
    def get_final_statements(self, fund_id: int, session: Session) -> List[TaxStatement]:
        """
        Get all final tax statements for a fund.
        
        Note: This method currently returns all tax statements for the fund.
        The concept of "final" tax statements is determined by business logic
        comparing tax_payment_date with fund end date, not by a database field.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            List of TaxStatement objects for the fund
        """
        cache_key = f"final_tax_statements:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database for all statements (final determination is business logic)
        statements = session.query(TaxStatement).filter(
            TaxStatement.fund_id == fund_id
        ).order_by(desc(TaxStatement.financial_year)).all()
        
        # Cache the result
        self._cache[cache_key] = statements
        
        return statements
    
    def get_statement_count_by_fund(self, fund_id: int, session: Session) -> int:
        """
        Get the total count of tax statements for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Total count of tax statements for the fund
        """
        cache_key = f"tax_statement_count:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(func.count(TaxStatement.id)).filter(
            TaxStatement.fund_id == fund_id
        ).scalar()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def get_by_fund_after_date(self, fund_id: int, after_date: date, session: Session) -> List[TaxStatement]:
        """
        Get tax statements for a fund after a specific date.
        
        Args:
            fund_id: ID of the fund
            after_date: Date to filter after
            session: Database session
            
        Returns:
            List of tax statements after the specified date
        """
        cache_key = f"tax_statements:fund:{fund_id}:after:{after_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        statements = session.query(TaxStatement).filter(
            and_(
                TaxStatement.fund_id == fund_id,
                TaxStatement.tax_payment_date > after_date
            )
        ).order_by(TaxStatement.tax_payment_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = statements
        
        return statements
    
    def _clear_statement_cache(self, statement_id: int) -> None:
        """Clear cache for a specific tax statement."""
        cache_key = f"tax_statement:{statement_id}"
        self._cache.pop(cache_key, None)
    
    def _clear_fund_cache(self, fund_id: Optional[int]) -> None:
        """Clear cache for tax statements by fund."""
        if fund_id:
            # Clear all fund-related caches
            for key in list(self._cache.keys()):
                if f"tax_statements:fund:{fund_id}" in key or f"final_tax_statements:fund:{fund_id}" in key or f"tax_statement_count:fund:{fund_id}" in key:
                    self._cache.pop(key, None)
    
    def _clear_entity_cache(self, entity_id: Optional[int]) -> None:
        """Clear cache for tax statements by entity."""
        if entity_id:
            for key in list(self._cache.keys()):
                if f"tax_statements:entity:{entity_id}" in key:
                    self._cache.pop(key, None)
    
    def _clear_year_cache(self, financial_year: Optional[str]) -> None:
        """Clear cache for tax statements by year."""
        if financial_year:
            for key in list(self._cache.keys()):
                if f"tax_statements:entity:" in key and f":year:{financial_year}" in key:
                    self._cache.pop(key, None)
    
    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
