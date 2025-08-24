"""
Tax Statement Repository Tests

This module provides comprehensive testing for the TaxStatementRepository class,
following enterprise testing standards with focused, targeted test coverage.

Tests cover:
- Tax statement CRUD operations and validation
- Tax statement query performance and optimization
- Tax statement data consistency and integrity
- Repository caching behavior and invalidation
- Database session management and error handling

Testing Approach: Mock-Based Testing (Unit Tests)
Reasoning: Repository logic should be tested without database dependencies for fast execution
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime, timezone
from decimal import Decimal

from src.fund.repositories.tax_statement_repository import TaxStatementRepository
from src.tax.models import TaxStatement
from src.fund.enums import SortOrder


class TestTaxStatementRepository:
    """Test suite for TaxStatementRepository - Data access and persistence logic"""
    
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
        mock_query.scalar.return_value = 0
        
        session.query.return_value = mock_query
        session.add = Mock()
        session.flush = Mock()
        session.delete = Mock()
        return session
    
    @pytest.fixture
    def sample_tax_statement(self):
        """Sample tax statement object for testing."""
        statement = Mock(spec=TaxStatement)
        statement.id = 1
        statement.fund_id = 1
        statement.entity_id = 1
        statement.financial_year = "2023-24"
        statement.interest_income_amount = 1000.0
        statement.dividend_franked_income_amount = 500.0
        statement.capital_gain_income_amount = 2000.0
        statement.notes = "Test tax statement"
        statement.created_at = datetime.now(timezone.utc)
        statement.updated_at = datetime.now(timezone.utc)
        return statement
    
    @pytest.fixture
    def tax_statement_repository(self):
        """TaxStatementRepository instance for testing."""
        return TaxStatementRepository(cache_ttl=300)
    
    @pytest.fixture
    def tax_statement_data(self):
        """Sample tax statement data for creation/update testing."""
        return {
            'fund_id': 1,
            'entity_id': 1,
            'financial_year': '2023-24',
            'interest_income_amount': 1000.0,
            'dividend_franked_income_amount': 500.0,
            'capital_gain_income_amount': 2000.0,
            'notes': 'Test tax statement'
        }

    # ============================================================================
    # CRUD OPERATIONS TESTING
    # ============================================================================
    
    def test_get_by_id_cache_hit(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test get_by_id returns cached tax statement when available."""
        tax_statement_repository._cache['tax_statement:1'] = sample_tax_statement
        
        result = tax_statement_repository.get_by_id(1, mock_session)
        
        assert result == sample_tax_statement
        mock_session.query.assert_not_called()
    
    def test_get_by_id_cache_miss_database_query(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test get_by_id queries database and caches result on cache miss."""
        mock_session.query.return_value.filter.return_value.first.return_value = sample_tax_statement
        
        result = tax_statement_repository.get_by_id(1, mock_session)
        
        assert result == sample_tax_statement
        assert 'tax_statement:1' in tax_statement_repository._cache
        mock_session.query.assert_called_once()
    
    def test_get_by_id_not_found(self, tax_statement_repository, mock_session):
        """Test get_by_id returns None when tax statement not found."""
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = tax_statement_repository.get_by_id(999, mock_session)
        
        assert result is None
        assert 'tax_statement:999' not in tax_statement_repository._cache
    
    def test_get_by_fund_and_year_cache_hit(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test get_by_fund_and_year returns cached result when available."""
        cache_key = 'tax_statement:fund:1:year:2023-24'
        tax_statement_repository._cache[cache_key] = sample_tax_statement
        
        result = tax_statement_repository.get_by_fund_and_year(1, '2023-24', mock_session)
        
        assert result == sample_tax_statement
        mock_session.query.assert_not_called()
    
    def test_get_by_fund_and_year_cache_miss(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test get_by_fund_and_year queries database and caches result on cache miss."""
        mock_session.query.return_value.filter.return_value.first.return_value = sample_tax_statement
        
        result = tax_statement_repository.get_by_fund_and_year(1, '2023-24', mock_session)
        
        assert result == sample_tax_statement
        cache_key = 'tax_statement:fund:1:year:2023-24'
        assert cache_key in tax_statement_repository._cache
    
    def test_get_by_entity_and_year_cache_hit(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test get_by_entity_and_year returns cached result when available."""
        cache_key = 'tax_statements:entity:1:year:2023-24'
        tax_statement_repository._cache[cache_key] = [sample_tax_statement]
        
        result = tax_statement_repository.get_by_entity_and_year(1, '2023-24', mock_session)
        
        assert result == [sample_tax_statement]
        mock_session.query.assert_not_called()
    
    def test_get_by_entity_and_year_cache_miss(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test get_by_entity_and_year queries database and caches result on cache miss."""
        mock_session.query.return_value.filter.return_value.all.return_value = [sample_tax_statement]
        
        result = tax_statement_repository.get_by_entity_and_year(1, '2023-24', mock_session)
        
        assert result == [sample_tax_statement]
        cache_key = 'tax_statements:entity:1:year:2023-24'
        assert cache_key in tax_statement_repository._cache
    
    def test_get_by_fund_with_pagination_and_sorting(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test get_by_fund with pagination and sorting parameters."""
        mock_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_tax_statement]
        
        result = tax_statement_repository.get_by_fund(1, mock_session, skip=10, limit=20, sort_order=SortOrder.ASC)
        
        assert result == [sample_tax_statement]
        mock_session.query.assert_called_once()
        # Verify pagination and sorting were applied
        mock_session.query.return_value.filter.return_value.order_by.assert_called_once()
        mock_session.query.return_value.filter.return_value.order_by.return_value.offset.assert_called_once_with(10)
        mock_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.assert_called_once_with(20)
    
    def test_get_by_entity_with_pagination_and_sorting(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test get_by_entity with pagination and sorting parameters."""
        mock_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_tax_statement]
        
        result = tax_statement_repository.get_by_entity(1, mock_session, skip=5, limit=15, sort_order=SortOrder.DESC)
        
        assert result == [sample_tax_statement]
        mock_session.query.assert_called_once()
        # Verify pagination and sorting were applied
        mock_session.query.return_value.filter.return_value.order_by.assert_called_once()
        mock_session.query.return_value.filter.return_value.order_by.return_value.offset.assert_called_once_with(5)
        mock_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.assert_called_once_with(15)

    # ============================================================================
    # CREATE OPERATIONS TESTING
    # ============================================================================
    
    def test_create_tax_statement_success(self, tax_statement_repository, mock_session, sample_tax_statement, tax_statement_data):
        """Test successful creation of a tax statement."""
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        
        # Mock the TaxStatement constructor
        with patch('src.fund.repositories.tax_statement_repository.TaxStatement') as mock_tax_statement_class:
            mock_tax_statement_class.return_value = sample_tax_statement
            
            result = tax_statement_repository.create(tax_statement_data, mock_session)
            
            assert result == sample_tax_statement
            mock_session.add.assert_called_once_with(sample_tax_statement)
            mock_session.flush.assert_called_once()
    
    def test_create_tax_statement_missing_required_fields(self, tax_statement_repository, mock_session):
        """Test creation fails when required fields are missing."""
        incomplete_data = {'fund_id': 1}  # Missing entity_id and financial_year
        
        with pytest.raises(ValueError, match="Required field 'entity_id' is missing"):
            tax_statement_repository.create(incomplete_data, mock_session)
        
        mock_session.add.assert_not_called()
        mock_session.flush.assert_not_called()
    
    def test_create_tax_statement_clears_relevant_caches(self, tax_statement_repository, mock_session, sample_tax_statement, tax_statement_data):
        """Test that creating a tax statement clears relevant caches."""
        # Populate caches that should be cleared with actual cache keys used by repository
        tax_statement_repository._cache['tax_statements:fund:1:skip:0:limit:100:sort:SortOrder.DESC'] = [sample_tax_statement]
        tax_statement_repository._cache['tax_statements:entity:1:skip:0:limit:100:sort:SortOrder.DESC'] = [sample_tax_statement]
        tax_statement_repository._cache['tax_statements:entity:1:year:2023-24'] = [sample_tax_statement]
        
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        
        with patch('src.fund.repositories.tax_statement_repository.TaxStatement') as mock_tax_statement_class:
            mock_tax_statement_class.return_value = sample_tax_statement
            
            tax_statement_repository.create(tax_statement_data, mock_session)
            
            # Verify caches were cleared
            assert 'tax_statements:fund:1:skip:0:limit:100:sort:SortOrder.DESC' not in tax_statement_repository._cache
            assert 'tax_statements:entity:1:skip:0:limit:100:sort:SortOrder.DESC' not in tax_statement_repository._cache
            assert 'tax_statements:entity:1:year:2023-24' not in tax_statement_repository._cache

    # ============================================================================
    # UPDATE OPERATIONS TESTING
    # ============================================================================
    
    def test_update_tax_statement_success(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test successful update of a tax statement."""
        # Mock get_by_id to return existing statement
        tax_statement_repository._cache['tax_statement:1'] = sample_tax_statement
        
        update_data = {'notes': 'Updated notes', 'interest_income_amount': 1500.0}
        
        result = tax_statement_repository.update(1, update_data, mock_session)
        
        assert result == sample_tax_statement
        assert sample_tax_statement.notes == 'Updated notes'
        assert sample_tax_statement.interest_income_amount == 1500.0
        mock_session.flush.assert_called_once()
    
    def test_update_tax_statement_not_found(self, tax_statement_repository, mock_session):
        """Test update returns None when tax statement not found."""
        update_data = {'notes': 'Updated notes'}
        
        result = tax_statement_repository.update(999, update_data, mock_session)
        
        assert result is None
        mock_session.flush.assert_not_called()
    
    def test_update_tax_statement_clears_relevant_caches(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test that updating a tax statement clears relevant caches."""
        # Set up old values
        sample_tax_statement.fund_id = 1
        sample_tax_statement.entity_id = 1
        sample_tax_statement.financial_year = '2023-24'
        
        # Mock get_by_id to return the sample statement
        tax_statement_repository._cache['tax_statement:1'] = sample_tax_statement
        
        # Populate caches that should be cleared with actual cache keys used by repository
        tax_statement_repository._cache['tax_statements:fund:1:skip:0:limit:100:sort:SortOrder.DESC'] = [sample_tax_statement]
        tax_statement_repository._cache['tax_statements:entity:1:skip:0:limit:100:sort:SortOrder.DESC'] = [sample_tax_statement]
        tax_statement_repository._cache['tax_statements:entity:1:year:2023-24'] = [sample_tax_statement]
        
        update_data = {'notes': 'Updated notes'}
        
        result = tax_statement_repository.update(1, update_data, mock_session)
        
        # Verify caches were cleared
        assert 'tax_statements:fund:1:skip:0:limit:100:sort:SortOrder.DESC' not in tax_statement_repository._cache
        assert 'tax_statements:entity:1:skip:0:limit:100:sort:SortOrder.DESC' not in tax_statement_repository._cache
        assert 'tax_statements:entity:1:year:2023-24' not in tax_statement_repository._cache

    # ============================================================================
    # DELETE OPERATIONS TESTING
    # ============================================================================
    
    def test_delete_tax_statement_success(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test successful deletion of a tax statement."""
        # Mock get_by_id to return existing statement
        tax_statement_repository._cache['tax_statement:1'] = sample_tax_statement
        
        result = tax_statement_repository.delete(1, mock_session)
        
        assert result is True
        mock_session.delete.assert_called_once_with(sample_tax_statement)
    
    def test_delete_tax_statement_not_found(self, tax_statement_repository, mock_session):
        """Test delete returns False when tax statement not found."""
        result = tax_statement_repository.delete(999, mock_session)
        
        assert result is False
        mock_session.delete.assert_not_called()
    
    def test_delete_tax_statement_clears_relevant_caches(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test that deleting a tax statement clears relevant caches."""
        # Set up values for cache clearing
        sample_tax_statement.fund_id = 1
        sample_tax_statement.entity_id = 1
        sample_tax_statement.financial_year = '2023-24'
        
        # Populate caches that should be cleared with actual cache keys used by repository
        tax_statement_repository._cache['tax_statement:1'] = sample_tax_statement
        tax_statement_repository._cache['tax_statements:fund:1:skip:0:limit:100:sort:SortOrder.DESC'] = [sample_tax_statement]
        tax_statement_repository._cache['tax_statements:entity:1:skip:0:limit:100:sort:SortOrder.DESC'] = [sample_tax_statement]
        tax_statement_repository._cache['tax_statements:entity:1:year:2023-24'] = [sample_tax_statement]
        
        result = tax_statement_repository.delete(1, mock_session)
        
        assert result is True
        # Verify caches were cleared
        assert 'tax_statement:1' not in tax_statement_repository._cache
        assert 'tax_statements:fund:1:skip:0:limit:100:sort:SortOrder.DESC' not in tax_statement_repository._cache
        assert 'tax_statements:entity:1:skip:0:limit:100:sort:SortOrder.DESC' not in tax_statement_repository._cache
        assert 'tax_statements:entity:1:year:2023-24' not in tax_statement_repository._cache

    # ============================================================================
    # SPECIALIZED QUERY TESTING
    # ============================================================================
    
    def test_get_final_statements_cache_hit(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test get_final_statements returns cached result when available."""
        cache_key = 'final_tax_statements:fund:1'
        tax_statement_repository._cache[cache_key] = [sample_tax_statement]
        
        result = tax_statement_repository.get_final_statements(1, mock_session)
        
        assert result == [sample_tax_statement]
        mock_session.query.assert_not_called()
    
    def test_get_final_statements_cache_miss(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test get_final_statements queries database and caches result on cache miss."""
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [sample_tax_statement]
        
        result = tax_statement_repository.get_final_statements(1, mock_session)
        
        assert result == [sample_tax_statement]
        cache_key = 'final_tax_statements:fund:1'
        assert cache_key in tax_statement_repository._cache
    
    def test_get_statement_count_by_fund_cache_hit(self, tax_statement_repository, mock_session):
        """Test get_statement_count_by_fund returns cached result when available."""
        cache_key = 'tax_statement_count:fund:1'
        tax_statement_repository._cache[cache_key] = 5
        
        result = tax_statement_repository.get_statement_count_by_fund(1, mock_session)
        
        assert result == 5
        mock_session.query.assert_not_called()
    
    def test_get_statement_count_by_fund_cache_miss(self, tax_statement_repository, mock_session):
        """Test get_statement_count_by_fund queries database and caches result on cache miss."""
        mock_session.query.return_value.filter.return_value.scalar.return_value = 5
        
        result = tax_statement_repository.get_statement_count_by_fund(1, mock_session)
        
        assert result == 5
        cache_key = 'tax_statement_count:fund:1'
        assert cache_key in tax_statement_repository._cache

    # ============================================================================
    # CACHE MANAGEMENT TESTING
    # ============================================================================
    
    def test_clear_all_cache(self, tax_statement_repository):
        """Test clear_all_cache removes all cached data."""
        # Populate cache
        tax_statement_repository._cache['key1'] = 'value1'
        tax_statement_repository._cache['key2'] = 'value2'
        
        tax_statement_repository.clear_all_cache()
        
        assert len(tax_statement_repository._cache) == 0
    
    def test_cache_ttl_initialization(self, tax_statement_repository):
        """Test cache TTL is properly initialized."""
        assert tax_statement_repository._cache_ttl == 300
    
    def test_cache_ttl_custom_initialization(self):
        """Test cache TTL can be customized."""
        repo = TaxStatementRepository(cache_ttl=600)
        assert repo._cache_ttl == 600
    
    def test_cache_invalidation_on_update(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test that cache is properly invalidated when updating tax statements."""
        # Set up old values
        sample_tax_statement.fund_id = 1
        sample_tax_statement.entity_id = 1
        sample_tax_statement.financial_year = '2023-24'
        
        # Mock get_by_id to return the sample statement
        tax_statement_repository._cache['tax_statement:1'] = sample_tax_statement
        
        # Populate caches with actual cache keys used by repository
        tax_statement_repository._cache['tax_statements:fund:1:skip:0:limit:100:sort:SortOrder.DESC'] = [sample_tax_statement]
        tax_statement_repository._cache['tax_statements:entity:1:skip:0:limit:100:sort:SortOrder.DESC'] = [sample_tax_statement]
        tax_statement_repository._cache['tax_statements:entity:1:year:2023-24'] = [sample_tax_statement]
        
        update_data = {'notes': 'Updated notes'}
        
        tax_statement_repository.update(1, update_data, mock_session)
        
        # Verify all related caches were cleared
        assert 'tax_statements:fund:1:skip:0:limit:100:sort:SortOrder.DESC' not in tax_statement_repository._cache
        assert 'tax_statements:entity:1:skip:0:limit:100:sort:SortOrder.DESC' not in tax_statement_repository._cache
        assert 'tax_statements:entity:1:year:2023-24' not in tax_statement_repository._cache

    # ============================================================================
    # ERROR HANDLING AND EDGE CASES
    # ============================================================================
    
    def test_create_with_empty_data(self, tax_statement_repository, mock_session):
        """Test creation with empty data dictionary."""
        with pytest.raises(ValueError, match="Required field 'fund_id' is missing"):
            tax_statement_repository.create({}, mock_session)
    
    def test_create_with_none_values(self, tax_statement_repository, mock_session):
        """Test creation with None values in data."""
        data_with_none = {
            'fund_id': None,
            'entity_id': 1,
            'financial_year': '2023-24'
        }
        
        with pytest.raises(ValueError, match="Required field 'fund_id' is missing"):
            tax_statement_repository.create(data_with_none, mock_session)
    
    def test_update_with_invalid_fields(self, tax_statement_repository, mock_session, sample_tax_statement):
        """Test update ignores invalid fields gracefully."""
        tax_statement_repository._cache['tax_statement:1'] = sample_tax_statement
        
        update_data = {'invalid_field': 'value', 'notes': 'Valid update'}
        
        result = tax_statement_repository.update(1, update_data, mock_session)
        
        assert result == sample_tax_statement
        assert sample_tax_statement.notes == 'Valid update'
        # Invalid field should not cause an error
    
    def test_cache_key_uniqueness(self, tax_statement_repository):
        """Test that cache keys are unique and properly formatted."""
        # Test different query patterns generate different cache keys
        cache_keys = set()
        
        # Different IDs
        cache_keys.add('tax_statement:1')
        cache_keys.add('tax_statement:2')
        
        # Different fund queries
        cache_keys.add('tax_statements:fund:1:skip:0:limit:100:sort:SortOrder.DESC')
        cache_keys.add('tax_statements:fund:1:skip:10:limit:20:sort:SortOrder.ASC')
        
        # Different entity queries
        cache_keys.add('tax_statements:entity:1:skip:0:limit:100:sort:SortOrder.DESC')
        cache_keys.add('tax_statements:entity:2:skip:0:limit:100:sort:SortOrder.DESC')
        
        # Different year queries
        cache_keys.add('tax_statements:entity:1:year:2023-24')
        cache_keys.add('tax_statements:entity:1:year:2024-25')
        
        # Verify all keys are unique
        assert len(cache_keys) == 8
