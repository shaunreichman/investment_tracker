"""
Test Duration Months Calculator.

This module provides comprehensive tests for the DurationMonthsCalculator class.
"""

import pytest
from datetime import date

from src.shared.calculators.duration_months_calculator import DurationMonthsCalculator


class TestDurationMonthsCalculator:
    """
    Test cases for DurationMonthsCalculator.
    """

    def test_calculate_duration_months_same_date(self):
        """
        Test duration calculation when start and end dates are the same.
        """
        test_date = date(2024, 6, 15)
        result = DurationMonthsCalculator.calculate_duration_months(test_date, test_date)
        assert result == 0

    def test_calculate_duration_months_same_month_different_days(self):
        """
        Test duration calculation within the same month.
        """
        # Same month, later day
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 6, 10), date(2024, 6, 25)
        )
        assert result == 0

        # Same month, earlier day (should be 0 since we return max(0, result))
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 6, 25), date(2024, 6, 10)
        )
        assert result == 0

    def test_calculate_duration_months_exact_months(self):
        """
        Test duration calculation for exact month differences.
        """
        # Exactly 1 month later
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2024, 2, 15)
        )
        assert result == 1

        # Exactly 2 months later
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2024, 3, 15)
        )
        assert result == 2

        # Exactly 12 months later (1 year)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2025, 1, 15)
        )
        assert result == 12

        # Exactly 24 months later (2 years)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2026, 1, 15)
        )
        assert result == 24

    def test_calculate_duration_months_with_day_adjustment(self):
        """
        Test duration calculation with day-of-month adjustments.
        """
        # 1 month later but earlier day (should be 0 months)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 25), date(2024, 2, 15)  # 15 < 25
        )
        assert result == 0

        # 2 months later but earlier day (should be 1 month)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 25), date(2024, 3, 15)  # 15 < 25
        )
        assert result == 1

        # 1 month later with later day (should be 1 month)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2024, 2, 25)  # 25 >= 15
        )
        assert result == 1

        # 1 month later with same day (should be 1 month)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2024, 2, 15)  # 15 == 15
        )
        assert result == 1

    def test_calculate_duration_months_across_years(self):
        """
        Test duration calculation across different years.
        """
        # December to January (next year)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 12, 15), date(2025, 1, 15)
        )
        assert result == 1

        # December to February (next year)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 12, 15), date(2025, 2, 15)
        )
        assert result == 2

        # January to December (same year)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2024, 12, 15)
        )
        assert result == 11

        # Multiple years
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2022, 6, 15), date(2024, 6, 15)
        )
        assert result == 24

    def test_calculate_duration_months_leap_year_edge_cases(self):
        """
        Test duration calculation with leap year edge cases.
        """
        # February 29th in leap year to next year
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 2, 29), date(2025, 2, 28)  # 28 < 29, so 11 months
        )
        assert result == 11

        # February 28th in non-leap year to next year
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2023, 2, 28), date(2024, 2, 28)  # 28 == 28, so 12 months
        )
        assert result == 12

        # February 29th to March (leap year)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 2, 29), date(2024, 3, 29)  # 29 == 29, so 1 month
        )
        assert result == 1

        # February 28th to March (non-leap year)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2023, 2, 28), date(2023, 3, 28)  # 28 == 28, so 1 month
        )
        assert result == 1

    def test_calculate_duration_months_month_boundaries(self):
        """
        Test duration calculation across month boundaries.
        """
        # January 31st to February 28th (non-leap year)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2023, 1, 31), date(2023, 2, 28)  # 28 < 31, so 0 months
        )
        assert result == 0

        # January 31st to February 29th (leap year)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 31), date(2024, 2, 29)  # 29 < 31, so 0 months
        )
        assert result == 0

        # January 31st to March 31st
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 31), date(2024, 3, 31)  # 31 == 31, so 2 months
        )
        assert result == 2

        # January 31st to March 30th
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 31), date(2024, 3, 30)  # 30 < 31, so 1 month
        )
        assert result == 1

    def test_calculate_duration_months_negative_results_become_zero(self):
        """
        Test that negative duration calculations return 0.
        """
        # End date before start date
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 6, 15), date(2024, 5, 15)
        )
        assert result == 0

        # End date much before start date
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 6, 15), date(2023, 6, 15)
        )
        assert result == 0

        # Same month but end day before start day
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 6, 25), date(2024, 6, 10)
        )
        assert result == 0

    def test_calculate_duration_months_large_spans(self):
        """
        Test duration calculation for large time spans.
        """
        # 10 years
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2014, 1, 15), date(2024, 1, 15)
        )
        assert result == 120

        # 5 years and 7 months (from June 2018 to January 2024)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2018, 6, 15), date(2024, 1, 15)  # 6*12 + (1-6) = 72 + (-5) = 67 months
        )
        assert result == 67

        # 3 years and 8 months (from August 2020 to April 2024)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2020, 8, 15), date(2024, 4, 15)  # 4*12 + (4-8) = 48 + (-4) = 44 months
        )
        assert result == 44

    def test_calculate_duration_months_static_method(self):
        """
        Test that the method is properly defined as a static method.
        """
        # Should be callable without instantiating the class
        assert callable(DurationMonthsCalculator.calculate_duration_months)
        
        # Test that it works without creating an instance
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2024, 2, 15)
        )
        assert result == 1

    def test_calculate_duration_months_edge_case_year_transition(self):
        """
        Test duration calculation across year transitions.
        """
        # December 31st to January 1st (next year)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2023, 12, 31), date(2024, 1, 1)  # 1 < 31, so 0 months
        )
        assert result == 0

        # December 31st to January 31st (next year)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2023, 12, 31), date(2024, 1, 31)  # 31 == 31, so 1 month
        )
        assert result == 1

        # December 1st to January 31st (next year)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2023, 12, 1), date(2024, 1, 31)  # 31 >= 1, so 1 month
        )
        assert result == 1

    def test_calculate_duration_months_quarterly_examples(self):
        """
        Test duration calculation with quarterly examples.
        """
        # Q1 to Q2 (3 months)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2024, 4, 15)
        )
        assert result == 3

        # Q1 to Q3 (6 months)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2024, 7, 15)
        )
        assert result == 6

        # Q1 to Q4 (9 months)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2024, 10, 15)
        )
        assert result == 9

        # Q1 to Q1 next year (12 months)
        result = DurationMonthsCalculator.calculate_duration_months(
            date(2024, 1, 15), date(2025, 1, 15)
        )
        assert result == 12
