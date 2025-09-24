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
from src.fund.enums import EventType, SortFieldFund
from src.shared.enums.shared_enums import SortOrder

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
        
    def _clear_fund_cache(self, fund_id: int) -> None:
        """Clear cache for events by fund."""
        for key in list(self._cache.keys()):
            if f"fund:{fund_id}" in key:
                self._cache.pop(key, None)
    
    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
