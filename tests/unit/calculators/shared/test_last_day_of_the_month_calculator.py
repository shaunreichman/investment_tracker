"""
Test Last Day of the Month Calculator.

This module provides comprehensive tests for the LastDayOfTheMonthCalculator class.
"""

import pytest
from datetime import date

from src.shared.calculators.last_day_of_the_month_calculator import LastDayOfTheMonthCalculator


class TestLastDayOfTheMonthCalculator:
    """
    Test cases for LastDayOfTheMonthCalculator.
    """

    def test_is_last_day_of_the_month_valid_last_days(self):
        """
        Test calculator with valid last day of month dates.
        """
        # Test January 31st (last day of January)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 1, 31)) is True

        # Test February 29th in leap year (last day of February)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 2, 29)) is True

        # Test February 28th in non-leap year (last day of February)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2023, 2, 28)) is True

        # Test April 30th (last day of April)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 4, 30)) is True

        # Test June 30th (last day of June)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 6, 30)) is True

        # Test September 30th (last day of September)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 9, 30)) is True

        # Test November 30th (last day of November)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 11, 30)) is True

        # Test December 31st (last day of December)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 12, 31)) is True

        # Test March 31st (last day of March)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 3, 31)) is True

        # Test May 31st (last day of May)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 5, 31)) is True

        # Test July 31st (last day of July)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 7, 31)) is True

        # Test August 31st (last day of August)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 8, 31)) is True

        # Test October 31st (last day of October)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 10, 31)) is True

    def test_is_last_day_of_the_month_invalid_not_last_days(self):
        """
        Test calculator with invalid dates (not last day of month).
        """
        # Test January 30th (should be 31st)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 1, 30)) is False

        # Test February 27th (should be 28th or 29th)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2023, 2, 27)) is False

        # Test March 30th (should be 31st)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 3, 30)) is False

        # Test April 29th (should be 30th)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 4, 29)) is False

        # Test May 30th (should be 31st)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 5, 30)) is False

        # Test June 29th (should be 30th)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 6, 29)) is False

        # Test July 30th (should be 31st)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 7, 30)) is False

        # Test August 30th (should be 31st)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 8, 30)) is False

        # Test September 29th (should be 30th)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 9, 29)) is False

        # Test October 30th (should be 31st)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 10, 30)) is False

        # Test November 29th (should be 30th)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 11, 29)) is False

        # Test December 30th (should be 31st)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 12, 30)) is False

    def test_is_last_day_of_the_month_leap_year_edge_cases(self):
        """
        Test calculator with leap year edge cases.
        """
        # Test February 29th in leap year (2024)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 2, 29)) is True

        # Test February 28th in non-leap year (2023)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2023, 2, 28)) is True

        # Test February 28th in leap year (should be False, as 29th is the last day)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 2, 28)) is False

        # Test February 29th in non-leap year (should be False, as this date doesn't exist)
        # Note: This test validates that Python's date constructor will raise ValueError
        # for invalid dates like Feb 29 in non-leap years
        with pytest.raises(ValueError, match="day is out of range for month"):
            date(2023, 2, 29)

    def test_is_last_day_of_the_month_different_years(self):
        """
        Test calculator across different years.
        """
        # Test various years with January 31st
        for year in [2020, 2021, 2022, 2023, 2024, 2025]:
            assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(year, 1, 31)) is True
            assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(year, 1, 30)) is False

        # Test leap years vs non-leap years for February
        # 2020, 2024 are leap years
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2020, 2, 29)) is True
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 2, 29)) is True

        # 2021, 2022, 2023, 2025 are non-leap years
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2021, 2, 28)) is True
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2022, 2, 28)) is True
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2023, 2, 28)) is True
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2025, 2, 28)) is True

    def test_is_last_day_of_the_month_edge_case_months(self):
        """
        Test calculator with edge case months (30-day vs 31-day months).
        """
        # 31-day months: January, March, May, July, August, October, December
        months_31_days = [1, 3, 5, 7, 8, 10, 12]
        for month in months_31_days:
            assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, month, 31)) is True
            assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, month, 30)) is False

        # 30-day months: April, June, September, November
        months_30_days = [4, 6, 9, 11]
        for month in months_30_days:
            assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, month, 30)) is True
            # Test that 31st day is invalid for 30-day months
            with pytest.raises(ValueError, match="day is out of range for month"):
                date(2024, month, 31)

    def test_is_last_day_of_the_month_static_method(self):
        """
        Test that the method is properly defined as a static method.
        """
        # Should be callable without instantiating the class
        assert callable(LastDayOfTheMonthCalculator.is_last_day_of_the_month)
        
        # Test that it works without creating an instance
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 1, 31)) is True
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 1, 30)) is False

    def test_is_last_day_of_the_month_year_boundary(self):
        """
        Test calculator with year boundary edge cases.
        """
        # Test December 31st (last day of year)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2023, 12, 31)) is True
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 12, 31)) is True

        # Test January 1st (first day of year, not last day of month)
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 1, 1)) is False

        # Test year transition from 2023 to 2024
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2023, 12, 31)) is True
        assert LastDayOfTheMonthCalculator.is_last_day_of_the_month(date(2024, 1, 1)) is False
