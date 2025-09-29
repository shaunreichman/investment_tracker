"""
Fund Validation Service Unit Tests.

This module tests the FundValidationService class, focusing on business rule validation
and error handling. Tests are precise and focused on validation logic without testing
repository or model functionality directly.

Test Coverage:
- Fund deletion validation with dependency checking
- Fund event creation validation routing and business rules
- Capital call validation (fund type, commitment amount)
- Return of capital validation (fund type, equity balance)
- Unit purchase validation (fund type)
- Unit sale validation (fund type, available units)
- NAV update validation (fund type)
- Distribution validation (no business rules)
- Tax statement deletion validation (no business rules)
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.fund.services.fund_validation_service import FundValidationService
from src.fund.models import Fund
from src.fund.enums.fund_enums import FundTrackingType
from src.fund.enums.fund_event_enums import EventType
from tests.factories.fund_factories import FundFactory, FundEventFactory, FundTaxStatementFactory


class TestFundValidationService:
    """Test suite for FundValidationService."""

    @pytest.fixture
    def service(self):
        """Create a FundValidationService instance for testing."""
        return FundValidationService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_fund(self):
        """Mock fund instance."""
        return FundFactory.build(
            id=1, 
            name='Test Fund',
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,
            current_equity_balance=50000.0,
            current_units=1000.0
        )

    @pytest.fixture
    def mock_fund_events(self):
        """Mock fund events list."""
        return [FundEventFactory.build() for _ in range(2)]

    @pytest.fixture
    def mock_tax_statements(self):
        """Mock tax statements list."""
        return [FundTaxStatementFactory.build() for _ in range(1)]

    ################################################################################
    # Test validate_fund_deletion method
    ################################################################################

    def test_validate_fund_deletion_success_when_no_dependencies(self, service, mock_session, mock_fund):
        """Test successful fund deletion validation when no dependencies exist."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_events, \
             patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=[]) as mock_tax:
            
            # Act
            result = service.validate_fund_deletion(mock_fund, mock_session)

            # Assert
            assert result == {}
            mock_events.assert_called_once_with(mock_session, fund_ids=[mock_fund.id])
            mock_tax.assert_called_once_with(fund_id=mock_fund.id, session=mock_session)

    def test_validate_fund_deletion_fails_when_fund_events_exist(self, service, mock_session, mock_fund, mock_fund_events):
        """Test fund deletion validation fails when fund events exist."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_events, \
             patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=[]) as mock_tax:
            
            # Act
            result = service.validate_fund_deletion(mock_fund, mock_session)

            # Assert
            assert 'fund_events' in result
            assert len(result['fund_events']) == 1
            assert "Cannot delete fund with 2 fund events" in result['fund_events'][0]
            assert "Fund must have 0 events to be deleted" in result['fund_events'][0]

    def test_validate_fund_deletion_fails_when_tax_statements_exist(self, service, mock_session, mock_fund, mock_tax_statements):
        """Test fund deletion validation fails when tax statements exist."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_events, \
             patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=mock_tax_statements) as mock_tax:
            
            # Act
            result = service.validate_fund_deletion(mock_fund, mock_session)

            # Assert
            assert 'tax_statements' in result
            assert len(result['tax_statements']) == 1
            assert "Cannot delete fund with 1 tax statements" in result['tax_statements'][0]
            assert "Fund must have 0 tax statements to be deleted" in result['tax_statements'][0]

    def test_validate_fund_deletion_fails_when_both_dependencies_exist(self, service, mock_session, mock_fund, mock_fund_events, mock_tax_statements):
        """Test fund deletion validation fails when both fund events and tax statements exist."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_events, \
             patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=mock_tax_statements) as mock_tax:
            
            # Act
            result = service.validate_fund_deletion(mock_fund, mock_session)

            # Assert
            assert 'fund_events' in result
            assert 'tax_statements' in result
            assert len(result['fund_events']) == 1
            assert len(result['tax_statements']) == 1

    ################################################################################
    # Test validate_fund_event_creation method
    ################################################################################

    def test_validate_fund_event_creation_routes_to_capital_call_validation(self, service, mock_session):
        """Test that fund event creation routes to capital call validation."""
        # Arrange
        event_data = {'event_type': EventType.CAPITAL_CALL, 'tracking_type': FundTrackingType.COST_BASED}
        
        with patch.object(service, 'validate_capital_call', return_value={}) as mock_validate:
            # Act
            result = service.validate_fund_event_creation(event_data, mock_session)

            # Assert
            assert result == {}
            mock_validate.assert_called_once_with(event_data, mock_session)

    def test_validate_fund_event_creation_routes_to_return_of_capital_validation(self, service, mock_session):
        """Test that fund event creation routes to return of capital validation."""
        # Arrange
        event_data = {'event_type': EventType.RETURN_OF_CAPITAL, 'tracking_type': FundTrackingType.COST_BASED}
        
        with patch.object(service, 'validate_return_of_capital', return_value={}) as mock_validate:
            # Act
            result = service.validate_fund_event_creation(event_data, mock_session)

            # Assert
            assert result == {}
            mock_validate.assert_called_once_with(event_data, mock_session)

    def test_validate_fund_event_creation_routes_to_unit_purchase_validation(self, service, mock_session):
        """Test that fund event creation routes to unit purchase validation."""
        # Arrange
        event_data = {'event_type': EventType.UNIT_PURCHASE, 'tracking_type': FundTrackingType.NAV_BASED}
        
        with patch.object(service, 'validate_unit_purchase', return_value={}) as mock_validate:
            # Act
            result = service.validate_fund_event_creation(event_data, mock_session)

            # Assert
            assert result == {}
            mock_validate.assert_called_once_with(event_data, mock_session)

    def test_validate_fund_event_creation_routes_to_unit_sale_validation(self, service, mock_session):
        """Test that fund event creation routes to unit sale validation."""
        # Arrange
        event_data = {'event_type': EventType.UNIT_SALE, 'tracking_type': FundTrackingType.NAV_BASED}
        
        with patch.object(service, 'validate_unit_sale', return_value={}) as mock_validate:
            # Act
            result = service.validate_fund_event_creation(event_data, mock_session)

            # Assert
            assert result == {}
            mock_validate.assert_called_once_with(event_data, mock_session)

    def test_validate_fund_event_creation_routes_to_nav_update_validation(self, service, mock_session):
        """Test that fund event creation routes to NAV update validation."""
        # Arrange
        event_data = {'event_type': EventType.NAV_UPDATE, 'tracking_type': FundTrackingType.NAV_BASED}
        
        with patch.object(service, 'validate_nav_update', return_value={}) as mock_validate:
            # Act
            result = service.validate_fund_event_creation(event_data, mock_session)

            # Assert
            assert result == {}
            mock_validate.assert_called_once_with(event_data, mock_session)

    def test_validate_fund_event_creation_routes_to_distribution_validation(self, service, mock_session):
        """Test that fund event creation routes to distribution validation."""
        # Arrange
        event_data = {'event_type': EventType.DISTRIBUTION, 'tracking_type': FundTrackingType.COST_BASED}
        
        with patch.object(service, 'validate_distribution', return_value={}) as mock_validate:
            # Act
            result = service.validate_fund_event_creation(event_data, mock_session)

            # Assert
            assert result == {}
            mock_validate.assert_called_once_with(event_data, mock_session)

    def test_validate_fund_event_creation_raises_error_for_invalid_event_type(self, service, mock_session):
        """Test that fund event creation raises ValueError for invalid event type."""
        # Arrange
        event_data = {'event_type': 'INVALID_TYPE', 'tracking_type': FundTrackingType.COST_BASED}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid event type: INVALID_TYPE"):
            service.validate_fund_event_creation(event_data, mock_session)

    ################################################################################
    # Test validate_capital_call method
    ################################################################################

    def test_validate_capital_call_success_for_cost_based_fund(self, service, mock_session, mock_fund):
        """Test successful capital call validation for cost-based fund."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 1,
            'amount': 50000.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund:
            # Act
            result = service.validate_capital_call(event_data, mock_session)

            # Assert
            assert result == {}
            mock_get_fund.assert_called_once_with(1, mock_session)

    def test_validate_capital_call_fails_for_nav_based_fund(self, service, mock_session, mock_fund):
        """Test capital call validation fails for NAV-based fund."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.NAV_BASED,
            'fund_id': 1,
            'amount': 50000.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund:
            # Act
            result = service.validate_capital_call(event_data, mock_session)

            # Assert
            assert 'fund_type' in result
            assert "Capital calls are only applicable for cost-based funds" in result['fund_type']

    def test_validate_capital_call_fails_when_amount_exceeds_commitment(self, service, mock_session, mock_fund):
        """Test capital call validation fails when amount exceeds commitment."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 1,
            'amount': 150000.0  # Exceeds commitment_amount of 100000.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund:
            # Act
            result = service.validate_capital_call(event_data, mock_session)

            # Assert
            assert 'amount' in result
            assert "Cannot call more capital than remaining commitment" in result['amount']

    def test_validate_capital_call_raises_error_when_fund_not_found(self, service, mock_session):
        """Test capital call validation raises error when fund not found."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 999,
            'amount': 50000.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=None) as mock_get_fund:
            # Act & Assert
            with pytest.raises(ValueError, match="Fund not found"):
                service.validate_capital_call(event_data, mock_session)

    def test_validate_capital_call_success_when_commitment_amount_is_none(self, service, mock_session):
        """Test capital call validation succeeds when commitment amount is None."""
        # Arrange
        mock_fund_no_commitment = FundFactory.build(commitment_amount=None)
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 1,
            'amount': 50000.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund_no_commitment) as mock_get_fund:
            # Act
            result = service.validate_capital_call(event_data, mock_session)

            # Assert
            assert result == {}

    ################################################################################
    # Test validate_return_of_capital method
    ################################################################################

    def test_validate_return_of_capital_success_for_cost_based_fund(self, service, mock_session, mock_fund):
        """Test successful return of capital validation for cost-based fund."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 1,
            'amount': 25000.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund:
            # Act
            result = service.validate_return_of_capital(event_data, mock_session)

            # Assert
            assert result == {}
            mock_get_fund.assert_called_once_with(1, mock_session)

    def test_validate_return_of_capital_fails_for_nav_based_fund(self, service, mock_session, mock_fund):
        """Test return of capital validation fails for NAV-based fund."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.NAV_BASED,
            'fund_id': 1,
            'amount': 25000.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund:
            # Act
            result = service.validate_return_of_capital(event_data, mock_session)

            # Assert
            assert 'fund_type' in result
            assert "Returns of capital are only applicable for cost-based funds" in result['fund_type']

    def test_validate_return_of_capital_fails_when_amount_exceeds_equity(self, service, mock_session, mock_fund):
        """Test return of capital validation fails when amount exceeds equity balance."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 1,
            'amount': 75000.0  # Exceeds current_equity_balance of 50000.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund:
            # Act
            result = service.validate_return_of_capital(event_data, mock_session)

            # Assert
            assert 'amount' in result
            assert "Cannot return more capital than remaining equity" in result['amount']

    def test_validate_return_of_capital_raises_error_when_fund_not_found(self, service, mock_session):
        """Test return of capital validation raises error when fund not found."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 999,
            'amount': 25000.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=None) as mock_get_fund:
            # Act & Assert
            with pytest.raises(ValueError, match="Fund not found"):
                service.validate_return_of_capital(event_data, mock_session)

    def test_validate_return_of_capital_success_when_equity_balance_is_none(self, service, mock_session):
        """Test return of capital validation succeeds when equity balance is None."""
        # Arrange
        mock_fund_no_equity = FundFactory.build(current_equity_balance=None)
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 1,
            'amount': 25000.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund_no_equity) as mock_get_fund:
            # Act
            result = service.validate_return_of_capital(event_data, mock_session)

            # Assert
            assert result == {}

    ################################################################################
    # Test validate_unit_purchase method
    ################################################################################

    def test_validate_unit_purchase_success_for_nav_based_fund(self, service, mock_session):
        """Test successful unit purchase validation for NAV-based fund."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.NAV_BASED,
            'fund_id': 1,
            'units': 100.0
        }
        
        # Act
        result = service.validate_unit_purchase(event_data, mock_session)

        # Assert
        assert result == {}

    def test_validate_unit_purchase_fails_for_cost_based_fund(self, service, mock_session):
        """Test unit purchase validation fails for cost-based fund."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 1,
            'units': 100.0
        }
        
        # Act
        result = service.validate_unit_purchase(event_data, mock_session)

        # Assert
        assert 'fund_type' in result
        assert "Unit purchases are only applicable for NAV-based funds" in result['fund_type']

    ################################################################################
    # Test validate_unit_sale method
    ################################################################################

    def test_validate_unit_sale_success_for_nav_based_fund(self, service, mock_session, mock_fund):
        """Test successful unit sale validation for NAV-based fund."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.NAV_BASED,
            'fund_id': 1,
            'units': 100.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund:
            # Act
            result = service.validate_unit_sale(event_data, mock_session)

            # Assert
            assert result == {}
            mock_get_fund.assert_called_once_with(1, mock_session)

    def test_validate_unit_sale_fails_for_cost_based_fund(self, service, mock_session, mock_fund):
        """Test unit sale validation fails for cost-based fund."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 1,
            'units': 100.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund:
            # Act
            result = service.validate_unit_sale(event_data, mock_session)

            # Assert
            assert 'fund_type' in result
            assert "Unit sales are only applicable for NAV-based funds" in result['fund_type']

    def test_validate_unit_sale_fails_when_units_exceed_available(self, service, mock_session, mock_fund):
        """Test unit sale validation fails when trying to sell more units than available."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.NAV_BASED,
            'fund_id': 1,
            'units': 1500.0  # Exceeds current_units of 1000.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund:
            # Act
            result = service.validate_unit_sale(event_data, mock_session)

            # Assert
            assert 'units' in result
            assert "Insufficient units: trying to sell 1500.0 but only 1000.0 available" in result['units']

    def test_validate_unit_sale_raises_error_when_fund_not_found(self, service, mock_session):
        """Test unit sale validation raises error when fund not found."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.NAV_BASED,
            'fund_id': 999,
            'units': 100.0
        }
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=None) as mock_get_fund:
            # Act & Assert
            with pytest.raises(ValueError, match="Fund not found"):
                service.validate_unit_sale(event_data, mock_session)

    ################################################################################
    # Test validate_nav_update method
    ################################################################################

    def test_validate_nav_update_success_for_nav_based_fund(self, service, mock_session):
        """Test successful NAV update validation for NAV-based fund."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.NAV_BASED,
            'fund_id': 1,
            'nav_per_share': 1.25
        }
        
        # Act
        result = service.validate_nav_update(event_data, mock_session)

        # Assert
        assert result == {}

    def test_validate_nav_update_fails_for_cost_based_fund(self, service, mock_session):
        """Test NAV update validation fails for cost-based fund."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 1,
            'nav_per_share': 1.25
        }
        
        # Act
        result = service.validate_nav_update(event_data, mock_session)

        # Assert
        assert 'fund_type' in result
        assert "NAV updates are only applicable for NAV-based funds" in result['fund_type']

    ################################################################################
    # Test validate_distribution method
    ################################################################################

    def test_validate_distribution_always_succeeds(self, service, mock_session):
        """Test distribution validation always succeeds (no business rules)."""
        # Arrange
        event_data = {
            'tracking_type': FundTrackingType.COST_BASED,
            'fund_id': 1,
            'amount': 10000.0
        }
        
        # Act
        result = service.validate_distribution(event_data, mock_session)

        # Assert
        assert result == {}

    ################################################################################
    # Test validate_fund_tax_statement_deletion method
    ################################################################################

    def test_validate_fund_tax_statement_deletion_always_succeeds(self, service, mock_session):
        """Test fund tax statement deletion validation always succeeds (no business rules)."""
        # Arrange
        fund_tax_statement_id = 1
        
        # Act
        result = service.validate_fund_tax_statement_deletion(fund_tax_statement_id, mock_session)

        # Assert
        assert result == {}

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.fund_event_repository is not None
        assert service.fund_tax_statement_repository is not None
        assert service.fund_repository is not None
        assert hasattr(service, 'fund_event_repository')
        assert hasattr(service, 'fund_tax_statement_repository')
        assert hasattr(service, 'fund_repository')
