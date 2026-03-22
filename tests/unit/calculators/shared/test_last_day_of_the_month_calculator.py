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

    def test_get_last_day_of_the_month_valid_dates(self):
        """
        Test get_last_day_of_the_month with various valid dates.
        """
        # Test January dates - should return January 31st
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 1, 1)) == date(2024, 1, 31)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 1, 15)) == date(2024, 1, 31)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 1, 31)) == date(2024, 1, 31)

        # Test February dates - should return February 29th in leap year
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 2, 1)) == date(2024, 2, 29)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 2, 15)) == date(2024, 2, 29)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 2, 29)) == date(2024, 2, 29)

        # Test February dates - should return February 28th in non-leap year
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2023, 2, 1)) == date(2023, 2, 28)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2023, 2, 15)) == date(2023, 2, 28)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2023, 2, 28)) == date(2023, 2, 28)

        # Test April dates (30-day month) - should return April 30th
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 4, 1)) == date(2024, 4, 30)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 4, 15)) == date(2024, 4, 30)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 4, 30)) == date(2024, 4, 30)

        # Test December dates - should return December 31st
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 12, 1)) == date(2024, 12, 31)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 12, 15)) == date(2024, 12, 31)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 12, 31)) == date(2024, 12, 31)

    def test_get_last_day_of_the_month_all_months(self):
        """
        Test get_last_day_of_the_month for all months of the year.
        """
        # Test all months with first day of month
        test_cases = [
            (1, 31),   # January
            (2, 29),   # February (leap year 2024)
            (3, 31),   # March
            (4, 30),   # April
            (5, 31),   # May
            (6, 30),   # June
            (7, 31),   # July
            (8, 31),   # August
            (9, 30),   # September
            (10, 31),  # October
            (11, 30),  # November
            (12, 31),  # December
        ]
        
        for month, expected_day in test_cases:
            result = LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, month, 1))
            assert result == date(2024, month, expected_day), f"Month {month} should return day {expected_day}"

    def test_get_last_day_of_the_month_leap_year_edge_cases(self):
        """
        Test get_last_day_of_the_month with leap year edge cases.
        """
        # Leap years: 2020, 2024, 2028
        leap_years = [2020, 2024, 2028]
        for year in leap_years:
            result = LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(year, 2, 15))
            assert result == date(year, 2, 29), f"Leap year {year} should return Feb 29"

        # Non-leap years: 2021, 2022, 2023, 2025
        non_leap_years = [2021, 2022, 2023, 2025]
        for year in non_leap_years:
            result = LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(year, 2, 15))
            assert result == date(year, 2, 28), f"Non-leap year {year} should return Feb 28"

    def test_get_last_day_of_the_month_year_boundary(self):
        """
        Test get_last_day_of_the_month across year boundaries.
        """
        # Test December to January transition
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2023, 12, 15)) == date(2023, 12, 31)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 1, 15)) == date(2024, 1, 31)

        # Test year 2000 (leap year)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2000, 2, 15)) == date(2000, 2, 29)

        # Test year 2100 (not a leap year - century rule)
        assert LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2100, 2, 15)) == date(2100, 2, 28)

    def test_get_last_day_of_the_month_30_vs_31_day_months(self):
        """
        Test get_last_day_of_the_month for months with different numbers of days.
        """
        # 31-day months
        months_31_days = [1, 3, 5, 7, 8, 10, 12]
        for month in months_31_days:
            result = LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, month, 15))
            assert result == date(2024, month, 31), f"Month {month} should return day 31"

        # 30-day months
        months_30_days = [4, 6, 9, 11]
        for month in months_30_days:
            result = LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, month, 15))
            assert result == date(2024, month, 30), f"Month {month} should return day 30"

    def test_get_last_day_of_the_month_static_method(self):
        """
        Test that get_last_day_of_the_month is properly defined as a static method.
        """
        # Should be callable without instantiating the class
        assert callable(LastDayOfTheMonthCalculator.get_last_day_of_the_month)
        
        # Test that it works without creating an instance
        result = LastDayOfTheMonthCalculator.get_last_day_of_the_month(date(2024, 1, 15))
        assert result == date(2024, 1, 31)

    def test_get_last_day_of_the_month_consistency_with_is_last_day(self):
        """
        Test that get_last_day_of_the_month and is_last_day_of_the_month are consistent.
        """
        test_dates = [
            date(2024, 1, 1),   # First day of month
            date(2024, 1, 15),  # Middle of month
            date(2024, 1, 31),  # Last day of month
            date(2024, 2, 29),  # Leap year last day
            date(2023, 2, 28),  # Non-leap year last day
            date(2024, 4, 30),  # 30-day month last day
        ]
        
        for test_date in test_dates:
            # Get the last day of the month for this date
            last_day = LastDayOfTheMonthCalculator.get_last_day_of_the_month(test_date)
            
            # Verify that the returned date is actually the last day of its month
            is_last_day = LastDayOfTheMonthCalculator.is_last_day_of_the_month(last_day)
            assert is_last_day is True, f"Date {last_day} should be the last day of its month"

    def test_get_last_day_of_the_month_same_month_consistency(self):
        """
        Test that any date in the same month returns the same last day.
        """
        # Test January 2024 - all dates should return January 31st
        january_dates = [date(2024, 1, day) for day in range(1, 32)]
        for test_date in january_dates:
            result = LastDayOfTheMonthCalculator.get_last_day_of_the_month(test_date)
            assert result == date(2024, 1, 31), f"Date {test_date} should return January 31st"

        # Test April 2024 (30-day month) - all dates should return April 30th
        april_dates = [date(2024, 4, day) for day in range(1, 31)]
        for test_date in april_dates:
            result = LastDayOfTheMonthCalculator.get_last_day_of_the_month(test_date)
            assert result == date(2024, 4, 30), f"Date {test_date} should return April 30th"

        # Test February 2024 (leap year) - all dates should return February 29th
        february_dates = [date(2024, 2, day) for day in range(1, 30)]
        for test_date in february_dates:
            result = LastDayOfTheMonthCalculator.get_last_day_of_the_month(test_date)
            assert result == date(2024, 2, 29), f"Date {test_date} should return February 29th"
