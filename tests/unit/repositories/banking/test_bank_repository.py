"""
Bank Repository Tests

This module provides comprehensive testing for the BankRepository class,
following enterprise testing standards with focused, targeted test coverage.

Tests cover:
- Bank CRUD operations and validation
- Bank query performance and optimization
- Bank data consistency and integrity
- Repository caching behavior and invalidation
- Database session management and error handling

Testing Approach: Mock-Based Testing (Unit Tests)
Reasoning: Repository logic should be tested without database dependencies for fast execution
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone
from decimal import Decimal

from src.banking.repositories.bank_repository import BankRepository
from src.banking.models.bank import Bank
from src.banking.enums import Country, SortOrder


class TestBankRepository:
    """Test suite for BankRepository - Data access and persistence logic"""
    
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
        
        session.query.return_value = mock_query
        session.add = Mock()
        session.flush = Mock()
        session.delete = Mock()
        return session
    
    @pytest.fixture
    def sample_bank(self):
        """Sample bank object for testing."""
        bank = Mock(spec=Bank)
        bank.id = 1
        bank.name = "Test Bank"
        bank.country = Country.AU
        bank.swift_bic = "TESTAU2S"
        bank.created_at = datetime.now(timezone.utc)
        bank.updated_at = datetime.now(timezone.utc)
        return bank
    
    @pytest.fixture
    def sample_banks_list(self):
        """Sample list of banks for testing."""
        banks = []
        for i in range(3):
            bank = Mock(spec=Bank)
            bank.id = i + 1
            bank.name = f"Test Bank {i + 1}"
            bank.country = Country.AU
            bank.swift_bic = f"TESTAU{i+1}S"
            banks.append(bank)
        return banks
    
    @pytest.fixture
    def bank_repository(self):
        """BankRepository instance for testing."""
        return BankRepository(cache_ttl=300)
    
    @pytest.fixture
    def bank_data(self):
        """Sample bank data for creation/update testing."""
        return {
            'name': 'New Test Bank',
            'country': Country.US,
            'swift_bic': 'NEWUS2S'
        }

    # ============================================================================
    # CRUD OPERATIONS TESTING
    # ============================================================================
    
    def test_get_by_id_cache_hit(self, bank_repository, mock_session, sample_bank):
        """Test get_by_id returns cached bank when available."""
        bank_repository._cache['bank:1'] = sample_bank
        
        result = bank_repository.get_by_id(1, mock_session)
        
        assert result == sample_bank
        mock_session.query.assert_not_called()
    
    def test_get_by_id_cache_miss_database_query(self, bank_repository, mock_session, sample_bank):
        """Test get_by_id queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_bank
        mock_session.query.return_value = mock_query
        
        result = bank_repository.get_by_id(1, mock_session)
        
        assert result == sample_bank
        assert 'bank:1' in bank_repository._cache
        assert bank_repository._cache['bank:1'] == sample_bank
    
    def test_get_by_id_not_found(self, bank_repository, mock_session):
        """Test get_by_id returns None when bank not found."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = bank_repository.get_by_id(999, mock_session)
        
        assert result is None
        assert 'bank:999' not in bank_repository._cache
    
    def test_get_by_name_and_country_cache_hit(self, bank_repository, mock_session, sample_bank):
        """Test get_by_name_and_country returns cached bank when available."""
        cache_key = f"bank:name_country:{sample_bank.name}:{sample_bank.country.value}"
        bank_repository._cache[cache_key] = sample_bank
        
        result = bank_repository.get_by_name_and_country(sample_bank.name, sample_bank.country.value, mock_session)
        
        assert result == sample_bank
        mock_session.query.assert_not_called()
    
    def test_get_by_name_and_country_cache_miss(self, bank_repository, mock_session, sample_bank):
        """Test get_by_name_and_country queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_bank
        mock_session.query.return_value = mock_query
        
        result = bank_repository.get_by_name_and_country("Test Bank", "AU", mock_session)
        
        assert result == sample_bank
        cache_key = "bank:name_country:Test Bank:AU"
        assert cache_key in bank_repository._cache
    
    def test_get_by_swift_bic_cache_hit(self, bank_repository, mock_session, sample_bank):
        """Test get_by_swift_bic returns cached bank when available."""
        cache_key = f"bank:swift_bic:{sample_bank.swift_bic}"
        bank_repository._cache[cache_key] = sample_bank
        
        result = bank_repository.get_by_swift_bic(sample_bank.swift_bic, mock_session)
        
        assert result == sample_bank
        mock_session.query.assert_not_called()
    
    def test_get_by_swift_bic_cache_miss(self, bank_repository, mock_session, sample_bank):
        """Test get_by_swift_bic queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_bank
        mock_session.query.return_value = mock_query
        
        result = bank_repository.get_by_swift_bic("TESTAU2S", mock_session)
        
        assert result == sample_bank
        assert 'bank:swift_bic:TESTAU2S' in bank_repository._cache
    
    def test_get_banks_paginated(self, bank_repository, mock_session, sample_banks_list):
        """Test get_banks_paginated returns correct pagination results."""
        # Create separate mock queries for the two different queries
        mock_count_query = Mock()
        mock_count_query.scalar.return_value = 3
        
        mock_data_query = Mock()
        mock_data_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = sample_banks_list
        
        # Set up session to return different mocks for different queries
        # First call: session.query(func.count(Bank.id)).scalar()
        # Second call: session.query(Bank).order_by(Bank.name).offset(offset).limit(page_size).all()
        mock_session.query.side_effect = [
            mock_count_query,  # func.count(Bank.id)
            mock_data_query    # Bank
        ]
        
        banks, total_count = bank_repository.get_banks_paginated(mock_session, page=1, page_size=2)
        
        assert banks == sample_banks_list
        assert total_count == 3
    
    def test_get_banks_paginated_page_2(self, bank_repository, mock_session, sample_banks_list):
        """Test get_banks_paginated handles page 2 correctly."""
        # Create separate mock queries for the two different queries
        mock_count_query = Mock()
        mock_count_query.scalar.return_value = 3
        
        mock_data_query = Mock()
        mock_data_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = sample_banks_list[2:]
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [mock_count_query, mock_data_query]
        
        banks, total_count = bank_repository.get_banks_paginated(mock_session, page=2, page_size=1)
        
        assert total_count == 3
    
    def test_get_by_country_cache_hit(self, bank_repository, mock_session, sample_banks_list):
        """Test get_by_country returns cached banks when available."""
        cache_key = "banks:country:AU"
        bank_repository._cache[cache_key] = sample_banks_list
        
        result = bank_repository.get_by_country("AU", mock_session)
        
        assert result == sample_banks_list
        mock_session.query.assert_not_called()
    
    def test_get_by_country_cache_miss(self, bank_repository, mock_session, sample_banks_list):
        """Test get_by_country queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = sample_banks_list
        mock_session.query.return_value = mock_query
        
        result = bank_repository.get_by_country("AU", mock_session)
        
        assert result == sample_banks_list
        assert "banks:country:AU" in bank_repository._cache
    
    def test_get_all_cache_hit(self, bank_repository, mock_session, sample_banks_list):
        """Test get_all returns cached banks when available."""
        cache_key = "banks:all"
        bank_repository._cache[cache_key] = sample_banks_list
        
        result = bank_repository.get_all(mock_session)
        
        assert result == sample_banks_list
        mock_session.query.assert_not_called()
    
    def test_get_all_cache_miss(self, bank_repository, mock_session, sample_banks_list):
        """Test get_all queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.all.return_value = sample_banks_list
        mock_session.query.return_value = mock_query
        
        result = bank_repository.get_all(mock_session)
        
        assert result == sample_banks_list
        assert "banks:all" in bank_repository._cache
    
    def test_get_with_accounts_count(self, bank_repository, mock_session):
        """Test get_with_accounts_count returns banks with account counts."""
        mock_result = [
            (Mock(spec=Bank, id=1, name="Bank 1", country=Country.AU, swift_bic="BANK1"), 5),
            (Mock(spec=Bank, id=2, name="Bank 2", country=Country.US, swift_bic="BANK2"), 3)
        ]
        
        mock_query = Mock()
        mock_query.outerjoin.return_value.group_by.return_value.all.return_value = mock_result
        mock_session.query.return_value = mock_query
        
        result = bank_repository.get_with_accounts_count(mock_session)
        
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[0]['accounts_count'] == 5
        assert result[1]['id'] == 2
        assert result[1]['accounts_count'] == 3
    
    def test_create_bank(self, bank_repository, mock_session, sample_bank):
        """Test create adds bank to session and clears caches."""
        result = bank_repository.create(sample_bank, mock_session)
        
        assert result == sample_bank
        mock_session.add.assert_called_once_with(sample_bank)
        mock_session.flush.assert_called_once()
        # Cache should be cleared
        assert len(bank_repository._cache) == 0
    
    def test_update_bank(self, bank_repository, mock_session, sample_bank):
        """Test update flushes session and clears caches."""
        result = bank_repository.update(sample_bank, mock_session)
        
        assert result == sample_bank
        mock_session.flush.assert_called_once()
        # Cache should be cleared
        assert len(bank_repository._cache) == 0
    
    def test_delete_bank(self, bank_repository, mock_session, sample_bank):
        """Test delete removes bank from session and clears caches."""
        bank_repository.delete(sample_bank, mock_session)
        
        mock_session.delete.assert_called_once_with(sample_bank)
        mock_session.flush.assert_called_once()
        # Cache should be cleared
        assert len(bank_repository._cache) == 0
    
    def test_exists_cache_hit_true(self, bank_repository, mock_session):
        """Test exists returns cached result when available."""
        bank_repository._cache['bank:exists:1'] = True
        
        result = bank_repository.exists(1, mock_session)
        
        assert result is True
        mock_session.query.assert_not_called()
    
    def test_exists_cache_hit_false(self, bank_repository, mock_session):
        """Test exists returns cached result when available."""
        bank_repository._cache['bank:exists:1'] = False
        
        result = bank_repository.exists(1, mock_session)
        
        assert result is False
        mock_session.query.assert_not_called()
    
    def test_exists_cache_miss(self, bank_repository, mock_session):
        """Test exists queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = Mock()  # Bank exists
        mock_session.query.return_value = mock_query
        
        result = bank_repository.exists(1, mock_session)
        
        assert result is True
        assert 'bank:exists:1' in bank_repository._cache
    
    def test_exists_not_found(self, bank_repository, mock_session):
        """Test exists returns False when bank not found."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None  # Bank doesn't exist
        mock_session.query.return_value = mock_query
        
        result = bank_repository.exists(999, mock_session)
        
        assert result is False
        assert 'bank:exists:999' in bank_repository._cache
    
    def test_count_by_country_cache_hit(self, bank_repository, mock_session):
        """Test count_by_country returns cached count when available."""
        bank_repository._cache['banks:count:country:AU'] = 5
        
        result = bank_repository.count_by_country("AU", mock_session)
        
        assert result == 5
        mock_session.query.assert_not_called()
    
    def test_count_by_country_cache_miss(self, bank_repository, mock_session):
        """Test count_by_country queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 5
        mock_session.query.return_value = mock_query
        
        result = bank_repository.count_by_country("AU", mock_session)
        
        assert result == 5
        assert "banks:count:country:AU" in bank_repository._cache
    
    def test_get_total_count_cache_hit(self, bank_repository, mock_session):
        """Test get_total_count returns cached count when available."""
        bank_repository._cache['banks:total_count'] = 10
        
        result = bank_repository.get_total_count(mock_session)
        
        assert result == 10
        mock_session.query.assert_not_called()
    
    def test_get_total_count_cache_miss(self, bank_repository, mock_session):
        """Test get_total_count queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.count.return_value = 10
        mock_session.query.return_value = mock_query
        
        result = bank_repository.get_total_count(mock_session)
        
        assert result == 10
        assert "banks:total_count" in bank_repository._cache
    
    def test_search_cache_hit(self, bank_repository, mock_session, sample_banks_list):
        """Test search returns cached results when available."""
        cache_key = "banks:search:test"
        bank_repository._cache[cache_key] = sample_banks_list
        
        result = bank_repository.search("test", mock_session)
        
        assert result == sample_banks_list
        mock_session.query.assert_not_called()
    
    def test_search_cache_miss(self, bank_repository, mock_session, sample_banks_list):
        """Test search queries database and caches result on cache miss."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = sample_banks_list
        mock_session.query.return_value = mock_query
        
        result = bank_repository.search("test", mock_session)
        
        assert result == sample_banks_list
        assert "banks:search:test" in bank_repository._cache
    
    def test_search_empty_term(self, bank_repository, mock_session):
        """Test search returns empty list for empty search term."""
        result = bank_repository.search("", mock_session)
        
        assert result == []
        mock_session.query.assert_not_called()
    
    def test_search_none_term(self, bank_repository, mock_session):
        """Test search returns empty list for None search term."""
        result = bank_repository.search(None, mock_session)
        
        assert result == []
        mock_session.query.assert_not_called()

    # ============================================================================
    # CACHE MANAGEMENT TESTING
    # ============================================================================
    
    def test_clear_cache(self, bank_repository, mock_session):
        """Test clear_cache removes all cached data."""
        # Populate cache
        bank_repository._cache['bank:1'] = Mock()
        bank_repository._cache['banks:all'] = []
        bank_repository._cache['other:data'] = 'value'
        
        bank_repository.clear_cache()
        
        assert len(bank_repository._cache) == 0
    
    def test_clear_bank_caches(self, bank_repository, mock_session):
        """Test _clear_bank_caches removes only bank-related caches."""
        # Populate cache with mixed data
        bank_repository._cache['bank:1'] = Mock()
        bank_repository._cache['banks:all'] = []
        bank_repository._cache['other:data'] = 'value'
        bank_repository._cache['bank:exists:1'] = True
        
        bank_repository._clear_bank_caches()
        
        assert 'other:data' in bank_repository._cache
        assert 'bank:1' not in bank_repository._cache
        assert 'banks:all' not in bank_repository._cache
        assert 'bank:exists:1' not in bank_repository._cache
    
    def test_cache_ttl_initialization(self):
        """Test repository initializes with correct cache TTL."""
        repo = BankRepository(cache_ttl=600)
        assert repo._cache_ttl == 600
        
        repo_default = BankRepository()
        assert repo_default._cache_ttl == 300  # Default value

    # ============================================================================
    # EDGE CASES AND ERROR HANDLING
    # ============================================================================
    
    def test_get_by_id_zero_id(self, bank_repository, mock_session):
        """Test get_by_id handles zero ID gracefully."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = bank_repository.get_by_id(0, mock_session)
        
        assert result is None
    
    def test_get_by_id_negative_id(self, bank_repository, mock_session):
        """Test get_by_id handles negative ID gracefully."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = bank_repository.get_by_id(-1, mock_session)
        
        assert result is None
    
    def test_pagination_edge_cases(self, bank_repository, mock_session):
        """Test pagination handles edge cases gracefully."""
        # Create separate mock queries for the two different queries
        mock_count_query = Mock()
        mock_count_query.scalar.return_value = 0
        
        mock_data_query = Mock()
        mock_data_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        
        # Set up session to return different mocks for different queries
        mock_session.query.side_effect = [mock_count_query, mock_data_query]
        
        # Test page 0 (should become offset 0)
        banks, count = bank_repository.get_banks_paginated(mock_session, page=0, page_size=10)
        assert count == 0
    
    def test_search_special_characters(self, bank_repository, mock_session):
        """Test search handles special characters in search terms."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        
        # Test with special characters
        result = bank_repository.search("test@#$%", mock_session)
        assert result == []
        
        # Test with SQL injection attempt
        result = bank_repository.search("'; DROP TABLE banks; --", mock_session)
        assert result == []
    
    def test_country_validation(self, bank_repository, mock_session):
        """Test repository handles invalid country codes gracefully."""
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        
        # Test with invalid country code
        result = bank_repository.get_by_country("INVALID", mock_session)
        assert result == []
        
        # Test with empty country code
        result = bank_repository.get_by_country("", mock_session)
        assert result == []
    
    def test_swift_bic_validation(self, bank_repository, mock_session):
        """Test repository handles invalid SWIFT/BIC codes gracefully."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        # Test with empty SWIFT/BIC
        result = bank_repository.get_by_swift_bic("", mock_session)
        assert result is None
        
        # Test with very long SWIFT/BIC
        long_swift = "A" * 100
        result = bank_repository.get_by_swift_bic(long_swift, mock_session)
        assert result is None
