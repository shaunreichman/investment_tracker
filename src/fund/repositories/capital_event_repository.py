"""
Capital Event Repository.

This repository provides data access operations for capital-related fund events
(CAPITAL_CALL, RETURN_OF_CAPITAL), implementing the repository pattern for 
clean separation of concerns.

Key responsibilities:
- Capital event CRUD operations
- Capital event querying and filtering
- Capital event aggregations
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.fund.models import FundEvent
from src.fund.enums import SortFieldFund, EventType
from src.shared.enums.shared_enums import SortOrder



class CapitalEventRepository:
    """
    Repository for capital event data access operations.
    
    This repository handles all database operations for capital events including
    CRUD operations, bulk operations, and optimized queries for capital event processing.
    It provides a clean interface for business logic components to interact with
    capital event data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the capital event repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def create_capital_call(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a capital call event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created capital call event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.CAPITAL_CALL
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def create_return_of_capital(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a return of capital event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created return of capital event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.RETURN_OF_CAPITAL
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def _clear_fund_cache(self, fund_id: int) -> None:
        """Clear cache for events by fund."""
        for key in list(self._cache.keys()):
            if f"fund:{fund_id}" in key:
                self._cache.pop(key, None)
    
    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
