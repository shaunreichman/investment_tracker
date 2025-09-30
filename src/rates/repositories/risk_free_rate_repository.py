"""
Risk Free Rate Repository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date

from src.rates.models import RiskFreeRate
from src.shared.enums.shared_enums import Currency, SortOrder
from src.rates.enums.risk_free_rate_enums import RiskFreeRateType, SortFieldRiskFreeRate

class RiskFreeRateRepository:
    """
    Risk Free Rate Repository.

    This repository handles all database operations for risk free rates including
    CRUD operations, complex queries. It provides
    a clean interface for business logic components to interact with
    risk free rate data without direct database access.
    """
    def __init__(self):
        """
        Initialize the Risk Free Rate Repository.

        Args:
            None
        """
        pass


    ################################################################################
    # Get Risk Free Rates
    ################################################################################

    def get_risk_free_rates(self, session: Session,
                            currency: Optional[Currency] = None,
                            rate_type: Optional[RiskFreeRateType] = None,
                            sort_by: Optional[SortFieldRiskFreeRate] = SortFieldRiskFreeRate.DATE,
                            sort_order: Optional[SortOrder] = SortOrder.ASC) -> List[RiskFreeRate]:
        """
        Get risk free rates.

        Args:
            session: Database session
            currency: Currency of the risk free rates to retrieve
            rate_type: Type of the risk free rates to retrieve
        Returns:
            List of risk free rates
        """
        # Validate sort field
        if sort_by not in SortFieldRiskFreeRate:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")
        
        # Get all risk free rates
        risk_free_rates = session.query(RiskFreeRate)
        if currency:
            risk_free_rates = risk_free_rates.filter(RiskFreeRate.currency == currency.value)
        if rate_type:
            risk_free_rates = risk_free_rates.filter(RiskFreeRate.rate_type == rate_type.value)

        # Apply sorting
        if sort_by == SortFieldRiskFreeRate.DATE:
            risk_free_rates = risk_free_rates.order_by(RiskFreeRate.date.asc() if sort_order == SortOrder.ASC else RiskFreeRate.date.desc())
        elif sort_by == SortFieldRiskFreeRate.CURRENCY:
            risk_free_rates = risk_free_rates.order_by(RiskFreeRate.currency.asc() if sort_order == SortOrder.ASC else RiskFreeRate.currency.desc())

        risk_free_rates = risk_free_rates.all()

        return risk_free_rates

    def get_risk_free_rate_by_id(self, risk_free_rate_id: int, session: Session) -> Optional[RiskFreeRate]:
        """
        Get a risk free rate by its ID.

        Args:
            risk_free_rate_id: ID of the risk free rate to retrieve
            session: Database session

        Returns:
            Risk free rate if found, None otherwise
        """
        # Query database
        risk_free_rate = session.query(RiskFreeRate).filter(RiskFreeRate.id == risk_free_rate_id).first()
        
        return risk_free_rate


    ################################################################################
    # Create Risk Free Rate
    ################################################################################

    def create_risk_free_rate(self, risk_free_rate_data: Dict[str, Any], session: Session) -> RiskFreeRate:
        """
        Create a new risk free rate.

        Args:
            risk_free_rate_data: Dictionary containing risk free rate data
            session: Database session

        Returns:
            Risk free rate if created, None otherwise
        """
        risk_free_rate = RiskFreeRate(**risk_free_rate_data)
        session.add(risk_free_rate)
        session.flush()

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
            return False

        session.delete(risk_free_rate)
        session.flush()

        return True