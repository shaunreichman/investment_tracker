"""
Fund Tax Statement Repository Unit Tests.

This module tests the FundTaxStatementRepository class, focusing on data access operations,
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
from datetime import date

from src.fund.repositories.fund_tax_statement_repository import FundTaxStatementRepository
from src.fund.models import FundTaxStatement
from src.fund.enums.fund_tax_statement_enums import SortFieldFundTaxStatement
from src.shared.enums.shared_enums import SortOrder
from tests.factories.fund_factories import FundTaxStatementFactory


class TestFundTaxStatementRepository:
    """Test suite for FundTaxStatementRepository."""

    @pytest.fixture
    def repository(self):
        """Create a FundTaxStatementRepository instance for testing."""
        return FundTaxStatementRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_tax_statement_data(self):
        """Sample tax statement data for testing."""
        return {
            'fund_id': 1,
            'entity_id': 1,
            'financial_year': '2023-24',
            'financial_year_start_date': date(2023, 7, 1),
            'financial_year_end_date': date(2024, 6, 30),
            'tax_payment_date': date(2024, 5, 15),
            'statement_date': date(2024, 3, 1),
            'interest_income_amount': 1000.0,
            'interest_income_tax_rate': 30.0,
            'interest_tax_amount': 300.0,
            'dividend_franked_income_amount': 500.0,
            'dividend_unfranked_income_amount': 200.0,
            'capital_gain_income_amount': 1500.0,
            'accountant': 'Test Accountant',
            'notes': 'Test notes'
        }

    ################################################################################
    # Test get_fund_tax_statements method
    ################################################################################

    def test_get_fund_tax_statements_returns_all_statements(self, repository, mock_session):
        """Test that get_fund_tax_statements returns all statements when no filters applied."""
        # Arrange
        expected_statements = [FundTaxStatementFactory.build() for _ in range(3)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_statements

        # Act
        result = repository.get_fund_tax_statements(mock_session)

        # Assert
        assert result == expected_statements
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statements_with_fund_id_filter(self, repository, mock_session):
        """Test that get_fund_tax_statements filters by fund_id correctly."""
        # Arrange
        fund_id = 1
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_tax_statements(mock_session, fund_id=fund_id)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statements_with_entity_id_filter(self, repository, mock_session):
        """Test that get_fund_tax_statements filters by entity_id correctly."""
        # Arrange
        entity_id = 1
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_tax_statements(mock_session, entity_id=entity_id)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statements_with_financial_year_filter(self, repository, mock_session):
        """Test that get_fund_tax_statements filters by financial_year correctly."""
        # Arrange
        financial_year = '2023-24'
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_tax_statements(mock_session, financial_year=financial_year)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statements_with_date_filters(self, repository, mock_session):
        """Test that get_fund_tax_statements filters by date ranges correctly."""
        # Arrange
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_tax_statements(mock_session, 
                                         start_tax_payment_date=start_date,
                                         end_tax_payment_date=end_date)

        # Assert
        assert mock_query.filter.call_count == 2  # Two date filters applied
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statements_with_multiple_filters(self, repository, mock_session):
        """Test that get_fund_tax_statements applies multiple filters correctly."""
        # Arrange
        fund_id = 1
        entity_id = 1
        financial_year = '2023-24'
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_tax_statements(mock_session, 
                                         fund_id=fund_id,
                                         entity_id=entity_id,
                                         financial_year=financial_year)

        # Assert
        assert mock_query.filter.call_count == 3
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statements_sorts_by_financial_year_asc(self, repository, mock_session):
        """Test that get_fund_tax_statements sorts by financial_year in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_tax_statements(mock_session, 
                                         sort_by=SortFieldFundTaxStatement.FINANCIAL_YEAR,
                                         sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statements_sorts_by_financial_year_desc(self, repository, mock_session):
        """Test that get_fund_tax_statements sorts by financial_year in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_tax_statements(mock_session, 
                                         sort_by=SortFieldFundTaxStatement.FINANCIAL_YEAR,
                                         sort_order=SortOrder.DESC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statements_sorts_by_tax_payment_date(self, repository, mock_session):
        """Test that get_fund_tax_statements sorts by tax_payment_date correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_tax_statements(mock_session, 
                                         sort_by=SortFieldFundTaxStatement.TAX_PAYMENT_DATE,
                                         sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statements_sorts_by_created_at(self, repository, mock_session):
        """Test that get_fund_tax_statements sorts by created_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_tax_statements(mock_session, 
                                         sort_by=SortFieldFundTaxStatement.CREATED_AT,
                                         sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statements_sorts_by_updated_at(self, repository, mock_session):
        """Test that get_fund_tax_statements sorts by updated_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_tax_statements(mock_session, 
                                         sort_by=SortFieldFundTaxStatement.UPDATED_AT,
                                         sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statements_raises_error_for_invalid_sort_field(self, repository, mock_session):
        """Test that get_fund_tax_statements raises ValueError for invalid sort field."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_fund_tax_statements(mock_session, sort_by="INVALID_FIELD")

    def test_get_fund_tax_statements_raises_error_for_invalid_sort_order(self, repository, mock_session):
        """Test that get_fund_tax_statements raises ValueError for invalid sort order."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_fund_tax_statements(mock_session, sort_order="INVALID_ORDER")

    def test_get_fund_tax_statements_uses_cache(self, repository, mock_session):
        """Test that get_fund_tax_statements uses cache for repeated queries."""
        # Arrange
        expected_statements = [FundTaxStatementFactory.build() for _ in range(2)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_statements

        # Act - First call
        result1 = repository.get_fund_tax_statements(mock_session)
        # Second call with same parameters
        result2 = repository.get_fund_tax_statements(mock_session)

        # Assert
        assert result1 == expected_statements
        assert result2 == expected_statements
        # Should only query database once due to caching
        mock_session.query.assert_called_once()

    ################################################################################
    # Test get_fund_tax_statement_by_id method
    ################################################################################

    def test_get_fund_tax_statement_by_id_returns_statement_when_found(self, repository, mock_session):
        """Test that get_fund_tax_statement_by_id returns statement when found."""
        # Arrange
        statement_id = 1
        expected_statement = FundTaxStatementFactory.build(id=statement_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_statement

        # Act
        result = repository.get_fund_tax_statement_by_id(statement_id, mock_session)

        # Assert
        assert result == expected_statement
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_get_fund_tax_statement_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_fund_tax_statement_by_id returns None when statement not found."""
        # Arrange
        statement_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_fund_tax_statement_by_id(statement_id, mock_session)

        # Assert
        assert result is None

    def test_get_fund_tax_statement_by_id_uses_cache(self, repository, mock_session):
        """Test that get_fund_tax_statement_by_id uses cache for repeated queries."""
        # Arrange
        statement_id = 1
        expected_statement = FundTaxStatementFactory.build(id=statement_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_statement

        # Act - First call
        result1 = repository.get_fund_tax_statement_by_id(statement_id, mock_session)
        # Second call with same ID
        result2 = repository.get_fund_tax_statement_by_id(statement_id, mock_session)

        # Assert
        assert result1 == expected_statement
        assert result2 == expected_statement
        # Should only query database once due to caching
        mock_session.query.assert_called_once()

    ################################################################################
    # Test create_fund_tax_statement method
    ################################################################################

    def test_create_fund_tax_statement_creates_and_returns_statement(self, repository, mock_session, sample_tax_statement_data):
        """Test that create_fund_tax_statement creates and returns a statement."""
        # Arrange
        expected_statement = FundTaxStatementFactory.build(**sample_tax_statement_data)
        with patch('src.fund.repositories.fund_tax_statement_repository.FundTaxStatement', return_value=expected_statement):
            # Act
            result = repository.create_fund_tax_statement(sample_tax_statement_data, mock_session)

            # Assert
            assert result == expected_statement
            mock_session.add.assert_called_once_with(expected_statement)
            mock_session.flush.assert_called_once()

    def test_create_fund_tax_statement_caches_result(self, repository, mock_session, sample_tax_statement_data):
        """Test that create_fund_tax_statement caches the created statement."""
        # Arrange
        expected_statement = FundTaxStatementFactory.build(id=1, **sample_tax_statement_data)
        with patch('src.fund.repositories.fund_tax_statement_repository.FundTaxStatement', return_value=expected_statement):
            # Act
            repository.create_fund_tax_statement(sample_tax_statement_data, mock_session)

            # Assert
            # Verify the statement is cached
            cache_key = f"fund_tax_statement:{expected_statement.id}"
            assert cache_key in repository._cache
            assert repository._cache[cache_key] == expected_statement

    ################################################################################
    # Test delete_fund_tax_statement method
    ################################################################################

    def test_delete_fund_tax_statement_deletes_existing_statement(self, repository, mock_session):
        """Test that delete_fund_tax_statement deletes an existing statement."""
        # Arrange
        statement_id = 1
        expected_statement = FundTaxStatementFactory.build(id=statement_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_statement

        # Act
        result = repository.delete_fund_tax_statement(statement_id, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(expected_statement)

    def test_delete_fund_tax_statement_returns_false_for_nonexistent_statement(self, repository, mock_session):
        """Test that delete_fund_tax_statement returns False for nonexistent statement."""
        # Arrange
        statement_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_fund_tax_statement(statement_id, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()

    def test_delete_fund_tax_statement_clears_cache(self, repository, mock_session):
        """Test that delete_fund_tax_statement clears relevant caches."""
        # Arrange
        statement_id = 1
        expected_statement = FundTaxStatementFactory.build(id=statement_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_statement

        # Pre-populate cache
        cache_key = f"fund_tax_statement:{statement_id}"
        repository._cache[cache_key] = expected_statement

        # Act
        result = repository.delete_fund_tax_statement(statement_id, mock_session)

        # Assert
        assert result is True
        # Cache should be cleared
        assert cache_key not in repository._cache

    ################################################################################
    # Test cache management
    ################################################################################

    def test_clear_fund_tax_statement_cache_clears_specific_cache(self, repository):
        """Test that _clear_fund_tax_statement_cache clears specific cache entry."""
        # Arrange
        statement_id = 1
        cache_key = f"fund_tax_statement:{statement_id}"
        repository._cache = {
            cache_key: 'statement_data',
            'other_key': 'other_data'
        }

        # Act
        repository._clear_fund_tax_statement_cache(statement_id)

        # Assert
        assert cache_key not in repository._cache
        assert 'other_key' in repository._cache  # Other cache entries should remain

    def test_cache_ttl_initialization(self):
        """Test that repository initializes with correct cache TTL."""
        # Act
        repository = FundTaxStatementRepository(cache_ttl=600)

        # Assert
        assert repository._cache_ttl == 600
        assert isinstance(repository._cache, dict)
        assert len(repository._cache) == 0

    def test_default_cache_ttl_initialization(self):
        """Test that repository initializes with default cache TTL."""
        # Act
        repository = FundTaxStatementRepository()

        # Assert
        assert repository._cache_ttl == 300  # Default value
        assert isinstance(repository._cache, dict)
        assert len(repository._cache) == 0

    ################################################################################
    # Test edge cases and error handling
    ################################################################################

    def test_get_fund_tax_statements_with_none_filters(self, repository, mock_session):
        """Test that get_fund_tax_statements handles None filters correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_tax_statements(mock_session, 
                                         fund_id=None,
                                         entity_id=None,
                                         financial_year=None,
                                         start_tax_payment_date=None,
                                         end_tax_payment_date=None)

        # Assert
        # Should not apply any filters
        mock_query.filter.assert_not_called()
        mock_session.query.assert_called_once_with(FundTaxStatement)

    def test_create_fund_tax_statement_with_empty_data(self, repository, mock_session):
        """Test that create_fund_tax_statement handles empty data correctly."""
        # Arrange
        empty_data = {}
        expected_statement = FundTaxStatementFactory.build()
        with patch('src.fund.repositories.fund_tax_statement_repository.FundTaxStatement', return_value=expected_statement):
            # Act
            result = repository.create_fund_tax_statement(empty_data, mock_session)

            # Assert
            assert result == expected_statement
            mock_session.add.assert_called_once_with(expected_statement)
            mock_session.flush.assert_called_once()
