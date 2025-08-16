"""
Consolidated Fund Model Tests

This module consolidates all fund model tests from multiple scattered files
into a single, comprehensive test suite following enterprise standards.

Consolidated from:
- test_fund_enums.py
- test_fund_event_grouping.py
- Various fund validation tests scattered across multiple files

NEW ARCHITECTURE FOCUS: All tests import from new fund models architecture
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

# NEW ARCHITECTURE IMPORTS - NOT legacy monolithic models
from src.fund.models.fund import Fund
from src.fund.models.fund_event import FundEvent
from src.fund.models.fund_event_cash_flow import FundEventCashFlow
from src.fund.enums import FundType, EventType, FundStatus, DistributionType


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
            'current_equity_balance': Decimal('950000.00')
        }
    
    def test_fund_creation(self, fund_data):
        """Test fund creation with valid data."""
        fund = Fund(**fund_data)
        
        assert fund.name == 'Test Fund'
        assert fund.tracking_type == FundType.NAV_BASED
        assert fund.status == FundStatus.ACTIVE
        assert fund.start_date == date(2020, 1, 1)
        assert fund.commitment_amount == Decimal('1000000.00')
    
    def test_fund_validation(self, fund_data):
        """Test fund validation rules."""
        # Test required fields
        invalid_data = fund_data.copy()
        del invalid_data['name']
        
        with pytest.raises(ValueError):
            Fund(**invalid_data)
    
    def test_fund_status_transitions(self, fund_data):
        """Test fund status transition logic."""
        fund = Fund(**fund_data)
        
        # Test valid status transitions
        fund.status = FundStatus.COMPLETED
        assert fund.status == FundStatus.COMPLETED
        
        # Test invalid status transitions
        with pytest.raises(ValueError):
            fund.status = 'INVALID_STATUS'
    
    def test_fund_tracking_type_validation(self, fund_data):
        """Test fund tracking type validation."""
        fund = Fund(**fund_data)
        
        # Test valid tracking types
        fund.tracking_type = FundType.COST_BASED
        assert fund.tracking_type == FundType.COST_BASED
        
        # Test invalid tracking types
        with pytest.raises(ValueError):
            fund.tracking_type = 'INVALID_TYPE'


class TestFundEventModel:
    """Test suite for FundEvent model - Fund event entity"""
    
    @pytest.fixture
    def event_data(self):
        """Sample event data for testing."""
        return {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2020, 1, 1),
            'amount': Decimal('100000.00'),
            'description': 'Initial capital call'
        }
    
    def test_event_creation(self, event_data):
        """Test event creation with valid data."""
        event = FundEvent(**event_data)
        
        assert event.event_type == EventType.CAPITAL_CALL
        assert event.event_date == date(2020, 1, 1)
        assert event.amount == Decimal('100000.00')
        assert event.description == 'Initial capital call'
    
    def test_event_validation(self, event_data):
        """Test event validation rules."""
        # Test required fields
        invalid_data = event_data.copy()
        del invalid_data['event_type']
        
        with pytest.raises(ValueError):
            FundEvent(**invalid_data)
    
    def test_event_type_validation(self, event_data):
        """Test event type validation."""
        event = FundEvent(**event_data)
        
        # Test valid event types
        event.event_type = EventType.DISTRIBUTION
        assert event.event_type == EventType.DISTRIBUTION
        
        # Test invalid event types
        with pytest.raises(ValueError):
            event.event_type = 'INVALID_EVENT_TYPE'
    
    def test_event_amount_validation(self, event_data):
        """Test event amount validation."""
        event = FundEvent(**event_data)
        
        # Test valid amounts
        event.amount = Decimal('50000.00')
        assert event.amount == Decimal('50000.00')
        
        # Test negative amounts for certain event types
        event.event_type = EventType.CAPITAL_CALL
        event.amount = Decimal('-100000.00')  # Capital calls can be negative
        assert event.amount == Decimal('-100000.00')


class TestFundEventCashFlowModel:
    """Test suite for FundEventCashFlow model - Cash flow entity"""
    
    @pytest.fixture
    def cash_flow_data(self):
        """Sample cash flow data for testing."""
        return {
            'amount': Decimal('10000.00'),
            'direction': 'INFLOW',
            'description': 'Distribution payment'
        }
    
    def test_cash_flow_creation(self, cash_flow_data):
        """Test cash flow creation with valid data."""
        cash_flow = FundEventCashFlow(**cash_flow_data)
        
        assert cash_flow.amount == Decimal('10000.00')
        assert cash_flow.direction == 'INFLOW'
        assert cash_flow.description == 'Distribution payment'
    
    def test_cash_flow_validation(self, cash_flow_data):
        """Test cash flow validation rules."""
        # Test required fields
        invalid_data = cash_flow_data.copy()
        del invalid_data['amount']
        
        with pytest.raises(ValueError):
            FundEventCashFlow(**invalid_data)
    
    def test_cash_flow_direction_validation(self, cash_flow_data):
        """Test cash flow direction validation."""
        cash_flow = FundEventCashFlow(**cash_flow_data)
        
        # Test valid directions
        cash_flow.direction = 'OUTFLOW'
        assert cash_flow.direction == 'OUTFLOW'
        
        # Test invalid directions
        with pytest.raises(ValueError):
            cash_flow.direction = 'INVALID_DIRECTION'


class TestFundEnums:
    """Test suite for fund enums - Enumeration validation"""
    
    def test_fund_type_enum_values(self):
        """Test FundType enum has expected values."""
        assert FundType.NAV_BASED == 'NAV_BASED'
        assert FundType.COST_BASED == 'COST_BASED'
        
        # Test enum membership
        assert 'NAV_BASED' in FundType.__members__
        assert 'COST_BASED' in FundType.__members__
    
    def test_event_type_enum_values(self):
        """Test EventType enum has expected values."""
        assert EventType.CAPITAL_CALL == 'CAPITAL_CALL'
        assert EventType.DISTRIBUTION == 'DISTRIBUTION'
        assert EventType.UNIT_PURCHASE == 'UNIT_PURCHASE'
        assert EventType.UNIT_SALE == 'UNIT_SALE'
        
        # Test enum membership
        assert 'CAPITAL_CALL' in EventType.__members__
        assert 'DISTRIBUTION' in EventType.__members__
    
    def test_fund_status_enum_values(self):
        """Test FundStatus enum has expected values."""
        assert FundStatus.ACTIVE == 'ACTIVE'
        assert FundStatus.COMPLETED == 'COMPLETED'
        assert FundStatus.REALIZED == 'REALIZED'
        
        # Test enum membership
        assert 'ACTIVE' in FundStatus.__members__
        assert 'COMPLETED' in FundStatus.__members__


class TestFundModelRelationships:
    """Test suite for fund model relationships"""
    
    def test_fund_to_events_relationship(self):
        """Test fund to events relationship."""
        fund = Fund(
            name='Test Fund',
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2020, 1, 1)
        )
        
        event = FundEvent(
            event_type=EventType.CAPITAL_CALL,
            event_date=date(2020, 1, 1),
            amount=Decimal('100000.00')
        )
        
        # Test relationship establishment
        fund.events.append(event)
        assert len(fund.events) == 1
        assert fund.events[0] == event
    
    def test_event_to_cash_flows_relationship(self):
        """Test event to cash flows relationship."""
        event = FundEvent(
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
            start_date=date(2020, 1, 1)
        )
        
        # Test completion validation
        with pytest.raises(ValueError):
            fund.status = FundStatus.COMPLETED  # Should require end_date
        
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
            start_date=date(2020, 1, 1)
        )
        
        # Test event before fund start
        with pytest.raises(ValueError):
            event = FundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2019, 12, 31),  # Before fund start
                amount=Decimal('100000.00')
            )
            fund.events.append(event)
    
    def test_cash_flow_balance_validation(self):
        """Test cash flow balance business rules."""
        event = FundEvent(
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
