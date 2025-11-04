"""
Fund Financial Year Service.
"""

from src.fund.models import Fund
from src.fund.calculators.financial_year_calculator import FinancialYearCalculator
from datetime import date
from src.fund.services.fund_service import FundService
from sqlalchemy.orm import Session

class FundFinancialYearService:
    """
    Fund Financial Year Service.

    This module provides the FundFinancialYearService class, which handles fund financial year operations and business logic.
    The service provides clean separation of concerns for:
    - Get the financial years for a fund

    The service uses the FinancialYearCalculator to perform operations.
    """
    def __init__(self):
        """
        Initialize the FundFinancialYearService.

        Args:
            financial_year_calculator: Financial year calculator to use
            fund_service: Fund service to use
        """
        self.financial_year_calculator = FinancialYearCalculator()
        self.fund_service = FundService()

    def get_financial_years_for_fund(self, fund_id: int, session: Session) -> list[str]:
        """Get the financial years for a fund.

        Args:
            fund_id: ID of the fund
            session: Database session

        Returns:
            List[str]: List of financial years

        Raises:
            ValueError: If fund start date or tax statement financial year type is not set
        """
        fund = self.fund_service.get_fund_by_id(fund_id, session)
        if not fund.start_date:
            raise ValueError("Fund start date is required")
        if not fund.tax_statement_financial_year_type:
            raise ValueError("Fund tax statement financial year type is required")

        start_date = fund.start_date
        end_date = date.today() if not fund.end_date else fund.end_date
        financial_years = self.financial_year_calculator.calculate_financial_years_for_fund(start_date, end_date, fund.tax_statement_financial_year_type)
        return financial_years