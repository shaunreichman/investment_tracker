"""
Tests for FinancialYearCalculator.

Tests the pure mathematical calculations for financial year date calculations.
"""

import pytest
from datetime import date

from src.fund.calculators.financial_year_calculator import FinancialYearCalculator
from src.fund.enums.fund_enums import FundTaxStatementFinancialYearType


class TestFinancialYearCalculator:
    """Test cases for FinancialYearCalculator."""
    
    def test_calculate_financial_year_dates_half_year_basic(self):
        """Test basic half-year financial year calculation.
        
        Note: financial_year represents the END year.
        So "2023" means July 1, 2022 to June 30, 2023.
        """
        # Setup
        financial_year = "2023"
        tax_statement_financial_year_type = FundTaxStatementFinancialYearType.HALF_YEAR
        
        # Execute
        fy_start, fy_end = FinancialYearCalculator.calculate_financial_year_dates(
            financial_year, tax_statement_financial_year_type
        )
        
        # Verify - financial year "2023" represents the END year
        assert fy_start == date(2022, 7, 1)  # July 1 of year BEFORE
        assert fy_end == date(2023, 6, 30)   # June 30 of the END year
    
    def test_calculate_financial_year_dates_calendar_year_basic(self):
        """Test basic calendar year financial year calculation."""
        # Setup
        financial_year = "2023"
        tax_statement_financial_year_type = FundTaxStatementFinancialYearType.CALENDAR_YEAR
        
        # Execute
        fy_start, fy_end = FinancialYearCalculator.calculate_financial_year_dates(
            financial_year, tax_statement_financial_year_type
        )
        
        # Verify
        assert fy_start == date(2023, 1, 1)
        assert fy_end == date(2023, 12, 31)
    
    def test_calculate_financial_year_dates_half_year_different_years(self):
        """Test half-year financial year calculation for different years.
        
        Note: financial_year represents the END year.
        """
        # Test cases: (financial_year, expected_start, expected_end)
        test_cases = [
            ("2020", date(2019, 7, 1), date(2020, 6, 30)),
            ("2021", date(2020, 7, 1), date(2021, 6, 30)),
            ("2022", date(2021, 7, 1), date(2022, 6, 30)),
            ("2024", date(2023, 7, 1), date(2024, 6, 30)),
            ("2030", date(2029, 7, 1), date(2030, 6, 30)),
        ]
        
        for financial_year, expected_start, expected_end in test_cases:
            # Execute
            fy_start, fy_end = FinancialYearCalculator.calculate_financial_year_dates(
                financial_year, FundTaxStatementFinancialYearType.HALF_YEAR
            )
            
            # Verify
            assert fy_start == expected_start, f"Failed for year {financial_year}"
            assert fy_end == expected_end, f"Failed for year {financial_year}"
    
    def test_calculate_financial_year_dates_calendar_year_different_years(self):
        """Test calendar year financial year calculation for different years."""
        # Test cases: (financial_year, expected_start, expected_end)
        test_cases = [
            ("2020", date(2020, 1, 1), date(2020, 12, 31)),
            ("2021", date(2021, 1, 1), date(2021, 12, 31)),
            ("2022", date(2022, 1, 1), date(2022, 12, 31)),
            ("2024", date(2024, 1, 1), date(2024, 12, 31)),
            ("2030", date(2030, 1, 1), date(2030, 12, 31)),
        ]
        
        for financial_year, expected_start, expected_end in test_cases:
            # Execute
            fy_start, fy_end = FinancialYearCalculator.calculate_financial_year_dates(
                financial_year, FundTaxStatementFinancialYearType.CALENDAR_YEAR
            )
            
            # Verify
            assert fy_start == expected_start, f"Failed for year {financial_year}"
            assert fy_end == expected_end, f"Failed for year {financial_year}"
    
    def test_calculate_financial_year_dates_leap_year_half_year(self):
        """Test half-year financial year calculation with leap year.
        
        Note: financial_year represents the END year.
        """
        # Setup - 2024 is a leap year (END year)
        financial_year = "2024"
        tax_statement_financial_year_type = FundTaxStatementFinancialYearType.HALF_YEAR
        
        # Execute
        fy_start, fy_end = FinancialYearCalculator.calculate_financial_year_dates(
            financial_year, tax_statement_financial_year_type
        )
        
        # Verify - financial year "2024" (leap year) represents the END year
        assert fy_start == date(2023, 7, 1)  # Start in previous year
        assert fy_end == date(2024, 6, 30)   # End in leap year (June 30 is always valid)
    
    def test_calculate_financial_year_dates_leap_year_calendar_year(self):
        """Test calendar year financial year calculation with leap year."""
        # Setup - 2024 is a leap year
        financial_year = "2024"
        tax_statement_financial_year_type = FundTaxStatementFinancialYearType.CALENDAR_YEAR
        
        # Execute
        fy_start, fy_end = FinancialYearCalculator.calculate_financial_year_dates(
            financial_year, tax_statement_financial_year_type
        )
        
        # Verify
        assert fy_start == date(2024, 1, 1)
        assert fy_end == date(2024, 12, 31)  # December 31 is always valid
    
    def test_calculate_financial_year_dates_invalid_financial_year_length(self):
        """Test validation for invalid financial year string length."""
        # Test cases: (invalid_financial_year, expected_error_message)
        test_cases = [
            ("", "Financial year must be 4 digits"),
            ("23", "Financial year must be 4 digits"),
            ("202", "Financial year must be 4 digits"),
            ("20234", "Financial year must be 4 digits"),
        ]
        
        for invalid_financial_year, expected_error_message in test_cases:
            # Execute & Verify
            with pytest.raises(ValueError, match=expected_error_message):
                FinancialYearCalculator.calculate_financial_year_dates(
                    invalid_financial_year, FundTaxStatementFinancialYearType.CALENDAR_YEAR
                )
    
    def test_calculate_financial_year_dates_invalid_financial_year_non_numeric(self):
        """Test validation for non-numeric financial year string."""
        # Test cases: (invalid_financial_year, expected_error_message)
        test_cases = [
            ("abcd", "invalid literal for int\\(\\) with base 10: 'abcd'"),
            ("202a", "invalid literal for int\\(\\) with base 10: '202a'"),
            ("a023", "invalid literal for int\\(\\) with base 10: 'a023'"),
            ("20a3", "invalid literal for int\\(\\) with base 10: '20a3'"),
            ("2023a", "Financial year must be 4 digits"),  # This one fails length check first
        ]
        
        for invalid_financial_year, expected_error_message in test_cases:
            # Execute & Verify
            with pytest.raises(ValueError, match=expected_error_message):
                FinancialYearCalculator.calculate_financial_year_dates(
                    invalid_financial_year, FundTaxStatementFinancialYearType.CALENDAR_YEAR
                )
    
    def test_calculate_financial_year_dates_invalid_tax_statement_type(self):
        """Test validation for invalid tax statement financial year type."""
        # Setup
        financial_year = "2023"
        invalid_tax_statement_type = "INVALID_TYPE"  # Not a valid enum value
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Invalid tax statement financial year type"):
            FinancialYearCalculator.calculate_financial_year_dates(
                financial_year, invalid_tax_statement_type
            )
    
    def test_calculate_financial_year_dates_none_tax_statement_type(self):
        """Test validation for None tax statement financial year type."""
        # Setup
        financial_year = "2023"
        tax_statement_type = None
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Invalid tax statement financial year type"):
            FinancialYearCalculator.calculate_financial_year_dates(
                financial_year, tax_statement_type
            )
    
    def test_calculate_financial_year_dates_boundary_years(self):
        """Test financial year calculation for boundary years.
        
        Note: For HALF_YEAR type, financial_year represents the END year.
        """
        # Test very early and very late years
        test_cases = [
            ("1900", FundTaxStatementFinancialYearType.CALENDAR_YEAR, date(1900, 1, 1), date(1900, 12, 31)),
            ("1900", FundTaxStatementFinancialYearType.HALF_YEAR, date(1899, 7, 1), date(1900, 6, 30)),
            ("2099", FundTaxStatementFinancialYearType.CALENDAR_YEAR, date(2099, 1, 1), date(2099, 12, 31)),
            ("2099", FundTaxStatementFinancialYearType.HALF_YEAR, date(2098, 7, 1), date(2099, 6, 30)),
        ]
        
        for financial_year, tax_type, expected_start, expected_end in test_cases:
            # Execute
            fy_start, fy_end = FinancialYearCalculator.calculate_financial_year_dates(
                financial_year, tax_type
            )
            
            # Verify
            assert fy_start == expected_start, f"Failed for year {financial_year} with type {tax_type}"
            assert fy_end == expected_end, f"Failed for year {financial_year} with type {tax_type}"
    
    def test_calculate_financial_year_dates_return_type(self):
        """Test that the method returns the correct tuple type."""
        # Setup
        financial_year = "2023"
        tax_statement_financial_year_type = FundTaxStatementFinancialYearType.CALENDAR_YEAR
        
        # Execute
        result = FinancialYearCalculator.calculate_financial_year_dates(
            financial_year, tax_statement_financial_year_type
        )
        
        # Verify
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], date)
        assert isinstance(result[1], date)
    
    def test_calculate_financial_year_dates_consistency(self):
        """Test that the same input always produces the same output."""
        # Setup
        financial_year = "2023"
        tax_statement_financial_year_type = FundTaxStatementFinancialYearType.HALF_YEAR
        
        # Execute multiple times
        result1 = FinancialYearCalculator.calculate_financial_year_dates(
            financial_year, tax_statement_financial_year_type
        )
        result2 = FinancialYearCalculator.calculate_financial_year_dates(
            financial_year, tax_statement_financial_year_type
        )
        
        # Verify
        assert result1 == result2
        assert result1[0] == result2[0]  # Start dates match
        assert result1[1] == result2[1]  # End dates match
    
    def test_calculate_financial_year_dates_half_year_vs_calendar_year_difference(self):
        """Test that half-year and calendar year produce different results for the same year.
        
        Note: For HALF_YEAR type, financial_year represents the END year.
        So "2023" means:
        - HALF_YEAR: July 1, 2022 to June 30, 2023
        - CALENDAR_YEAR: Jan 1, 2023 to Dec 31, 2023
        """
        # Setup
        financial_year = "2023"
        
        # Execute
        half_year_result = FinancialYearCalculator.calculate_financial_year_dates(
            financial_year, FundTaxStatementFinancialYearType.HALF_YEAR
        )
        calendar_year_result = FinancialYearCalculator.calculate_financial_year_dates(
            financial_year, FundTaxStatementFinancialYearType.CALENDAR_YEAR
        )
        
        # Verify
        assert half_year_result != calendar_year_result
        assert half_year_result[0] != calendar_year_result[0]  # Different start dates
        assert half_year_result[1] != calendar_year_result[1]  # Different end dates
        
        # Half year should start EARLIER (July 2022) than calendar year (Jan 2023)
        # But half year should end EARLIER (June 2023) than calendar year (Dec 2023)
        assert half_year_result[0] < calendar_year_result[0]  # July 1, 2022 < January 1, 2023
        assert half_year_result[1] < calendar_year_result[1]  # June 30, 2023 < December 31, 2023
    
    def test_calculate_financial_year_dates_half_year_span(self):
        """Test that half-year financial year spans exactly 12 months.
        
        Note: financial_year represents the END year.
        So "2023" means July 1, 2022 to June 30, 2023.
        """
        # Setup
        financial_year = "2023"
        tax_statement_financial_year_type = FundTaxStatementFinancialYearType.HALF_YEAR
        
        # Execute
        fy_start, fy_end = FinancialYearCalculator.calculate_financial_year_dates(
            financial_year, tax_statement_financial_year_type
        )
        
        # Verify - Calculate the difference in days
        from datetime import timedelta
        span_days = (fy_end - fy_start).days + 1  # +1 to include both start and end dates
        
        # Half year should span 365 days (or 366 in leap year)
        # Since we're testing July 2022 -> June 2023, neither year is a leap year, so 365 days
        assert span_days == 365
    
    def test_calculate_financial_year_dates_calendar_year_span(self):
        """Test that calendar year financial year spans exactly 12 months."""
        # Setup
        financial_year = "2023"
        tax_statement_financial_year_type = FundTaxStatementFinancialYearType.CALENDAR_YEAR
        
        # Execute
        fy_start, fy_end = FinancialYearCalculator.calculate_financial_year_dates(
            financial_year, tax_statement_financial_year_type
        )
        
        # Verify - Calculate the difference in days
        from datetime import timedelta
        span_days = (fy_end - fy_start).days + 1  # +1 to include both start and end dates
        
        # Calendar year should span 365 days (or 366 in leap year)
        # Since we're testing 2023, it should be 365 days
        assert span_days == 365
