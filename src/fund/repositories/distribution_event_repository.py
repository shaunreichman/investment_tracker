"""
Distribution Event Repository.

This repository provides data access operations for distribution-related fund events
(DISTRIBUTION), implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Distribution event CRUD operations
- Distribution event querying and filtering
- Distribution event aggregations
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.fund.models import FundEvent, DistributionType
from src.fund.enums import EventType, TaxPaymentType, GroupType
from src.fund.repositories import FundEventRepository


class DistributionEventRepository:
    """
    Repository for distribution event data access operations.
    
    This repository handles all database operations for distribution events including
    CRUD operations, bulk operations, and optimized queries for distribution event processing.
    It provides a clean interface for business logic components to interact with
    distribution event data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the distribution event repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def create_distribution(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> 'FundEvent':
        """
        Create a new distribution event and handle tax event creation/grouping if applicable.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing distribution event data
            session: Database session
            
        Returns:
            Created FundEvent object (the distribution event)
            
        Raises:
            TypeError: If event_data is not a dictionary
            ValueError: If required fields are missing
        """
        # Type validation - ensure event_data is a dictionary
        if not isinstance(event_data, dict):
            raise TypeError(f"event_data must be a dictionary, got {type(event_data).__name__}")
        
        # Validate required fields
        required_fields = ['fund_id', 'event_type', 'event_date', 'amount']
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Ensure event_type is DISTRIBUTION
        if event_data.get('event_type') != EventType.DISTRIBUTION:
            raise ValueError(f"Event type must be DISTRIBUTION, got {event_data.get('event_type')}")

        if event_data.get('has_withholding_tax') and event_data.get('distribution_type') == DistributionType.INTEREST.value:
            # Generate the necessary Group ID
            fund_event_repo = FundEventRepository()
            group_id = fund_event_repo.generate_group_id(session)

            # Create the Interest Distribution Event
            event_data['is_grouped'] = True
            event_data['group_id'] = group_id
            event_data['group_type'] = GroupType.INTEREST_WITHHOLDING
            event_data['group_position'] = 0
            distribution_event = FundEvent(**event_data)
            session.add(distribution_event)
            session.flush()

            # Create the Tax Event
            tax_event_data = dict()
            tax_event_data['event_type'] = EventType.TAX_PAYMENT
            tax_event_data['event_date'] = event_data.get('event_date')
            tax_event_data['fund_id'] = fund_id
            tax_event_data['description'] = event_data.get('description')
            tax_event_data['reference_number'] = event_data.get('reference_number')
            tax_event_data['amount'] = -event_data.get('tax_withholding', 0)
            tax_event_data['tax_payment_type'] = TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
            tax_event_data['is_grouped'] = True
            tax_event_data['group_id'] = group_id
            tax_event_data['group_type'] = GroupType.INTEREST_WITHHOLDING
            tax_event_data['group_position'] = 1

            from src.fund.repositories import TaxEventRepository
            tax_event_repo = TaxEventRepository()
            tax_event = tax_event_repo.create_tax_payment(fund_id, tax_event_data, session)
            
            self._clear_fund_cache(fund_id)
            self._clear_date_cache(event_data.get('event_date'))
            self._clear_type_cache(EventType.DISTRIBUTION)
            
            return distribution_event
        
        else:
            # Create the Distribution Event
            distribution_event = FundEvent(**event_data)
            session.add(distribution_event)
            session.flush()
            
            # Clear relevant caches
            self._clear_fund_cache(fund_id)
            self._clear_date_cache(event_data.get('event_date'))
            self._clear_type_cache(EventType.DISTRIBUTION)
            
            return distribution_event
    
    def get_by_fund(self, fund_id: int, session: Session) -> List[FundEvent]:
        """
        Get all distribution events for a specific fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            List of FundEvent objects
        """
        cache_key = f"distributions_fund_{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.DISTRIBUTION
            )
        ).order_by(FundEvent.event_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_by_fund_and_date_range(self, fund_id: int, start_date: date, end_date: date, 
                                 session: Session) -> List[FundEvent]:
        """
        Get distribution events for a fund within a date range.
        
        Args:
            fund_id: ID of the fund
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            session: Database session
            
        Returns:
            List of FundEvent objects
        """
        cache_key = f"distributions_fund_{fund_id}_dates_{start_date}_{end_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.DISTRIBUTION,
                FundEvent.event_date >= start_date,
                FundEvent.event_date <= end_date
            )
        ).order_by(FundEvent.event_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_total_distributions(self, fund_id: int, session: Session) -> float:
        """
        Get total distribution amount for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Total distribution amount
        """
        cache_key = f"total_distributions_fund_{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        result = session.query(func.sum(FundEvent.amount)).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.DISTRIBUTION
            )
        ).scalar()
        
        total = float(result) if result else 0.0
        
        # Cache the result
        self._cache[cache_key] = total
        
        return total
    
    def _clear_fund_cache(self, fund_id: int) -> None:
        """Clear cache entries for a specific fund."""
        keys_to_remove = [key for key in self._cache.keys() if f"fund_{fund_id}" in key]
        for key in keys_to_remove:
            del self._cache[key]
    
    def _clear_date_cache(self, event_date: date) -> None:
        """Clear cache entries for a specific date."""
        if event_date:
            keys_to_remove = [key for key in self._cache.keys() if str(event_date) in key]
            for key in keys_to_remove:
                del self._cache[key]
    
    def _clear_type_cache(self, event_type: EventType) -> None:
        """Clear cache entries for a specific event type."""
        if event_type == EventType.DISTRIBUTION:
            keys_to_remove = [key for key in self._cache.keys() if "distributions" in key]
            for key in keys_to_remove:
                del self._cache[key]

    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
