"""
Financial Year Calculator.

This module contains the financial year calculator class.
"""

from datetime import date
from src.fund.enums.fund_enums import FundTaxStatementFinancialYearType

class FinancialYearCalculator:
    """
    Financial year calculator class.
    """
    @staticmethod
    def calculate_financial_year_dates(financial_year: str, tax_statement_financial_year_type: FundTaxStatementFinancialYearType) -> tuple[date, date]:
        """
        Calculate the start and end dates for a financial year based on tax jurisdiction.
        """
        # Validate input
        if len(financial_year) != 4:
            raise ValueError("Financial year must be 4 digits")
        if tax_statement_financial_year_type not in FundTaxStatementFinancialYearType:
            raise ValueError("Invalid tax statement financial year type")

        if tax_statement_financial_year_type == FundTaxStatementFinancialYearType.HALF_YEAR:
            fy_start = date(int(financial_year), 7, 1)
            fy_end = date(int(financial_year) + 1, 6, 30)
        elif tax_statement_financial_year_type == FundTaxStatementFinancialYearType.CALENDAR_YEAR:
            fy_start = date(int(financial_year), 1, 1)
            fy_end = date(int(financial_year), 12, 31)

        return fy_start, fy_end