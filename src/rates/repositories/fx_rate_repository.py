"""
FX Rate Repository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date

from src.rates.models import FxRate
from src.shared.enums.shared_enums import Currency, SortOrder
from src.rates.enums.fx_rate_enums import SortFieldFxRate

class FxRateRepository:
    """
    FX Rate Repository.

    This repository handles all database operations for FX rates including
    CRUD operations, complex queries. It provides
    a clean interface for business logic components to interact with
    FX rate data without direct database access.
    """
    def __init__(self):
        """
        Initialize the FX Rate Repository.

        Args:
            None
        """
        pass

    ################################################################################
    # Get FX Rates
    ################################################################################

    def get_fx_rates(self, session: Session,
                        from_currency: Optional[Currency] = None,
                        to_currency: Optional[Currency] = None,
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None,
                        sort_by: Optional[SortFieldFxRate] = SortFieldFxRate.DATE,
                        sort_order: Optional[SortOrder] = SortOrder.ASC) -> List[FxRate]:
        """
        Get FX rates.

        Args:
            session: Database session
            from_currency: Currency of the FX rates to retrieve
            to_currency: Currency of the FX rates to retrieve
            start_date: Start date of the FX rates to retrieve
            end_date: End date of the FX rates to retrieve
            sort_by: Field to sort by
            sort_order: Order to sort by

        Returns:
            List of FX rates
        """
        # Validate sort field
        if sort_by not in SortFieldFxRate:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")
        
        # Get all FX rates
        fx_rates = session.query(FxRate)
        if from_currency:
            fx_rates = fx_rates.filter(FxRate.from_currency == from_currency.value)
        if to_currency:
            fx_rates = fx_rates.filter(FxRate.to_currency == to_currency.value)
        if start_date:
            fx_rates = fx_rates.filter(FxRate.date >= start_date)
        if end_date:
            fx_rates = fx_rates.filter(FxRate.date <= end_date)
        
        # Apply sorting
        if sort_by == SortFieldFxRate.DATE:
            fx_rates = fx_rates.order_by(FxRate.date.asc() if sort_order == SortOrder.ASC else FxRate.date.desc())
        elif sort_by == SortFieldFxRate.FROM_CURRENCY:
            fx_rates = fx_rates.order_by(FxRate.from_currency.asc() if sort_order == SortOrder.ASC else FxRate.from_currency.desc())
        elif sort_by == SortFieldFxRate.TO_CURRENCY:
            fx_rates = fx_rates.order_by(FxRate.to_currency.asc() if sort_order == SortOrder.ASC else FxRate.to_currency.desc())
        
        fx_rates = fx_rates.all()

        return fx_rates
    
    def get_fx_rate_by_id(self, fx_rate_id: int, session: Session) -> Optional[FxRate]:
        """
        Get a FX rate by its ID.

        Args:
            fx_rate_id: ID of the FX rate to retrieve
            session: Database session

        Returns:
            FX rate if found, None otherwise
        """
        # Query database
        fx_rate = session.query(FxRate).filter(FxRate.id == fx_rate_id).first()

        return fx_rate
    

    ################################################################################
    # Create FX Rate
    ################################################################################

    def create_fx_rate(self, fx_rate_data: Dict[str, Any], session: Session) -> FxRate:
        """
        Create a new FX rate.

        Args:
            fx_rate_data: Dictionary containing FX rate data
            session: Database session

        Returns:
            Created FX rate
        """
        fx_rate = FxRate(**fx_rate_data)
        session.add(fx_rate)
        session.flush()

        return fx_rate
    

    ################################################################################
    # Delete FX Rate
    ################################################################################

    def delete_fx_rate(self, fx_rate_id: int, session: Session) -> bool:
        """
        Delete a FX rate.

        Args:
            fx_rate_id: ID of the FX rate to delete
            session: Database session

        Returns:
            True if deleted, False otherwise
        """
        fx_rate = self.get_fx_rate_by_id(fx_rate_id, session)
        if not fx_rate:
            return False

        session.delete(fx_rate)
        session.flush()

        return True