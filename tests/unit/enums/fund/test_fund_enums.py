"""
Unit tests for Fund Enums Module.

This module tests the dedicated enums module that provides
type safety and clean separation of concerns for the fund system.
"""

import pytest
from src.fund.enums import (
    FundStatus, FundTrackingType, EventType, DistributionType, GroupType,
    CashFlowDirection, TaxPaymentType, TaxJurisdiction,
    get_all_enum_values, validate_enum_value, get_enum_display_name
)


class TestFundStatus:
    """Test suite for FundStatus enum."""
    
    def test_enum_values(self):
        """Test that FundStatus has the correct values."""
        assert FundStatus.ACTIVE.value == 'ACTIVE'
        assert FundStatus.REALIZED.value == 'REALIZED'
        assert FundStatus.COMPLETED.value == 'COMPLETED'
    
    def test_enum_count(self):
        """Test that FundStatus has exactly 4 values."""
        assert len(FundStatus) == 4
    
    def test_string_representation(self):
        """Test string representation of FundStatus values."""
        assert str(FundStatus.ACTIVE) == 'ACTIVE'
        assert str(FundStatus.REALIZED) == 'REALIZED'
        assert str(FundStatus.COMPLETED) == 'COMPLETED'
    
    def test_from_string_valid(self):
        """Test creating FundStatus from valid string values."""
        assert FundStatus.from_string('ACTIVE') == FundStatus.ACTIVE
        assert FundStatus.from_string('REALIZED') == FundStatus.REALIZED
        assert FundStatus.from_string('COMPLETED') == FundStatus.COMPLETED
    
    def test_from_string_invalid(self):
        """Test creating FundStatus from invalid string values."""
        with pytest.raises(ValueError, match="Invalid FundStatus"):
            FundStatus.from_string('invalid_status')


class TestFundTrackingType:
    """Test suite for FundTrackingType enum."""
    
    def test_enum_values(self):
        """Test that FundTrackingType has the correct values."""
        assert FundTrackingType.COST_BASED.value == 'COST_BASED'
        assert FundTrackingType.NAV_BASED.value == 'NAV_BASED'
    
    def test_enum_count(self):
        """Test that FundTrackingType has exactly 2 values."""
        assert len(FundTrackingType) == 2
    
    def test_from_string_valid(self):
        """Test creating FundTrackingType from valid string values."""
        assert FundTrackingType.from_string('COST_BASED') == FundTrackingType.COST_BASED
        assert FundTrackingType.from_string('NAV_BASED') == FundTrackingType.NAV_BASED


class TestEventType:
    """Test suite for EventType enum."""
    
    def test_enum_values(self):
        """Test that EventType has the correct values."""
        assert EventType.CAPITAL_CALL.value == 'CAPITAL_CALL'
        assert EventType.DISTRIBUTION.value == 'DISTRIBUTION'
        assert EventType.NAV_UPDATE.value == 'NAV_UPDATE'
    
    def test_equity_event_detection(self):
        """Test equity event detection methods."""
        assert EventType.is_equity_event(EventType.CAPITAL_CALL) is True
        assert EventType.is_equity_event(EventType.DISTRIBUTION) is False
        assert EventType.is_equity_event(EventType.UNIT_PURCHASE) is True
    
    def test_distribution_event_detection(self):
        """Test distribution event detection methods."""
        assert EventType.is_distribution_event(EventType.DISTRIBUTION) is True
        assert EventType.is_distribution_event(EventType.CAPITAL_CALL) is False
    
    def test_system_event_detection(self):
        """Test system event detection methods."""
        assert EventType.is_system_event(EventType.DAILY_RISK_FREE_INTEREST_CHARGE) is True
        assert EventType.is_system_event(EventType.CAPITAL_CALL) is False


class TestDistributionType:
    """Test suite for DistributionType enum."""
    
    def test_enum_values(self):
        """Test that DistributionType has the correct values."""
        assert DistributionType.INCOME.value == 'INCOME'
        assert DistributionType.DIVIDEND_FRANKED.value == 'DIVIDEND_FRANKED'
        assert DistributionType.INTEREST.value == 'INTEREST'
    
    def test_taxable_distribution_detection(self):
        """Test taxable distribution detection methods."""
        assert DistributionType.is_taxable(DistributionType.INCOME) is True
        assert DistributionType.is_taxable(DistributionType.DIVIDEND_FRANKED) is True
        assert DistributionType.is_taxable(DistributionType.INTEREST) is True
    
    def test_enum_count(self):
        """Test that DistributionType has exactly 6 values."""
        assert len(DistributionType) == 6
    
    def test_franking_credits_detection(self):
        """Test franking credits detection methods."""
        assert DistributionType.has_franking_credits(DistributionType.DIVIDEND_FRANKED) is True
        assert DistributionType.has_franking_credits(DistributionType.DIVIDEND_UNFRANKED) is False
        assert DistributionType.has_franking_credits(DistributionType.INTEREST) is False


class TestCashFlowDirection:
    """Test suite for CashFlowDirection enum."""
    
    def test_enum_values(self):
        """Test that CashFlowDirection has the correct values."""
        assert CashFlowDirection.INFLOW.value == 'INFLOW'
        assert CashFlowDirection.OUTFLOW.value == 'OUTFLOW'
    
    def test_enum_count(self):
        """Test that CashFlowDirection has exactly 2 values."""
        assert len(CashFlowDirection) == 2
    
    def test_from_string_valid(self):
        """Test creating CashFlowDirection from valid string values."""
        assert CashFlowDirection.from_string('INFLOW') == CashFlowDirection.INFLOW
        assert CashFlowDirection.from_string('OUTFLOW') == CashFlowDirection.OUTFLOW
    
    def test_direction_detection(self):
        """Test direction detection methods."""
        assert CashFlowDirection.is_incoming(CashFlowDirection.INFLOW) is True
        assert CashFlowDirection.is_incoming(CashFlowDirection.OUTFLOW) is False
        assert CashFlowDirection.is_outgoing(CashFlowDirection.OUTFLOW) is True
        assert CashFlowDirection.is_outgoing(CashFlowDirection.INFLOW) is False


class TestTaxPaymentType:
    """Test suite for TaxPaymentType enum."""
    
    def test_enum_values(self):
        """Test that TaxPaymentType has the correct values."""
        assert TaxPaymentType.CAPITAL_GAINS_TAX.value == 'CAPITAL_GAINS_TAX'
        assert TaxPaymentType.DIVIDENDS_FRANKED_TAX.value == 'DIVIDENDS_FRANKED_TAX'
        assert TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING.value == 'NON_RESIDENT_INTEREST_WITHHOLDING'
    
    def test_enum_count(self):
        """Test that TaxPaymentType has exactly 6 values."""
        assert len(TaxPaymentType) == 6
    
    def test_withholding_tax_detection(self):
        """Test withholding tax detection methods."""
        assert TaxPaymentType.is_withholding_tax(TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING) is True
        assert TaxPaymentType.is_withholding_tax(TaxPaymentType.CAPITAL_GAINS_TAX) is False
    
    def test_dividend_tax_detection(self):
        """Test dividend tax detection methods."""
        assert TaxPaymentType.is_dividend_tax(TaxPaymentType.DIVIDENDS_FRANKED_TAX) is True
        assert TaxPaymentType.is_dividend_tax(TaxPaymentType.DIVIDENDS_UNFRANKED_TAX) is True
        assert TaxPaymentType.is_dividend_tax(TaxPaymentType.CAPITAL_GAINS_TAX) is False


class TestTaxJurisdiction:
    """Test suite for TaxJurisdiction enum."""
    
    def test_enum_values(self):
        """Test that TaxJurisdiction has the correct values."""
        assert TaxJurisdiction.AU.value == 'AU'
        assert TaxJurisdiction.US.value == 'US'
        assert TaxJurisdiction.UK.value == 'UK'
        assert TaxJurisdiction.OTHER.value == 'OTHER'
    
    def test_enum_count(self):
        """Test that TaxJurisdiction has exactly 4 values."""
        assert len(TaxJurisdiction) == 4
    
    def test_franking_credits_support(self):
        """Test franking credits support detection."""
        assert TaxJurisdiction.has_franking_credits(TaxJurisdiction.AU) is True
        assert TaxJurisdiction.has_franking_credits(TaxJurisdiction.US) is False
        assert TaxJurisdiction.has_franking_credits(TaxJurisdiction.UK) is False
    
    def test_cgt_discount_support(self):
        """Test capital gains tax discount support."""
        assert TaxJurisdiction.has_cgt_discount(TaxJurisdiction.AU) is True
        assert TaxJurisdiction.has_cgt_discount(TaxJurisdiction.UK) is True
        assert TaxJurisdiction.has_cgt_discount(TaxJurisdiction.US) is False


class TestGroupType:
    """Test suite for GroupType enum."""
    
    def test_enum_values(self):
        """Test that GroupType has the correct values."""
        assert GroupType.INTEREST_WITHHOLDING.value == 'INTEREST_WITHHOLDING'
        assert GroupType.TAX_STATEMENT.value == 'TAX_STATEMENT'
    
    def test_enum_count(self):
        """Test that GroupType has exactly 2 values."""
        assert len(GroupType) == 2


class TestEnumUtilityFunctions:
    """Test suite for enum utility functions."""
    
    def test_get_all_enum_values(self):
        """Test getting all enum values."""
        fund_status_values = get_all_enum_values(FundStatus)
        assert 'ACTIVE' in fund_status_values
        assert 'SUSPENDED' in fund_status_values
        assert 'REALIZED' in fund_status_values
        assert 'COMPLETED' in fund_status_values
        assert len(fund_status_values) == 4
    
    def test_validate_enum_value_valid(self):
        """Test validating valid enum values."""
        assert validate_enum_value(FundStatus, 'ACTIVE') is True
        assert validate_enum_value(FundTrackingType, 'NAV_BASED') is True
    
    def test_validate_enum_value_invalid(self):
        """Test validating invalid enum values."""
        assert validate_enum_value(FundStatus, 'invalid') is False
        assert validate_enum_value(FundTrackingType, 'invalid_type') is False
    
    def test_get_enum_display_name(self):
        """Test getting human-readable display names."""
        assert get_enum_display_name(FundStatus.ACTIVE) == 'Active'
        assert get_enum_display_name(FundTrackingType.NAV_BASED) == 'Nav Based'
        assert get_enum_display_name(EventType.CAPITAL_CALL) == 'Capital Call'


class TestEnumIntegration:
    """Test suite for enum integration and usage patterns."""
    
    def test_enum_comparison(self):
        """Test that enum comparison works correctly."""
        status = FundStatus.ACTIVE
        assert status == FundStatus.ACTIVE
        assert status != FundStatus.REALIZED
        assert status.value == 'ACTIVE'
    
    def test_enum_in_collections(self):
        """Test that enums work correctly in collections."""
        statuses = {FundStatus.ACTIVE, FundStatus.REALIZED}
        assert FundStatus.ACTIVE in statuses
        assert FundStatus.COMPLETED not in statuses
    
    def test_enum_as_dict_keys(self):
        """Test that enums work correctly as dictionary keys."""
        status_map = {
            FundStatus.ACTIVE: "Fund is ACTIVE",
            FundStatus.REALIZED: "Fund is realized"
        }
        assert status_map[FundStatus.ACTIVE] == "Fund is ACTIVE"
        assert status_map[FundStatus.REALIZED] == "Fund is realized"
