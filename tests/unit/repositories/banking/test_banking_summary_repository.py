"""
Banking Summary Repository Tests

This module provides comprehensive testing for the BankingSummaryRepository class,
following enterprise testing standards with focused, targeted test coverage.

Tests cover:
- Banking summary data and statistics
- Aggregated calculations across banks and accounts
- Cross-module data access for reporting
- Performance-optimized summary queries
- Repository caching behavior and invalidation

Testing Approach: Mock-Based Testing (Unit Tests)
Reasoning: Repository logic should be tested without database dependencies for fast execution
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone
from decimal import Decimal

from src.banking.repositories.banking_summary_repository import BankingSummaryRepository
from src.banking.models.bank import Bank
from src.banking.models.bank_account import BankAccount
from src.banking.enums import Country, Currency, AccountStatus


class TestBankingSummaryRepository:
    """Test suite for BankingSummaryRepository - Summary data and aggregated calculations"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session for testing."""
        session = Mock()
        
        # Create a mock query object that can be chained
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.first.return_value = None
        mock_query.all.return_value = []
        mock_query.count.return_value = 0
        mock_query.scalar.return_value = 0
        mock_query.distinct.return_value = mock_query
        
        session.query.return_value = mock_query
        return session
    
    def create_mock_query_chain(self, final_return_value):
        """Helper method to create a properly chained mock query."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        
        # Set the final return value based on the method called
        if hasattr(final_return_value, '__iter__') and not isinstance(final_return_value, str):
            # For lists/tuples, set both all() and the group_by().all() chain
            mock_query.all.return_value = final_return_value
            # Also set the group_by().all() chain to return the same value
            mock_query.group_by.return_value.all.return_value = final_return_value
        else:
            # For scalars, set count, scalar, and first methods
            mock_query.count.return_value = final_return_value
            mock_query.scalar.return_value = final_return_value
            mock_query.first.return_value = final_return_value
            
        return mock_query
    
    @pytest.fixture
    def sample_bank(self):
        """Sample bank object for testing."""
        bank = Mock(spec=Bank)
        bank.id = 1
        bank.name = "Test Bank"
        bank.country = Country.AU
        bank.swift_bic = "TESTAU2S"
        return bank
    
    @pytest.fixture
    def sample_bank_account(self):
        """Sample bank account object for testing."""
        account = Mock(spec=BankAccount)
        account.id = 1
        account.entity_id = 1
        account.bank_id = 1
        account.account_name = "Test Account"
        account.account_number = "1234567890"
        account.currency = Currency.AUD
        account.status = AccountStatus.ACTIVE
        account.is_active = True
        return account
    
    @pytest.fixture
    def banking_summary_repository(self):
        """BankingSummaryRepository instance for testing."""
        return BankingSummaryRepository(cache_ttl=300)

    # ============================================================================
    # BANKING OVERVIEW TESTING
    # ============================================================================
    
    def test_get_banking_overview_cache_hit(self, banking_summary_repository, mock_session):
        """Test get_banking_overview returns cached overview when available."""
        cached_overview = {
            'total_banks': 5,
            'total_accounts': 20,
            'active_accounts': 18,
            'inactive_accounts': 2,
            'currency_distribution': {'AUD': 15, 'USD': 5},
            'country_distribution': {'AU': 3, 'US': 2}
        }
        banking_summary_repository._cache['banking:overview'] = cached_overview
        
        result = banking_summary_repository.get_banking_overview(mock_session)
        
        assert result == cached_overview
        mock_session.query.assert_not_called()
    
    def test_get_banking_overview_cache_miss(self, banking_summary_repository, mock_session):
        """Test get_banking_overview queries database and caches result on cache miss."""
        # Create separate mock queries for each database call using the helper method
        mock_bank_count = self.create_mock_query_chain(5)
        mock_account_count = self.create_mock_query_chain(20)
        mock_active_count = self.create_mock_query_chain(18)
        mock_inactive_count = self.create_mock_query_chain(2)
        
        mock_currency_query = self.create_mock_query_chain([
            ('AUD', 15), ('USD', 5)
        ])
        
        mock_country_query = self.create_mock_query_chain([
            ('AU', 3), ('US', 2)
        ])
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [
            mock_bank_count,      # Bank.count()
            mock_account_count,    # BankAccount.count()
            mock_active_count,     # BankAccount.filter().count() for active
            mock_inactive_count,   # BankAccount.filter().filter().count() for inactive
            mock_currency_query,   # BankAccount.currency group by
            mock_country_query     # Bank.country group by
        ]
        
        result = banking_summary_repository.get_banking_overview(mock_session)
        
        assert result['total_banks'] == 5
        assert result['total_accounts'] == 20
        assert result['active_accounts'] == 18
        assert result['inactive_accounts'] == 2
        assert "banking:overview" in banking_summary_repository._cache
    
    def test_get_banking_overview_currency_distribution(self, banking_summary_repository, mock_session):
        """Test get_banking_overview properly formats currency distribution."""
        # Create separate mock queries for each database call using the helper method
        mock_bank_count = self.create_mock_query_chain(2)
        mock_account_count = self.create_mock_query_chain(5)
        mock_active_count = self.create_mock_query_chain(4)
        mock_inactive_count = self.create_mock_query_chain(1)
        
        # Mock the currency distribution query
        mock_currency_query = self.create_mock_query_chain([
            ('AUD', 3), ('USD', 2)
        ])
        
        # Mock the country distribution query
        mock_country_query = self.create_mock_query_chain([
            ('AU', 2)
        ])
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [
            mock_bank_count,      # Bank.count()
            mock_account_count,    # BankAccount.count()
            mock_active_count,     # BankAccount.filter().filter().count() for active
            mock_inactive_count,   # BankAccount.filter().filter().filter().count() for inactive
            mock_currency_query,   # BankAccount.currency group by
            mock_country_query     # Bank.country group by
        ]
        
        result = banking_summary_repository.get_banking_overview(mock_session)
        
        assert result['currency_distribution'] == {'AUD': 3, 'USD': 2}
        assert result['country_distribution'] == {'AU': 2}

    # ============================================================================
    # BANK SUMMARY TESTING
    # ============================================================================
    
    def test_get_bank_summary_cache_hit(self, banking_summary_repository, mock_session):
        """Test get_bank_summary returns cached summary when available."""
        cached_summary = {
            'bank_id': 1,
            'bank_name': 'Test Bank',
            'total_accounts': 10,
            'active_accounts': 8,
            'inactive_accounts': 2
        }
        banking_summary_repository._cache['banking:bank_summary:1'] = cached_summary
        
        result = banking_summary_repository.get_bank_summary(1, mock_session)
        
        assert result == cached_summary
        mock_session.query.assert_not_called()
    
    def test_get_bank_summary_cache_miss(self, banking_summary_repository, mock_session):
        """Test get_bank_summary queries database and caches result on cache miss."""
        # Mock bank query with proper attribute access
        mock_bank = Mock()
        mock_bank.id = 1
        mock_bank.name = "Test Bank"
        mock_bank.country = Country.AU
        mock_bank.swift_bic = "TESTAU2S"
        
        mock_bank_query = self.create_mock_query_chain(mock_bank)
        
        # Mock account stats query
        mock_stats_query = self.create_mock_query_chain([
            ('AUD', AccountStatus.ACTIVE, 5),   # AUD, active, count 5
            ('AUD', AccountStatus.SUSPENDED, 1),  # AUD, inactive, count 1
            ('USD', AccountStatus.ACTIVE, 3),   # USD, active, count 3
            ('USD', AccountStatus.SUSPENDED, 1)   # USD, inactive, count 1
        ])
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [mock_bank_query, mock_stats_query]
        
        result = banking_summary_repository.get_bank_summary(1, mock_session)
        
        assert result['bank_id'] == 1
        assert result['bank_name'] == "Test Bank"
        assert result['total_accounts'] == 10
        assert result['active_accounts'] == 8
        assert result['inactive_accounts'] == 2
        assert "banking:bank_summary:1" in banking_summary_repository._cache
    
    def test_get_bank_summary_bank_not_found(self, banking_summary_repository, mock_session):
        """Test get_bank_summary returns empty dict when bank not found."""
        mock_query = self.create_mock_query_chain(None)
        mock_session.query.return_value = mock_query
        
        result = banking_summary_repository.get_bank_summary(999, mock_session)
        
        assert result == {}
    
    def test_get_bank_summary_currency_stats_formatting(self, banking_summary_repository, mock_session):
        """Test get_bank_summary properly formats currency statistics."""
        # Mock bank query with proper attribute access
        mock_bank = Mock()
        mock_bank.id = 1
        mock_bank.name = "Test Bank"
        mock_bank.country = Country.AU
        mock_bank.swift_bic = "TESTAU2S"
        
        mock_bank_query = self.create_mock_query_chain(mock_bank)
        
        # Mock account stats query with specific currency data
        mock_stats_query = self.create_mock_query_chain([
            ('AUD', AccountStatus.ACTIVE, 3),   # AUD, active, count 3
            ('AUD', AccountStatus.SUSPENDED, 1),  # AUD, inactive, count 1
        ])
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [mock_bank_query, mock_stats_query]
        
        result = banking_summary_repository.get_bank_summary(1, mock_session)
        
        assert result['currency_distribution']['AUD']['active'] == 3
        assert result['currency_distribution']['AUD']['inactive'] == 1

    # ============================================================================
    # ENTITY BANKING SUMMARY TESTING
    # ============================================================================
    
    def test_get_entity_banking_summary_cache_hit(self, banking_summary_repository, mock_session):
        """Test get_entity_banking_summary returns cached summary when available."""
        cached_summary = {
            'entity_id': 1,
            'total_accounts': 5,
            'active_accounts': 4,
            'inactive_accounts': 1
        }
        banking_summary_repository._cache['banking:entity_summary:1'] = cached_summary
        
        result = banking_summary_repository.get_entity_banking_summary(1, mock_session)
        
        assert result == cached_summary
        mock_session.query.assert_not_called()
    
    def test_get_entity_banking_summary_cache_miss(self, banking_summary_repository, mock_session):
        """Test get_entity_banking_summary queries database and caches result on cache miss."""
        # Mock account stats query
        mock_stats_query = self.create_mock_query_chain([
            (1, 'AUD', AccountStatus.ACTIVE, 3),   # bank_id, currency, active, count
            (1, 'AUD', AccountStatus.SUSPENDED, 1),  # AUD, inactive, count 1
            (2, 'USD', AccountStatus.ACTIVE, 1),   # bank_id, currency, active, count
        ])
        
        # Mock bank query with proper attribute access
        mock_bank_1 = Mock()
        mock_bank_1.id = 1
        mock_bank_1.name = "Bank 1"
        mock_bank_1.country = Country.AU
        
        mock_bank_2 = Mock()
        mock_bank_2.id = 2
        mock_bank_2.name = "Bank 2"
        mock_bank_2.country = Country.US
        
        mock_bank_query = self.create_mock_query_chain([mock_bank_1, mock_bank_2])
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [mock_stats_query, mock_bank_query]
        
        result = banking_summary_repository.get_entity_banking_summary(1, mock_session)
        
        assert result['entity_id'] == 1
        assert result['total_accounts'] == 5
        assert result['active_accounts'] == 4
        assert result['inactive_accounts'] == 1
        assert "banking:entity_summary:1" in banking_summary_repository._cache
    
    def test_get_entity_banking_summary_bank_distribution(self, banking_summary_repository, mock_session):
        """Test get_entity_banking_summary properly formats bank distribution."""
        # Mock account stats query
        mock_stats_query = self.create_mock_query_chain([
            (1, 'AUD', AccountStatus.ACTIVE, 2),   # bank_id, currency, active, count
            (1, 'AUD', AccountStatus.SUSPENDED, 1),  # bank_id, currency, inactive, count
        ])
        
        # Mock bank query with proper attribute access
        mock_bank = Mock()
        mock_bank.id = 1
        mock_bank.name = "Bank 1"
        mock_bank.country = Country.AU
        
        mock_bank_query = self.create_mock_query_chain([mock_bank])
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [mock_stats_query, mock_bank_query]
        
        result = banking_summary_repository.get_entity_banking_summary(1, mock_session)
        
        assert result['bank_distribution'][1]['bank_name'] == "Bank 1"
        assert result['bank_distribution'][1]['accounts']['active'] == 2
        assert result['bank_distribution'][1]['accounts']['inactive'] == 1

    # ============================================================================
    # CURRENCY SUMMARY TESTING
    # ============================================================================
    
    def test_get_currency_summary_cache_hit(self, banking_summary_repository, mock_session):
        """Test get_currency_summary returns cached summary when available."""
        cached_summary = {
            'AUD': {'active': 10, 'inactive': 2, 'total': 12},
            'USD': {'active': 5, 'inactive': 1, 'total': 6}
        }
        banking_summary_repository._cache['banking:currency_summary'] = cached_summary
        
        result = banking_summary_repository.get_currency_summary(mock_session)
        
        assert result == cached_summary
        mock_session.query.assert_not_called()
    
    def test_get_currency_summary_cache_miss(self, banking_summary_repository, mock_session):
        """Test get_currency_summary queries database and caches result on cache miss."""
        # Mock currency stats query
        mock_query = Mock()
        mock_query.group_by.return_value.all.return_value = [
            ('AUD', AccountStatus.ACTIVE, 10),   # currency, active, count
            ('AUD', AccountStatus.SUSPENDED, 2),   # currency, inactive, count
            ('USD', AccountStatus.ACTIVE, 5),    # currency, active, count
            ('USD', AccountStatus.SUSPENDED, 1),   # currency, inactive, count
        ]
        mock_session.query.return_value = mock_query
        
        result = banking_summary_repository.get_currency_summary(mock_session)
        
        assert result['AUD']['active'] == 10
        assert result['AUD']['inactive'] == 2
        assert result['AUD']['total'] == 12
        assert result['USD']['active'] == 5
        assert result['USD']['inactive'] == 1
        assert result['USD']['total'] == 6
        assert "banking:currency_summary" in banking_summary_repository._cache

    # ============================================================================
    # COUNTRY SUMMARY TESTING
    # ============================================================================
    
    def test_get_country_summary_cache_hit(self, banking_summary_repository, mock_session):
        """Test get_country_summary returns cached summary when available."""
        cached_summary = {
            'AU': {'bank_count': 3, 'account_count': 15},
            'US': {'bank_count': 2, 'account_count': 10}
        }
        banking_summary_repository._cache['banking:country_summary'] = cached_summary
        
        result = banking_summary_repository.get_country_summary(mock_session)
        
        assert result == cached_summary
        mock_session.query.assert_not_called()
    
    def test_get_country_summary_cache_miss(self, banking_summary_repository, mock_session):
        """Test get_country_summary queries database and caches result on cache miss."""
        # Mock country stats query
        mock_query = Mock()
        mock_query.outerjoin.return_value.group_by.return_value.all.return_value = [
            ('AU', 3, 15),  # country, bank_count, account_count
            ('US', 2, 10),  # country, bank_count, account_count
        ]
        mock_session.query.return_value = mock_query
        
        result = banking_summary_repository.get_country_summary(mock_session)
        
        assert result['AU']['bank_count'] == 3
        assert result['AU']['account_count'] == 15
        assert result['US']['bank_count'] == 2
        assert result['US']['account_count'] == 10
        assert "banking:country_summary" in banking_summary_repository._cache

    # ============================================================================
    # TOP BANKS BY ACCOUNTS TESTING
    # ============================================================================
    
    def test_get_top_banks_by_accounts_cache_hit(self, banking_summary_repository, mock_session):
        """Test get_top_banks_by_accounts returns cached results when available."""
        cached_results = [
            {'bank_id': 1, 'bank_name': 'Bank 1', 'bank_country': 'AU', 'account_count': 10},
            {'bank_id': 2, 'bank_name': 'Bank 2', 'bank_country': 'US', 'account_count': 8}
        ]
        banking_summary_repository._cache['banking:top_banks:5'] = cached_results
        
        result = banking_summary_repository.get_top_banks_by_accounts(mock_session, limit=5)
        
        assert result == cached_results
        mock_session.query.assert_not_called()
    
    def test_get_top_banks_by_accounts_cache_miss(self, banking_summary_repository, mock_session):
        """Test get_top_banks_by_accounts queries database and caches result on cache miss."""
        # Mock top banks query with proper bank objects
        mock_bank_1 = Mock()
        mock_bank_1.id = 1
        mock_bank_1.name = "Bank 1"
        mock_bank_1.country = Country.AU
        
        mock_bank_2 = Mock()
        mock_bank_2.id = 2
        mock_bank_2.name = "Bank 2"
        mock_bank_2.country = Country.US
        
        mock_query = self.create_mock_query_chain([
            (mock_bank_1, 10),
            (mock_bank_2, 8)
        ])
        mock_session.query.return_value = mock_query
        
        result = banking_summary_repository.get_top_banks_by_accounts(mock_session, limit=5)
        
        assert len(result) == 2
        assert result[0]['bank_id'] == 1
        assert result[0]['bank_name'] == "Bank 1"
        assert result[0]['account_count'] == 10
        assert result[1]['bank_id'] == 2
        assert result[1]['bank_name'] == "Bank 2"
        assert result[1]['account_count'] == 8
        assert "banking:top_banks:5" in banking_summary_repository._cache

    # ============================================================================
    # BANKING ACTIVITY SUMMARY TESTING
    # ============================================================================
    
    def test_get_banking_activity_summary_cache_hit(self, banking_summary_repository, mock_session):
        """Test get_banking_activity_summary returns cached summary when available."""
        cached_summary = {
            'total_banks': 5,
            'total_accounts': 20,
            'active_accounts': 18,
            'inactive_accounts': 2,
            'unique_currencies': 3,
            'unique_countries': 2,
            'accounts_per_bank_avg': 4.0,
            'activity_rate': 90.0
        }
        banking_summary_repository._cache['banking:activity_summary'] = cached_summary
        
        result = banking_summary_repository.get_banking_activity_summary(mock_session)
        
        assert result == cached_summary
        mock_session.query.assert_not_called()
    
    def test_get_banking_activity_summary_cache_miss(self, banking_summary_repository, mock_session):
        """Test get_banking_activity_summary queries database and caches result on cache miss."""
        # Create separate mock queries for each database call using the helper method
        mock_bank_count = self.create_mock_query_chain(5)  # total_banks
        mock_account_count = self.create_mock_query_chain(20)  # total_accounts
        mock_active_count = self.create_mock_query_chain(18)  # active_accounts
        
        # Mock distinct count queries
        mock_currency_distinct = self.create_mock_query_chain(3)  # unique_currencies
        mock_country_distinct = self.create_mock_query_chain(2)  # unique_countries
        
        # Mock average accounts per bank query
        mock_avg_query = self.create_mock_query_chain(4.0)
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [
            mock_bank_count,        # Bank.count()
            mock_account_count,      # BankAccount.count()
            mock_active_count,       # BankAccount.filter().filter().count() for active
            mock_currency_distinct,  # BankAccount.currency.distinct().count()
            mock_country_distinct,   # Bank.country.distinct().count()
            mock_avg_query          # BankAccount join Bank group by avg
        ]
        
        result = banking_summary_repository.get_banking_activity_summary(mock_session)
        
        assert result['total_banks'] == 5
        assert result['total_accounts'] == 20
        assert result['active_accounts'] == 18
        assert result['inactive_accounts'] == 2
        assert result['unique_currencies'] == 3
        assert result['unique_countries'] == 2
        assert result['accounts_per_bank_avg'] == 4.0
        assert result['activity_rate'] == 90.0
        assert "banking:activity_summary" in banking_summary_repository._cache
    
    def test_get_banking_activity_summary_zero_accounts(self, banking_summary_repository, mock_session):
        """Test get_banking_activity_summary handles zero accounts gracefully."""
        # Mock queries returning zero using the helper method
        mock_bank_count = self.create_mock_query_chain(0)  # total_banks
        mock_account_count = self.create_mock_query_chain(0)  # total_accounts
        mock_active_count = self.create_mock_query_chain(0)  # active_accounts
        
        mock_currency_distinct = self.create_mock_query_chain(0)  # unique_currencies
        mock_country_distinct = self.create_mock_query_chain(0)  # unique_countries
        
        mock_avg_query = self.create_mock_query_chain(None)
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [
            mock_bank_count,        # Bank.count()
            mock_account_count,      # BankAccount.count()
            mock_active_count,       # BankAccount.filter().filter().count() for active
            mock_currency_distinct,  # BankAccount.currency.distinct().count()
            mock_country_distinct,   # Bank.country.distinct().count()
            mock_avg_query          # BankAccount join Bank group by avg
        ]
        
        result = banking_summary_repository.get_banking_activity_summary(mock_session)
        
        assert result['total_accounts'] == 0
        assert result['active_accounts'] == 0
        assert result['inactive_accounts'] == 0
        assert result['activity_rate'] == 0.0
        assert result['accounts_per_bank_avg'] == 0

    # ============================================================================
    # CACHE MANAGEMENT TESTING
    # ============================================================================
    
    def test_clear_cache(self, banking_summary_repository, mock_session):
        """Test clear_cache removes all cached data."""
        # Populate cache
        banking_summary_repository._cache['banking:overview'] = {}
        banking_summary_repository._cache['banking:bank_summary:1'] = {}
        banking_summary_repository._cache['other:data'] = 'value'
        
        banking_summary_repository.clear_cache()
        
        assert len(banking_summary_repository._cache) == 0
    
    def test_clear_bank_caches(self, banking_summary_repository, mock_session):
        """Test clear_bank_caches removes only bank-related caches."""
        # Populate cache with mixed data
        banking_summary_repository._cache['banking:bank_summary:1'] = {}
        banking_summary_repository._cache['banking:overview'] = {}
        banking_summary_repository._cache['other:data'] = 'value'
        
        banking_summary_repository.clear_bank_caches(1)
        
        assert 'other:data' in banking_summary_repository._cache
        assert 'banking:bank_summary:1' not in banking_summary_repository._cache
        assert 'banking:overview' in banking_summary_repository._cache  # Not bank-specific
    
    def test_clear_entity_caches(self, banking_summary_repository, mock_session):
        """Test clear_entity_caches removes only entity-related caches."""
        # Populate cache with mixed data
        banking_summary_repository._cache['banking:entity_summary:1'] = {}
        banking_summary_repository._cache['banking:overview'] = {}
        banking_summary_repository._cache['other:data'] = 'value'
        
        banking_summary_repository.clear_entity_caches(1)
        
        assert 'other:data' in banking_summary_repository._cache
        assert 'banking:entity_summary:1' not in banking_summary_repository._cache
        assert 'banking:overview' in banking_summary_repository._cache  # Not entity-specific
    
    def test_cache_ttl_initialization(self):
        """Test repository initializes with correct cache TTL."""
        repo = BankingSummaryRepository(cache_ttl=600)
        assert repo._cache_ttl == 600
        
        repo_default = BankingSummaryRepository()
        assert repo_default._cache_ttl == 300  # Default value

    # ============================================================================
    # EDGE CASES AND ERROR HANDLING
    # ============================================================================
    
    def test_get_bank_summary_zero_id(self, banking_summary_repository, mock_session):
        """Test get_bank_summary handles zero bank ID gracefully."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = banking_summary_repository.get_bank_summary(0, mock_session)
        
        assert result == {}
    
    def test_get_bank_summary_negative_id(self, banking_summary_repository, mock_session):
        """Test get_bank_summary handles negative bank ID gracefully."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = banking_summary_repository.get_bank_summary(-1, mock_session)
        
        assert result == {}
    
    def test_get_entity_banking_summary_zero_id(self, banking_summary_repository, mock_session):
        """Test get_entity_banking_summary handles zero entity ID gracefully."""
        mock_query = self.create_mock_query_chain([])
        mock_session.query.return_value = mock_query
        
        result = banking_summary_repository.get_entity_banking_summary(0, mock_session)
        
        assert result['entity_id'] == 0
        assert result['total_accounts'] == 0
        assert result['active_accounts'] == 0
        assert result['inactive_accounts'] == 0
    
    def test_get_entity_banking_summary_negative_id(self, banking_summary_repository, mock_session):
        """Test get_entity_banking_summary handles negative entity ID gracefully."""
        mock_query = self.create_mock_query_chain([])
        mock_session.query.return_value = mock_query
        
        result = banking_summary_repository.get_entity_banking_summary(-1, mock_session)
        
        assert result['entity_id'] == -1
        assert result['total_accounts'] == 0
        assert result['active_accounts'] == 0
        assert result['inactive_accounts'] == 0
    
    def test_get_top_banks_by_accounts_zero_limit(self, banking_summary_repository, mock_session):
        """Test get_top_banks_by_accounts handles zero limit gracefully."""
        mock_query = self.create_mock_query_chain([])
        mock_session.query.return_value = mock_query
        
        result = banking_summary_repository.get_top_banks_by_accounts(mock_session, limit=0)
        
        assert result == []
    
    def test_get_top_banks_by_accounts_negative_limit(self, banking_summary_repository, mock_session):
        """Test get_top_banks_by_accounts handles negative limit gracefully."""
        mock_query = self.create_mock_query_chain([])
        mock_session.query.return_value = mock_query
        
        result = banking_summary_repository.get_top_banks_by_accounts(mock_session, limit=-5)
        
        assert result == []
    
    def test_empty_database_handling(self, banking_summary_repository, mock_session):
        """Test repository handles empty database gracefully."""
        # Create a simple mock that returns 0 for count() and [] for all()
        mock_query = Mock()
        mock_query.count.return_value = 0
        mock_query.all.return_value = []
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        
        mock_session.query.return_value = mock_query
        
        # Test just the overview method with empty database
        overview = banking_summary_repository.get_banking_overview(mock_session)
        assert overview['total_banks'] == 0
        assert overview['total_accounts'] == 0
        assert overview['active_accounts'] == 0
        assert overview['inactive_accounts'] == 0
        assert overview['currency_distribution'] == {}
        assert overview['country_distribution'] == {}
        
        # Test that the result was cached
        assert "banking:overview" in banking_summary_repository._cache
