"""
Fund Repository Tests

This module provides comprehensive testing for the FundRepository class,
following enterprise testing standards with focused, targeted test coverage.

Tests cover:
- Fund CRUD operations and validation
- Fund query performance and optimization
- Fund data consistency and integrity
- Repository caching behavior and invalidation
- Database session management and error handling

Testing Approach: Mock-Based Testing (Unit Tests)
Reasoning: Repository logic should be tested without database dependencies for fast execution
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone
from decimal import Decimal

from src.fund.repositories.fund_repository import FundRepository
from src.fund.models.fund import Fund
from src.fund.enums import FundStatus, FundTrackingType


class TestFundRepository:
    """Test suite for FundRepository - Data access and persistence logic"""
    
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
        
        session.query.return_value = mock_query
        session.add = Mock()
        session.flush = Mock()
        session.delete = Mock()
        return session
    
    @pytest.fixture
    def sample_fund(self):
        """Sample fund object for testing."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Test Fund"
        fund.investment_company_id = 1
        fund.entity_id = 1
        fund.status = FundStatus.ACTIVE
        fund.fund_type = FundTrackingType.NAV_BASED
        fund.created_at = datetime.now(timezone.utc)
        return fund
    
    @pytest.fixture
    def fund_repository(self):
        """FundRepository instance for testing."""
        return FundRepository(cache_ttl=300)
    
    @pytest.fixture
    def fund_data(self):
        """Sample fund data for creation/update testing."""
        return {
            'name': 'New Test Fund',
            'description': 'A new test fund',
            'tracking_type': FundTrackingType.NAV_BASED,
            'status': FundStatus.ACTIVE,
            'commitment_amount': Decimal('1000000.00'),
            'investment_company_id': 1,
            'entity_id': 1
        }

    # ============================================================================
    # CRUD OPERATIONS TESTING
    # ============================================================================
    
    def test_get_by_id_cache_hit(self, fund_repository, mock_session, sample_fund):
        """Test get_by_id returns cached fund when available."""
        fund_repository._cache['fund:1'] = sample_fund
        
        result = fund_repository.get_by_id(1, mock_session)
        
        assert result == sample_fund
        mock_session.query.assert_not_called()
    
    def test_get_by_id_cache_miss_database_query(self, fund_repository, mock_session, sample_fund):
        """Test get_by_id queries database and caches result on cache miss."""
        mock_session.query.return_value.first.return_value = sample_fund
        
        result = fund_repository.get_by_id(1, mock_session)
        
        assert result == sample_fund
        mock_session.query.assert_called_once()
        assert fund_repository._cache['fund:1'] == sample_fund
    
    def test_get_by_id_not_found(self, fund_repository, mock_session):
        """Test get_by_id returns None when fund not found."""
        mock_session.query.first.return_value = None
        
        result = fund_repository.get_by_id(999, mock_session)
        
        assert result is None
        assert 'fund:999' not in fund_repository._cache
    
    def test_create_fund_success(self, fund_repository, mock_session, fund_data):
        """Test successful fund creation with valid data."""
        mock_fund = Mock(spec=Fund)
        mock_fund.investment_company_id = 1
        mock_fund.entity_id = 1
        
        with patch('src.fund.repositories.fund_repository.Fund', return_value=mock_fund):
            result = fund_repository.create(fund_data, mock_session)
        
        assert result == mock_fund
        mock_session.add.assert_called_once_with(mock_fund)
        mock_session.flush.assert_called_once()
    
    def test_create_fund_missing_required_fields(self, fund_repository, mock_session, fund_data):
        """Test fund creation fails with missing required fields."""
        invalid_data = fund_data.copy()
        del invalid_data['name']
        
        with pytest.raises(ValueError, match="Required field 'name' is missing"):
            fund_repository.create(invalid_data, mock_session)
    
    def test_update_fund_success(self, fund_repository, mock_session, sample_fund):
        """Test successful fund update."""
        fund_repository._cache['fund:1'] = sample_fund
        update_data = {'name': 'Updated Fund Name'}
        
        result = fund_repository.update(1, update_data, mock_session)
        
        assert result == sample_fund
        assert sample_fund.name == 'Updated Fund Name'
        mock_session.flush.assert_called_once()
    
    def test_delete_fund_success(self, fund_repository, mock_session, sample_fund):
        """Test successful fund deletion."""
        fund_repository._cache['fund:1'] = sample_fund
        
        result = fund_repository.delete(1, mock_session)
        
        assert result is True
        mock_session.delete.assert_called_once_with(sample_fund)

    # ============================================================================
    # QUERY OPERATIONS TESTING
    # ============================================================================
    
    def test_get_funds_by_status_cache_hit(self, fund_repository, mock_session):
        """Test get_funds_by_status returns cached funds when available."""
        cached_funds = [Mock(), Mock()]
        fund_repository._cache['funds:status:ACTIVE'] = cached_funds
        
        result = fund_repository.get_funds_by_status(FundStatus.ACTIVE, mock_session)
        
        assert result == cached_funds
        mock_session.query.assert_not_called()
    
    def test_get_funds_by_type_cache_miss(self, fund_repository, mock_session):
        """Test get_funds_by_type queries database and caches result."""
        funds_list = [Mock(), Mock()]
        mock_session.query.return_value.all.return_value = funds_list
        
        result = fund_repository.get_funds_by_type(FundTrackingType.NAV_BASED, mock_session)
        
        assert result == funds_list
        mock_session.query.assert_called_once()
        assert fund_repository._cache['funds:type:NAV_BASED'] == funds_list
    
    def test_search_funds_with_valid_term(self, fund_repository, mock_session):
        """Test search_funds with valid search term."""
        funds_list = [Mock(), Mock()]
        mock_session.query.return_value.all.return_value = funds_list
        
        result = fund_repository.search_funds("Test", mock_session)
        
        assert result == funds_list
        mock_session.query.assert_called_once()
    
    def test_search_funds_with_empty_term(self, fund_repository, mock_session):
        """Test search_funds returns empty list with empty search term."""
        result = fund_repository.search_funds("", mock_session)
        
        assert result == []
        mock_session.query.assert_not_called()

    # ============================================================================
    # CACHE MANAGEMENT TESTING
    # ============================================================================
    
    def test_clear_fund_cache(self, fund_repository):
        """Test clearing cache for a specific fund."""
        fund_repository._cache['fund:1'] = 'test_data'
        fund_repository._cache['fund:2'] = 'other_data'
        
        fund_repository._clear_fund_cache(1)
        
        assert 'fund:1' not in fund_repository._cache
        assert 'fund:2' in fund_repository._cache
    
    def test_clear_all_cache(self, fund_repository):
        """Test clearing all cached data."""
        fund_repository._cache['fund:1'] = 'test_data'
        fund_repository._cache['funds:company:1'] = 'other_data'
        
        fund_repository.clear_all_cache()
        
        assert len(fund_repository._cache) == 0

    # ============================================================================
    # INITIALIZATION AND CONFIGURATION TESTING
    # ============================================================================
    
    def test_repository_initialization_default_cache_ttl(self):
        """Test repository initialization with default cache TTL."""
        repository = FundRepository()
        
        assert repository._cache_ttl == 300
        assert repository._cache == {}
    
    def test_repository_initialization_custom_cache_ttl(self):
        """Test repository initialization with custom cache TTL."""
        repository = FundRepository(cache_ttl=600)
        
        assert repository._cache_ttl == 600
        assert repository._cache == {}
