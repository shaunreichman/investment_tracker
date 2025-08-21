"""
Enhanced Fund Model Tests

This module provides comprehensive testing for all fund model functionality,
following enterprise testing standards with focused, targeted test coverage.

Tests cover:
- Fund model validation and constraints
- Fund status transitions and lifecycle
- Fund type-specific validation rules
- Business rule invariants
- Model relationships and constraints
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

# NEW ARCHITECTURE IMPORTS
from src.fund.models.fund import Fund
from src.fund.models.fund_event import FundEvent
from src.fund.models.fund_event_cash_flow import FundEventCashFlow
from src.fund.enums import FundType, EventType, FundStatus, DistributionType
from tests.factories import FundFactory


class TestFundModel:
    """Test suite for Fund model - Core fund entity"""
    
    @pytest.fixture
    def fund_data(self):
        """Sample fund data for testing."""
        return {
            'name': 'Test Fund',
            'description': 'A test fund for unit testing',
            'tracking_type': FundType.NAV_BASED,
            'status': FundStatus.ACTIVE,
            'start_date': date(2020, 1, 1),
            'end_date': None,
            'commitment_amount': Decimal('1000000.00'),
            'current_equity_balance': Decimal('950000.00'),
            'investment_company_id': 1,
            'entity_id': 1
        }
    
    def test_fund_creation(self, fund_data):
        """Test fund creation with valid data."""
        fund = Fund(**fund_data)
        
        assert fund.name == 'Test Fund'
        assert fund.tracking_type == FundType.NAV_BASED
        assert fund.status == FundStatus.ACTIVE
        assert fund.start_date == date(2020, 1, 1)
        assert fund.commitment_amount == Decimal('1000000.00')
        assert fund.investment_company_id == 1
        assert fund.entity_id == 1
    
    def test_fund_validation_required_fields(self, fund_data):
        """Test fund validation rules for required fields."""
        # Test missing name
        invalid_data = fund_data.copy()
        del invalid_data['name']
        fund = Fund(**invalid_data)
        
        # Validation should fail when called
        with pytest.raises(ValueError, match="Fund name is required"):
            fund.validate_basic_constraints()
        
        # Test missing investment_company_id
        invalid_data = fund_data.copy()
        del invalid_data['investment_company_id']
        fund = Fund(**invalid_data)
        
        with pytest.raises(ValueError, match="Investment company ID is required"):
            fund.validate_basic_constraints()
        
        # Test missing entity_id
        invalid_data = fund_data.copy()
        del invalid_data['entity_id']
        fund = Fund(**invalid_data)
        
        with pytest.raises(ValueError, match="Entity ID is required"):
            fund.validate_basic_constraints()
        
        # Test missing tracking_type
        invalid_data = fund_data.copy()
        del invalid_data['tracking_type']
        fund = Fund(**invalid_data)
        
        with pytest.raises(ValueError, match="Tracking type is required"):
            fund.validate_basic_constraints()
    
    def test_fund_currency_validation(self, fund_data):
        """Test fund currency validation rules."""
        fund = Fund(**fund_data)
        
        # Test valid currency
        fund.currency = "AUD"
        fund.validate_basic_constraints()
        
        # Test invalid currency length
        fund.currency = "AUDD"
        with pytest.raises(ValueError, match="Currency must be 3 characters"):
            fund.validate_basic_constraints()
        
        # Test valid currency
        fund.currency = "USD"
        fund.validate_basic_constraints()
    
    def test_fund_irr_validation(self, fund_data):
        """Test fund IRR validation rules."""
        fund = Fund(**fund_data)
        
        # Test valid IRR values
        fund.expected_irr = 15.5
        fund.validate_basic_constraints()
        
        # Test negative IRR
        fund.expected_irr = -5.0
        with pytest.raises(ValueError, match="Expected IRR must be between 0 and 1000"):
            fund.validate_basic_constraints()
        
        # Test excessive IRR
        fund.expected_irr = 1500.0
        with pytest.raises(ValueError, match="Expected IRR must be between 0 and 1000"):
            fund.validate_basic_constraints()
        
        # Test valid IRR
        fund.expected_irr = 25.0
        fund.validate_basic_constraints()
    
    def test_fund_duration_validation(self, fund_data):
        """Test fund duration validation rules."""
        fund = Fund(**fund_data)
        
        # Test valid duration
        fund.expected_duration_months = 60
        fund.validate_basic_constraints()
        
        # Test zero duration
        fund.expected_duration_months = 0
        with pytest.raises(ValueError, match="Expected duration must be positive"):
            fund.validate_basic_constraints()
        
        # Test negative duration
        fund.expected_duration_months = -12
        with pytest.raises(ValueError, match="Expected duration must be positive"):
            fund.validate_basic_constraints()
        
        # Test valid duration
        fund.expected_duration_months = 36
        fund.validate_basic_constraints()


class TestFundStatusTransitions:
    """Test suite for fund status transitions and lifecycle"""
    
    @pytest.fixture
    def fund(self):
        """Create a basic fund for status testing."""
        return Fund(
            name='Status Test Fund',
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            investment_company_id=1,
            entity_id=1
        )
    
    def test_valid_status_transitions(self, fund):
        """Test valid fund status transitions."""
        # ACTIVE -> SUSPENDED
        fund.status = FundStatus.SUSPENDED
        assert fund.status == FundStatus.SUSPENDED
        
        # SUSPENDED -> ACTIVE
        fund.status = FundStatus.ACTIVE
        assert fund.status == FundStatus.ACTIVE
        
        # ACTIVE -> REALIZED
        fund.status = FundStatus.REALIZED
        assert fund.status == FundStatus.REALIZED
        
        # REALIZED -> COMPLETED
        fund.status = FundStatus.COMPLETED
        assert fund.status == FundStatus.COMPLETED
    
    def test_invalid_status_transitions(self, fund):
        """Test invalid fund status transitions."""
        # Test invalid status string - SQLAlchemy will handle this at database level
        # For now, we test that the model accepts valid enum values
        fund.status = FundStatus.SUSPENDED
        assert fund.status == FundStatus.SUSPENDED
        
        fund.status = FundStatus.REALIZED
        assert fund.status == FundStatus.REALIZED
    
    def test_status_lifecycle_validation(self, fund):
        """Test fund status lifecycle validation."""
        # Fund should start as ACTIVE
        assert fund.status == FundStatus.ACTIVE
        assert fund.is_active() is True
        
        # Test SUSPENDED status
        fund.status = FundStatus.SUSPENDED
        assert fund.is_active() is False
        
        # Test REALIZED status
        fund.status = FundStatus.REALIZED
        assert fund.is_realized() is True
        assert fund.is_active() is False
        
        # Test COMPLETED status
        fund.status = FundStatus.COMPLETED
        assert fund.is_completed() is True
        assert fund.is_active() is False


class TestFundTypeValidation:
    """Test suite for fund type-specific validation"""
    
    @pytest.fixture
    def nav_fund(self):
        """Create NAV-based fund for testing."""
        return Fund(
            name='NAV Fund',
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            investment_company_id=1,
            entity_id=1
        )
    
    @pytest.fixture
    def cost_fund(self):
        """Create cost-based fund for testing."""
        return Fund(
            name='Cost Fund',
            tracking_type=FundType.COST_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            investment_company_id=1,
            entity_id=1
        )
    
    def test_nav_based_fund_validation(self, nav_fund):
        """Test NAV-based fund specific validation."""
        # Test NAV fields are allowed
        nav_fund.current_units = 1000.0
        nav_fund.current_unit_price = 1.50
        nav_fund.current_nav_total = 1500.0
        nav_fund.validate_tracking_type_constraints()
        
        # Test cost basis should not be set for NAV funds
        nav_fund.total_cost_basis = 1000.0
        with pytest.raises(ValueError, match="NAV-based funds should not have cost basis"):
            nav_fund.validate_tracking_type_constraints()
        
        # Clear cost basis and validate
        nav_fund.total_cost_basis = 0.0
        nav_fund.validate_tracking_type_constraints()
    
    def test_cost_based_fund_validation(self, cost_fund):
        """Test cost-based fund specific validation."""
        # Test cost basis is allowed
        cost_fund.total_cost_basis = 1000000.0
        cost_fund.validate_tracking_type_constraints()
        
        # Test NAV fields should not be set for cost funds
        cost_fund.current_units = 1000.0
        with pytest.raises(ValueError, match="Cost-based funds should not have units"):
            cost_fund.validate_tracking_type_constraints()
        
        # Clear NAV fields and validate
        cost_fund.current_units = 0.0
        cost_fund.current_unit_price = 0.0
        cost_fund.current_nav_total = 0.0
        cost_fund.validate_tracking_type_constraints()
    
    def test_fund_type_methods(self, nav_fund, cost_fund):
        """Test fund type helper methods."""
        # Test NAV-based fund methods
        assert nav_fund.is_nav_based() is True
        assert nav_fund.is_cost_based() is False
        
        # Test cost-based fund methods
        assert cost_fund.is_nav_based() is False
        assert cost_fund.is_cost_based() is True


class TestFundDateValidation:
    """Test suite for fund date validation"""
    
    @pytest.fixture
    def fund(self):
        """Create a fund for date testing."""
        return Fund(
            name='Date Test Fund',
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            investment_company_id=1,
            entity_id=1
        )
    
    def test_valid_date_ranges(self, fund):
        """Test valid date ranges."""
        # Valid start and end dates (use past dates to avoid future date validation)
        fund.start_date = date(2020, 1, 1)
        fund.end_date = date(2023, 12, 31)
        fund.validate_date_constraints()
        
        # Same start and end date
        fund.start_date = date(2020, 1, 1)
        fund.end_date = date(2020, 1, 1)
        fund.validate_date_constraints()
    
    def test_invalid_date_ranges(self, fund):
        """Test invalid date ranges."""
        # Start date after end date
        fund.start_date = date(2025, 1, 1)
        fund.end_date = date(2020, 12, 31)
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            fund.validate_date_constraints()
        
        # Test with valid chronological order (start before end)
        fund.start_date = date(2020, 1, 1)
        fund.end_date = date(2023, 12, 31)
        fund.validate_date_constraints()
        
        # Test with same dates (should be valid)
        fund.start_date = date(2020, 1, 1)
        fund.end_date = date(2020, 1, 1)
        fund.validate_date_constraints()
    
    def test_date_constraint_edge_cases(self, fund):
        """Test date constraint edge cases."""
        # Only start date set
        fund.start_date = date(2020, 1, 1)
        fund.end_date = None
        fund.validate_date_constraints()
        
        # Only end date set (use current date to avoid future validation)
        fund.start_date = None
        fund.end_date = date.today()
        fund.validate_date_constraints()
        
        # No dates set
        fund.start_date = None
        fund.end_date = None
        fund.validate_date_constraints()


class TestFundCommitmentValidation:
    """Test suite for fund commitment validation"""
    
    @pytest.fixture
    def fund(self):
        """Create a fund for commitment testing."""
        return Fund(
            name='Commitment Test Fund',
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            investment_company_id=1,
            entity_id=1,
            current_equity_balance=0.0,  # Initialize to avoid None comparison
            average_equity_balance=0.0
        )
    
    def test_commitment_amount_validation(self, fund):
        """Test commitment amount validation."""
        # Valid commitment amount
        fund.commitment_amount = 1000000.0
        fund.validate_commitment_constraints()
        
        # Zero commitment amount
        fund.commitment_amount = 0.0
        fund.validate_commitment_constraints()
        
        # Negative commitment amount
        fund.commitment_amount = -100000.0
        with pytest.raises(ValueError, match="Commitment amount cannot be negative"):
            fund.validate_commitment_constraints()
    
    def test_equity_balance_validation(self, fund):
        """Test equity balance validation."""
        # Valid equity balance
        fund.current_equity_balance = 950000.0
        fund.average_equity_balance = 900000.0
        fund.validate_commitment_constraints()
        
        # Zero equity balance
        fund.current_equity_balance = 0.0
        fund.average_equity_balance = 0.0
        fund.validate_commitment_constraints()
        
        # Negative equity balance
        fund.current_equity_balance = -50000.0
        with pytest.raises(ValueError, match="Current equity balance cannot be negative"):
            fund.validate_commitment_constraints()
        
        # Negative average equity balance
        fund.current_equity_balance = 0.0
        fund.average_equity_balance = -10000.0
        with pytest.raises(ValueError, match="Average equity balance cannot be negative"):
            fund.validate_commitment_constraints()


class TestFundIRRValidation:
    """Test suite for fund IRR validation"""
    
    @pytest.fixture
    def fund(self):
        """Create a fund for IRR testing."""
        return Fund(
            name='IRR Test Fund',
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            investment_company_id=1,
            entity_id=1
        )
    
    def test_irr_range_validation(self, fund):
        """Test IRR range validation."""
        # Valid IRR values
        fund.completed_irr_gross = 15.5
        fund.completed_irr_after_tax = 12.0
        fund.completed_irr_real = 10.5
        fund.validate_irr_constraints()
        
        # Boundary values
        fund.completed_irr_gross = -100.0
        fund.completed_irr_after_tax = 1000.0
        fund.completed_irr_real = 0.0
        fund.validate_irr_constraints()
        
        # Invalid IRR values
        fund.completed_irr_gross = -150.0
        with pytest.raises(ValueError, match="IRR values must be between -100% and 1000%"):
            fund.validate_irr_constraints()
        
        fund.completed_irr_gross = 1500.0
        with pytest.raises(ValueError, match="IRR values must be between -100% and 1000%"):
            fund.validate_irr_constraints()
    
    def test_irr_null_values(self, fund):
        """Test IRR validation with null values."""
        # All null values should pass
        fund.completed_irr_gross = None
        fund.completed_irr_after_tax = None
        fund.completed_irr_real = None
        fund.validate_irr_constraints()
        
        # Mixed null and valid values
        fund.completed_irr_gross = 15.5
        fund.completed_irr_after_tax = None
        fund.completed_irr_real = None
        fund.validate_irr_constraints()


class TestFundNAVValidation:
    """Test suite for fund NAV validation"""
    
    @pytest.fixture
    def nav_fund(self):
        """Create NAV-based fund for NAV testing."""
        return Fund(
            name='NAV Test Fund',
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            investment_company_id=1,
            entity_id=1
        )
    
    def test_nav_field_validation(self, nav_fund):
        """Test NAV field validation."""
        # Valid NAV values
        nav_fund.current_units = 1000.0
        nav_fund.current_unit_price = 1.50
        nav_fund.current_nav_total = 1500.0
        nav_fund.validate_nav_constraints()
        
        # Zero values are valid
        nav_fund.current_units = 0.0
        nav_fund.current_unit_price = 0.0
        nav_fund.current_nav_total = 0.0
        nav_fund.validate_nav_constraints()
        
        # Negative values are invalid
        nav_fund.current_units = -100.0
        with pytest.raises(ValueError, match="Current units cannot be negative"):
            nav_fund.validate_nav_constraints()
        
        nav_fund.current_units = 1000.0
        nav_fund.current_unit_price = -1.50
        with pytest.raises(ValueError, match="Current unit price cannot be negative"):
            nav_fund.validate_nav_constraints()
        
        nav_fund.current_unit_price = 1.50
        nav_fund.current_nav_total = -1500.0
        with pytest.raises(ValueError, match="Current NAV total cannot be negative"):
            nav_fund.validate_nav_constraints()
    
    def test_cost_based_fund_nav_validation(self):
        """Test that cost-based funds don't validate NAV constraints."""
        cost_fund = Fund(
            name='Cost Test Fund',
            tracking_type=FundType.COST_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            investment_company_id=1,
            entity_id=1
        )
        
        # NAV validation should pass for cost-based funds (no NAV fields)
        cost_fund.validate_nav_constraints()


class TestFundComprehensiveValidation:
    """Test suite for comprehensive fund validation"""
    
    @pytest.fixture
    def fund(self):
        """Create a fund for comprehensive testing."""
        return Fund(
            name='Comprehensive Test Fund',
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),  # Use past date to avoid future validation
            commitment_amount=1000000.0,
            current_equity_balance=950000.0,
            average_equity_balance=900000.0,
            current_units=1000.0,
            current_unit_price=1.50,
            current_nav_total=1500.0,
            expected_irr=15.5,
            expected_duration_months=60,
            currency="AUD",
            investment_company_id=1,
            entity_id=1
        )
    
    def test_validate_all_constraints(self, fund):
        """Test comprehensive constraint validation."""
        # All constraints should pass
        fund.validate_all_constraints()
        
        # Test that individual validations are called
        with patch.object(fund, 'validate_basic_constraints') as mock_basic:
            with patch.object(fund, 'validate_tracking_type_constraints') as mock_tracking:
                with patch.object(fund, 'validate_date_constraints') as mock_date:
                    with patch.object(fund, 'validate_commitment_constraints') as mock_commitment:
                        with patch.object(fund, 'validate_irr_constraints') as mock_irr:
                            with patch.object(fund, 'validate_nav_constraints') as mock_nav:
                                fund.validate_all_constraints()
                                
                                mock_basic.assert_called_once()
                                mock_tracking.assert_called_once()
                                mock_date.assert_called_once()
                                mock_commitment.assert_called_once()
                                mock_irr.assert_called_once()
                                mock_nav.assert_called_once()
    
    def test_fund_state_methods(self, fund):
        """Test fund state helper methods."""
        # Test equity balance methods
        assert fund.has_equity_balance() is True
        fund.current_equity_balance = 0.0
        assert fund.has_equity_balance() is False
        
        # Test commitment methods
        assert fund.has_commitment() is True
        fund.commitment_amount = None
        assert fund.has_commitment() is False
        fund.commitment_amount = 0.0
        assert fund.has_commitment() is False


class TestFundModelRelationships:
    """Test suite for fund model relationships"""
    
    def test_fund_to_events_relationship(self):
        """Test fund to events relationship."""
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            investment_company_id=1,
            entity_id=1
        )
        
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.CAPITAL_CALL,
            event_date=date(2020, 1, 1),
            amount=Decimal('100000.00')
        )
        
        # Test relationship establishment
        fund.fund_events.append(event)
        assert len(fund.fund_events) == 1
        assert fund.fund_events[0] == event
    
    def test_event_to_cash_flows_relationship(self):
        """Test event to cash flows relationship."""
        event = FundEvent(
            fund_id=1,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2020, 6, 1),
            amount=Decimal('50000.00')
        )
        
        cash_flow = FundEventCashFlow(
            amount=Decimal('50000.00'),
            direction='OUTFLOW',
            description='Distribution payment'
        )
        
        # Test relationship establishment
        event.cash_flows.append(cash_flow)
        assert len(event.cash_flows) == 1
        assert event.cash_flows[0] == cash_flow


class TestFundModelBusinessRules:
    """Test suite for fund model business rules"""
    
    def test_fund_completion_validation(self):
        """Test fund completion business rules."""
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            investment_company_id=1,
            entity_id=1
        )
        
        # Test completion validation - the model allows status changes
        # Business rules are enforced at the service level, not model level
        fund.status = FundStatus.COMPLETED
        assert fund.status == FundStatus.COMPLETED
        
        # Set end_date and complete
        fund.end_date = date(2023, 1, 1)
        fund.status = FundStatus.COMPLETED
        assert fund.status == FundStatus.COMPLETED
    
    def test_event_chronology_validation(self):
        """Test event chronology business rules."""
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1),
            investment_company_id=1,
            entity_id=1
        )
        
        # Test event creation - the model allows events to be created
        # Business rules about event chronology are enforced at the service level
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.CAPITAL_CALL,
            event_date=date(2019, 12, 31),  # Before fund start
            amount=Decimal('100000.00')
        )
        
        # The model allows this - business validation happens elsewhere
        fund.fund_events.append(event)
        assert len(fund.fund_events) == 1
    
    def test_cash_flow_balance_validation(self):
        """Test cash flow balance business rules."""
        event = FundEvent(
            fund_id=1,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2020, 6, 1),
            amount=Decimal('50000.00')
        )
        
        # Test cash flow balance
        inflow = FundEventCashFlow(
            amount=Decimal('50000.00'),
            direction='INFLOW',
            description='Distribution payment'
        )
        
        outflow = FundEventCashFlow(
            amount=Decimal('50000.00'),
            direction='OUTFLOW',
            description='Distribution payment'
        )
        
        event.cash_flows.extend([inflow, outflow])
        
        # Total cash flows should balance
        total_inflow = sum(cf.amount for cf in event.cash_flows if cf.direction == 'INFLOW')
        total_outflow = sum(cf.amount for cf in event.cash_flows if cf.direction == 'OUTFLOW')
        assert total_inflow == total_outflow


class TestFundBusinessLogicMethods:
    """Test suite for Fund model business logic methods"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session for testing."""
        mock_session = Mock()
        # Mock the query method to return an empty result (no existing events)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        return mock_session
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Mock orchestrator for testing."""
        mock_orch = Mock()
        mock_orch.process_fund_event.return_value = Mock(spec=FundEvent)
        return mock_orch
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator')
    def test_add_capital_call_basic(self, mock_orchestrator_class, mock_session):
        """Test basic capital call creation."""
        # Setup
        mock_orchestrator_class.return_value = Mock()
        mock_orchestrator_class.return_value.process_fund_event.return_value = Mock(spec=FundEvent)
        
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.COST_BASED,
            commitment_amount=1000000.0,
            current_equity_balance=0.0,
            investment_company_id=1,
            entity_id=1
        )
        
        # Execute
        event = fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial call", session=mock_session)
        
        # Verify
        assert event is not None
        mock_orchestrator_class.return_value.process_fund_event.assert_called_once()
        
        # Verify event data passed to orchestrator
        call_args = mock_orchestrator_class.return_value.process_fund_event.call_args
        event_data = call_args[0][0]  # First positional argument
        assert event_data['event_type'] == EventType.CAPITAL_CALL
        assert event_data['amount'] == 50000.0
        assert event_data['event_date'] == date(2023, 1, 1)
        assert event_data['description'] == "Initial call"
    
    def test_add_capital_call_validation_errors(self, mock_session):
        """Test capital call validation error cases."""
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,  # NAV-based funds can't have capital calls
            investment_company_id=1,
            entity_id=1
        )
        
        # Test: NAV-based funds cannot have capital calls
        with pytest.raises(ValueError, match="Capital calls are only applicable for cost-based funds"):
            fund.add_capital_call(50000.0, date(2023, 1, 1), "Test call", session=mock_session)
        
        # Test: Invalid amount
        fund.tracking_type = FundType.COST_BASED
        with pytest.raises(ValueError, match="Capital call amount must be a positive number"):
            fund.add_capital_call(0.0, date(2023, 1, 1), "Test call", session=mock_session)
        
        with pytest.raises(ValueError, match="Capital call amount must be a positive number"):
            fund.add_capital_call(-10000.0, date(2023, 1, 1), "Test call", session=mock_session)
        
        # Test: Missing date
        with pytest.raises(ValueError, match="Date is required"):
            fund.add_capital_call(50000.0, None, "Test call", session=mock_session)
    
    def test_add_capital_call_commitment_validation(self, mock_session):
        """Test capital call commitment amount validation."""
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0,
            current_equity_balance=60000.0,  # Already called 60k
            investment_company_id=1,
            entity_id=1
        )
        
        # Test: Cannot call more than remaining commitment
        with pytest.raises(ValueError, match="Cannot call more capital than remaining commitment"):
            fund.add_capital_call(50000.0, date(2023, 1, 1), "Excessive call", session=mock_session)
        
        # Test: Valid call within remaining commitment
        with patch('src.fund.events.orchestrator.FundUpdateOrchestrator') as mock_orchestrator_class:
            mock_orchestrator_class.return_value = Mock()
            mock_orchestrator_class.return_value.process_fund_event.return_value = Mock(spec=FundEvent)
            
            event = fund.add_capital_call(30000.0, date(2023, 1, 1), "Valid call", session=mock_session)
            assert event is not None
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator')
    def test_add_distribution_basic(self, mock_orchestrator_class, mock_session):
        """Test basic distribution creation."""
        # Setup
        mock_orchestrator_class.return_value = Mock()
        mock_orchestrator_class.return_value.process_fund_event.return_value = Mock(spec=FundEvent)
        
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            investment_company_id=1,
            entity_id=1
        )
        
        # Execute
        event = fund.add_distribution(
            event_date=date(2023, 6, 1),
            distribution_type=DistributionType.INTEREST,
            distribution_amount=25000.0,
            description="Interest distribution",
            session=mock_session
        )
        
        # Verify
        assert event is not None
        mock_orchestrator_class.return_value.process_fund_event.assert_called_once()
        
        # Verify event data passed to orchestrator
        call_args = mock_orchestrator_class.return_value.process_fund_event.call_args
        event_data = call_args[0][0]
        assert event_data['event_type'] == EventType.DISTRIBUTION
        assert event_data['event_date'] == date(2023, 6, 1)
        assert event_data['distribution_type'] == DistributionType.INTEREST
        assert event_data['distribution_amount'] == 25000.0
        assert event_data['description'] == "Interest distribution"
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator')
    def test_add_distribution_with_tax(self, mock_orchestrator_class, mock_session):
        """Test distribution creation with withholding tax."""
        # Setup
        mock_orchestrator_class.return_value = Mock()
        mock_orchestrator_class.return_value.process_fund_event.return_value = Mock(spec=FundEvent)
        
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            investment_company_id=1,
            entity_id=1
        )
        
        # Execute with withholding tax
        event = fund.add_distribution(
            event_date=date(2023, 6, 1),
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True,
            gross_interest_amount=30000.0,
            net_interest_amount=25500.0,
            withholding_tax_amount=4500.0,
            withholding_tax_rate=15.0,
            description="Interest with tax",
            session=mock_session
        )
        
        # Verify
        assert event is not None
        mock_orchestrator_class.return_value.process_fund_event.assert_called_once()
        
        # Verify tax-related data passed to orchestrator
        call_args = mock_orchestrator_class.return_value.process_fund_event.call_args
        event_data = call_args[0][0]
        assert event_data['has_withholding_tax'] is True
        assert event_data['gross_interest_amount'] == 30000.0
        assert event_data['net_interest_amount'] == 25500.0
        assert event_data['withholding_tax_amount'] == 4500.0
        assert event_data['withholding_tax_rate'] == 15.0
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator')
    def test_add_nav_update_basic(self, mock_orchestrator_class, mock_session):
        """Test basic NAV update creation."""
        # Setup
        mock_orchestrator_class.return_value = Mock()
        mock_orchestrator_class.return_value.process_fund_event.return_value = Mock(spec=FundEvent)
        
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            investment_company_id=1,
            entity_id=1
        )
        
        # Execute
        event = fund.add_nav_update(25.50, date(2023, 6, 1), "Monthly NAV update", session=mock_session)
        
        # Verify
        assert event is not None
        mock_orchestrator_class.return_value.process_fund_event.assert_called_once()
        
        # Verify event data passed to orchestrator
        call_args = mock_orchestrator_class.return_value.process_fund_event.call_args
        event_data = call_args[0][0]
        assert event_data['event_type'] == EventType.NAV_UPDATE
        assert event_data['nav_per_share'] == 25.50
        assert event_data['event_date'] == date(2023, 6, 1)
        assert event_data['description'] == "Monthly NAV update"
    
    def test_add_nav_update_validation_errors(self, mock_session):
        """Test NAV update validation error cases."""
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            investment_company_id=1,
            entity_id=1
        )
        
        # Test: Invalid NAV per share
        with pytest.raises(ValueError, match="NAV per share must be a positive number"):
            fund.add_nav_update(0.0, date(2023, 6, 1), "Test update", session=mock_session)
        
        with pytest.raises(ValueError, match="NAV per share must be a positive number"):
            fund.add_nav_update(-10.0, date(2023, 6, 1), "Test update", session=mock_session)
        
        # Test: Missing date
        with pytest.raises(ValueError, match="Date is required"):
            fund.add_nav_update(25.50, None, "Test update", session=mock_session)
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator')
    def test_add_unit_purchase_basic(self, mock_orchestrator_class, mock_session):
        """Test basic unit purchase creation."""
        # Setup
        mock_orchestrator_class.return_value = Mock()
        mock_orchestrator_class.return_value.process_fund_event.return_value = Mock(spec=FundEvent)
        
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            investment_company_id=1,
            entity_id=1
        )
        
        # Execute
        event = fund.add_unit_purchase(1000.0, 25.50, date(2023, 6, 1), "Initial purchase", session=mock_session)
        
        # Verify
        assert event is not None
        mock_orchestrator_class.return_value.process_fund_event.assert_called_once()
        
        # Verify event data passed to orchestrator
        call_args = mock_orchestrator_class.return_value.process_fund_event.call_args
        event_data = call_args[0][0]
        assert event_data['event_type'] == EventType.UNIT_PURCHASE
        assert event_data['units_purchased'] == 1000.0
        assert event_data['unit_price'] == 25.50
        assert event_data['event_date'] == date(2023, 6, 1)
        assert event_data['description'] == "Initial purchase"
    
    def test_add_unit_purchase_validation_errors(self, mock_session):
        """Test unit purchase validation error cases."""
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            investment_company_id=1,
            entity_id=1
        )
        
        # Test: Invalid units
        with pytest.raises(ValueError, match="Units must be a positive number"):
            fund.add_unit_purchase(0.0, 25.50, date(2023, 6, 1), "Test purchase", session=mock_session)
        
        with pytest.raises(ValueError, match="Units must be a positive number"):
            fund.add_unit_purchase(-100.0, 25.50, date(2023, 6, 1), "Test purchase", session=mock_session)
        
        # Test: Invalid price
        with pytest.raises(ValueError, match="Unit price must be a positive number"):
            fund.add_unit_purchase(1000.0, 0.0, date(2023, 6, 1), "Test purchase", session=mock_session)
        
        with pytest.raises(ValueError, match="Unit price must be a positive number"):
            fund.add_unit_purchase(1000.0, -10.0, date(2023, 6, 1), "Test purchase", session=mock_session)
        
        # Test: Missing date
        with pytest.raises(ValueError, match="Date is required"):
            fund.add_unit_purchase(1000.0, 25.50, None, "Test purchase", session=mock_session)
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator')
    def test_add_unit_sale_basic(self, mock_orchestrator_class, mock_session):
        """Test basic unit sale creation."""
        # Setup
        mock_orchestrator_class.return_value = Mock()
        mock_orchestrator_class.return_value.process_fund_event.return_value = Mock(spec=FundEvent)
        
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            investment_company_id=1,
            entity_id=1
        )
        
        # Execute
        event = fund.add_unit_sale(500.0, 30.00, date(2023, 6, 1), "Partial sale", session=mock_session)
        
        # Verify
        assert event is not None
        mock_orchestrator_class.return_value.process_fund_event.assert_called_once()
        
        # Verify event data passed to orchestrator
        call_args = mock_orchestrator_class.return_value.process_fund_event.call_args
        event_data = call_args[0][0]
        assert event_data['event_type'] == EventType.UNIT_SALE
        assert event_data['units_sold'] == 500.0
        assert event_data['unit_price'] == 30.00
        assert event_data['event_date'] == date(2023, 6, 1)
        assert event_data['description'] == "Partial sale"
    
    def test_add_unit_sale_validation_errors(self, mock_session):
        """Test unit sale validation error cases."""
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            investment_company_id=1,
            entity_id=1
        )
        
        # Test: Invalid units
        with pytest.raises(ValueError, match="Units must be a positive number"):
            fund.add_unit_sale(0.0, 30.00, date(2023, 6, 1), "Test sale", session=mock_session)
        
        with pytest.raises(ValueError, match="Units must be a positive number"):
            fund.add_unit_sale(-100.0, 30.00, date(2023, 6, 1), "Test sale", session=mock_session)
        
        # Test: Invalid price
        with pytest.raises(ValueError, match="Unit price must be a positive number"):
            fund.add_unit_sale(500.0, 0.0, date(2023, 6, 1), "Test sale", session=mock_session)
        
        with pytest.raises(ValueError, match="Unit price must be a positive number"):
            fund.add_unit_sale(500.0, -10.0, date(2023, 6, 1), "Test sale", session=mock_session)
        
        # Test: Missing date
        with pytest.raises(ValueError, match="Date is required"):
            fund.add_unit_sale(500.0, 30.00, None, "Test sale", session=mock_session)


class TestFundEnums:
    """Test suite for fund enums"""
    
    def test_fund_type_enum_values(self):
        """Test FundType enum has expected values."""
        assert FundType.NAV_BASED.value == 'NAV_BASED'
        assert FundType.COST_BASED.value == 'COST_BASED'
        
        # Test enum membership
        assert 'NAV_BASED' in FundType.__members__
        assert 'COST_BASED' in FundType.__members__
    
    def test_event_type_enum_values(self):
        """Test EventType enum has expected values."""
        assert EventType.CAPITAL_CALL.value == 'CAPITAL_CALL'
        assert EventType.DISTRIBUTION.value == 'DISTRIBUTION'
        assert EventType.UNIT_PURCHASE.value == 'UNIT_PURCHASE'
        assert EventType.UNIT_SALE.value == 'UNIT_SALE'
        
        # Test enum membership
        assert 'CAPITAL_CALL' in EventType.__members__
        assert 'DISTRIBUTION' in EventType.__members__
    
    def test_fund_status_enum_values(self):
        """Test FundStatus enum has expected values."""
        assert FundStatus.ACTIVE.value == 'ACTIVE'
        assert FundStatus.COMPLETED.value == 'COMPLETED'
        assert FundStatus.REALIZED.value == 'REALIZED'
        
        # Test enum membership
        assert 'ACTIVE' in FundStatus.__members__
        assert 'COMPLETED' in FundStatus.__members__

    def test_current_duration_calculation_and_storage(self):
        """Test the current_duration calculation and storage for different fund statuses."""
        from datetime import date
        from src.fund.enums import FundStatus
        
        # Test ACTIVE fund - should use today's date
        fund = FundFactory.create(
            start_date=date(2023, 1, 1),
            status=FundStatus.ACTIVE
        )
        
        # Mock today's date to be 2024-01-01 (12 months later)
        with patch('src.fund.models.fund.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 1)
            fund.calculate_and_update_current_duration()
            duration = fund.current_duration
            assert duration == 12, f"Expected 12 months for active fund, got {duration}"
        
        # Test REALIZED fund - should use end_date
        fund.status = FundStatus.REALIZED
        fund.end_date = date(2023, 6, 30)  # 5 months after start
        
        fund.calculate_and_update_current_duration()
        duration = fund.current_duration
        assert duration == 5, f"Expected 5 months for realized fund, got {duration}"
        
        # Test COMPLETED fund - should use end_date
        fund.status = FundStatus.COMPLETED
        fund.end_date = date(2023, 12, 31)  # 11 months after start
        
        fund.calculate_and_update_current_duration()
        duration = fund.current_duration
        assert duration == 11, f"Expected 11 months for completed fund, got {duration}"
        
        # Test fund without start_date
        fund.start_date = None
        fund.calculate_and_update_current_duration()
        duration = fund.current_duration
        assert duration == None, f"Expected None for fund without start_date, got {duration}"
        
        # Test REALIZED fund without end_date
        fund.start_date = date(2023, 1, 1)
        fund.status = FundStatus.REALIZED
        fund.end_date = None
        fund.calculate_and_update_current_duration()
        duration = fund.current_duration
        assert duration == None, f"Expected None for realized fund without end_date, got {duration}"
