"""
Bank Account Repository Tests

This module provides comprehensive testing for the BankAccountRepository class,
following enterprise testing standards with focused, targeted test coverage.

Tests cover:
- Bank account CRUD operations and validation
- Bank account query performance and optimization
- Bank account data consistency and integrity
- Repository caching behavior and invalidation
- Database session management and error handling

Testing Approach: Mock-Based Testing (Unit Tests)
Reasoning: Repository logic should be tested without database dependencies for fast execution
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone
from decimal import Decimal

from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.banking.models.bank_account import BankAccount
from src.banking.models.bank import Bank
from src.banking.enums import Currency, AccountStatus, Country


class TestBankAccountRepository:
    """Test suite for BankAccountRepository - Data access and persistence logic"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session for testing."""
        session = Mock()
        
        # Create a mock query object that can be chained
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.first.return_value = None
        mock_query.all.return_value = []
        mock_query.count.return_value = 0
        mock_query.scalar.return_value = 0
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        
        session.query.return_value = mock_query
        session.add = Mock()
        session.flush = Mock()
        session.delete = Mock()
        return session
    
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
        account.created_at = datetime.now(timezone.utc)
        account.updated_at = datetime.now(timezone.utc)
        return account
    
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
    def sample_bank_accounts_list(self):
        """Sample list of bank accounts for testing."""
        accounts = []
        for i in range(3):
            account = Mock(spec=BankAccount)
            account.id = i + 1
            account.entity_id = 1
            account.bank_id = 1
            account.account_name = f"Test Account {i + 1}"
            account.account_number = f"123456789{i}"
            account.currency = Currency.AUD
            account.status = AccountStatus.ACTIVE
            accounts.append(account)
        return accounts
    
    @pytest.fixture
    def bank_account_repository(self):
        """BankAccountRepository instance for testing."""
        return BankAccountRepository(cache_ttl=300)
    
    @pytest.fixture
    def bank_account_data(self):
        """Sample bank account data for creation/update testing."""
        return {
            'entity_id': 1,
            'bank_id': 1,
            'account_name': 'New Test Account',
            'account_number': '9876543210',
            'currency': Currency.USD,
            'status': AccountStatus.ACTIVE
        }

    # ============================================================================
    # CRUD OPERATIONS TESTING
    # ============================================================================
    
    def test_get_by_id_cache_hit(self, bank_account_repository, mock_session, sample_bank_account):
        """Test get_by_id returns cached account when available."""
        bank_account_repository._cache['bank_account:1'] = sample_bank_account
        
        result = bank_account_repository.get_by_id(1, mock_session)
        
        assert result == sample_bank_account
        mock_session.query.assert_not_called()
    
    def test_get_by_id_cache_miss_database_query(self, bank_account_repository, mock_session, sample_bank_account):
        """Test get_by_id queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_bank_account
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_by_id(1, mock_session)
        
        assert result == sample_bank_account
        assert 'bank_account:1' in bank_account_repository._cache
        assert bank_account_repository._cache['bank_account:1'] == sample_bank_account
    
    def test_get_by_id_not_found(self, bank_account_repository, mock_session):
        """Test get_by_id returns None when account not found."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_by_id(999, mock_session)
        
        assert result is None
        assert 'bank_account:999' not in bank_account_repository._cache
    
    def test_get_by_unique_cache_hit(self, bank_account_repository, mock_session, sample_bank_account):
        """Test get_by_unique returns cached account when available."""
        cache_key = f"bank_account:unique:{sample_bank_account.entity_id}:{sample_bank_account.bank_id}:{sample_bank_account.account_number}"
        bank_account_repository._cache[cache_key] = sample_bank_account
        
        result = bank_account_repository.get_by_unique(
            sample_bank_account.entity_id,
            sample_bank_account.bank_id,
            sample_bank_account.account_number,
            mock_session
        )
        
        assert result == sample_bank_account
        mock_session.query.assert_not_called()
    
    def test_get_by_unique_cache_miss(self, bank_account_repository, mock_session, sample_bank_account):
        """Test get_by_unique queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_bank_account
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_by_unique(1, 1, "1234567890", mock_session)
        
        assert result == sample_bank_account
        cache_key = "bank_account:unique:1:1:1234567890"
        assert cache_key in bank_account_repository._cache
    
    def test_get_by_entity_cache_hit(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_by_entity returns cached accounts when available."""
        cache_key = f"bank_accounts:entity:1"
        bank_account_repository._cache[cache_key] = sample_bank_accounts_list
        
        result = bank_account_repository.get_by_entity(1, mock_session)
        
        assert result == sample_bank_accounts_list
        mock_session.query.assert_not_called()
    
    def test_get_by_entity_cache_miss(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_by_entity queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.options.return_value.filter.return_value.all.return_value = sample_bank_accounts_list
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_by_entity(1, mock_session)
        
        assert result == sample_bank_accounts_list
        assert "bank_accounts:entity:1" in bank_account_repository._cache
    
    def test_get_bank_accounts_paginated(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_bank_accounts_paginated returns correct pagination results."""
        # Create separate mock queries for the two different queries
        mock_count_query = Mock()
        mock_count_query.scalar.return_value = 3
        
        mock_data_query = Mock()
        mock_data_query.options.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = sample_bank_accounts_list
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [mock_count_query, mock_data_query]
        
        accounts, total_count = bank_account_repository.get_bank_accounts_paginated(mock_session, page=1, page_size=2)
        
        assert accounts == sample_bank_accounts_list
        assert total_count == 3
    
    def test_get_bank_accounts_paginated_page_2(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_bank_accounts_paginated handles page 2 correctly."""
        # Create separate mock queries for the two different queries
        mock_count_query = Mock()
        mock_count_query.scalar.return_value = 3
        
        mock_data_query = Mock()
        mock_data_query.options.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = sample_bank_accounts_list[2:]
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [mock_count_query, mock_data_query]
        
        accounts, total_count = bank_account_repository.get_bank_accounts_paginated(mock_session, page=2, page_size=1)
        
        assert total_count == 3
    
    def test_get_by_bank_cache_hit(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_by_bank returns cached accounts when available."""
        cache_key = f"bank_accounts:bank:1"
        bank_account_repository._cache[cache_key] = sample_bank_accounts_list
        
        result = bank_account_repository.get_by_bank(1, mock_session)
        
        assert result == sample_bank_accounts_list
        mock_session.query.assert_not_called()
    
    def test_get_by_bank_cache_miss(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_by_bank queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = sample_bank_accounts_list
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_by_bank(1, mock_session)
        
        assert result == sample_bank_accounts_list
        assert "bank_accounts:bank:1" in bank_account_repository._cache
    
    def test_get_by_currency_cache_hit(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_by_currency returns cached accounts when available."""
        cache_key = f"bank_accounts:currency:AUD"
        bank_account_repository._cache[cache_key] = sample_bank_accounts_list
        
        result = bank_account_repository.get_by_currency("AUD", mock_session)
        
        assert result == sample_bank_accounts_list
        mock_session.query.assert_not_called()
    
    def test_get_by_currency_cache_miss(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_by_currency queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = sample_bank_accounts_list
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_by_currency("AUD", mock_session)
        
        assert result == sample_bank_accounts_list
        assert "bank_accounts:currency:AUD" in bank_account_repository._cache
    
    def test_get_active_accounts_cache_hit(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_active_accounts returns cached accounts when available."""
        cache_key = "bank_accounts:active"
        bank_account_repository._cache[cache_key] = sample_bank_accounts_list
        
        result = bank_account_repository.get_active_accounts(mock_session)
        
        assert result == sample_bank_accounts_list
        mock_session.query.assert_not_called()
    
    def test_get_active_accounts_cache_miss(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_active_accounts queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = sample_bank_accounts_list
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_active_accounts(mock_session)
        
        assert result == sample_bank_accounts_list
        assert "bank_accounts:active" in bank_account_repository._cache
    
    def test_get_inactive_accounts_cache_hit(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_inactive_accounts returns cached accounts when available."""
        cache_key = "bank_accounts:inactive"
        bank_account_repository._cache[cache_key] = sample_bank_accounts_list
        
        result = bank_account_repository.get_inactive_accounts(mock_session)
        
        assert result == sample_bank_accounts_list
        mock_session.query.assert_not_called()
    
    def test_get_inactive_accounts_cache_miss(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_inactive_accounts queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = sample_bank_accounts_list
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_inactive_accounts(mock_session)
        
        assert result == sample_bank_accounts_list
        assert "bank_accounts:inactive" in bank_account_repository._cache
    
    def test_get_all_cache_hit(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_all returns cached accounts when available."""
        cache_key = "bank_accounts:all"
        bank_account_repository._cache[cache_key] = sample_bank_accounts_list
        
        result = bank_account_repository.get_all(mock_session)
        
        assert result == sample_bank_accounts_list
        mock_session.query.assert_not_called()
    
    def test_get_all_cache_miss(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test get_all queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.all.return_value = sample_bank_accounts_list
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_all(mock_session)
        
        assert result == sample_bank_accounts_list
        assert "bank_accounts:all" in bank_account_repository._cache
    
    def test_get_with_bank_info(self, bank_account_repository, mock_session):
        """Test get_with_bank_info returns accounts with bank information."""
        # Create properly configured mock objects
        mock_bank1 = Mock(spec=Bank)
        mock_bank1.name = "Bank 1"
        mock_bank1.country = Country.AU
        mock_bank1.swift_bic = "BANK1"
        
        mock_bank2 = Mock(spec=Bank)
        mock_bank2.name = "Bank 2"
        mock_bank2.country = Country.US
        mock_bank2.swift_bic = "BANK2"
        
        mock_result = [
            (Mock(spec=BankAccount, id=1, entity_id=1, bank_id=1, account_name="Account 1", 
                  account_number="123", currency=Currency.AUD, status=AccountStatus.ACTIVE),
             mock_bank1),
            (Mock(spec=BankAccount, id=2, entity_id=1, bank_id=2, account_name="Account 2", 
                  account_number="456", currency=Currency.USD, status=AccountStatus.ACTIVE),
             mock_bank2)
        ]
        
        mock_query = Mock()
        mock_query.join.return_value.all.return_value = mock_result
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_with_bank_info(mock_session)
        
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[0]['bank_name'] == "Bank 1"
        assert result[1]['id'] == 2
        assert result[1]['bank_name'] == "Bank 2"
    
    def test_get_by_entity_with_bank_info(self, bank_account_repository, mock_session):
        """Test get_by_entity_with_bank_info returns entity accounts with bank information."""
        # Create properly configured mock objects
        mock_bank1 = Mock(spec=Bank)
        mock_bank1.name = "Bank 1"
        mock_bank1.country = Country.AU
        mock_bank1.swift_bic = "BANK1"
        
        mock_result = [
            (Mock(spec=BankAccount, id=1, entity_id=1, bank_id=1, account_name="Account 1", 
                  account_number="123", currency=Currency.AUD, status=AccountStatus.ACTIVE),
             mock_bank1)
        ]
        
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.all.return_value = mock_result
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_by_entity_with_bank_info(1, mock_session)
        
        assert len(result) == 1
        assert result[0]['id'] == 1
        assert result[0]['entity_id'] == 1
        assert result[0]['bank_name'] == "Bank 1"
    
    def test_create_bank_account(self, bank_account_repository, mock_session, sample_bank_account):
        """Test create adds account to session and clears caches."""
        result = bank_account_repository.create(sample_bank_account, mock_session)
        
        assert result == sample_bank_account
        mock_session.add.assert_called_once_with(sample_bank_account)
        mock_session.flush.assert_called_once()
        # Cache should be cleared
        assert len(bank_account_repository._cache) == 0
    
    def test_update_bank_account(self, bank_account_repository, mock_session, sample_bank_account):
        """Test update flushes session and clears caches."""
        result = bank_account_repository.update(sample_bank_account, mock_session)
        
        assert result == sample_bank_account
        mock_session.flush.assert_called_once()
        # Cache should be cleared
        assert len(bank_account_repository._cache) == 0
    
    def test_delete_bank_account(self, bank_account_repository, mock_session, sample_bank_account):
        """Test delete removes account from session and clears caches."""
        bank_account_repository.delete(sample_bank_account, mock_session)
        
        mock_session.delete.assert_called_once_with(sample_bank_account)
        mock_session.flush.assert_called_once()
        # Cache should be cleared
        assert len(bank_account_repository._cache) == 0
    
    def test_exists_cache_hit_true(self, bank_account_repository, mock_session):
        """Test exists returns cached result when available."""
        bank_account_repository._cache['bank_account:exists:1'] = True
        
        result = bank_account_repository.exists(1, mock_session)
        
        assert result is True
        mock_session.query.assert_not_called()
    
    def test_exists_cache_hit_false(self, bank_account_repository, mock_session):
        """Test exists returns cached result when available."""
        bank_account_repository._cache['bank_account:exists:1'] = False
        
        result = bank_account_repository.exists(1, mock_session)
        
        assert result is False
        mock_session.query.assert_not_called()
    
    def test_exists_cache_miss(self, bank_account_repository, mock_session):
        """Test exists queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = Mock()  # Account exists
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.exists(1, mock_session)
        
        assert result is True
        assert 'bank_account:exists:1' in bank_account_repository._cache
    
    def test_exists_not_found(self, bank_account_repository, mock_session):
        """Test exists returns False when account not found."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None  # Account doesn't exist
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.exists(999, mock_session)
        
        assert result is False
        assert 'bank_account:exists:999' in bank_account_repository._cache
    
    def test_count_by_entity_cache_hit(self, bank_account_repository, mock_session):
        """Test count_by_entity returns cached count when available."""
        bank_account_repository._cache['bank_accounts:count:entity:1'] = 5
        
        result = bank_account_repository.count_by_entity(1, mock_session)
        
        assert result == 5
        mock_session.query.assert_not_called()
    
    def test_count_by_entity_cache_miss(self, bank_account_repository, mock_session):
        """Test count_by_entity queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 5
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.count_by_entity(1, mock_session)
        
        assert result == 5
        assert "bank_accounts:count:entity:1" in bank_account_repository._cache
    
    def test_count_by_bank_cache_hit(self, bank_account_repository, mock_session):
        """Test count_by_bank returns cached count when available."""
        bank_account_repository._cache['bank_accounts:count:bank:1'] = 3
        
        result = bank_account_repository.count_by_bank(1, mock_session)
        
        assert result == 3
        mock_session.query.assert_not_called()
    
    def test_count_by_bank_cache_miss(self, bank_account_repository, mock_session):
        """Test count_by_bank queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 3
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.count_by_bank(1, mock_session)
        
        assert result == 3
        assert "bank_accounts:count:bank:1" in bank_account_repository._cache
    
    def test_count_by_currency_cache_hit(self, bank_account_repository, mock_session):
        """Test count_by_currency returns cached count when available."""
        bank_account_repository._cache['bank_accounts:count:currency:AUD'] = 4
        
        result = bank_account_repository.count_by_currency("AUD", mock_session)
        
        assert result == 4
        mock_session.query.assert_not_called()
    
    def test_count_by_currency_cache_miss(self, bank_account_repository, mock_session):
        """Test count_by_currency queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 4
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.count_by_currency("AUD", mock_session)
        
        assert result == 4
        assert "bank_accounts:count:currency:AUD" in bank_account_repository._cache
    
    def test_get_total_count_cache_hit(self, bank_account_repository, mock_session):
        """Test get_total_count returns cached count when available."""
        bank_account_repository._cache['bank_accounts:total_count'] = 10
        
        result = bank_account_repository.get_total_count(mock_session)
        
        assert result == 10
        mock_session.query.assert_not_called()
    
    def test_get_total_count_cache_miss(self, bank_account_repository, mock_session):
        """Test get_total_count queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.count.return_value = 10
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_total_count(mock_session)
        
        assert result == 10
        assert "bank_accounts:total_count" in bank_account_repository._cache
    
    def test_search_cache_hit(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test search returns cached results when available."""
        cache_key = "bank_accounts:search:test"
        bank_account_repository._cache[cache_key] = sample_bank_accounts_list
        
        result = bank_account_repository.search("test", mock_session)
        
        assert result == sample_bank_accounts_list
        mock_session.query.assert_not_called()
    
    def test_search_cache_miss(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test search queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = sample_bank_accounts_list
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.search("test", mock_session)
        
        assert result == sample_bank_accounts_list
        assert "bank_accounts:search:test" in bank_account_repository._cache
    
    def test_search_empty_term(self, bank_account_repository, mock_session):
        """Test search returns empty list for empty search term."""
        result = bank_account_repository.search("", mock_session)
        
        assert result == []
        mock_session.query.assert_not_called()
    
    def test_search_none_term(self, bank_account_repository, mock_session):
        """Test search returns empty list for None search term."""
        result = bank_account_repository.search(None, mock_session)
        
        assert result == []
        mock_session.query.assert_not_called()

    # ============================================================================
    # CACHE MANAGEMENT TESTING
    # ============================================================================
    
    def test_clear_cache(self, bank_account_repository, mock_session):
        """Test clear_cache removes all cached data."""
        # Populate cache
        bank_account_repository._cache['bank_account:1'] = Mock()
        bank_account_repository._cache['bank_accounts:all'] = []
        bank_account_repository._cache['other:data'] = 'value'
        
        bank_account_repository.clear_cache()
        
        assert len(bank_account_repository._cache) == 0
    
    def test_clear_bank_account_caches(self, bank_account_repository, mock_session):
        """Test _clear_bank_account_caches removes only bank account-related caches."""
        # Populate cache with mixed data
        bank_account_repository._cache['bank_account:1'] = Mock()
        bank_account_repository._cache['bank_accounts:all'] = []
        bank_account_repository._cache['other:data'] = 'value'
        bank_account_repository._cache['bank_account:exists:1'] = True
        
        bank_account_repository._clear_bank_account_caches()
        
        assert 'other:data' in bank_account_repository._cache
        assert 'bank_account:1' not in bank_account_repository._cache
        assert 'bank_accounts:all' not in bank_account_repository._cache
        assert 'bank_account:exists:1' not in bank_account_repository._cache
    
    def test_cache_ttl_initialization(self):
        """Test repository initializes with correct cache TTL."""
        repo = BankAccountRepository(cache_ttl=600)
        assert repo._cache_ttl == 600
        
        repo_default = BankAccountRepository()
        assert repo_default._cache_ttl == 300  # Default value

    # ============================================================================
    # EDGE CASES AND ERROR HANDLING
    # ============================================================================
    
    def test_get_by_id_zero_id(self, bank_account_repository, mock_session):
        """Test get_by_id handles zero ID gracefully."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_by_id(0, mock_session)
        
        assert result is None
    
    def test_get_by_id_negative_id(self, bank_account_repository, mock_session):
        """Test get_by_id handles negative ID gracefully."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = bank_account_repository.get_by_id(-1, mock_session)
        
        assert result is None
    
    def test_pagination_edge_cases(self, bank_account_repository, mock_session):
        """Test pagination handles edge cases gracefully."""
        # Create separate mock queries for the two different queries
        mock_count_query = Mock()
        mock_count_query.scalar.return_value = 0
        
        mock_data_query = Mock()
        mock_data_query.options.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [mock_count_query, mock_data_query]
        
        # Test page 0 (should become offset 0)
        accounts, count = bank_account_repository.get_bank_accounts_paginated(mock_session, page=0, page_size=10)
        assert count == 0
    
    def test_search_special_characters(self, bank_account_repository, mock_session):
        """Test search handles special characters in search terms."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        
        # Test with special characters
        result = bank_account_repository.search("test@#$%", mock_session)
        assert result == []
        
        # Test with SQL injection attempt
        result = bank_account_repository.search("'; DROP TABLE bank_accounts; --", mock_session)
        assert result == []
    
    def test_entity_id_validation(self, bank_account_repository, mock_session):
        """Test repository handles invalid entity IDs gracefully."""
        # Create properly configured mock query
        mock_query = Mock()
        mock_query.options.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        
        # Test with invalid entity ID
        result = bank_account_repository.get_by_entity(-1, mock_session)
        assert result == []
        
        # Test with zero entity ID
        result = bank_account_repository.get_by_entity(0, mock_session)
        assert result == []
    
    def test_bank_id_validation(self, bank_account_repository, mock_session):
        """Test repository handles invalid bank IDs gracefully."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        
        # Test with invalid bank ID
        result = bank_account_repository.get_by_bank(-1, mock_session)
        assert result == []
        
        # Test with zero bank ID
        result = bank_account_repository.get_by_bank(0, mock_session)
        assert result == []
    
    def test_currency_validation(self, bank_account_repository, mock_session):
        """Test repository handles invalid currency codes gracefully."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        
        # Test with invalid currency code
        result = bank_account_repository.get_by_currency("INVALID", mock_session)
        assert result == []
        
        # Test with empty currency code
        result = bank_account_repository.get_by_currency("", mock_session)
        assert result == []
    
    def test_account_number_validation(self, bank_account_repository, mock_session):
        """Test repository handles invalid account numbers gracefully."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        # Test with empty account number
        result = bank_account_repository.get_by_unique(1, 1, "", mock_session)
        assert result is None
        
        # Test with very long account number
        long_account = "A" * 1000
        result = bank_account_repository.get_by_unique(1, 1, long_account, mock_session)
        assert result is None
    
    def test_joinedload_behavior(self, bank_account_repository, mock_session, sample_bank_accounts_list):
        """Test that joinedload is properly applied for bank relationship."""
        mock_query = Mock()
        mock_query.options.return_value.filter.return_value.all.return_value = sample_bank_accounts_list
        mock_session.query.return_value = mock_query
        
        bank_account_repository.get_by_entity(1, mock_session)
        
        # Verify that options() was called to apply joinedload
        mock_query.options.assert_called_once()
    
    def test_join_behavior_for_bank_info(self, bank_account_repository, mock_session):
        """Test that join is properly applied when getting bank information."""
        mock_query = Mock()
        mock_query.join.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        
        bank_account_repository.get_with_bank_info(mock_session)
        
        # Verify that join() was called
        mock_query.join.assert_called_once()
