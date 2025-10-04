"""
Test Rate Validation Service.

This module provides focused tests for the RateValidationService class,
specifically testing the validation logic using the shared calculator.
"""

import pytest
from datetime import date
from unittest.mock import Mock
from sqlalchemy.orm import Session

from src.rates.services.rate_validation_service import RateValidationService


class TestRateValidationService:
    """
    Test cases for RateValidationService.
    """

    def setup_method(self):
        """
        Set up test fixtures.
        """
        self.service = RateValidationService()
        self.session = Mock(spec=Session)

    def test_validate_fx_rate_creation_valid_data(self):
        """
        Test FX rate validation with valid data.
        """
        fx_rate_data = {
            'date': date(2024, 1, 31),  # Valid last day of month
            'fx_rate': 1.5  # Valid positive rate
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        assert errors == {}

    def test_validate_fx_rate_creation_valid_string_date(self):
        """
        Test FX rate validation with valid string date.
        """
        fx_rate_data = {
            'date': '2024-01-31',  # Valid last day of month as string
            'fx_rate': 1.5  # Valid positive rate
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        assert errors == {}

    def test_validate_fx_rate_creation_invalid_date_not_last_day(self):
        """
        Test FX rate validation with invalid date (not last day of month).
        """
        fx_rate_data = {
            'date': date(2024, 1, 30),  # Invalid: not last day of month
            'fx_rate': 1.5
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        
        assert 'date' in errors
        assert len(errors['date']) == 1
        assert "FX rate date must be the last day of the month" in errors['date'][0]

    def test_validate_fx_rate_creation_invalid_string_date(self):
        """
        Test FX rate validation with invalid string date.
        """
        fx_rate_data = {
            'date': '2024-01-30',  # Invalid: not last day of month as string
            'fx_rate': 1.5
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        
        assert 'date' in errors
        assert len(errors['date']) == 1
        assert "FX rate date must be the last day of the month" in errors['date'][0]

    def test_validate_fx_rate_creation_invalid_rate_zero(self):
        """
        Test FX rate validation with zero rate.
        """
        fx_rate_data = {
            'date': date(2024, 1, 31),  # Valid last day of month
            'fx_rate': 0  # Invalid: zero rate
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        
        assert 'fx_rate' in errors
        assert len(errors['fx_rate']) == 1
        assert "FX rate must be greater than 0" in errors['fx_rate'][0]

    def test_validate_fx_rate_creation_invalid_rate_negative(self):
        """
        Test FX rate validation with negative rate.
        """
        fx_rate_data = {
            'date': date(2024, 1, 31),  # Valid last day of month
            'fx_rate': -1.5  # Invalid: negative rate
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        
        assert 'fx_rate' in errors
        assert len(errors['fx_rate']) == 1
        assert "FX rate must be greater than 0" in errors['fx_rate'][0]

    def test_validate_fx_rate_creation_valid_small_rate(self):
        """
        Test FX rate validation with very small positive rate.
        """
        fx_rate_data = {
            'date': date(2024, 1, 31),  # Valid last day of month
            'fx_rate': 0.0001  # Valid: very small positive rate
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        assert errors == {}

    def test_validate_fx_rate_creation_valid_large_rate(self):
        """
        Test FX rate validation with large positive rate.
        """
        fx_rate_data = {
            'date': date(2024, 1, 31),  # Valid last day of month
            'fx_rate': 1000.0  # Valid: large positive rate
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        assert errors == {}

    def test_validate_fx_rate_creation_multiple_validation_errors(self):
        """
        Test FX rate validation with multiple validation errors.
        """
        fx_rate_data = {
            'date': date(2024, 1, 30),  # Invalid: not last day of month
            'fx_rate': -1.5  # Invalid: negative rate
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        
        # Should have both date and fx_rate errors
        assert len(errors) == 2
        assert 'date' in errors
        assert 'fx_rate' in errors
        
        # Check date error
        assert len(errors['date']) == 1
        assert "FX rate date must be the last day of the month" in errors['date'][0]
        
        # Check fx_rate error
        assert len(errors['fx_rate']) == 1
        assert "FX rate must be greater than 0" in errors['fx_rate'][0]

    def test_validate_fx_rate_creation_leap_year_valid_dates(self):
        """
        Test FX rate validation with leap year valid dates.
        """
        # February 29th in leap year (2024)
        fx_rate_data = {
            'date': date(2024, 2, 29),
            'fx_rate': 1.5
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        assert errors == {}

        # February 28th in non-leap year (2023)
        fx_rate_data = {
            'date': date(2023, 2, 28),
            'fx_rate': 1.5
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        assert errors == {}

    def test_validate_fx_rate_creation_different_month_lengths(self):
        """
        Test FX rate validation with different month lengths.
        """
        # 31-day months
        months_31_days = [1, 3, 5, 7, 8, 10, 12]
        for month in months_31_days:
            fx_rate_data = {
                'date': date(2024, month, 31),
                'fx_rate': 1.5
            }
            errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
            assert errors == {}, f"Month {month} (31 days) should be valid"

        # 30-day months
        months_30_days = [4, 6, 9, 11]
        for month in months_30_days:
            fx_rate_data = {
                'date': date(2024, month, 30),
                'fx_rate': 1.5
            }
            errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
            assert errors == {}, f"Month {month} (30 days) should be valid"

    def test_validate_fx_rate_creation_uses_calculator(self):
        """
        Test that the service properly uses the LastDayOfTheMonthCalculator.
        """
        # This test ensures the service is using the calculator correctly
        # by testing various edge cases that the calculator handles
        
        # Test with February in leap year
        fx_rate_data = {
            'date': date(2024, 2, 28),  # Should be invalid (29th is last day)
            'fx_rate': 1.5
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        assert 'date' in errors

        # Test with February in non-leap year
        fx_rate_data = {
            'date': date(2023, 2, 28),  # Should be valid (28th is last day)
            'fx_rate': 1.5
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        assert errors == {}

    def test_validate_fx_rate_creation_return_type(self):
        """
        Test that the method returns the correct type (Dict[str, List[str]]).
        """
        # Valid data should return empty dict
        fx_rate_data = {
            'date': date(2024, 1, 31),
            'fx_rate': 1.5
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        assert isinstance(errors, dict)
        assert errors == {}

        # Invalid data should return dict with list values
        fx_rate_data = {
            'date': date(2024, 1, 30),
            'fx_rate': -1.5
        }
        errors = self.service.validate_fx_rate_creation(fx_rate_data, self.session)
        assert isinstance(errors, dict)
        assert 'date' in errors
        assert 'fx_rate' in errors
        assert isinstance(errors['date'], list)
        assert isinstance(errors['fx_rate'], list)
        assert len(errors['date']) == 1
        assert len(errors['fx_rate']) == 1
