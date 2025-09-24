"""
Unit Event Repository.

This repository provides data access operations for unit-related fund events
(UNIT_PURCHASE, UNIT_SALE, NAV_UPDATE), implementing the repository pattern for 
clean separation of concerns.

Key responsibilities:
- Unit event CRUD operations
- Unit event querying and filtering
- Unit event aggregations
- NAV update operations
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.fund.models import FundEvent
from src.fund.enums import EventType, SortFieldFund
from src.shared.enums.shared_enums import SortOrder

class UnitEventRepository:
    """
    Repository for unit event data access operations.
    
    This repository handles all database operations for unit events including
    CRUD operations, bulk operations, and optimized queries for unit event processing.
    It provides a clean interface for business logic components to interact with
    unit event data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the unit event repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def create_unit_purchase(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a unit purchase event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created unit purchase event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.UNIT_PURCHASE
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def create_unit_sale(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a unit sale event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created unit sale event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.UNIT_SALE
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def create_nav_update(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a NAV update event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created NAV update event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.NAV_UPDATE
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
