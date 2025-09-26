"""
Risk Free Rate Service.

This module provides the risk free rate service,
representing risk free rates in the system.
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from src.shared.enums.shared_enums import Currency
from src.rates.enums.risk_free_rate_enums import RiskFreeRateType, SortFieldRiskFreeRate
from src.shared.enums.shared_enums import SortOrder
from src.rates.models import RiskFreeRate
from src.rates.repositories import RiskFreeRateRepository

class RiskFreeRateService:
    """Risk Free Rate Service."""

    def __init__(self):
        """Initialize the Risk Free Rate Service."""
        self.risk_free_rate_repository = RiskFreeRateRepository()


    ################################################################################
    # Get Risk Free Rates
    ################################################################################

    def get_risk_free_rates(self, session: Session,
        currency: Optional[Currency] = None,
        rate_type: Optional[RiskFreeRateType] = None,
        sort_by: Optional[SortFieldRiskFreeRate] = SortFieldRiskFreeRate.DATE,
        sort_order: Optional[SortOrder] = SortOrder.ASC
    ) -> List[RiskFreeRate]:
        """
        Get risk free rates.

        Args:
            session: Database session
            currency: Currency of the risk free rates to retrieve
            rate_type: Type of the risk free rates to retrieve
            sort_by: Field to sort by
            sort_order: Order to sort by

        Returns:
            List of risk free rates
        """
        return self.risk_free_rate_repository.get_risk_free_rates(session, currency, rate_type, sort_by, sort_order)

    def get_risk_free_rate_by_id(self, risk_free_rate_id: int, session: Session) -> Optional[RiskFreeRate]:
        """
        Get a risk free rate by its ID.

        Args:
            risk_free_rate_id: ID of the risk free rate to retrieve
            session: Database session
        Returns:
            Risk free rate if found, None otherwise
        """
        return self.risk_free_rate_repository.get_risk_free_rate_by_id(risk_free_rate_id, session)

    ################################################################################
    # Create Risk Free Rate
    ################################################################################

    def create_risk_free_rate(self, risk_free_rate_data: Dict[str, Any], session: Session) -> RiskFreeRate:
        """
        Create a new risk free rate.

        Args:
            risk_free_rate_data: Data to create a risk free rate
            session: Database session

        Returns:
            Risk free rate if created, None otherwise
        """
        risk_free_rate = self.risk_free_rate_repository.create_risk_free_rate(risk_free_rate_data, session)
        if not risk_free_rate:
            raise ValueError(f"Failed to create risk free rate")

        return risk_free_rate


    ################################################################################
    # Delete Risk Free Rate
    ################################################################################

    def delete_risk_free_rate(self, risk_free_rate_id: int, session: Session) -> bool:
        """
        Delete a risk free rate.

        Args:
            risk_free_rate_id: ID of the risk free rate to delete
            session: Database session

        Returns:
            True if deleted, False otherwise
        """
        risk_free_rate = self.get_risk_free_rate_by_id(risk_free_rate_id, session)
        if not risk_free_rate:
            raise ValueError(f"Risk free rate not found")

        success = self.risk_free_rate_repository.delete_risk_free_rate(risk_free_rate_id, session)
        if not success:
            raise ValueError(f"Failed to delete risk free rate")

        return success