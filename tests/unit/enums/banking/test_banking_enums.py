"""
Banking Enums Tests

This module tests the banking enum validation and business logic.
Focus: Enum values, validation methods, and business logic only.

Other aspects covered elsewhere:
- Model usage: test_bank_model.py, test_bank_account_model.py
- Service validation: test_banking_validation_service.py
- API validation: test_banking_controller.py
"""

import pytest

from src.banking.enums import (
    Country, Currency, AccountStatus, BankType, BankAccountType,
    SortOrder, BankingDomainEventType,
    get_all_enum_values, validate_enum_value, get_enum_display_name
)


class TestCountryEnum:
    """Test suite for Country enum"""
    
    def test_country_values(self):
        """Test all country enum values."""
        expected_countries = [
            'AU', 'US', 'UK', 'CA', 'NZ', 'SG', 'HK', 'JP', 'DE', 'FR'
        ]
        
        actual_countries = [country.value for country in Country]
        assert actual_countries == expected_countries
    
    def test_country_string_representation(self):
        """Test country string representation."""
        country = Country.AU
        assert str(country) == 'AU'
        assert repr(country) == '<Country.AU: \'AU\'>'
    
    def test_country_from_string_valid(self):
        """Test creating country from valid string."""
        # Test all valid countries
        for country in Country:
            result = Country.from_string(country.value)
            assert result == country
    
    def test_country_from_string_invalid(self):
        """Test creating country from invalid string."""
        invalid_countries = ['XX', 'INVALID', '', '123', 'AUSTRALIA']
        
        for invalid_country in invalid_countries:
            with pytest.raises(ValueError, match=f"Invalid Country: {invalid_country}"):
                Country.from_string(invalid_country)
    
    def test_country_swift_requirement(self):
        """Test SWIFT/BIC requirement logic."""
        # Countries that require SWIFT/BIC
        swift_required = [Country.US, Country.UK, Country.CA, Country.DE, Country.FR, Country.JP]
        
        for country in swift_required:
            assert Country.has_swift_requirement(country) is True
        
        # Countries that don't require SWIFT/BIC
        swift_not_required = [Country.AU, Country.NZ, Country.SG, Country.HK]
        
        for country in swift_not_required:
            assert Country.has_swift_requirement(country) is False


class TestCurrencyEnum:
    """Test suite for Currency enum"""
    
    def test_currency_values(self):
        """Test all currency enum values."""
        expected_currencies = [
            'AUD', 'USD', 'EUR', 'GBP', 'CAD', 'NZD', 'SGD', 'HKD', 'JPY', 'CHF'
        ]
        
        actual_currencies = [currency.value for currency in Currency]
        assert actual_currencies == expected_currencies
    
    def test_currency_string_representation(self):
        """Test currency string representation."""
        currency = Currency.AUD
        assert str(currency) == 'AUD'
        assert repr(currency) == '<Currency.AUD: \'AUD\'>'
    
    def test_currency_from_string_valid(self):
        """Test creating currency from valid string."""
        # Test all valid currencies
        for currency in Currency:
            result = Currency.from_string(currency.value)
            assert result == currency
    
    def test_currency_from_string_invalid(self):
        """Test creating currency from invalid string."""
        invalid_currencies = ['XXX', 'INVALID', '', '123', 'DOLLAR']
        
        for invalid_currency in invalid_currencies:
            with pytest.raises(ValueError, match=f"Invalid Currency: {invalid_currency}"):
                Currency.from_string(invalid_currency)
    
    def test_currency_major_currency(self):
        """Test major currency identification."""
        # Major world currencies
        major_currencies = [Currency.USD, Currency.EUR, Currency.GBP, Currency.JPY, Currency.CHF]
        
        for currency in major_currencies:
            assert Currency.is_major_currency(currency) is True
        
        # Non-major currencies
        non_major_currencies = [Currency.AUD, Currency.CAD, Currency.NZD, Currency.SGD, Currency.HKD]
        
        for currency in non_major_currencies:
            assert Currency.is_major_currency(currency) is False
    
    def test_currency_decimal_places(self):
        """Test currency decimal places logic."""
        # Most currencies use 2 decimal places
        two_decimal_currencies = [
            Currency.AUD, Currency.USD, Currency.EUR, Currency.GBP, Currency.CAD,
            Currency.NZD, Currency.SGD, Currency.HKD, Currency.CHF
        ]
        
        for currency in two_decimal_currencies:
            assert Currency.get_decimal_places(currency) == 2
        
        # Japanese Yen uses 0 decimal places
        assert Currency.get_decimal_places(Currency.JPY) == 0


class TestAccountStatusEnum:
    """Test suite for AccountStatus enum"""
    
    def test_account_status_values(self):
        """Test all account status enum values."""
        expected_statuses = [
            'ACTIVE', 'SUSPENDED', 'CLOSED', 'PENDING_VERIFICATION', 'RESTRICTED'
        ]
        
        actual_statuses = [status.value for status in AccountStatus]
        assert actual_statuses == expected_statuses
    
    def test_account_status_string_representation(self):
        """Test account status string representation."""
        status = AccountStatus.ACTIVE
        assert str(status) == 'ACTIVE'
        assert repr(status) == '<AccountStatus.ACTIVE: \'ACTIVE\'>'
    
    def test_account_status_from_string_valid(self):
        """Test creating account status from valid string."""
        # Test all valid statuses
        for status in AccountStatus:
            result = AccountStatus.from_string(status.value)
            assert result == status
    
    def test_account_status_from_string_invalid(self):
        """Test creating account status from invalid string."""
        invalid_statuses = ['INVALID', 'UNKNOWN', '', '123', 'ACTIVE_STATUS']
        
        for invalid_status in invalid_statuses:
            with pytest.raises(ValueError, match=f"Invalid AccountStatus: {invalid_status}"):
                AccountStatus.from_string(invalid_status)
    
    def test_account_status_can_transact(self):
        """Test transaction capability logic."""
        # Only ACTIVE accounts can transact
        assert AccountStatus.can_transact(AccountStatus.ACTIVE) is True
        
        # Other statuses cannot transact
        non_transacting_statuses = [
            AccountStatus.SUSPENDED, AccountStatus.CLOSED,
            AccountStatus.PENDING_VERIFICATION, AccountStatus.RESTRICTED
        ]
        
        for status in non_transacting_statuses:
            assert AccountStatus.can_transact(status) is False
    
    def test_account_status_is_operational(self):
        """Test operational status logic."""
        # All statuses except CLOSED are operational
        operational_statuses = [
            AccountStatus.ACTIVE, AccountStatus.SUSPENDED,
            AccountStatus.PENDING_VERIFICATION, AccountStatus.RESTRICTED
        ]
        
        for status in operational_statuses:
            assert AccountStatus.is_operational(status) is True
        
        # CLOSED accounts are not operational
        assert AccountStatus.is_operational(AccountStatus.CLOSED) is False
    
    def test_account_status_requires_verification(self):
        """Test verification requirement logic."""
        # Only PENDING_VERIFICATION requires verification
        assert AccountStatus.requires_verification(AccountStatus.PENDING_VERIFICATION) is True
        
        # Other statuses don't require verification
        non_verification_statuses = [
            AccountStatus.ACTIVE, AccountStatus.SUSPENDED,
            AccountStatus.CLOSED, AccountStatus.RESTRICTED
        ]
        
        for status in non_verification_statuses:
            assert AccountStatus.requires_verification(status) is False


class TestBankTypeEnum:
    """Test suite for BankType enum"""
    
    def test_bank_type_values(self):
        """Test all bank type enum values."""
        expected_types = [
            'COMMERCIAL', 'INVESTMENT', 'CENTRAL', 'COOPERATIVE', 'ISLAMIC', 'DIGITAL'
        ]
        
        actual_types = [bank_type.value for bank_type in BankType]
        assert actual_types == expected_types
    
    def test_bank_type_string_representation(self):
        """Test bank type string representation."""
        bank_type = BankType.COMMERCIAL
        assert str(bank_type) == 'COMMERCIAL'
        assert repr(bank_type) == '<BankType.COMMERCIAL: \'COMMERCIAL\'>'
    
    def test_bank_type_from_string_valid(self):
        """Test creating bank type from valid string."""
        # Test all valid bank types
        for bank_type in BankType:
            result = BankType.from_string(bank_type.value)
            assert result == bank_type
    
    def test_bank_type_from_string_invalid(self):
        """Test creating bank type from invalid string."""
        invalid_types = ['INVALID', 'UNKNOWN', '', '123', 'BANK_TYPE']
        
        for invalid_type in invalid_types:
            with pytest.raises(ValueError, match=f"Invalid BankType: {invalid_type}"):
                BankType.from_string(invalid_type)
    
    def test_bank_type_licensing_requirement(self):
        """Test licensing requirement logic."""
        # Types that require special licensing
        licensed_types = [BankType.INVESTMENT, BankType.CENTRAL, BankType.ISLAMIC]
        
        for bank_type in licensed_types:
            assert BankType.requires_licensing(bank_type) is True
        
        # Types that don't require special licensing
        non_licensed_types = [BankType.COMMERCIAL, BankType.COOPERATIVE, BankType.DIGITAL]
        
        for bank_type in non_licensed_types:
            assert BankType.requires_licensing(bank_type) is False
    
    def test_bank_type_digital_native(self):
        """Test digital native identification."""
        # Only DIGITAL type is digital-native
        assert BankType.is_digital_native(BankType.DIGITAL) is True
        
        # Other types are not digital-native
        non_digital_types = [
            BankType.COMMERCIAL, BankType.INVESTMENT, BankType.CENTRAL,
            BankType.COOPERATIVE, BankType.ISLAMIC
        ]
        
        for bank_type in non_digital_types:
            assert BankType.is_digital_native(bank_type) is False


class TestBankAccountTypeEnum:
    """Test suite for BankAccountType enum"""
    
    def test_account_type_values(self):
        """Test all account type enum values."""
        expected_types = [
            'CHECKING', 'SAVINGS', 'INVESTMENT', 'BUSINESS', 'TRUST', 'JOINT'
        ]
        
        actual_types = [account_type.value for account_type in BankAccountType]
        assert actual_types == expected_types
    
    def test_account_type_string_representation(self):
        """Test account type string representation."""
        account_type = BankAccountType.CHECKING
        assert str(account_type) == 'CHECKING'
        assert repr(account_type) == '<BankAccountType.CHECKING: \'CHECKING\'>'
    
    def test_account_type_from_string_valid(self):
        """Test creating account type from valid string."""
        # Test all valid account types
        for account_type in BankAccountType:
            result = BankAccountType.from_string(account_type.value)
            assert result == account_type
    
    def test_account_type_from_string_invalid(self):
        """Test creating account type from invalid string."""
        invalid_types = ['INVALID', 'UNKNOWN', '', '123', 'ACCOUNT_TYPE']
        
        for invalid_type in invalid_types:
            with pytest.raises(ValueError, match=f"Invalid BankAccountType: {invalid_type}"):
                BankAccountType.from_string(invalid_type)
    
    def test_account_type_interest_earning(self):
        """Test interest earning logic."""
        # Types that typically earn interest
        interest_accounts = [BankAccountType.SAVINGS, BankAccountType.INVESTMENT]
        
        for account_type in interest_accounts:
            assert BankAccountType.earns_interest(account_type) is True
        
        # Types that don't typically earn interest
        non_interest_accounts = [
            BankAccountType.CHECKING, BankAccountType.BUSINESS, BankAccountType.TRUST, BankAccountType.JOINT
        ]
        
        for account_type in non_interest_accounts:
            assert BankAccountType.earns_interest(account_type) is False
    
    def test_account_type_kyc_requirement(self):
        """Test KYC requirement logic."""
        # Types that require KYC verification
        kyc_required = [BankAccountType.BUSINESS, BankAccountType.TRUST, BankAccountType.INVESTMENT]
        
        for account_type in kyc_required:
            assert BankAccountType.requires_kyc(account_type) is True
        
        # Types that don't require KYC verification
        kyc_not_required = [BankAccountType.CHECKING, BankAccountType.SAVINGS, BankAccountType.JOINT]
        
        for account_type in kyc_not_required:
            assert BankAccountType.requires_kyc(account_type) is False


class TestSortOrderEnum:
    """Test suite for SortOrder enum"""
    
    def test_sort_order_values(self):
        """Test all sort order enum values."""
        expected_orders = ['ASC', 'DESC']
        
        actual_orders = [order.value for order in SortOrder]
        assert actual_orders == expected_orders
    
    def test_sort_order_string_representation(self):
        """Test sort order string representation."""
        order = SortOrder.ASC
        assert str(order) == 'ASC'
        assert repr(order) == '<SortOrder.ASC: \'ASC\'>'
    
    def test_sort_order_from_string_valid(self):
        """Test creating sort order from valid string."""
        # Test all valid sort orders
        for order in SortOrder:
            result = SortOrder.from_string(order.value)
            assert result == order
    
    def test_sort_order_from_string_invalid(self):
        """Test creating sort order from invalid string."""
        invalid_orders = ['INVALID', 'UP', 'DOWN', '', '123']
        
        for invalid_order in invalid_orders:
            with pytest.raises(ValueError, match=f"Invalid SortOrder: {invalid_order}"):
                SortOrder.from_string(invalid_order)
    
    def test_sort_order_reverse_logic(self):
        """Test reverse logic."""
        assert SortOrder.is_reverse(SortOrder.DESC) is True
        assert SortOrder.is_reverse(SortOrder.ASC) is False


class TestBankingDomainEventTypeEnum:
    """Test suite for BankingDomainEventType enum"""
    
    def test_event_type_values(self):
        """Test all banking domain event type enum values."""
        expected_event_types = [
            'BANK_CREATED', 'BANK_UPDATED', 'BANK_DELETED',
            'BANK_ACCOUNT_CREATED', 'BANK_ACCOUNT_UPDATED', 'BANK_ACCOUNT_DELETED',
            'CURRENCY_CHANGED', 'ACCOUNT_STATUS_CHANGED'
        ]
        
        actual_event_types = [event_type.value for event_type in BankingDomainEventType]
        assert actual_event_types == expected_event_types
    
    def test_event_type_string_representation(self):
        """Test banking domain event type string representation."""
        event_type = BankingDomainEventType.BANK_CREATED
        assert str(event_type) == 'BANK_CREATED'
        assert repr(event_type) == '<BankingDomainEventType.BANK_CREATED: \'BANK_CREATED\'>'
    
    def test_event_type_from_string_valid(self):
        """Test creating banking domain event type from valid string."""
        # Test all valid event types
        for event_type in BankingDomainEventType:
            result = BankingDomainEventType.from_string(event_type.value)
            assert result == event_type
    
    def test_event_type_from_string_invalid(self):
        """Test creating banking domain event type from invalid string."""
        invalid_event_types = ['INVALID', 'UNKNOWN', '', '123', 'EVENT_TYPE']
        
        for invalid_event_type in invalid_event_types:
            with pytest.raises(ValueError, match=f"Invalid BankingDomainEventType: {invalid_event_type}"):
                BankingDomainEventType.from_string(invalid_event_type)


class TestEnumUtilityFunctions:
    """Test suite for enum utility functions"""
    
    def test_get_all_enum_values(self):
        """Test get_all_enum_values utility function."""
        # Test with Country enum
        country_values = get_all_enum_values(Country)
        expected_countries = ['AU', 'US', 'UK', 'CA', 'NZ', 'SG', 'HK', 'JP', 'DE', 'FR']
        assert country_values == expected_countries
        
        # Test with Currency enum
        currency_values = get_all_enum_values(Currency)
        expected_currencies = ['AUD', 'USD', 'EUR', 'GBP', 'CAD', 'NZD', 'SGD', 'HKD', 'JPY', 'CHF']
        assert currency_values == expected_currencies
    
    def test_validate_enum_value(self):
        """Test validate_enum_value utility function."""
        # Test valid values
        assert validate_enum_value(Country, 'AU') is True
        assert validate_enum_value(Country, 'US') is True
        assert validate_enum_value(Currency, 'AUD') is True
        assert validate_enum_value(Currency, 'USD') is True
        
        # Test invalid values
        assert validate_enum_value(Country, 'XX') is False
        assert validate_enum_value(Country, 'INVALID') is False
        assert validate_enum_value(Currency, 'XXX') is False
        assert validate_enum_value(Currency, 'INVALID') is False
    
    def test_get_enum_display_name(self):
        """Test get_enum_display_name utility function."""
        # Test various enum values
        assert get_enum_display_name(Country.AU) == 'AU'
        assert get_enum_display_name(Country.US) == 'US'
        assert get_enum_display_name(Currency.AUD) == 'AUD'
        assert get_enum_display_name(AccountStatus.ACTIVE) == 'ACTIVE'
        assert get_enum_display_name(BankType.COMMERCIAL) == 'COMMERCIAL'
        assert get_enum_display_name(BankAccountType.CHECKING) == 'CHECKING'
        assert get_enum_display_name(SortOrder.ASC) == 'ASC'
        assert get_enum_display_name(BankingDomainEventType.BANK_CREATED) == 'BANK_CREATED'


class TestEnumIntegration:
    """Test suite for enum integration and consistency"""
    
    def test_enum_value_consistency(self):
        """Test that enum values are consistent across the system."""
        # Test that all enums have string values
        all_enums = [Country, Currency, AccountStatus, BankType, BankAccountType, SortOrder, BankingDomainEventType]
        
        for enum_class in all_enums:
            for enum_value in enum_class:
                assert isinstance(enum_value.value, str)
                assert len(enum_value.value) > 0
    
    def test_enum_method_consistency(self):
        """Test that all enums have consistent method signatures."""
        # Test that all enums have from_string method
        all_enums = [Country, Currency, AccountStatus, BankType, BankAccountType, SortOrder, BankingDomainEventType]
        
        for enum_class in all_enums:
            assert hasattr(enum_class, 'from_string')
            assert callable(getattr(enum_class, 'from_string'))
    
    def test_enum_string_conversion(self):
        """Test that all enums can be converted to and from strings."""
        # Test string conversion for all enums
        all_enums = [Country, Currency, AccountStatus, BankType, BankAccountType, SortOrder, BankingDomainEventType]
        
        for enum_class in all_enums:
            for enum_value in enum_class:
                # Test string conversion
                string_value = str(enum_value)
                assert isinstance(string_value, str)
                
                # Test from_string conversion
                converted_value = enum_class.from_string(string_value)
                assert converted_value == enum_value
