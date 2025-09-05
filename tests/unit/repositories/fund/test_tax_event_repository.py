"""
Test TaxEventRepository functionality.

This module tests the TaxEventRepository that provides
data access operations for tax-related fund events.

Testing Focus:
- Tax event CRUD operations
- Tax event querying and filtering
- Tax event aggregations
- Interest charge operations
- Data persistence operations
- Caching behavior and invalidation

Testing Approach: Mock-Based Testing (Unit Tests)
- Use mocks for database session and query results
- Test repository logic in isolation
- Focus on data access patterns and validation
- Validate caching behavior and performance
"""

import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.fund.repositories.tax_event_repository import TaxEventRepository
from src.fund.models import FundEvent
from src.fund.enums import EventType, SortOrder, DistributionType, TaxPaymentType, GroupType


class TestTaxEventRepository:
    """Test the TaxEventRepository class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create repository instance
        self.repository = TaxEventRepository(cache_ttl=300)
        
        # Create mock session
        self.mock_session = Mock(spec=Session)
        
        # Create mock tax events
        self.mock_tax_payment = Mock(spec=FundEvent)
        self.mock_tax_payment.id = 1
        self.mock_tax_payment.fund_id = 100
        self.mock_tax_payment.event_type = EventType.TAX_PAYMENT
        self.mock_tax_payment.event_date = date(2024, 1, 15)
        self.mock_tax_payment.amount = 5000.0
        
        self.mock_interest_charge = Mock(spec=FundEvent)
        self.mock_interest_charge.id = 2
        self.mock_interest_charge.fund_id = 100
        self.mock_interest_charge.event_type = EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        self.mock_interest_charge.event_date = date(2024, 2, 15)
        self.mock_interest_charge.amount = 100.0
        
        self.mock_eofy_debt = Mock(spec=FundEvent)
        self.mock_eofy_debt.id = 3
        self.mock_eofy_debt.fund_id = 100
        self.mock_eofy_debt.event_type = EventType.EOFY_DEBT_COST
        self.mock_eofy_debt.event_date = date(2024, 6, 30)
        self.mock_eofy_debt.amount = 2000.0
        
        self.mock_tax_events = [self.mock_tax_payment, self.mock_interest_charge, self.mock_eofy_debt]
    
    # ============================================================================
    # CREATE METHODS
    # ============================================================================
    
    def test_create_tax_payment_success(self):
        """Test successful creation of tax payment event."""
        # Arrange
        fund_id = 100
        event_data = {
            'event_date': date(2024, 1, 15),
            'amount': 5000.0,
            'description': 'Tax payment'
        }
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        
        # Act
        with patch('src.fund.repositories.tax_event_repository.FundEvent') as mock_fund_event_class:
            mock_fund_event_class.return_value = self.mock_tax_payment
            result = self.repository.create_tax_payment(fund_id, event_data, self.mock_session)
        
        # Assert
        assert result == self.mock_tax_payment
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        
        # Verify event_data was modified correctly
        assert event_data['event_type'] == EventType.TAX_PAYMENT
        assert event_data['fund_id'] == fund_id
    
    def test_create_daily_interest_charge_success(self):
        """Test successful creation of daily interest charge event."""
        # Arrange
        fund_id = 100
        event_data = {
            'event_date': date(2024, 2, 15),
            'amount': 100.0,
            'description': 'Daily interest charge'
        }
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        
        # Act
        with patch('src.fund.repositories.tax_event_repository.FundEvent') as mock_fund_event_class:
            mock_fund_event_class.return_value = self.mock_interest_charge
            result = self.repository.create_daily_interest_charge(fund_id, event_data, self.mock_session)
        
        # Assert
        assert result == self.mock_interest_charge
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        
        # Verify event_data was modified correctly
        assert event_data['event_type'] == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        assert event_data['fund_id'] == fund_id
    
    def test_create_eofy_debt_cost_success(self):
        """Test successful creation of EOFY debt cost event."""
        # Arrange
        fund_id = 100
        event_data = {
            'event_date': date(2024, 6, 30),
            'amount': 2000.0,
            'description': 'EOFY debt cost'
        }
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        
        # Act
        with patch('src.fund.repositories.tax_event_repository.FundEvent') as mock_fund_event_class:
            mock_fund_event_class.return_value = self.mock_eofy_debt
            result = self.repository.create_eofy_debt_cost(fund_id, event_data, self.mock_session)
        
        # Assert
        assert result == self.mock_eofy_debt
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        
        # Verify event_data was modified correctly
        assert event_data['event_type'] == EventType.EOFY_DEBT_COST
        assert event_data['fund_id'] == fund_id
    
    # ============================================================================
    # QUERY METHODS
    # ============================================================================
    
    def test_get_tax_events_success(self):
        """Test successful retrieval of tax events."""
        # Arrange
        fund_id = 100
        skip = 0
        limit = 10
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = self.mock_tax_events
        
        # Act
        result = self.repository.get_tax_events(
            fund_id, self.mock_session, skip, limit, start_date, end_date
        )
        
        # Assert
        assert result == self.mock_tax_events
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called_once()
        mock_query.offset.assert_called_once_with(skip)
        mock_query.limit.assert_called_once_with(limit)
        mock_query.all.assert_called_once()
    
    def test_get_tax_events_caching(self):
        """Test that get_tax_events uses caching."""
        # Arrange
        fund_id = 100
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = self.mock_tax_events
        
        # Act - First call
        result1 = self.repository.get_tax_events(fund_id, self.mock_session)
        
        # Act - Second call (should use cache)
        result2 = self.repository.get_tax_events(fund_id, self.mock_session)
        
        # Assert
        assert result1 == result2
        # Query should only be called once due to caching
        self.mock_session.query.assert_called_once()
    
    def test_get_tax_events_by_type_and_date_range_success(self):
        """Test successful retrieval of tax events by type and date range."""
        # Arrange
        fund_id = 100
        event_type = EventType.TAX_PAYMENT
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [self.mock_tax_payment]
        
        # Act
        result = self.repository.get_tax_events_by_type_and_date_range(
            fund_id, event_type, start_date, end_date, self.mock_session
        )
        
        # Assert
        assert result == [self.mock_tax_payment]
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
    
    # ============================================================================
    # AGGREGATION METHODS
    # ============================================================================
    
    def test_get_total_tax_payments_success(self):
        """Test successful calculation of total tax payments."""
        # Arrange
        fund_id = 100
        expected_total = 5000.0
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = expected_total
        
        # Act
        result = self.repository.get_total_tax_payments(fund_id, self.mock_session)
        
        # Assert
        assert result == expected_total
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_total_tax_payments_zero_result(self):
        """Test calculation of total tax payments when result is None."""
        # Arrange
        fund_id = 100
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None
        
        # Act
        result = self.repository.get_total_tax_payments(fund_id, self.mock_session)
        
        # Assert
        assert result == 0.0
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_total_daily_interest_charges_success(self):
        """Test successful calculation of total daily interest charges."""
        # Arrange
        fund_id = 100
        expected_total = 1000.0
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = expected_total
        
        # Act
        result = self.repository.get_total_daily_interest_charges(fund_id, self.mock_session)
        
        # Assert
        assert result == expected_total
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_daily_interest_charges_by_financial_year_success(self):
        """Test successful calculation of daily interest charges by financial year."""
        # Arrange
        fund_id = 100
        financial_year = 2024
        expected_total = 500.0
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = expected_total
        
        # Act
        result = self.repository.get_daily_interest_charges_by_financial_year(
            fund_id, financial_year, self.mock_session
        )
        
        # Assert
        assert result == expected_total
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called()
        mock_query.scalar.assert_called_once()
    
    def test_get_daily_interest_charges_by_financial_year_zero_result(self):
        """Test calculation of daily interest charges when result is None."""
        # Arrange
        fund_id = 100
        financial_year = 2024
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None
        
        # Act
        result = self.repository.get_daily_interest_charges_by_financial_year(
            fund_id, financial_year, self.mock_session
        )
        
        # Assert
        assert result == 0.0
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called()
        mock_query.scalar.assert_called_once()
    
    # ============================================================================
    # DELETE METHODS
    # ============================================================================
    
    def test_delete_tax_events_by_type_success(self):
        """Test successful deletion of tax events by type."""
        # Arrange
        fund_id = 100
        event_type = EventType.TAX_PAYMENT
        expected_count = 2
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [self.mock_tax_payment, self.mock_tax_payment]
        
        # Mock session delete
        self.mock_session.delete = Mock()
        
        # Act
        result = self.repository.delete_tax_events_by_type(fund_id, event_type, self.mock_session)
        
        # Assert
        assert result == expected_count
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.all.assert_called_once()
        assert self.mock_session.delete.call_count == expected_count
    
    def test_delete_tax_events_by_type_no_events(self):
        """Test deletion of tax events by type when no events exist."""
        # Arrange
        fund_id = 100
        event_type = EventType.TAX_PAYMENT
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        
        # Mock session delete
        self.mock_session.delete = Mock()
        
        # Act
        result = self.repository.delete_tax_events_by_type(fund_id, event_type, self.mock_session)
        
        # Assert
        assert result == 0
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.all.assert_called_once()
        self.mock_session.delete.assert_not_called()
    
    # ============================================================================
    # CACHE MANAGEMENT
    # ============================================================================
    
    def test_clear_fund_cache(self):
        """Test clearing cache for a specific fund."""
        # Arrange
        fund_id = 100
        
        # Add some cache entries
        self.repository._cache = {
            f"fund:{fund_id}:tax_events": self.mock_tax_events,
            f"fund:{fund_id}:total_tax_payments": 5000.0,
            "fund:200:tax_events": [self.mock_tax_payment],
            "other:key": "value"
        }
        
        # Act
        self.repository._clear_fund_cache(fund_id)
        
        # Assert
        expected_cache = {
            "fund:200:tax_events": [self.mock_tax_payment],
            "other:key": "value"
        }
        assert self.repository._cache == expected_cache
    
    def test_clear_all_cache(self):
        """Test clearing all cache entries."""
        # Arrange
        self.repository._cache = {
            "key1": "value1",
            "key2": "value2"
        }
        
        # Act
        self.repository.clear_all_cache()
        
        # Assert
        assert self.repository._cache == {}
    
    # ============================================================================
    # ERROR HANDLING
    # ============================================================================
    
    def test_repository_initialization(self):
        """Test repository initialization with default cache TTL."""
        # Act
        repository = TaxEventRepository()
        
        # Assert
        assert repository._cache == {}
        assert repository._cache_ttl == 300
    
    def test_repository_initialization_custom_ttl(self):
        """Test repository initialization with custom cache TTL."""
        # Act
        repository = TaxEventRepository(cache_ttl=600)
        
        # Assert
        assert repository._cache == {}
        assert repository._cache_ttl == 600
