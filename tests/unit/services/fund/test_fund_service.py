"""
Tests for FundService.

This test file focuses on testing the orchestration logic in FundService,
not the delegated functionality which is tested in specialized service tests.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import date

from src.fund.services.fund_service import FundService
from src.fund.enums import FundStatus, FundType, EventType
from src.fund.models import Fund, FundEvent


class TestFundService:
    """Test cases for FundService orchestration logic."""

    @pytest.fixture
    def fund_service(self):
        """Create FundService instance with mocked dependencies."""
        with patch('src.fund.services.fund_service.FundRepository'), \
             patch('src.fund.services.fund_service.FundEventRepository'), \
             patch('src.fund.services.fund_service.TaxStatementRepository'), \
             patch('src.fund.services.fund_service.FundEventService'), \
             patch('src.fund.services.fund_service.FundValidationService'):
            return FundService()

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_fund_data(self):
        """Sample fund data for testing."""
        return {
            'name': 'Test Fund',
            'entity_id': 1,
            'investment_company_id': 1,
            'fund_type': 'Private Equity',
            'tracking_type': 'COST_BASED'
        }

    def test_create_fund_success(self, fund_service, mock_session, sample_fund_data):
        """Test successful fund creation."""
        # Arrange
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.create.return_value = mock_fund

        # Act
        result = fund_service.create_fund(sample_fund_data, mock_session)

        # Assert
        assert result == mock_fund
        fund_service.fund_repository.create.assert_called_once()
        call_args = fund_service.fund_repository.create.call_args[0]
        assert call_args[1] == mock_session  # session parameter

    def test_create_fund_missing_required_fields(self, fund_service, mock_session):
        """Test fund creation with missing required fields."""
        # Test missing name
        with pytest.raises(ValueError, match="Required field 'name' is missing"):
            fund_service.create_fund({'entity_id': 1, 'investment_company_id': 1}, mock_session)

        # Test missing entity_id
        with pytest.raises(ValueError, match="Required field 'entity_id' is missing"):
            fund_service.create_fund({'name': 'Test', 'investment_company_id': 1}, mock_session)

        # Test missing investment_company_id
        with pytest.raises(ValueError, match="Required field 'investment_company_id' is missing"):
            fund_service.create_fund({'name': 'Test', 'entity_id': 1}, mock_session)

    def test_create_fund_invalid_tracking_type(self, fund_service, mock_session):
        """Test fund creation with invalid tracking_type."""
        fund_data = {
            'name': 'Test Fund',
            'entity_id': 1,
            'investment_company_id': 1,
            'tracking_type': 'INVALID_TYPE'
        }

        with pytest.raises(ValueError, match="Invalid tracking_type"):
            fund_service.create_fund(fund_data, mock_session)

    def test_create_fund_tracking_type_conversion(self, fund_service, mock_session):
        """Test that tracking_type string is converted to enum."""
        fund_data = {
            'name': 'Test Fund',
            'entity_id': 1,
            'investment_company_id': 1,
            'tracking_type': 'COST_BASED'
        }
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.create.return_value = mock_fund

        # Act
        fund_service.create_fund(fund_data, mock_session)

        # Assert
        call_args = fund_service.fund_repository.create.call_args[0]
        processed_data = call_args[0]
        assert processed_data['tracking_type'] == FundType.COST_BASED

    def test_update_fund_success(self, fund_service, mock_session):
        """Test successful fund update."""
        # Arrange
        fund_id = 1
        update_data = {'name': 'Updated Fund'}
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.update.return_value = mock_fund

        # Act
        result = fund_service.update_fund(fund_id, update_data, mock_session)

        # Assert
        assert result == mock_fund
        fund_service.fund_repository.update.assert_called_once_with(fund_id, update_data, mock_session)

    def test_update_fund_not_found(self, fund_service, mock_session):
        """Test fund update when fund is not found."""
        # Arrange
        fund_id = 999
        update_data = {'name': 'Updated Fund'}
        fund_service.fund_repository.update.return_value = None

        # Act
        result = fund_service.update_fund(fund_id, update_data, mock_session)

        # Assert
        assert result is None

    def test_delete_fund_success(self, fund_service, mock_session):
        """Test successful fund deletion."""
        # Arrange
        fund_id = 1
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.get_by_id.return_value = mock_fund
        fund_service.validation_service.validate_fund_deletion.return_value = []
        fund_service.fund_repository.delete.return_value = True

        # Act
        result = fund_service.delete_fund(fund_id, mock_session)

        # Assert
        assert result is True
        fund_service.validation_service.validate_fund_deletion.assert_called_once_with(mock_fund, mock_session)
        fund_service.fund_repository.delete.assert_called_once_with(fund_id, mock_session)

    def test_delete_fund_not_found(self, fund_service, mock_session):
        """Test fund deletion when fund is not found."""
        # Arrange
        fund_id = 999
        fund_service.fund_repository.get_by_id.return_value = None

        # Act
        result = fund_service.delete_fund(fund_id, mock_session)

        # Assert
        assert result is False
        fund_service.fund_repository.delete.assert_not_called()

    def test_delete_fund_validation_failure(self, fund_service, mock_session):
        """Test fund deletion with validation failure."""
        # Arrange
        fund_id = 1
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.get_by_id.return_value = mock_fund
        validation_errors = ["Fund has active investments"]
        fund_service.validation_service.validate_fund_deletion.return_value = validation_errors

        # Act & Assert
        with pytest.raises(ValueError, match="Deletion validation failed"):
            fund_service.delete_fund(fund_id, mock_session)

        fund_service.fund_repository.delete.assert_not_called()

    def test_get_fund_success(self, fund_service, mock_session):
        """Test successful fund retrieval with events."""
        # Arrange
        fund_id = 1
        mock_fund = Mock(spec=Fund)
        mock_events = [Mock(spec=FundEvent), Mock(spec=FundEvent)]
        fund_service.fund_repository.get_by_id.return_value = mock_fund
        fund_service.fund_event_repository.get_by_fund.return_value = mock_events

        # Act
        result = fund_service.get_fund(fund_id, mock_session)

        # Assert
        assert result == mock_fund
        assert result.events == mock_events
        fund_service.fund_repository.get_by_id.assert_called_once_with(fund_id, mock_session)
        fund_service.fund_event_repository.get_by_fund.assert_called_once_with(fund_id, mock_session)

    def test_get_fund_not_found(self, fund_service, mock_session):
        """Test fund retrieval when fund is not found."""
        # Arrange
        fund_id = 999
        fund_service.fund_repository.get_by_id.return_value = None

        # Act
        result = fund_service.get_fund(fund_id, mock_session)

        # Assert
        assert result is None
        fund_service.fund_event_repository.get_by_fund.assert_not_called()

    def test_get_funds_by_status(self, fund_service, mock_session):
        """Test getting funds filtered by status."""
        # Arrange
        status = FundStatus.ACTIVE
        mock_funds = [Mock(spec=Fund), Mock(spec=Fund)]
        fund_service.fund_repository.get_funds_by_status.return_value = mock_funds

        # Act
        result = fund_service.get_funds(mock_session, status=status)

        # Assert
        assert result == mock_funds
        fund_service.fund_repository.get_funds_by_status.assert_called_once_with(status, mock_session)

    def test_get_funds_by_type(self, fund_service, mock_session):
        """Test getting funds filtered by type."""
        # Arrange
        fund_type = FundType.COST_BASED
        mock_funds = [Mock(spec=Fund)]
        fund_service.fund_repository.get_funds_by_type.return_value = mock_funds

        # Act
        result = fund_service.get_funds(mock_session, fund_type=fund_type)

        # Assert
        assert result == mock_funds
        fund_service.fund_repository.get_funds_by_type.assert_called_once_with(fund_type, mock_session)

    def test_get_funds_all(self, fund_service, mock_session):
        """Test getting all funds."""
        # Arrange
        mock_funds = [Mock(spec=Fund), Mock(spec=Fund), Mock(spec=Fund)]
        fund_service.fund_repository.get_all_funds.return_value = mock_funds

        # Act
        result = fund_service.get_funds(mock_session)

        # Assert
        assert result == mock_funds
        fund_service.fund_repository.get_all_funds.assert_called_once_with(mock_session)

    def test_get_fund_events_success(self, fund_service, mock_session):
        """Test successful fund events retrieval."""
        # Arrange
        fund_id = 1
        event_types = [EventType.CAPITAL_CALL, EventType.DISTRIBUTION]
        mock_events = [Mock(spec=FundEvent), Mock(spec=FundEvent)]
        fund_service.fund_event_repository.get_by_fund.return_value = mock_events

        # Act
        result = fund_service.get_fund_events(fund_id, mock_session, event_types)

        # Assert
        assert result == mock_events
        fund_service.fund_event_repository.get_by_fund.assert_called_once_with(fund_id, mock_session, event_types)

    def test_get_fund_events_no_filter(self, fund_service, mock_session):
        """Test fund events retrieval without type filter."""
        # Arrange
        fund_id = 1
        mock_events = [Mock(spec=FundEvent)]
        fund_service.fund_event_repository.get_by_fund.return_value = mock_events

        # Act
        result = fund_service.get_fund_events(fund_id, mock_session)

        # Assert
        assert result == mock_events
        fund_service.fund_event_repository.get_by_fund.assert_called_once_with(fund_id, mock_session, None)

    def test_get_fund_event_success(self, fund_service, mock_session):
        """Test successful single fund event retrieval."""
        # Arrange
        fund_id = 1
        event_id = 1
        mock_fund = Mock(spec=Fund)
        mock_event = Mock(spec=FundEvent)
        mock_event.fund_id = fund_id
        fund_service.fund_repository.get_by_id.return_value = mock_fund
        fund_service.fund_event_repository.get_by_id.return_value = mock_event

        # Act
        result = fund_service.get_fund_event(fund_id, event_id, mock_session)

        # Assert
        assert result == mock_event
        fund_service.fund_repository.get_by_id.assert_called_once_with(fund_id, mock_session)
        fund_service.fund_event_repository.get_by_id.assert_called_once_with(event_id, mock_session)

    def test_get_fund_event_fund_not_found(self, fund_service, mock_session):
        """Test fund event retrieval when fund is not found."""
        # Arrange
        fund_id = 999
        event_id = 1
        fund_service.fund_repository.get_by_id.return_value = None

        # Act
        result = fund_service.get_fund_event(fund_id, event_id, mock_session)

        # Assert
        assert result is None
        fund_service.fund_event_repository.get_by_id.assert_not_called()

    def test_get_fund_event_event_not_found(self, fund_service, mock_session):
        """Test fund event retrieval when event is not found."""
        # Arrange
        fund_id = 1
        event_id = 999
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.get_by_id.return_value = mock_fund
        fund_service.fund_event_repository.get_by_id.return_value = None

        # Act
        result = fund_service.get_fund_event(fund_id, event_id, mock_session)

        # Assert
        assert result is None

    def test_get_fund_event_wrong_fund(self, fund_service, mock_session):
        """Test fund event retrieval when event belongs to different fund."""
        # Arrange
        fund_id = 1
        event_id = 1
        mock_fund = Mock(spec=Fund)
        mock_event = Mock(spec=FundEvent)
        mock_event.fund_id = 2  # Different fund ID
        fund_service.fund_repository.get_by_id.return_value = mock_fund
        fund_service.fund_event_repository.get_by_id.return_value = mock_event

        # Act
        result = fund_service.get_fund_event(fund_id, event_id, mock_session)

        # Assert
        assert result is None

    # ============================================================================
    # EDGE CASE TESTS - Additional test cases for comprehensive coverage
    # ============================================================================

    def test_create_fund_with_empty_string_fields(self, fund_service, mock_session):
        """Test fund creation with empty string values for required fields."""
        # Note: The service only checks if fields exist in the dictionary, not if they have valid values
        # Empty strings and None values are passed through to the repository layer
        
        # Test empty name - should pass through to repository
        fund_data = {'name': '', 'entity_id': 1, 'investment_company_id': 1}
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.create.return_value = mock_fund
        
        result = fund_service.create_fund(fund_data, mock_session)
        assert result == mock_fund
        
        # Test None name - should pass through to repository
        fund_data = {'name': None, 'entity_id': 1, 'investment_company_id': 1}
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.create.return_value = mock_fund
        
        result = fund_service.create_fund(fund_data, mock_session)
        assert result == mock_fund

    def test_create_fund_with_none_entity_id(self, fund_service, mock_session):
        """Test fund creation with None entity_id."""
        # Note: The service only checks if fields exist in the dictionary, not if they have valid values
        # None values are passed through to the repository layer
        fund_data = {'name': 'Test Fund', 'entity_id': None, 'investment_company_id': 1}
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.create.return_value = mock_fund
        
        result = fund_service.create_fund(fund_data, mock_session)
        assert result == mock_fund

    def test_create_fund_with_none_investment_company_id(self, fund_service, mock_session):
        """Test fund creation with None investment_company_id."""
        # Note: The service only checks if fields exist in the dictionary, not if they have valid values
        # None values are passed through to the repository layer
        fund_data = {'name': 'Test Fund', 'entity_id': 1, 'investment_company_id': None}
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.create.return_value = mock_fund
        
        result = fund_service.create_fund(fund_data, mock_session)
        assert result == mock_fund

    def test_create_fund_with_all_tracking_types(self, fund_service, mock_session):
        """Test fund creation with all valid tracking types."""
        valid_tracking_types = ['COST_BASED', 'NAV_BASED']
        
        for tracking_type in valid_tracking_types:
            fund_data = {
                'name': f'Test Fund {tracking_type}',
                'entity_id': 1,
                'investment_company_id': 1,
                'tracking_type': tracking_type
            }
            mock_fund = Mock(spec=Fund)
            fund_service.fund_repository.create.return_value = mock_fund

            # Act
            result = fund_service.create_fund(fund_data, mock_session)

            # Assert
            assert result == mock_fund
            call_args = fund_service.fund_repository.create.call_args[0]
            processed_data = call_args[0]
            assert processed_data['tracking_type'] == FundType(tracking_type)

    def test_create_fund_with_fund_type_string_preserved(self, fund_service, mock_session):
        """Test that fund_type string values are preserved as-is for backward compatibility."""
        fund_data = {
            'name': 'Test Fund',
            'entity_id': 1,
            'investment_company_id': 1,
            'fund_type': 'Custom Fund Type String',
            'tracking_type': 'COST_BASED'
        }
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.create.return_value = mock_fund

        # Act
        fund_service.create_fund(fund_data, mock_session)

        # Assert
        call_args = fund_service.fund_repository.create.call_args[0]
        processed_data = call_args[0]
        assert processed_data['fund_type'] == 'Custom Fund Type String'  # Preserved as string

    def test_update_fund_with_empty_data(self, fund_service, mock_session):
        """Test fund update with empty update data."""
        # Arrange
        fund_id = 1
        update_data = {}
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.update.return_value = mock_fund

        # Act
        result = fund_service.update_fund(fund_id, update_data, mock_session)

        # Assert
        assert result == mock_fund
        fund_service.fund_repository.update.assert_called_once_with(fund_id, update_data, mock_session)

    def test_update_fund_with_none_data(self, fund_service, mock_session):
        """Test fund update with None update data."""
        # Arrange
        fund_id = 1
        update_data = None
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.update.return_value = mock_fund

        # Act
        result = fund_service.update_fund(fund_id, update_data, mock_session)

        # Assert
        assert result == mock_fund
        fund_service.fund_repository.update.assert_called_once_with(fund_id, update_data, mock_session)

    def test_delete_fund_with_invalid_fund_id(self, fund_service, mock_session):
        """Test fund deletion with invalid fund ID types."""
        # Note: The service doesn't validate ID types - it passes them through to the repository
        # The repository layer will handle the validation and may raise exceptions
        
        # Test with string ID - repository will handle this
        fund_service.fund_repository.get_by_id.return_value = None
        result = fund_service.delete_fund("invalid_id", mock_session)
        assert result is False  # Fund not found
        
        # Test with None ID - repository will handle this
        fund_service.fund_repository.get_by_id.return_value = None
        result = fund_service.delete_fund(None, mock_session)
        assert result is False  # Fund not found

    def test_get_funds_with_multiple_filters(self, fund_service, mock_session):
        """Test getting funds with both status and type filters (should prioritize status)."""
        # Arrange
        status = FundStatus.ACTIVE
        fund_type = FundType.COST_BASED
        mock_funds = [Mock(spec=Fund)]
        fund_service.fund_repository.get_funds_by_status.return_value = mock_funds

        # Act
        result = fund_service.get_funds(mock_session, status=status, fund_type=fund_type)

        # Assert
        assert result == mock_funds
        # Should call status filter (prioritized) and not type filter
        fund_service.fund_repository.get_funds_by_status.assert_called_once_with(status, mock_session)
        fund_service.fund_repository.get_funds_by_type.assert_not_called()

    def test_get_fund_events_with_empty_event_types_list(self, fund_service, mock_session):
        """Test fund events retrieval with empty event types list."""
        # Arrange
        fund_id = 1
        event_types = []
        mock_events = []
        fund_service.fund_event_repository.get_by_fund.return_value = mock_events

        # Act
        result = fund_service.get_fund_events(fund_id, mock_session, event_types)

        # Assert
        assert result == mock_events
        fund_service.fund_event_repository.get_by_fund.assert_called_once_with(fund_id, mock_session, event_types)

    def test_get_fund_events_with_none_event_types(self, fund_service, mock_session):
        """Test fund events retrieval with None event types."""
        # Arrange
        fund_id = 1
        event_types = None
        mock_events = [Mock(spec=FundEvent)]
        fund_service.fund_event_repository.get_by_fund.return_value = mock_events

        # Act
        result = fund_service.get_fund_events(fund_id, mock_session, event_types)

        # Assert
        assert result == mock_events
        fund_service.fund_event_repository.get_by_fund.assert_called_once_with(fund_id, mock_session, None)

    def test_get_fund_event_with_invalid_ids(self, fund_service, mock_session):
        """Test fund event retrieval with invalid ID types."""
        # Note: The service doesn't validate ID types - it passes them through to the repository
        # The repository layer will handle the validation
        
        # Test with string fund_id - repository will handle this
        fund_service.fund_repository.get_by_id.return_value = None
        result = fund_service.get_fund_event("invalid_fund_id", 1, mock_session)
        assert result is None  # Fund not found
        
        # Test with string event_id - repository will handle this
        fund_service.fund_repository.get_by_id.return_value = Mock(spec=Fund)
        fund_service.fund_event_repository.get_by_id.return_value = None
        result = fund_service.get_fund_event(1, "invalid_event_id", mock_session)
        assert result is None  # Event not found
        
        # Test with None fund_id - repository will handle this
        fund_service.fund_repository.get_by_id.return_value = None
        result = fund_service.get_fund_event(None, 1, mock_session)
        assert result is None  # Fund not found

    def test_get_fund_event_security_check(self, fund_service, mock_session):
        """Test security: event belongs to different fund returns None."""
        # Arrange
        fund_id = 1
        event_id = 1
        mock_fund = Mock(spec=Fund)
        mock_event = Mock(spec=FundEvent)
        mock_event.fund_id = 999  # Completely different fund ID
        fund_service.fund_repository.get_by_id.return_value = mock_fund
        fund_service.fund_event_repository.get_by_id.return_value = mock_event

        # Act
        result = fund_service.get_fund_event(fund_id, event_id, mock_session)

        # Assert
        assert result is None
        # Verify both repository methods were called
        fund_service.fund_repository.get_by_id.assert_called_once_with(fund_id, mock_session)
        fund_service.fund_event_repository.get_by_id.assert_called_once_with(event_id, mock_session)

    def test_get_fund_with_no_events(self, fund_service, mock_session):
        """Test fund retrieval when fund exists but has no events."""
        # Arrange
        fund_id = 1
        mock_fund = Mock(spec=Fund)
        mock_events = []  # Empty events list
        fund_service.fund_repository.get_by_id.return_value = mock_fund
        fund_service.fund_event_repository.get_by_fund.return_value = mock_events

        # Act
        result = fund_service.get_fund(fund_id, mock_session)

        # Assert
        assert result == mock_fund
        assert result.events == []
        fund_service.fund_repository.get_by_id.assert_called_once_with(fund_id, mock_session)
        fund_service.fund_event_repository.get_by_fund.assert_called_once_with(fund_id, mock_session)

    def test_delete_fund_validation_errors_formatting(self, fund_service, mock_session):
        """Test fund deletion validation error message formatting."""
        # Arrange
        fund_id = 1
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.get_by_id.return_value = mock_fund
        validation_errors = ["Error 1", "Error 2", "Error 3"]
        fund_service.validation_service.validate_fund_deletion.return_value = validation_errors

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            fund_service.delete_fund(fund_id, mock_session)

        # Assert error message contains all validation errors
        error_message = str(exc_info.value)
        assert "Deletion validation failed" in error_message
        assert "Error 1" in error_message
        assert "Error 2" in error_message
        assert "Error 3" in error_message

    def test_get_funds_with_invalid_status_enum(self, fund_service, mock_session):
        """Test getting funds with invalid status enum value."""
        # This test ensures the service doesn't crash with invalid enum values
        # The repository layer should handle the validation
        invalid_status = "INVALID_STATUS"
        
        # Act - Should not crash, repository will handle validation
        result = fund_service.get_funds(mock_session, status=invalid_status)
        
        # Assert - Repository was called with the invalid status
        fund_service.fund_repository.get_funds_by_status.assert_called_once_with(invalid_status, mock_session)

    def test_get_funds_with_invalid_fund_type_enum(self, fund_service, mock_session):
        """Test getting funds with invalid fund type enum value."""
        # This test ensures the service doesn't crash with invalid enum values
        invalid_fund_type = "INVALID_TYPE"
        
        # Act - Should not crash, repository will handle validation
        result = fund_service.get_funds(mock_session, fund_type=invalid_fund_type)
        
        # Assert - Repository was called with the invalid type
        fund_service.fund_repository.get_funds_by_type.assert_called_once_with(invalid_fund_type, mock_session)

    def test_create_fund_repository_error_propagation(self, fund_service, mock_session, sample_fund_data):
        """Test that repository errors are properly propagated."""
        # Arrange
        fund_service.fund_repository.create.side_effect = Exception("Database connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            fund_service.create_fund(sample_fund_data, mock_session)

    def test_update_fund_repository_error_propagation(self, fund_service, mock_session):
        """Test that repository errors are properly propagated during update."""
        # Arrange
        fund_id = 1
        update_data = {'name': 'Updated Fund'}
        fund_service.fund_repository.update.side_effect = Exception("Database connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            fund_service.update_fund(fund_id, update_data, mock_session)

    def test_delete_fund_repository_error_propagation(self, fund_service, mock_session):
        """Test that repository errors are properly propagated during deletion."""
        # Arrange
        fund_id = 1
        mock_fund = Mock(spec=Fund)
        fund_service.fund_repository.get_by_id.return_value = mock_fund
        fund_service.validation_service.validate_fund_deletion.return_value = []
        fund_service.fund_repository.delete.side_effect = Exception("Database connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            fund_service.delete_fund(fund_id, mock_session)
