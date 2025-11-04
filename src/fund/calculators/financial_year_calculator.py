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


    @staticmethod
    def calculate_financial_years_for_fund(start_date: date, end_date: date, tax_statement_financial_year_type: FundTaxStatementFinancialYearType) -> list[str]:
        """
        Calculate the financial years for a fund.
        """
        financial_years = []
        if tax_statement_financial_year_type == FundTaxStatementFinancialYearType.HALF_YEAR:
            financial_year_start = start_date.year + 1 if start_date.month >= 7 else start_date.year
            financial_year_end = end_date.year + 1 if end_date.month >= 7 else end_date.year
        elif tax_statement_financial_year_type == FundTaxStatementFinancialYearType.CALENDAR_YEAR:
            financial_year_start = start_date.year
            financial_year_end = end_date.year
        
        # Append all the financial years between the start and end financial years
        for year in range(financial_year_start, financial_year_end + 1):
            financial_years.append(str(year))
        return financial_years