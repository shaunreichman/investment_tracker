"""
Fund PNL Service Unit Tests.

This module tests the FundPnlService class, focusing on business logic,
PNL calculations, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- PNL fund field updates with change tracking
- PNL calculations for different fund tracking types
- Service layer orchestration
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.fund.services.fund_pnl_service import FundPnlService
from src.fund.models import Fund, FundFieldChange
from src.fund.enums.fund_enums import FundTrackingType
from src.shared.enums.shared_enums import SortOrder
from tests.factories.fund_factories import FundFactory


class TestFundPnlService:
    """Test suite for FundPnlService."""

    @pytest.fixture
    def service(self):
        """Create a FundPnlService instance for testing."""
        return FundPnlService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_fund_cost_based(self):
        """Mock fund instance with cost-based tracking."""
        fund = FundFactory.build(
            id=1,
            tracking_type=FundTrackingType.COST_BASED
        )
        # PNL fields will be None by default from the factory
        return fund

    @pytest.fixture
    def mock_fund_nav_based(self):
        """Mock fund instance with NAV-based tracking."""
        fund = FundFactory.build(
            id=1,
            tracking_type=FundTrackingType.NAV_BASED
        )
        # Set NAV-specific fields
        fund.current_units = 1000.0
        fund.current_unit_price = 10.0
        # PNL fields will be None by default from the factory
        return fund

    @pytest.fixture
    def mock_fund_events(self):
        """Mock fund events for testing."""
        return [
            Mock(id=1, event_type='DISTRIBUTION', distribution_type='DIVIDEND_FRANKED', amount=100.0),
            Mock(id=2, event_type='DISTRIBUTION', distribution_type='INTEREST', amount=50.0),
            Mock(id=3, event_type='CAPITAL_CALL', amount=1000.0)
        ]

    ################################################################################
    # Test update_fund_pnl method - Cost-based funds
    ################################################################################

    def test_update_fund_pnl_cost_based_with_changes_returns_field_changes(self, service, mock_session, mock_fund_cost_based, mock_fund_events):
        """Test that update_fund_pnl returns field changes for cost-based funds when PNL values change."""
        # Arrange
        old_pnl = mock_fund_cost_based.pnl
        old_realized_pnl = mock_fund_cost_based.realized_pnl
        old_unrealized_pnl = mock_fund_cost_based.unrealized_pnl
        old_realized_pnl_dividend = mock_fund_cost_based.realized_pnl_dividend
        old_realized_pnl_interest = mock_fund_cost_based.realized_pnl_interest
        old_realized_pnl_distribution = mock_fund_cost_based.realized_pnl_distribution
        
        # Mock calculator to return different values
        mock_pnl_dict = {
            'pnl': 150.0,
            'realized_pnl': 150.0,
            'unrealized_pnl': 0.0,
            'realized_pnl_capital_gain': None,
            'unrealized_pnl_capital_gain': None,
            'realized_pnl_dividend': 100.0,
            'realized_pnl_interest': 50.0,
            'realized_pnl_distribution': 150.0
        }
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_repo, \
             patch.object(service.fund_pnl_calculator, 'calculate_pnl', return_value=mock_pnl_dict) as mock_calc:
            
            # Act
            result = service.update_fund_pnl(mock_fund_cost_based, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 6  # PNL fields changed (None to values, excluding capital gains which remain None)
            
            # Check PNL change
            pnl_change = next((change for change in result if change.field_name == 'pnl'), None)
            assert pnl_change is not None
            assert pnl_change.object == 'FUND'
            assert pnl_change.object_id == mock_fund_cost_based.id
            assert pnl_change.old_value == old_pnl
            assert pnl_change.new_value == 150.0
            
            # Check realized PNL change
            realized_pnl_change = next((change for change in result if change.field_name == 'realized_pnl'), None)
            assert realized_pnl_change is not None
            assert realized_pnl_change.old_value == old_realized_pnl
            assert realized_pnl_change.new_value == 150.0
            
            # Check dividend PNL change
            dividend_change = next((change for change in result if change.field_name == 'realized_pnl_dividend'), None)
            assert dividend_change is not None
            assert dividend_change.old_value == old_realized_pnl_dividend
            assert dividend_change.new_value == 100.0
            
            # Check interest PNL change
            interest_change = next((change for change in result if change.field_name == 'realized_pnl_interest'), None)
            assert interest_change is not None
            assert interest_change.old_value == old_realized_pnl_interest
            assert interest_change.new_value == 50.0
            
            # Check distribution PNL change
            distribution_change = next((change for change in result if change.field_name == 'realized_pnl_distribution'), None)
            assert distribution_change is not None
            assert distribution_change.old_value == old_realized_pnl_distribution
            assert distribution_change.new_value == 150.0
            
            # Verify fund was updated
            assert mock_fund_cost_based.pnl == 150.0
            assert mock_fund_cost_based.realized_pnl == 150.0
            assert mock_fund_cost_based.realized_pnl_dividend == 100.0
            assert mock_fund_cost_based.realized_pnl_interest == 50.0
            assert mock_fund_cost_based.realized_pnl_distribution == 150.0
            
            # Verify repository was called correctly
            mock_repo.assert_called_once_with(
                mock_session, 
                fund_ids=[mock_fund_cost_based.id], 
                sort_order=SortOrder.ASC
            )
            
            # Verify calculator was called correctly
            mock_calc.assert_called_once_with(fund_events=mock_fund_events, fund=mock_fund_cost_based)

    def test_update_fund_pnl_cost_based_no_changes_returns_none(self, service, mock_session, mock_fund_cost_based, mock_fund_events):
        """Test that update_fund_pnl returns None when no changes occur for cost-based funds."""
        # Arrange
        # Set the fund to have the same values as what the calculator will return
        mock_fund_cost_based.pnl = 0.0
        mock_fund_cost_based.realized_pnl = 0.0
        mock_fund_cost_based.unrealized_pnl = 0.0
        mock_fund_cost_based.realized_pnl_capital_gain = None
        mock_fund_cost_based.unrealized_pnl_capital_gain = None
        mock_fund_cost_based.realized_pnl_dividend = 0.0
        mock_fund_cost_based.realized_pnl_interest = 0.0
        mock_fund_cost_based.realized_pnl_distribution = 0.0
        
        mock_pnl_dict = {
            'pnl': 0.0,
            'realized_pnl': 0.0,
            'unrealized_pnl': 0.0,
            'realized_pnl_capital_gain': None,
            'unrealized_pnl_capital_gain': None,
            'realized_pnl_dividend': 0.0,
            'realized_pnl_interest': 0.0,
            'realized_pnl_distribution': 0.0
        }
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_repo, \
             patch.object(service.fund_pnl_calculator, 'calculate_pnl', return_value=mock_pnl_dict) as mock_calc:
            
            # Act
            result = service.update_fund_pnl(mock_fund_cost_based, mock_session)

            # Assert
            assert result is None
            assert mock_fund_cost_based.pnl == 0.0
            assert mock_fund_cost_based.realized_pnl == 0.0

    def test_update_fund_pnl_cost_based_partial_changes_returns_partial_changes(self, service, mock_session, mock_fund_cost_based, mock_fund_events):
        """Test that update_fund_pnl returns only changed fields for cost-based funds."""
        # Arrange
        # Set some fields to have the same values as what the calculator will return
        mock_fund_cost_based.unrealized_pnl = 0.0
        mock_fund_cost_based.realized_pnl_capital_gain = None
        mock_fund_cost_based.unrealized_pnl_capital_gain = None
        mock_fund_cost_based.realized_pnl_interest = 0.0
        
        mock_pnl_dict = {
            'pnl': 100.0,  # Changed
            'realized_pnl': 100.0,  # Changed
            'unrealized_pnl': 0.0,  # Same
            'realized_pnl_capital_gain': None,  # Same
            'unrealized_pnl_capital_gain': None,  # Same
            'realized_pnl_dividend': 100.0,  # Changed
            'realized_pnl_interest': 0.0,  # Same
            'realized_pnl_distribution': 100.0  # Changed
        }
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_repo, \
             patch.object(service.fund_pnl_calculator, 'calculate_pnl', return_value=mock_pnl_dict) as mock_calc:
            
            # Act
            result = service.update_fund_pnl(mock_fund_cost_based, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 4  # Only changed fields
            
            # Verify only changed fields are in result
            field_names = [change.field_name for change in result]
            assert 'pnl' in field_names
            assert 'realized_pnl' in field_names
            assert 'realized_pnl_dividend' in field_names
            assert 'realized_pnl_distribution' in field_names
            assert 'unrealized_pnl' not in field_names
            assert 'realized_pnl_interest' not in field_names

    ################################################################################
    # Test update_fund_pnl method - NAV-based funds
    ################################################################################

    def test_update_fund_pnl_nav_based_with_capital_gains_returns_field_changes(self, service, mock_session, mock_fund_nav_based, mock_fund_events):
        """Test that update_fund_pnl returns field changes for NAV-based funds with capital gains."""
        # Arrange
        old_pnl = mock_fund_nav_based.pnl
        old_realized_pnl = mock_fund_nav_based.realized_pnl
        old_unrealized_pnl = mock_fund_nav_based.unrealized_pnl
        old_realized_pnl_capital_gain = mock_fund_nav_based.realized_pnl_capital_gain
        old_unrealized_pnl_capital_gain = mock_fund_nav_based.unrealized_pnl_capital_gain
        
        # Mock calculator to return capital gains values
        mock_pnl_dict = {
            'pnl': 200.0,
            'realized_pnl': 150.0,
            'unrealized_pnl': 50.0,
            'realized_pnl_capital_gain': 100.0,
            'unrealized_pnl_capital_gain': 50.0,
            'realized_pnl_dividend': 50.0,
            'realized_pnl_interest': 0.0,
            'realized_pnl_distribution': 50.0
        }
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_repo, \
             patch.object(service.fund_pnl_calculator, 'calculate_pnl', return_value=mock_pnl_dict) as mock_calc:
            
            # Act
            result = service.update_fund_pnl(mock_fund_nav_based, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 8  # All PNL fields changed (None to values, including capital gains)
            
            # Check capital gains changes
            realized_capital_gain_change = next((change for change in result if change.field_name == 'realized_pnl_capital_gain'), None)
            assert realized_capital_gain_change is not None
            assert realized_capital_gain_change.old_value == old_realized_pnl_capital_gain
            assert realized_capital_gain_change.new_value == 100.0
            
            unrealized_capital_gain_change = next((change for change in result if change.field_name == 'unrealized_pnl_capital_gain'), None)
            assert unrealized_capital_gain_change is not None
            assert unrealized_capital_gain_change.old_value == old_unrealized_pnl_capital_gain
            assert unrealized_capital_gain_change.new_value == 50.0
            
            # Verify fund was updated
            assert mock_fund_nav_based.realized_pnl_capital_gain == 100.0
            assert mock_fund_nav_based.unrealized_pnl_capital_gain == 50.0

    def test_update_fund_pnl_nav_based_no_capital_gains_returns_field_changes(self, service, mock_session, mock_fund_nav_based, mock_fund_events):
        """Test that update_fund_pnl handles NAV-based funds with no capital gains correctly."""
        # Arrange
        mock_pnl_dict = {
            'pnl': 50.0,
            'realized_pnl': 50.0,
            'unrealized_pnl': 0.0,
            'realized_pnl_capital_gain': 0.0,
            'unrealized_pnl_capital_gain': 0.0,
            'realized_pnl_dividend': 50.0,
            'realized_pnl_interest': 0.0,
            'realized_pnl_distribution': 50.0
        }
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_repo, \
             patch.object(service.fund_pnl_calculator, 'calculate_pnl', return_value=mock_pnl_dict) as mock_calc:
            
            # Act
            result = service.update_fund_pnl(mock_fund_nav_based, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 8  # All fields changed (None to values, including 0.0)
            
            # Check that all fields are included
            field_names = [change.field_name for change in result]
            assert 'pnl' in field_names
            assert 'realized_pnl' in field_names
            assert 'unrealized_pnl' in field_names
            assert 'realized_pnl_dividend' in field_names
            assert 'realized_pnl_distribution' in field_names
            assert 'realized_pnl_capital_gain' in field_names
            assert 'unrealized_pnl_capital_gain' in field_names
            
            # Check capital gains changes (these should be 0.0, so change from None to 0.0)
            realized_capital_gain_change = next((change for change in result if change.field_name == 'realized_pnl_capital_gain'), None)
            assert realized_capital_gain_change is not None
            assert realized_capital_gain_change.new_value == 0.0
            
            unrealized_capital_gain_change = next((change for change in result if change.field_name == 'unrealized_pnl_capital_gain'), None)
            assert unrealized_capital_gain_change is not None
            assert unrealized_capital_gain_change.new_value == 0.0

    ################################################################################
    # Test update_fund_pnl method - Edge cases
    ################################################################################

    def test_update_fund_pnl_no_events_handles_gracefully(self, service, mock_session, mock_fund_cost_based):
        """Test that update_fund_pnl handles no events gracefully."""
        # Arrange
        # Set the fund to have the same values as what the calculator will return
        mock_fund_cost_based.pnl = 0.0
        mock_fund_cost_based.realized_pnl = 0.0
        mock_fund_cost_based.unrealized_pnl = 0.0
        mock_fund_cost_based.realized_pnl_capital_gain = None
        mock_fund_cost_based.unrealized_pnl_capital_gain = None
        mock_fund_cost_based.realized_pnl_dividend = 0.0
        mock_fund_cost_based.realized_pnl_interest = 0.0
        mock_fund_cost_based.realized_pnl_distribution = 0.0
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_repo, \
             patch.object(service.fund_pnl_calculator, 'calculate_pnl', return_value={
                 'pnl': 0.0, 'realized_pnl': 0.0, 'unrealized_pnl': 0.0,
                 'realized_pnl_capital_gain': None, 'unrealized_pnl_capital_gain': None,
                 'realized_pnl_dividend': 0.0, 'realized_pnl_interest': 0.0, 'realized_pnl_distribution': 0.0
             }) as mock_calc:
            
            # Act
            result = service.update_fund_pnl(mock_fund_cost_based, mock_session)

            # Assert
            assert result is None
            mock_repo.assert_called_once_with(
                mock_session, 
                fund_ids=[mock_fund_cost_based.id], 
                sort_order=SortOrder.ASC
            )
            mock_calc.assert_called_once_with(fund_events=[], fund=mock_fund_cost_based)

    def test_update_fund_pnl_preserves_original_values_when_no_changes(self, service, mock_session, mock_fund_cost_based, mock_fund_events):
        """Test that update_fund_pnl preserves original values when no changes occur."""
        # Arrange
        # Set the fund to have the same values as what the calculator will return
        mock_fund_cost_based.pnl = 0.0
        mock_fund_cost_based.realized_pnl = 0.0
        mock_fund_cost_based.unrealized_pnl = 0.0
        mock_fund_cost_based.realized_pnl_capital_gain = None
        mock_fund_cost_based.unrealized_pnl_capital_gain = None
        mock_fund_cost_based.realized_pnl_dividend = 0.0
        mock_fund_cost_based.realized_pnl_interest = 0.0
        mock_fund_cost_based.realized_pnl_distribution = 0.0
        
        original_pnl = mock_fund_cost_based.pnl
        original_realized_pnl = mock_fund_cost_based.realized_pnl
        
        mock_pnl_dict = {
            'pnl': original_pnl,
            'realized_pnl': original_realized_pnl,
            'unrealized_pnl': 0.0,
            'realized_pnl_capital_gain': None,
            'unrealized_pnl_capital_gain': None,
            'realized_pnl_dividend': 0.0,
            'realized_pnl_interest': 0.0,
            'realized_pnl_distribution': 0.0
        }
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_repo, \
             patch.object(service.fund_pnl_calculator, 'calculate_pnl', return_value=mock_pnl_dict) as mock_calc:
            
            # Act
            result = service.update_fund_pnl(mock_fund_cost_based, mock_session)

            # Assert
            assert result is None
            assert mock_fund_cost_based.pnl == original_pnl
            assert mock_fund_cost_based.realized_pnl == original_realized_pnl

    def test_update_fund_pnl_handles_none_events_gracefully(self, service, mock_session, mock_fund_cost_based):
        """Test that update_fund_pnl handles None events gracefully."""
        # Arrange
        # Set the fund to have the same values as what the calculator will return
        mock_fund_cost_based.pnl = 0.0
        mock_fund_cost_based.realized_pnl = 0.0
        mock_fund_cost_based.unrealized_pnl = 0.0
        mock_fund_cost_based.realized_pnl_capital_gain = None
        mock_fund_cost_based.unrealized_pnl_capital_gain = None
        mock_fund_cost_based.realized_pnl_dividend = 0.0
        mock_fund_cost_based.realized_pnl_interest = 0.0
        mock_fund_cost_based.realized_pnl_distribution = 0.0
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=None) as mock_repo, \
             patch.object(service.fund_pnl_calculator, 'calculate_pnl', return_value={
                 'pnl': 0.0, 'realized_pnl': 0.0, 'unrealized_pnl': 0.0,
                 'realized_pnl_capital_gain': None, 'unrealized_pnl_capital_gain': None,
                 'realized_pnl_dividend': 0.0, 'realized_pnl_interest': 0.0, 'realized_pnl_distribution': 0.0
             }) as mock_calc:
            
            # Act & Assert - should not raise error
            result = service.update_fund_pnl(mock_fund_cost_based, mock_session)
            assert result is None

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.fund_event_repository is not None
        assert service.fund_pnl_calculator is not None
        assert hasattr(service, 'fund_event_repository')
        assert hasattr(service, 'fund_pnl_calculator')

    def test_service_initializes_with_custom_dependencies(self):
        """Test that service can be initialized with custom dependencies."""
        # Arrange
        custom_repository = Mock()
        custom_calculator = Mock()
        
        # Act
        service = FundPnlService()
        service.fund_event_repository = custom_repository
        service.fund_pnl_calculator = custom_calculator
        
        # Assert
        assert service.fund_event_repository == custom_repository
        assert service.fund_pnl_calculator == custom_calculator

    ################################################################################
    # Test field change tracking
    ################################################################################

    def test_update_fund_pnl_creates_correct_fund_field_changes(self, service, mock_session, mock_fund_cost_based, mock_fund_events):
        """Test that update_fund_pnl creates correct FundFieldChange objects."""
        # Arrange
        mock_pnl_dict = {
            'pnl': 100.0,
            'realized_pnl': 100.0,
            'unrealized_pnl': 0.0,
            'realized_pnl_capital_gain': None,
            'unrealized_pnl_capital_gain': None,
            'realized_pnl_dividend': 100.0,
            'realized_pnl_interest': 0.0,
            'realized_pnl_distribution': 100.0
        }
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_repo, \
             patch.object(service.fund_pnl_calculator, 'calculate_pnl', return_value=mock_pnl_dict) as mock_calc:
            
            # Act
            result = service.update_fund_pnl(mock_fund_cost_based, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 6  # All fields changed (None to values)
            
            # Verify all changes are FundFieldChange objects with correct structure
            for change in result:
                assert isinstance(change, FundFieldChange)
                assert change.object == 'FUND'
                assert change.object_id == mock_fund_cost_based.id
                assert change.field_name in ['pnl', 'realized_pnl', 'unrealized_pnl', 'realized_pnl_dividend', 'realized_pnl_interest', 'realized_pnl_distribution']
                assert change.old_value is None  # Original values are None
                assert change.new_value in [100.0, 0.0]  # New values

    def test_update_fund_pnl_handles_mixed_field_changes(self, service, mock_session, mock_fund_cost_based, mock_fund_events):
        """Test that update_fund_pnl handles mixed field changes correctly."""
        # Arrange
        mock_pnl_dict = {
            'pnl': 150.0,
            'realized_pnl': 100.0,  # Different from pnl
            'unrealized_pnl': 50.0,  # Different from 0
            'realized_pnl_capital_gain': None,
            'unrealized_pnl_capital_gain': None,
            'realized_pnl_dividend': 75.0,  # Different from 0
            'realized_pnl_interest': 25.0,  # Different from 0
            'realized_pnl_distribution': 100.0  # Different from 0
        }
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_repo, \
             patch.object(service.fund_pnl_calculator, 'calculate_pnl', return_value=mock_pnl_dict) as mock_calc:
            
            # Act
            result = service.update_fund_pnl(mock_fund_cost_based, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 6  # All fields changed (None to values)
            
            # Verify each field change
            field_changes = {change.field_name: change for change in result}
            
            assert field_changes['pnl'].new_value == 150.0
            assert field_changes['realized_pnl'].new_value == 100.0
            assert field_changes['unrealized_pnl'].new_value == 50.0
            assert field_changes['realized_pnl_dividend'].new_value == 75.0
            assert field_changes['realized_pnl_interest'].new_value == 25.0
            assert field_changes['realized_pnl_distribution'].new_value == 100.0
