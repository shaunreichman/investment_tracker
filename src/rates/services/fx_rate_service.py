"""
FX Rate Service.
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date

from src.shared.enums.shared_enums import Currency
from src.rates.enums.fx_rate_enums import SortFieldFxRate
from src.shared.enums.shared_enums import SortOrder
from src.rates.models import FxRate
from src.rates.repositories.fx_rate_repository import FxRateRepository


class FxRateService:
    """
    FX Rate Service.

    This module provides the FxRateService class, which handles FX rate operations and business logic.
    The service provides clean separation of concerns for:
    - FX rate retrieval
    - FX rate creation
    - FX rate deletion

    The service uses the FxRateRepository to perform CRUD operations.
    The service is used by the FxRateController to handle FX rate operations.
    """

    def __init__(self):
        """
        Initialize the FX Rate Service.

        Args:
            fx_rate_repository: FX rate repository to use. If None, creates a new one.
        """
        self.fx_rate_repository = FxRateRepository()


    ################################################################################
    # Get FX Rates
    ################################################################################

    def get_fx_rates(self, session: Session,
        from_currency: Optional[Currency] = None,
        to_currency: Optional[Currency] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sort_by: Optional[SortFieldFxRate] = SortFieldFxRate.DATE,
        sort_order: Optional[SortOrder] = SortOrder.ASC
    ) -> List[FxRate]:
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
        return self.fx_rate_repository.get_fx_rates(session, from_currency, to_currency, start_date, end_date, sort_by, sort_order)

    def get_fx_rate_by_id(self, fx_rate_id: int, session: Session) -> Optional[FxRate]:
        """
        Get a FX rate by its ID.

        Args:
            fx_rate_id: ID of the FX rate to retrieve
            session: Database session

        Returns:
            FX rate if found, None otherwise
        """
        return self.fx_rate_repository.get_fx_rate_by_id(fx_rate_id, session)

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
        fx_rate = self.fx_rate_repository.create_fx_rate(fx_rate_data, session)
        if not fx_rate:
            raise ValueError(f"Failed to create FX rate")

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
        success = self.fx_rate_repository.delete_fx_rate(fx_rate_id, session)
        if not success:
            raise ValueError(f"Failed to delete FX rate")

        return success