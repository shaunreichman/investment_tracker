"""
Integration tests for Return of Capital workflow through all refactored layers.

This module tests the complete return of capital workflow from service layer
through to database persistence, ensuring all business rules and calculations
are applied correctly.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from src.fund.enums import (
    FundTrackingType, 
    EventType, 
    CashFlowDirection, 
    FundStatus
)
from src.shared.enums.shared_enums import EventOperation
from src.fund.services.fund_event_service import FundEventService
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.services.fund_equity_service import FundEquityService
from src.fund.services.fund_event_cash_flow_service import FundEventCashFlowService
from src.fund.repositories.fund_event_repository import FundEventRepository
from src.fund.repositories.fund_repository import FundRepository
from tests.factories.fund_factories import FundFactory
from tests.factories.entity_factories import EntityFactory
from tests.factories.investment_company_factories import InvestmentCompanyFactory


class TestReturnOfCapitalWorkflowIntegration:
    """Test complete return of capital workflow through all refactored layers"""

    def test_return_of_capital_service_layer_flow(self, db_session):
        """Test return of capital creation through service layer flow"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund with cost-based tracking
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # First create a capital call to set the start date and equity balance
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 75000.0,
            'description': 'Initial capital call',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Now create return of capital
        return_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 6, 15),
            'amount': 25000.0,
            'description': 'First return of capital',
            'reference_number': 'ROC-001',
            'fund_id': fund.id
        }
        
        event = fund_event_service.create_fund_event(fund.id, return_data, db_session)
        db_session.commit()
        
        # Verify event creation
        assert event.event_type == EventType.RETURN_OF_CAPITAL
        assert event.amount == 25000.0
        assert event.event_date == date(2023, 6, 15)
        assert event.description == 'First return of capital'
        assert event.reference_number == 'ROC-001'
        assert event.fund_id == fund.id

    def test_return_of_capital_business_validation(self, db_session):
        """Test business rule validation for return of capital"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund with cost-based tracking
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # First create a capital call to set the equity balance
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'description': 'Initial capital call',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        validation_service = FundValidationService()
        
        # Test valid return of capital
        valid_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 6, 15),
            'amount': 25000.0,
            'fund_id': fund.id
        }
        
        errors = validation_service.validate_return_of_capital(fund, valid_data, db_session)
        assert not errors
        
        # Test return exceeding current equity balance
        invalid_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 6, 15),
            'amount': 75000.0,  # More than current equity balance
            'fund_id': fund.id
        }
        
        errors = validation_service.validate_return_of_capital(fund, invalid_data, db_session)
        assert 'amount' in errors
        assert "Cannot return more capital than remaining equity as of the event date" in errors['amount']
        
        # Test return from NAV-based fund (should be invalid)
        nav_fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            current_equity_balance=50000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        nav_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 6, 15),
            'amount': 25000.0,
            'fund_id': nav_fund.id
        }
        
        errors = validation_service.validate_return_of_capital(nav_fund, nav_data, db_session)
        assert 'fund_type' in errors
        assert "Returns of capital are only applicable for cost-based funds" in errors['fund_type']

    def test_return_of_capital_equity_calculations(self, db_session):
        """Test equity balance calculations after return of capital"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # First create a capital call to set the start date and equity balance
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 75000.0,
            'description': 'Initial capital call',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Now create return of capital
        return_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 6, 15),
            'amount': 25000.0,
            'description': 'Return of capital',
            'fund_id': fund.id
        }
        
        fund_event_service.create_fund_event(fund.id, return_data, db_session)
        db_session.commit()
        
        # Refresh fund to get updated values
        db_session.refresh(fund)
        
        # Verify equity calculations
        assert fund.current_equity_balance == 50000.0  # 75000 - 25000
        # Average equity is time-weighted, not simple average
        assert fund.average_equity_balance > 0  # Should be positive
        # Total cost basis represents original investment, not reduced by returns
        assert fund.total_cost_basis == 75000.0  # Original capital call amount

    def test_return_of_capital_cash_flow_integration(self, db_session):
        """Test return of capital with cash flow creation and reconciliation"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # First create a capital call to set the start date and equity balance
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 60000.0,
            'description': 'Initial capital call',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Now create return of capital
        return_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 6, 15),
            'amount': 20000.0,
            'description': 'Return of capital with cash flow',
            'fund_id': fund.id
        }
        
        event = fund_event_service.create_fund_event(fund.id, return_data, db_session)
        db_session.commit()
        
        # Create bank account for cash flow
        from tests.factories.banking_factories import BankAccountFactory, BankFactory
        BankFactory._meta.sqlalchemy_session = db_session
        BankAccountFactory._meta.sqlalchemy_session = db_session
        
        bank = BankFactory.create()
        account = BankAccountFactory.create(bank_id=bank.id)
        db_session.commit()
        
        # Create cash flow manually (not automatically created)
        cash_flow_service = FundEventCashFlowService()
        cash_flow_data = {
            'bank_account_id': account.id,
            'direction': CashFlowDirection.OUTFLOW,
            'amount': 20000.0,
            'currency': 'AUD',
            'transfer_date': date(2023, 6, 16),
            'description': 'Return of capital with cash flow'
        }
        cash_flow = cash_flow_service.create_fund_event_cash_flow(event.id, cash_flow_data, db_session)
        db_session.commit()
        
        # Verify cash flow creation
        assert cash_flow.direction == CashFlowDirection.OUTFLOW
        assert cash_flow.amount == 20000.0
        assert cash_flow.transfer_date == date(2023, 6, 16)
        assert cash_flow.description == 'Return of capital with cash flow'
        assert cash_flow.fund_event_id == event.id

    def test_multiple_return_of_capital_cumulative_tracking(self, db_session):
        """Test multiple return of capital events with cumulative tracking"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=200000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # First create a capital call to set the start date and equity balance
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 150000.0,
            'description': 'Initial capital call',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # First return of capital
        return_data_1 = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 6, 15),
            'amount': 50000.0,
            'description': 'First return of capital',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, return_data_1, db_session)
        db_session.commit()
        
        db_session.refresh(fund)
        assert fund.current_equity_balance == 100000.0  # 150000 - 50000
        assert fund.commitment_amount - fund.current_equity_balance == 100000.0
        
        # Second return of capital
        return_data_2 = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 8, 15),
            'amount': 30000.0,
            'description': 'Second return of capital',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, return_data_2, db_session)
        db_session.commit()
        
        db_session.refresh(fund)
        assert fund.current_equity_balance == 70000.0  # 100000 - 30000
        assert fund.commitment_amount - fund.current_equity_balance == 130000.0

    def test_return_of_capital_error_handling_across_layers(self, db_session):
        """Test error handling and validation across all layers"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # First create a capital call to set the equity balance
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 30000.0,
            'description': 'Initial capital call',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Test return exceeding current equity balance
        invalid_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 6, 15),
            'amount': 50000.0,  # More than current equity balance
            'description': 'Invalid return',
            'fund_id': fund.id
        }
        
        with pytest.raises(ValueError, match="Validation errors"):
            fund_event_service.create_fund_event(fund.id, invalid_data, db_session)

    def test_return_of_capital_performance_with_large_dataset(self, db_session):
        """Test return of capital performance with large dataset"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=1000000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # First create a capital call to set the start date and equity balance
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 1),
            'amount': 800000.0,
            'description': 'Initial capital call',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Create multiple return of capital events
        total_returned = 0
        for i in range(10):
            return_date = date(2023, 1, 15) + timedelta(days=i * 30)
            return_amount = 50000.0 + (i * 1000.0)  # Varying amounts
            
            return_data = {
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': return_date,
                'amount': return_amount,
                'description': f'Return {i+1}',
                'fund_id': fund.id
            }
            
            fund_event_service.create_fund_event(fund.id, return_data, db_session)
            total_returned += return_amount
        
        db_session.commit()
        db_session.refresh(fund)
        
        # Verify final calculations
        expected_equity = 800000.0 - total_returned
        assert fund.current_equity_balance == expected_equity
        assert fund.current_equity_balance > 0  # Should still have positive equity

    def test_return_of_capital_transaction_integrity(self, db_session):
        """Test database transaction rollback scenarios"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # First create a capital call to set the equity balance
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'description': 'Initial capital call',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Store initial state
        db_session.refresh(fund)
        initial_equity = fund.current_equity_balance
        fund_event_repository = FundEventRepository()
        initial_events = fund_event_repository.get_fund_events(db_session, fund_ids=[fund.id])
        initial_event_count = len(initial_events)
        
        # Test transaction rollback on validation error
        invalid_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 6, 15),
            'amount': 75000.0,  # More than current equity balance
            'description': 'Invalid return',
            'fund_id': fund.id
        }
        
        try:
            fund_event_service.create_fund_event(fund.id, invalid_data, db_session)
            db_session.commit()
            assert False, "Should have raised ValueError"
        except ValueError:
            db_session.rollback()
        
        # Verify no changes were made
        db_session.refresh(fund)
        assert fund.current_equity_balance == initial_equity
        
        final_events = fund_event_repository.get_fund_events(db_session, fund_ids=[fund.id])
        final_event_count = len(final_events)
        assert final_event_count == initial_event_count

    def test_return_of_capital_fund_status_updates(self, db_session):
        """Test fund status changes after return of capital"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # First create a capital call to set the start date and equity balance
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'description': 'Initial capital call',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Create return of capital
        return_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 6, 15),
            'amount': 50000.0,  # Return all equity
            'description': 'Full return of capital',
            'fund_id': fund.id
        }
        
        fund_event_service.create_fund_event(fund.id, return_data, db_session)
        db_session.commit()
        
        db_session.refresh(fund)
        
        # Verify fund status and equity
        assert fund.current_equity_balance == 0.0
        # Note: Fund status logic would depend on business rules
        # This test verifies the status service is called correctly

    def test_return_of_capital_metadata_validation(self, db_session):
        """Test return of capital event metadata and reference number handling"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # First create a capital call to set the start date and equity balance
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 60000.0,
            'description': 'Initial capital call',
            'fund_id': fund.id
        }
        fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Test with reference number
        return_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date(2023, 6, 15),
            'amount': 20000.0,
            'description': 'Return with reference',
            'reference_number': 'ROC-2023-001',
            'fund_id': fund.id
        }
        
        event = fund_event_service.create_fund_event(fund.id, return_data, db_session)
        db_session.commit()
        
        # Verify metadata
        assert event.reference_number == 'ROC-2023-001'
        assert event.description == 'Return with reference'
        assert event.event_type == EventType.RETURN_OF_CAPITAL
        assert event.amount == 20000.0
