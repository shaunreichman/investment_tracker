"""
Test suite for FundPnlService - PNL calculation and update service.

This module tests the FundPnlService which handles updating fund PNL values
and tracking field changes. The service delegates actual calculations to
FundPnlCalculator and focuses on change detection and field updates.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from src.fund.services.fund_pnl_service import FundPnlService
from src.fund.models.fund import Fund
from src.fund.models.domain_event import FundFieldChange


class TestFundPnlService:
    """Test suite for FundPnlService - PNL update and change tracking service"""
    
    @pytest.fixture
    def service(self):
        """Create a FundPnlService instance for testing."""
        mock_session = Mock()
        return FundPnlService(mock_session)
    
    @pytest.fixture
    def mock_fund(self):
        """Create a mock Fund object with initial PNL values."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.pnl = Decimal('1000.00')
        fund.realized_pnl = Decimal('800.00')
        fund.unrealized_pnl = Decimal('200.00')
        fund.realized_pnl_capital_gain = Decimal('600.00')
        fund.unrealized_pnl_capital_gain = Decimal('200.00')
        fund.realized_pnl_dividend = Decimal('150.00')
        fund.realized_pnl_interest = Decimal('50.00')
        fund.realized_pnl_distribution = Decimal('200.00')
        return fund
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def mock_pnl_calculator_result(self):
        """Create mock PNL calculation results."""
        return {
            'pnl': Decimal('1200.00'),
            'realized_pnl': Decimal('900.00'),
            'unrealized_pnl': Decimal('300.00'),
            'realized_pnl_capital_gain': Decimal('700.00'),
            'unrealized_pnl_capital_gain': Decimal('300.00'),
            'realized_pnl_dividend': Decimal('150.00'),
            'realized_pnl_interest': Decimal('50.00'),
            'realized_pnl_distribution': Decimal('200.00')
        }

    # ============================================================================
    # SERVICE INITIALIZATION TESTS
    # ============================================================================
    
    def test_service_initialization(self, service):
        """Test service initialization with session."""
        assert service is not None
        assert isinstance(service, FundPnlService)
        assert hasattr(service, 'session')
        assert hasattr(service, 'logger')

    # ============================================================================
    # UPDATE FUND PNL TESTS - NO CHANGES
    # ============================================================================
    
    @patch('src.fund.calculators.fund_pnl_calculator.FundPnlCalculator')
    def test_update_fund_pnl_no_changes(self, mock_calculator_class, service, mock_fund, mock_session):
        """Test update_fund_pnl when no PNL values have changed."""
        # Arrange - Calculator returns same values as current fund values
        mock_calculator = Mock()
        mock_calculator_class.calculate_pnl.return_value = {
            'pnl': Decimal('1000.00'),
            'realized_pnl': Decimal('800.00'),
            'unrealized_pnl': Decimal('200.00'),
            'realized_pnl_capital_gain': Decimal('600.00'),
            'unrealized_pnl_capital_gain': Decimal('200.00'),
            'realized_pnl_dividend': Decimal('150.00'),
            'realized_pnl_interest': Decimal('50.00'),
            'realized_pnl_distribution': Decimal('200.00')
        }
        
        # Act
        result = service.update_fund_pnl(mock_fund, mock_session)
        
        # Assert - No changes detected, returns None
        assert result is None
        
        # Assert - Fund values remain unchanged
        assert mock_fund.pnl == Decimal('1000.00')
        assert mock_fund.realized_pnl == Decimal('800.00')
        assert mock_fund.unrealized_pnl == Decimal('200.00')
        
        # Assert - Calculator was called correctly
        mock_calculator_class.calculate_pnl.assert_called_once_with(mock_fund, mock_session)

    # ============================================================================
    # UPDATE FUND PNL TESTS - SINGLE FIELD CHANGES
    # ============================================================================
    
    @patch('src.fund.calculators.fund_pnl_calculator.FundPnlCalculator')
    def test_update_fund_pnl_single_field_change(self, mock_calculator_class, service, mock_fund, mock_session):
        """Test update_fund_pnl when only one field changes."""
        # Arrange - Only PNL changes
        mock_calculator_class.calculate_pnl.return_value = {
            'pnl': Decimal('1200.00'),  # Changed
            'realized_pnl': Decimal('800.00'),  # Unchanged
            'unrealized_pnl': Decimal('200.00'),  # Unchanged
            'realized_pnl_capital_gain': Decimal('600.00'),  # Unchanged
            'unrealized_pnl_capital_gain': Decimal('200.00'),  # Unchanged
            'realized_pnl_dividend': Decimal('150.00'),  # Unchanged
            'realized_pnl_interest': Decimal('50.00'),  # Unchanged
            'realized_pnl_distribution': Decimal('200.00')  # Unchanged
        }
        
        # Act
        result = service.update_fund_pnl(mock_fund, mock_session)
        
        # Assert - One change detected
        assert result is not None
        assert len(result) == 1
        assert isinstance(result[0], FundFieldChange)
        assert result[0].field_name == 'pnl'
        assert result[0].old_value == Decimal('1000.00')
        assert result[0].new_value == Decimal('1200.00')
        
        # Assert - Fund PNL updated
        assert mock_fund.pnl == Decimal('1200.00')

    @patch('src.fund.calculators.fund_pnl_calculator.FundPnlCalculator')
    def test_update_fund_pnl_realized_pnl_change(self, mock_calculator_class, service, mock_fund, mock_session):
        """Test update_fund_pnl when realized PNL changes."""
        # Arrange - Only realized PNL changes
        mock_calculator_class.calculate_pnl.return_value = {
            'pnl': Decimal('1000.00'),  # Unchanged
            'realized_pnl': Decimal('900.00'),  # Changed
            'unrealized_pnl': Decimal('200.00'),  # Unchanged
            'realized_pnl_capital_gain': Decimal('600.00'),  # Unchanged
            'unrealized_pnl_capital_gain': Decimal('200.00'),  # Unchanged
            'realized_pnl_dividend': Decimal('150.00'),  # Unchanged
            'realized_pnl_interest': Decimal('50.00'),  # Unchanged
            'realized_pnl_distribution': Decimal('200.00')  # Unchanged
        }
        
        # Act
        result = service.update_fund_pnl(mock_fund, mock_session)
        
        # Assert - One change detected
        assert result is not None
        assert len(result) == 1
        assert result[0].field_name == 'realized_pnl'
        assert result[0].old_value == Decimal('800.00')
        assert result[0].new_value == Decimal('900.00')
        
        # Assert - Fund realized PNL updated
        assert mock_fund.realized_pnl == Decimal('900.00')

    # ============================================================================
    # UPDATE FUND PNL TESTS - MULTIPLE FIELD CHANGES
    # ============================================================================
    
    @patch('src.fund.calculators.fund_pnl_calculator.FundPnlCalculator')
    def test_update_fund_pnl_multiple_changes(self, mock_calculator_class, service, mock_fund, mock_session):
        """Test update_fund_pnl when multiple fields change."""
        # Arrange - Multiple fields change
        mock_calculator_class.calculate_pnl.return_value = {
            'pnl': Decimal('1500.00'),  # Changed
            'realized_pnl': Decimal('1000.00'),  # Changed
            'unrealized_pnl': Decimal('500.00'),  # Changed
            'realized_pnl_capital_gain': Decimal('800.00'),  # Changed
            'unrealized_pnl_capital_gain': Decimal('500.00'),  # Changed
            'realized_pnl_dividend': Decimal('150.00'),  # Unchanged
            'realized_pnl_interest': Decimal('50.00'),  # Unchanged
            'realized_pnl_distribution': Decimal('200.00')  # Unchanged
        }
        
        # Act
        result = service.update_fund_pnl(mock_fund, mock_session)
        
        # Assert - Multiple changes detected
        assert result is not None
        assert len(result) == 5  # 5 fields changed
        
        # Assert - All changes are tracked correctly
        field_names = [change.field_name for change in result]
        assert 'pnl' in field_names
        assert 'realized_pnl' in field_names
        assert 'unrealized_pnl' in field_names
        assert 'realized_pnl_capital_gain' in field_names
        assert 'unrealized_pnl_capital_gain' in field_names
        
        # Assert - Fund values updated
        assert mock_fund.pnl == Decimal('1500.00')
        assert mock_fund.realized_pnl == Decimal('1000.00')
        assert mock_fund.unrealized_pnl == Decimal('500.00')
        assert mock_fund.realized_pnl_capital_gain == Decimal('800.00')
        assert mock_fund.unrealized_pnl_capital_gain == Decimal('500.00')

    # ============================================================================
    # UPDATE FUND PNL TESTS - ALL FIELD CHANGES
    # ============================================================================
    
    @patch('src.fund.calculators.fund_pnl_calculator.FundPnlCalculator')
    def test_update_fund_pnl_all_fields_change(self, mock_calculator_class, service, mock_fund, mock_session):
        """Test update_fund_pnl when all PNL fields change."""
        # Arrange - All fields change
        mock_calculator_class.calculate_pnl.return_value = {
            'pnl': Decimal('2000.00'),
            'realized_pnl': Decimal('1200.00'),
            'unrealized_pnl': Decimal('800.00'),
            'realized_pnl_capital_gain': Decimal('1000.00'),
            'unrealized_pnl_capital_gain': Decimal('800.00'),
            'realized_pnl_dividend': Decimal('200.00'),
            'realized_pnl_interest': Decimal('100.00'),
            'realized_pnl_distribution': Decimal('300.00')
        }
        
        # Act
        result = service.update_fund_pnl(mock_fund, mock_session)
        
        # Assert - All changes detected
        assert result is not None
        assert len(result) == 8  # All 8 fields changed
        
        # Assert - All field names are present
        field_names = [change.field_name for change in result]
        expected_fields = [
            'pnl', 'realized_pnl', 'unrealized_pnl',
            'realized_pnl_capital_gain', 'unrealized_pnl_capital_gain',
            'realized_pnl_dividend', 'realized_pnl_interest', 'realized_pnl_distribution'
        ]
        for field in expected_fields:
            assert field in field_names
        
        # Assert - All fund values updated
        assert mock_fund.pnl == Decimal('2000.00')
        assert mock_fund.realized_pnl == Decimal('1200.00')
        assert mock_fund.unrealized_pnl == Decimal('800.00')
        assert mock_fund.realized_pnl_capital_gain == Decimal('1000.00')
        assert mock_fund.unrealized_pnl_capital_gain == Decimal('800.00')
        assert mock_fund.realized_pnl_dividend == Decimal('200.00')
        assert mock_fund.realized_pnl_interest == Decimal('100.00')
        assert mock_fund.realized_pnl_distribution == Decimal('300.00')

    # ============================================================================
    # UPDATE FUND PNL TESTS - EDGE CASES
    # ============================================================================
    
    @patch('src.fund.calculators.fund_pnl_calculator.FundPnlCalculator')
    def test_update_fund_pnl_zero_values(self, mock_calculator_class, service, mock_fund, mock_session):
        """Test update_fund_pnl with zero values."""
        # Arrange - All values become zero
        mock_calculator_class.calculate_pnl.return_value = {
            'pnl': Decimal('0.00'),
            'realized_pnl': Decimal('0.00'),
            'unrealized_pnl': Decimal('0.00'),
            'realized_pnl_capital_gain': Decimal('0.00'),
            'unrealized_pnl_capital_gain': Decimal('0.00'),
            'realized_pnl_dividend': Decimal('0.00'),
            'realized_pnl_interest': Decimal('0.00'),
            'realized_pnl_distribution': Decimal('0.00')
        }
        
        # Act
        result = service.update_fund_pnl(mock_fund, mock_session)
        
        # Assert - All changes detected
        assert result is not None
        assert len(result) == 8
        
        # Assert - All fund values updated to zero
        assert mock_fund.pnl == Decimal('0.00')
        assert mock_fund.realized_pnl == Decimal('0.00')
        assert mock_fund.unrealized_pnl == Decimal('0.00')

    @patch('src.fund.calculators.fund_pnl_calculator.FundPnlCalculator')
    def test_update_fund_pnl_negative_values(self, mock_calculator_class, service, mock_fund, mock_session):
        """Test update_fund_pnl with negative values."""
        # Arrange - Negative PNL values
        mock_calculator_class.calculate_pnl.return_value = {
            'pnl': Decimal('-500.00'),
            'realized_pnl': Decimal('-200.00'),
            'unrealized_pnl': Decimal('-300.00'),
            'realized_pnl_capital_gain': Decimal('-200.00'),
            'unrealized_pnl_capital_gain': Decimal('-300.00'),
            'realized_pnl_dividend': Decimal('0.00'),
            'realized_pnl_interest': Decimal('0.00'),
            'realized_pnl_distribution': Decimal('0.00')
        }
        
        # Act
        result = service.update_fund_pnl(mock_fund, mock_session)
        
        # Assert - Changes detected
        assert result is not None
        assert len(result) == 8
        
        # Assert - Negative values handled correctly
        assert mock_fund.pnl == Decimal('-500.00')
        assert mock_fund.realized_pnl == Decimal('-200.00')
        assert mock_fund.unrealized_pnl == Decimal('-300.00')

    # ============================================================================
    # UPDATE FUND PNL TESTS - CALCULATOR INTEGRATION
    # ============================================================================
    
    @patch('src.fund.calculators.fund_pnl_calculator.FundPnlCalculator')
    def test_update_fund_pnl_calculator_called_correctly(self, mock_calculator_class, service, mock_fund, mock_session):
        """Test that FundPnlCalculator is called with correct parameters."""
        # Arrange
        mock_calculator_class.calculate_pnl.return_value = {
            'pnl': Decimal('1000.00'),
            'realized_pnl': Decimal('800.00'),
            'unrealized_pnl': Decimal('200.00'),
            'realized_pnl_capital_gain': Decimal('600.00'),
            'unrealized_pnl_capital_gain': Decimal('200.00'),
            'realized_pnl_dividend': Decimal('150.00'),
            'realized_pnl_interest': Decimal('50.00'),
            'realized_pnl_distribution': Decimal('200.00')
        }
        
        # Act
        service.update_fund_pnl(mock_fund, mock_session)
        
        # Assert - Calculator called with correct parameters
        mock_calculator_class.calculate_pnl.assert_called_once_with(mock_fund, mock_session)

    # ============================================================================
    # UPDATE FUND PNL TESTS - FIELD CHANGE OBJECTS
    # ============================================================================
    
    @patch('src.fund.calculators.fund_pnl_calculator.FundPnlCalculator')
    def test_update_fund_pnl_field_change_objects(self, mock_calculator_class, service, mock_fund, mock_session):
        """Test that FundFieldChange objects are created correctly."""
        # Arrange - Single field change
        mock_calculator_class.calculate_pnl.return_value = {
            'pnl': Decimal('1200.00'),  # Changed
            'realized_pnl': Decimal('800.00'),  # Unchanged
            'unrealized_pnl': Decimal('200.00'),  # Unchanged
            'realized_pnl_capital_gain': Decimal('600.00'),  # Unchanged
            'unrealized_pnl_capital_gain': Decimal('200.00'),  # Unchanged
            'realized_pnl_dividend': Decimal('150.00'),  # Unchanged
            'realized_pnl_interest': Decimal('50.00'),  # Unchanged
            'realized_pnl_distribution': Decimal('200.00')  # Unchanged
        }
        
        # Act
        result = service.update_fund_pnl(mock_fund, mock_session)
        
        # Assert - FieldChange object created correctly
        assert result is not None
        assert len(result) == 1
        
        field_change = result[0]
        assert isinstance(field_change, FundFieldChange)
        assert field_change.field_name == 'pnl'
        assert field_change.old_value == Decimal('1000.00')
        assert field_change.new_value == Decimal('1200.00')
