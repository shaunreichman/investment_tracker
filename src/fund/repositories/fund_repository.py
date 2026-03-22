"""
Fund Repository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from datetime import date

from src.fund.models import Fund
from src.fund.enums.fund_enums import FundStatus, FundTrackingType, SortFieldFund
from src.shared.enums.shared_enums import SortOrder


class FundRepository:
    """
    Fund Repository.

    This repository handles all database operations for funds including
    CRUD operations, complex queries. It provides
    a clean interface for business logic components to interact with
    fund data without direct database access.
    """
    
    def __init__(self):
        """
        Initialize the fund repository.
        
        Args:
            None
        """
        pass

    ################################################################################
    # Get Fund
    ################################################################################

    def get_funds(self, session: Session,
                    company_ids: Optional[List[int]] = None,
                    entity_ids: Optional[List[int]] = None,
                    fund_statuses: Optional[List[FundStatus]] = None,
                    fund_tracking_types: Optional[List[FundTrackingType]] = None,
                    start_start_date: Optional[date] = None,
                    end_start_date: Optional[date] = None,
                    start_end_date: Optional[date] = None,
                    end_end_date: Optional[date] = None,
                    sort_by: Optional[SortFieldFund] = SortFieldFund.START_DATE,
                    sort_order: Optional[SortOrder] = SortOrder.ASC,
                    include_fund_events: Optional[bool] = False,
                    include_fund_event_cash_flows: Optional[bool] = False,
                    include_fund_tax_statements: Optional[bool] = False
    ) -> List[Fund]:
        """
        Get all funds.

        Args:
            session: Database session
            company_ids: List of company IDs to filter by (optional)
            entity_ids: List of entity IDs to filter by (optional)
            fund_statuses: List of fund status to filter by (optional)
            fund_tracking_types: List of fund tracking type to filter by (optional)
            start_start_date: Start start date to filter by (optional)
            end_start_date: End start date to filter by (optional)
            start_end_date: End end date to filter by (optional)
            end_end_date: End end date to filter by (optional)
            sort_by: Field to sort by (optional)
            sort_order: Sort order (ascending or descending) (optional)
            include_fund_events: Optional flag to eager load events relationship (optional)
            include_fund_event_cash_flows: Optional flag to eager load cash flows relationship (optional, requires include_fund_events=True)
            include_fund_tax_statements: Optional flag to eager load tax statements relationship (optional)

        Returns:
            List of funds
        """
        # Use defaults if None is explicitly passed (overrides function default)
        if sort_by is None:
            sort_by = SortFieldFund.START_DATE
        if sort_order is None:
            sort_order = SortOrder.ASC
        
        # Validate sort field
        if sort_by not in SortFieldFund:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        # Validate parameter dependencies
        if include_fund_event_cash_flows and not include_fund_events:
            raise ValueError("include_fund_event_cash_flows requires include_fund_events to be True")

        # Query database
        query = session.query(Fund)

        # Add eager loading for relationships if requested
        if include_fund_events:
            query = query.options(selectinload(Fund.fund_events))

        if include_fund_event_cash_flows:
            query = query.options(selectinload(Fund.fund_events).selectinload('fund_event_cash_flows'))

        if include_fund_tax_statements:
            query = query.options(selectinload(Fund.fund_tax_statements))

        if company_ids:
            query = query.filter(Fund.company_id.in_(company_ids))
        if entity_ids:
            query = query.filter(Fund.entity_id.in_(entity_ids))
        if fund_statuses:
            query = query.filter(Fund.status.in_([fs.value for fs in fund_statuses]))
        if fund_tracking_types:
            query = query.filter(Fund.tracking_type.in_([ftt.value for ftt in fund_tracking_types]))
        if start_start_date:
            query = query.filter(Fund.start_date >= start_start_date)
        if end_start_date:
            query = query.filter(Fund.start_date <= end_start_date)
        if start_end_date:
            query = query.filter(Fund.end_date >= start_end_date)
        if end_end_date:
            query = query.filter(Fund.end_date <= end_end_date)

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

        return funds
    
    def get_fund_by_id(self, fund_id: int, session: Session, include_fund_events: Optional[bool] = False, include_fund_event_cash_flows: Optional[bool] = False, include_fund_tax_statements: Optional[bool] = False) -> Optional[Fund]:
        """
        Get a fund by its ID.
        
        Args:
            fund_id: ID of the fund to retrieve
            session: Database session
            include_fund_events: Optional flag to eager load events relationship (optional)
            include_fund_event_cash_flows: Optional flag to eager load cash flows relationship (optional, requires include_fund_events=True)
            include_fund_tax_statements: Optional flag to eager load tax statements relationship (optional)

        Returns:
            Fund object if found, None otherwise
        """
        # Validate parameter dependencies
        if include_fund_event_cash_flows and not include_fund_events:
            raise ValueError("include_fund_event_cash_flows requires include_fund_events to be True")

        # Query database
        query = session.query(Fund).filter(Fund.id == fund_id)

        # Add eager loading for relationships if requested
        if include_fund_events:
            query = query.options(selectinload(Fund.fund_events))

        if include_fund_event_cash_flows:
            query = query.options(selectinload(Fund.fund_events).selectinload('fund_event_cash_flows'))
            
        if include_fund_tax_statements:
            query = query.options(selectinload(Fund.fund_tax_statements))
        
        fund = query.first()
        
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
        
        return True