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
        
        The financial_year parameter represents the END year of the financial year.
        For example, financial year "2024" with HALF_YEAR means:
        - Start: July 1, 2023
        - End: June 30, 2024
        """
        # Validate input
        if len(financial_year) != 4:
            raise ValueError("Financial year must be 4 digits")
        if tax_statement_financial_year_type not in FundTaxStatementFinancialYearType:
            raise ValueError("Invalid tax statement financial year type")

        end_year = int(financial_year)
        
        if tax_statement_financial_year_type == FundTaxStatementFinancialYearType.HALF_YEAR:
            # Financial year ends in the given year, starts the year before
            fy_start = date(end_year - 1, 7, 1)  # July 1 of previous year
            fy_end = date(end_year, 6, 30)       # June 30 of given year
        elif tax_statement_financial_year_type == FundTaxStatementFinancialYearType.CALENDAR_YEAR:
            # Financial year is the same as calendar year
            fy_start = date(end_year, 1, 1)      # January 1 of given year
            fy_end = date(end_year, 12, 31)      # December 31 of given year

        return fy_start, fy_end