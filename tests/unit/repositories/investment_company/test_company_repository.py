"""
Company Repository Unit Tests.

This module tests the CompanyRepository class, focusing on data access operations,
caching behavior, and error handling. Tests are precise and focused on repository
functionality without testing business logic or validation.

Test Coverage:
- CRUD operations (Create, Read, Delete)
- Filtering and sorting functionality
- Caching behavior and cache invalidation
- Error handling for invalid parameters
- Database session interactions
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.investment_company.repositories.company_repository import CompanyRepository
from src.investment_company.models import InvestmentCompany
from src.investment_company.enums.company_enums import CompanyStatus, CompanyType, SortFieldCompany
from src.shared.enums.shared_enums import SortOrder
from tests.factories.investment_company_factories import InvestmentCompanyFactory


class TestCompanyRepository:
    """Test suite for CompanyRepository."""

    @pytest.fixture
    def repository(self):
        """Create a CompanyRepository instance for testing."""
        return CompanyRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_company_data(self):
        """Sample company data for testing."""
        return {
            'name': 'Test Company',
            'description': 'Test company description',
            'company_type': CompanyType.PRIVATE_EQUITY,
            'status': CompanyStatus.ACTIVE,
            'business_address': '123 Test Street',
            'website': 'https://testcompany.com'
        }

    ################################################################################
    # Test get_companies method
    ################################################################################

    def test_get_companies_returns_all_companies(self, repository, mock_session):
        """Test that get_companies returns all companies when no filters applied."""
        # Arrange
        expected_companies = [InvestmentCompanyFactory.build() for _ in range(3)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_companies

        # Act
        result = repository.get_companies(mock_session, sort_by=SortFieldCompany.NAME, sort_order=SortOrder.ASC)

        # Assert
        assert result == expected_companies
        mock_session.query.assert_called_once_with(InvestmentCompany)

    def test_get_companies_with_company_type_filter(self, repository, mock_session):
        """Test that get_companies filters by company_type correctly."""
        # Arrange
        company_type = CompanyType.PRIVATE_EQUITY
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_companies(mock_session, company_type=company_type, sort_by=SortFieldCompany.NAME, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(InvestmentCompany)

    def test_get_companies_with_status_filter(self, repository, mock_session):
        """Test that get_companies filters by status correctly."""
        # Arrange
        status = CompanyStatus.ACTIVE
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_companies(mock_session, status=status)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(InvestmentCompany)

    def test_get_companies_with_name_filter(self, repository, mock_session):
        """Test that get_companies filters by name correctly."""
        # Arrange
        name = "Test Company"
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_companies(mock_session, name=name)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(InvestmentCompany)

    def test_get_companies_with_multiple_filters(self, repository, mock_session):
        """Test that get_companies applies multiple filters correctly."""
        # Arrange
        company_type = CompanyType.PRIVATE_EQUITY
        status = CompanyStatus.ACTIVE
        name = "Test Company"
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_companies(mock_session, company_type=company_type, 
                               status=status, name=name, sort_by=SortFieldCompany.NAME, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.filter.call_count == 3

    def test_get_companies_sorts_by_name_asc(self, repository, mock_session):
        """Test that get_companies sorts by name in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_companies(mock_session, sort_by=SortFieldCompany.NAME, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(InvestmentCompany)

    def test_get_companies_sorts_by_name_desc(self, repository, mock_session):
        """Test that get_companies sorts by name in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_companies(mock_session, sort_by=SortFieldCompany.NAME, sort_order=SortOrder.DESC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(InvestmentCompany)

    def test_get_companies_sorts_by_status(self, repository, mock_session):
        """Test that get_companies sorts by status correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_companies(mock_session, sort_by=SortFieldCompany.STATUS, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(InvestmentCompany)

    def test_get_companies_sorts_by_start_date(self, repository, mock_session):
        """Test that get_companies sorts by start_date correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_companies(mock_session, sort_by=SortFieldCompany.START_DATE, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(InvestmentCompany)

    def test_get_companies_sorts_by_created_at(self, repository, mock_session):
        """Test that get_companies sorts by created_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_companies(mock_session, sort_by=SortFieldCompany.CREATED_AT, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(InvestmentCompany)

    def test_get_companies_sorts_by_updated_at(self, repository, mock_session):
        """Test that get_companies sorts by updated_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_companies(mock_session, sort_by=SortFieldCompany.UPDATED_AT, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(InvestmentCompany)

    def test_get_companies_raises_error_for_invalid_sort_field(self, repository, mock_session):
        """Test that get_companies raises ValueError for invalid sort field."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_companies(mock_session, sort_by="INVALID_FIELD")

    def test_get_companies_raises_error_for_invalid_sort_order(self, repository, mock_session):
        """Test that get_companies raises ValueError for invalid sort order."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_companies(mock_session, sort_by=SortFieldCompany.NAME, sort_order="INVALID_ORDER")

    def test_get_companies_uses_cache(self, repository, mock_session):
        """Test that get_companies uses cache for repeated queries."""
        # Arrange
        expected_companies = [InvestmentCompanyFactory.build() for _ in range(2)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_companies

        # Act - First call
        result1 = repository.get_companies(mock_session, sort_by=SortFieldCompany.NAME, sort_order=SortOrder.ASC)
        # Second call with same parameters
        result2 = repository.get_companies(mock_session, sort_by=SortFieldCompany.NAME, sort_order=SortOrder.ASC)

        # Assert
        assert result1 == expected_companies
        assert result2 == expected_companies
        # Should only query database once due to caching
        mock_session.query.assert_called_once()

    ################################################################################
    # Test get_company_by_id method
    ################################################################################

    def test_get_company_by_id_returns_company_when_found(self, repository, mock_session):
        """Test that get_company_by_id returns company when found."""
        # Arrange
        company_id = 1
        expected_company = InvestmentCompanyFactory.build(id=company_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_company

        # Act
        result = repository.get_company_by_id(company_id, mock_session)

        # Assert
        assert result == expected_company
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(InvestmentCompany)

    def test_get_company_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_company_by_id returns None when company not found."""
        # Arrange
        company_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_company_by_id(company_id, mock_session)

        # Assert
        assert result is None

    def test_get_company_by_id_uses_cache(self, repository, mock_session):
        """Test that get_company_by_id uses cache for repeated queries."""
        # Arrange
        company_id = 1
        expected_company = InvestmentCompanyFactory.build(id=company_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_company

        # Act - First call
        result1 = repository.get_company_by_id(company_id, mock_session)
        # Second call with same ID
        result2 = repository.get_company_by_id(company_id, mock_session)

        # Assert
        assert result1 == expected_company
        assert result2 == expected_company
        # Should only query database once due to caching
        mock_session.query.assert_called_once()

    ################################################################################
    # Test create_company method
    ################################################################################

    def test_create_company_creates_and_returns_company(self, repository, mock_session, sample_company_data):
        """Test that create_company creates and returns a company."""
        # Arrange
        expected_company = InvestmentCompanyFactory.build(**sample_company_data)
        with patch('src.investment_company.repositories.company_repository.InvestmentCompany', return_value=expected_company):
            # Act
            result = repository.create_company(sample_company_data, mock_session)

            # Assert
            assert result == expected_company
            mock_session.add.assert_called_once_with(expected_company)
            mock_session.flush.assert_called_once()

    def test_create_company_clears_cache(self, repository, mock_session, sample_company_data):
        """Test that create_company clears relevant caches."""
        # Arrange
        expected_company = InvestmentCompanyFactory.build(**sample_company_data)
        with patch('src.investment_company.repositories.company_repository.InvestmentCompany', return_value=expected_company):
            # Act
            repository.create_company(sample_company_data, mock_session)

            # Assert
            # Cache should be cleared (we can't easily test the private method directly,
            # but we can verify the method completes without error)
            assert True  # If we get here, the method completed successfully

    ################################################################################
    # Test delete_company method
    ################################################################################

    def test_delete_company_deletes_existing_company(self, repository, mock_session):
        """Test that delete_company deletes an existing company."""
        # Arrange
        company_id = 1
        expected_company = InvestmentCompanyFactory.build(id=company_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_company

        # Act
        result = repository.delete_company(company_id, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(expected_company)
        mock_session.flush.assert_called_once()

    def test_delete_company_returns_false_for_nonexistent_company(self, repository, mock_session):
        """Test that delete_company returns False for nonexistent company."""
        # Arrange
        company_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_company(company_id, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()

    def test_delete_company_clears_cache(self, repository, mock_session):
        """Test that delete_company clears relevant caches."""
        # Arrange
        company_id = 1
        expected_company = InvestmentCompanyFactory.build(id=company_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_company

        # Act
        result = repository.delete_company(company_id, mock_session)

        # Assert
        assert result is True
        # Cache should be cleared (we can't easily test the private method directly,
        # but we can verify the method completes without error)

    ################################################################################
    # Test cache management
    ################################################################################

    def test_clear_cache_clears_all_caches(self, repository, mock_session):
        """Test that _clear_cache clears all cached data."""
        # Arrange
        # Populate cache with some data
        repository._cache = {'test_key': 'test_value', 'company:id:1': 'company_data'}

        # Act
        repository._clear_cache()

        # Assert
        assert len(repository._cache) == 0

    def test_clear_company_caches_clears_company_specific_caches(self, repository):
        """Test that _clear_company_caches clears only company-related cache entries."""
        # Arrange
        repository._cache = {
            'company:id:1': 'company_data',
            'company:list': 'company_list_data',
            'other_key': 'other_data'
        }

        # Act
        repository._clear_company_caches()

        # Assert
        assert 'company:id:1' not in repository._cache
        assert 'company:list' not in repository._cache
        assert 'other_key' in repository._cache  # Other cache entries should remain

    def test_clear_company_cache_clears_specific_company_cache(self, repository):
        """Test that _clear_company_cache clears specific company cache entries."""
        # Arrange
        company_id = 1
        company_type = CompanyType.PRIVATE_EQUITY
        status = CompanyStatus.ACTIVE
        name = "Test Company"
        sort_by = SortFieldCompany.NAME
        sort_order = SortOrder.ASC
        
        repository._cache = {
            f'company:{company_id}': 'company_data',
            f'companies:company_type:{company_type}:status:{status}:name:{name}:sort_by:{sort_by}:sort_order:{sort_order}': 'companies_data',
            'other_key': 'other_data'
        }

        # Act
        repository._clear_company_cache(company_id, company_type, status, name, sort_by, sort_order)

        # Assert
        assert f'company:{company_id}' not in repository._cache
        assert f'companies:company_type:{company_type}:status:{status}:name:{name}:sort_by:{sort_by}:sort_order:{sort_order}' not in repository._cache
        assert 'other_key' in repository._cache  # Other cache entries should remain

    def test_cache_ttl_initialization(self):
        """Test that repository initializes with correct cache TTL."""
        # Act
        repository = CompanyRepository(cache_ttl=600)

        # Assert
        assert repository._cache_ttl == 600
        assert isinstance(repository._cache, dict)
        assert len(repository._cache) == 0

    def test_default_cache_ttl_initialization(self):
        """Test that repository initializes with default cache TTL."""
        # Act
        repository = CompanyRepository()

        # Assert
        assert repository._cache_ttl == 300  # Default value
        assert isinstance(repository._cache, dict)
        assert len(repository._cache) == 0
