"""
Fund Repository Unit Tests.

This module tests the FundRepository class, focusing on data access operations
and error handling. Tests are precise and focused on repository functionality
without testing business logic or validation.

Test Coverage:
- CRUD operations (Create, Read, Delete)
- Filtering and sorting functionality
- Error handling for invalid parameters
- Database session interactions
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.fund.repositories.fund_repository import FundRepository
from src.fund.models.fund import Fund
from src.fund.enums.fund_enums import FundStatus, FundTrackingType, SortFieldFund
from src.shared.enums.shared_enums import SortOrder
from tests.factories.fund_factories import FundFactory


class TestFundRepository:
    """Test suite for FundRepository."""

    @pytest.fixture
    def repository(self):
        """Create a FundRepository instance for testing."""
        return FundRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_fund_data(self):
        """Sample fund data for testing."""
        return {
            'name': 'Test Fund',
            'company_id': 1,
            'entity_id': 1,
            'tracking_type': FundTrackingType.NAV_BASED,
            'currency': 'AUD',
            'tax_jurisdiction': 'AU'
        }

    ################################################################################
    # Test get_funds method
    ################################################################################

    def test_get_funds_returns_all_funds(self, repository, mock_session):
        """Test that get_funds returns all funds when no filters applied."""
        # Arrange
        expected_funds = [FundFactory.build() for _ in range(3)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_funds

        # Act
        result = repository.get_funds(mock_session)

        # Assert
        assert result == expected_funds
        mock_session.query.assert_called_once_with(Fund)

    def test_get_funds_with_company_id_filter(self, repository, mock_session):
        """Test that get_funds filters by company_id correctly."""
        # Arrange
        company_id = 123
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_funds(mock_session, company_ids=[company_id])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Fund)

    def test_get_funds_with_entity_id_filter(self, repository, mock_session):
        """Test that get_funds filters by entity_id correctly."""
        # Arrange
        entity_id = 456
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_funds(mock_session, entity_ids=[entity_id])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Fund)

    def test_get_funds_with_fund_status_filter(self, repository, mock_session):
        """Test that get_funds filters by fund_status correctly."""
        # Arrange
        fund_status = FundStatus.ACTIVE
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_funds(mock_session, fund_statuses=[fund_status])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Fund)

    def test_get_funds_with_fund_tracking_type_filter(self, repository, mock_session):
        """Test that get_funds filters by fund_tracking_type correctly."""
        # Arrange
        tracking_type = FundTrackingType.NAV_BASED
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_funds(mock_session, fund_tracking_types=[tracking_type])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Fund)

    def test_get_funds_with_multiple_filters(self, repository, mock_session):
        """Test that get_funds applies multiple filters correctly."""
        # Arrange
        company_id = 123
        entity_id = 456
        fund_status = FundStatus.ACTIVE
        tracking_type = FundTrackingType.NAV_BASED
        
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_funds(
            mock_session,
            company_ids=[company_id],
            entity_ids=[entity_id],
            fund_statuses=[fund_status],
            fund_tracking_types=[tracking_type]
        )

        # Assert
        # Should be called 4 times for each filter
        assert mock_query.filter.call_count == 4
        mock_session.query.assert_called_once_with(Fund)

    def test_get_funds_sorting_by_name_asc(self, repository, mock_session):
        """Test that get_funds sorts by name in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_funds(mock_session, sort_by=SortFieldFund.NAME, sort_order=SortOrder.ASC)

        # Assert
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(Fund)

    def test_get_funds_sorting_by_status_desc(self, repository, mock_session):
        """Test that get_funds sorts by status in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_funds(mock_session, sort_by=SortFieldFund.STATUS, sort_order=SortOrder.DESC)

        # Assert
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(Fund)

    def test_get_funds_sorting_by_created_at_asc(self, repository, mock_session):
        """Test that get_funds sorts by created_at in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_funds(mock_session, sort_by=SortFieldFund.CREATED_AT, sort_order=SortOrder.ASC)

        # Assert
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(Fund)

    def test_get_funds_sorting_by_start_date_desc(self, repository, mock_session):
        """Test that get_funds sorts by start_date in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_funds(mock_session, sort_by=SortFieldFund.START_DATE, sort_order=SortOrder.DESC)

        # Assert
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(Fund)

    def test_get_funds_invalid_sort_field_raises_error(self, repository, mock_session):
        """Test that get_funds raises ValueError for invalid sort field."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_funds(mock_session, sort_by="INVALID_FIELD")

    def test_get_funds_invalid_sort_order_raises_error(self, repository, mock_session):
        """Test that get_funds raises ValueError for invalid sort order."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_funds(mock_session, sort_order="INVALID_ORDER")

    ################################################################################
    # Test get_fund_by_id method
    ################################################################################

    def test_get_fund_by_id_returns_fund(self, repository, mock_session):
        """Test that get_fund_by_id returns the correct fund."""
        # Arrange
        fund_id = 123
        expected_fund = FundFactory.build(id=fund_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_fund

        # Act
        result = repository.get_fund_by_id(fund_id, mock_session)

        # Assert
        assert result == expected_fund
        mock_session.query.assert_called_once_with(Fund)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    def test_get_fund_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_fund_by_id returns None when fund not found."""
        # Arrange
        fund_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_fund_by_id(fund_id, mock_session)

        # Assert
        assert result is None
        mock_session.query.assert_called_once_with(Fund)

    ################################################################################
    # Test create_fund method
    ################################################################################

    def test_create_fund_creates_fund_successfully(self, repository, mock_session, sample_fund_data):
        """Test that create_fund creates a fund successfully."""
        # Arrange
        expected_fund = FundFactory.build(**sample_fund_data)
        mock_session.flush.return_value = None

        # Act
        with patch('src.fund.repositories.fund_repository.Fund') as mock_fund_class:
            mock_fund_instance = Mock()
            mock_fund_instance.id = 123
            mock_fund_class.return_value = mock_fund_instance
            
            result = repository.create_fund(sample_fund_data, mock_session)

        # Assert
        mock_fund_class.assert_called_once_with(**sample_fund_data)
        mock_session.add.assert_called_once_with(mock_fund_instance)
        mock_session.flush.assert_called_once()
        assert result == mock_fund_instance

    ################################################################################
    # Test delete_fund method
    ################################################################################

    def test_delete_fund_deletes_fund_successfully(self, repository, mock_session):
        """Test that delete_fund deletes a fund successfully."""
        # Arrange
        fund_id = 123
        mock_fund = FundFactory.build(id=fund_id)
        
        # Mock get_fund_by_id to return the fund
        with patch.object(repository, 'get_fund_by_id', return_value=mock_fund):
            # Act
            result = repository.delete_fund(fund_id, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(mock_fund)

    def test_delete_fund_returns_false_when_fund_not_found(self, repository, mock_session):
        """Test that delete_fund returns False when fund not found."""
        # Arrange
        fund_id = 999
        
        # Mock get_fund_by_id to return None
        with patch.object(repository, 'get_fund_by_id', return_value=None):
            # Act
            result = repository.delete_fund(fund_id, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()

    ################################################################################
    # Test error handling
    ################################################################################

    def test_get_funds_with_none_session_raises_error(self, repository):
        """Test that get_funds raises appropriate error with None session."""
        # Act & Assert
        with pytest.raises(AttributeError):
            repository.get_funds(None)

    def test_get_fund_by_id_with_none_session_raises_error(self, repository):
        """Test that get_fund_by_id raises appropriate error with None session."""
        # Act & Assert
        with pytest.raises(AttributeError):
            repository.get_fund_by_id(123, None)

    def test_create_fund_with_none_session_raises_error(self, repository, sample_fund_data):
        """Test that create_fund raises appropriate error with None session."""
        # Act & Assert
        with pytest.raises(AttributeError):
            repository.create_fund(sample_fund_data, None)

    def test_delete_fund_with_none_session_raises_error(self, repository):
        """Test that delete_fund raises appropriate error with None session."""
        # Act & Assert
        with pytest.raises(AttributeError):
            repository.delete_fund(123, None)

