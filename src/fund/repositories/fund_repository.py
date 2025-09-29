"""
Fund Repository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.fund.models import Fund
from src.fund.enums.fund_enums import FundStatus, FundTrackingType, SortFieldFund
from src.shared.enums.shared_enums import SortOrder


class FundRepository:
    """
    Fund Repository.

    This repository handles all database operations for funds including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    fund data without direct database access.
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the fund repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl

    ################################################################################
    # Get Fund
    ################################################################################

    def get_funds(self, session: Session,
                    company_id: Optional[int] = None,
                    entity_id: Optional[int] = None,
                    fund_status: Optional[FundStatus] = None,
                    fund_tracking_type: Optional[FundTrackingType] = None,
                    sort_by: SortFieldFund = SortFieldFund.START_DATE,
                    sort_order: SortOrder = SortOrder.ASC
    ) -> List[Fund]:
        """
        Get all funds.

        Args:
            session: Database session
            company_id: ID of the company to filter by (optional)
            entity_id: ID of the entity to filter by (optional)
            fund_status: Fund status to filter by (optional)
            fund_tracking_type: Fund tracking type to filter by (optional)
            sort_by: Field to sort by (optional)
            sort_order: Sort order (ascending or descending) (optional)
            
        Returns:
            List of funds
        """
        # Validate sort field
        if sort_by not in SortFieldFund:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        cache_key = f"funds:company:{company_id}:entity:{entity_id}:status:{fund_status.value if fund_status else None}:type:{fund_tracking_type.value if fund_tracking_type else None}:sort_by:{sort_by.value}:sort_order:{sort_order.value}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        query = session.query(Fund)

        if company_id:
            query = query.filter(Fund.investment_company_id == company_id)
        if entity_id:
            query = query.filter(Fund.entity_id == entity_id)
        if fund_status:
            query = query.filter(Fund.status == fund_status)
        if fund_tracking_type:
            query = query.filter(Fund.tracking_type == fund_tracking_type)
        
        # Apply sorting
        if sort_by == SortFieldFund.NAME:
            query = query.order_by(Fund.name.asc() if sort_order == SortOrder.ASC else Fund.name.desc())
        elif sort_by == SortFieldFund.STATUS:
            query = query.order_by(Fund.status.asc() if sort_order == SortOrder.ASC else Fund.status.desc())
        elif sort_by == SortFieldFund.CREATED_AT:
            query = query.order_by(Fund.created_at.asc() if sort_order == SortOrder.ASC else Fund.created_at.desc())
        elif sort_by == SortFieldFund.START_DATE:
            query = query.order_by(Fund.start_date.asc() if sort_order == SortOrder.ASC else Fund.start_date.desc())

        funds = query.all()

        # Cache the result
        self._cache[cache_key] = funds
        
        return funds
    
    def get_fund_by_id(self, fund_id: int, session: Session) -> Optional[Fund]:
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
        
        # Cache the result (including None results)
        self._cache[cache_key] = fund
        
        return fund


    ################################################################################
    # Create Fund
    ################################################################################
    
    def create_fund(self, fund_data: Dict[str, Any], session: Session) -> Fund:
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
        # Create fund object
        fund = Fund(**fund_data)
        session.add(fund)
        session.flush()  # Get the ID without committing
        
        # Clear relevant caches
        self._clear_fund_cache(fund.id)
        
        return fund


    ################################################################################
    # Delete Fund
    ################################################################################
    
    def delete_fund(self, fund_id: int, session: Session) -> bool:
        """
        Delete a fund.
        
        Args:
            fund_id: ID of the fund to delete
            session: Database session
            
        Returns:
            True if fund was deleted, False if not found
        """
        fund = self.get_fund_by_id(fund_id, session)
        if not fund:
            return False
                
        # Delete the fund
        session.delete(fund)
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return True
    

    ################################################################################
    # Clear Cache
    ################################################################################
    
    def _clear_fund_cache(self, fund_id: int) -> None:
        """Clear cache for a specific fund."""
        cache_key = f"fund:{fund_id}"
        self._cache.pop(cache_key, None)