"""
Integration tests for Fund Event Cash Flow workflow through all refactored layers.

This module tests the complete fund event cash flow workflow from service layer
through to database persistence, ensuring all business rules, validations, and
calculations are applied correctly.

Tests cover:
- Complete workflow: Fund -> Fund Event -> Bank Account -> Cash Flow
- Cash flow creation for different event types
- Currency validation between bank account and cash flow
- Cash flow balance tracking and reconciliation
- Multiple cash flows per event
- Direction validation (INFLOW/OUTFLOW)
- Error handling and validation across all layers
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from src.fund.enums import (
    FundTrackingType, 
    EventType, 
    CashFlowDirection, 
    FundStatus,
    DistributionType
)
from src.shared.enums.shared_enums import EventOperation, Currency
from src.banking.enums import BankAccountStatus, BankAccountType
from src.entity.enums import EntityType
from src.fund.services.fund_event_service import FundEventService
from src.fund.services.fund_event_cash_flow_service import FundEventCashFlowService
from src.banking.services.bank_account_service import BankAccountService
from src.banking.services.bank_service import BankService
from src.entity.services.entity_service import EntityService
from src.fund.repositories.fund_event_cash_flow_repository import FundEventCashFlowRepository
from tests.factories.fund_factories import FundFactory
from tests.factories.entity_factories import EntityFactory
from tests.factories.investment_company_factories import InvestmentCompanyFactory
from tests.factories.banking_factories import BankFactory, BankAccountFactory


class TestFundEventCashFlowWorkflowIntegration:
    """Test complete fund event cash flow workflow through all refactored layers"""

    def test_complete_cash_flow_workflow_with_capital_call(self, db_session):
        """Test complete workflow: Fund -> Capital Call -> Bank Account -> Cash Flow"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # 1. Create entity
        entity = EntityFactory.create(
            name="Test Investor Entity",
            entity_type=EntityType.COMPANY,
            tax_jurisdiction="AU"
        )
        db_session.commit()
        
        # 2. Create fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=500000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        # 3. Create bank and bank account for investor
        bank = BankFactory.create(
            name="Test Bank",
            country="AU"
        )
        db_session.commit()
        
        bank_account_service = BankAccountService()
        bank_account_data = {
            'entity_id': entity.id,
            'account_name': 'Investor Operating Account',
            'account_number': '123456789',
            'currency': 'AUD',
            'account_type': 'CHECKING'
        }
        bank_account = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_data,
            session=db_session
        )
        db_session.commit()
        
        # 4. Create capital call event
        fund_event_service = FundEventService()
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 100000.0,
            'description': 'First capital call',
            'fund_id': fund.id
        }
        fund_event = fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # 5. Create cash flow for capital call
        cash_flow_service = FundEventCashFlowService()
        cash_flow_data = {
            'bank_account_id': bank_account.id,
            'direction': CashFlowDirection.OUTFLOW,  # Money leaving investor account
            'amount': 100000.0,
            'currency': 'AUD',
            'transfer_date': date(2023, 1, 16),
            'reference': 'CAPF001',
            'description': 'Capital call payment'
        }
        cash_flow = cash_flow_service.create_fund_event_cash_flow(fund_event.id, cash_flow_data, db_session)
        db_session.commit()
        
        # Verify entire workflow
        assert cash_flow is not None
        assert cash_flow.fund_event_id == fund_event.id
        assert cash_flow.bank_account_id == bank_account.id
        assert cash_flow.direction == CashFlowDirection.OUTFLOW
        assert cash_flow.amount == 100000.0
        assert cash_flow.currency == 'AUD'
        assert cash_flow.transfer_date == date(2023, 1, 16)
        assert cash_flow.reference == 'CAPF001'
        
        # Verify relationships
        assert cash_flow.bank_account.entity_id == entity.id
        assert cash_flow.fund_event.fund_id == fund.id
        
        # Verify cash flow balance tracking
        db_session.refresh(fund_event)
        assert fund_event.cash_flow_balance_amount == 100000.0
        assert fund_event.is_cash_flow_complete == True

    def test_distribution_cash_flow_with_inflow_direction(self, db_session):
        """Test distribution event with cash flow INFLOW direction"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create entity and fund
        entity = EntityFactory.create(entity_type=EntityType.PERSON)
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2023, 1, 1)
        )
        db_session.commit()
        
        # Create bank account
        bank = BankFactory.create()
        bank_account_service = BankAccountService()
        bank_account_data = {
            'entity_id': entity.id,
            'account_name': 'Distribution Account',
            'account_number': '987654321',
            'currency': 'USD',
            'account_type': 'SAVINGS'
        }
        bank_account = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_data,
            session=db_session
        )
        db_session.commit()
        
        # Create distribution event
        fund_event_service = FundEventService()
        distribution_data = {
            'event_type': EventType.DISTRIBUTION,
            'event_date': date(2023, 6, 30),
            'amount': 50000.0,
            'distribution_type': DistributionType.INCOME,
            'has_withholding_tax': False,
            'description': 'Semi-annual distribution',
            'fund_id': fund.id
        }
        fund_event = fund_event_service.create_fund_event(fund.id, distribution_data, db_session)
        db_session.commit()
        
        # Create cash flow for distribution (INFLOW to investor)
        cash_flow_service = FundEventCashFlowService()
        cash_flow_data = {
            'bank_account_id': bank_account.id,
            'direction': CashFlowDirection.INFLOW,  # Money coming into investor account
            'amount': 50000.0,
            'currency': 'USD',
            'transfer_date': date(2023, 7, 1),
            'reference': 'DIST-2023-Q2',
            'description': 'Q2 income distribution'
        }
        cash_flow = cash_flow_service.create_fund_event_cash_flow(fund_event.id, cash_flow_data, db_session)
        db_session.commit()
        
        # Verify cash flow
        assert cash_flow.direction == CashFlowDirection.INFLOW
        assert cash_flow.amount == 50000.0
        assert cash_flow.currency == 'USD'
        
        # Verify cash flow balance
        db_session.refresh(fund_event)
        assert fund_event.cash_flow_balance_amount == 50000.0
        assert fund_event.is_cash_flow_complete == True

    def test_multiple_cash_flows_for_single_event(self, db_session):
        """Test multiple cash flows for a single event (split payments)"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create entity and fund
        entity = EntityFactory.create(entity_type=EntityType.TRUST)
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=1000000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        # Create multiple bank accounts
        bank = BankFactory.create()
        bank_account_service = BankAccountService()
        
        # Account 1: AUD account
        bank_account_1_data = {
            'entity_id': entity.id,
            'account_name': 'AUD Operating Account',
            'account_number': '111111111',
            'currency': 'AUD',
            'account_type': 'CHECKING'
        }
        bank_account_1 = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_1_data,
            session=db_session
        )
        
        # Account 2: AUD savings account
        bank_account_2_data = {
            'entity_id': entity.id,
            'account_name': 'AUD Savings Account',
            'account_number': '222222222',
            'currency': 'AUD',
            'account_type': 'SAVINGS'
        }
        bank_account_2 = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_2_data,
            session=db_session
        )
        db_session.commit()
        
        # Create capital call event
        fund_event_service = FundEventService()
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 3, 15),
            'amount': 200000.0,
            'description': 'Large capital call - split payment',
            'fund_id': fund.id
        }
        fund_event = fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Create first cash flow (partial payment from account 1)
        cash_flow_service = FundEventCashFlowService()
        cash_flow_1_data = {
            'bank_account_id': bank_account_1.id,
            'direction': CashFlowDirection.OUTFLOW,
            'amount': 120000.0,
            'currency': 'AUD',
            'transfer_date': date(2023, 3, 16),
            'reference': 'PART1',
            'description': 'Partial payment from operating account'
        }
        cash_flow_1 = cash_flow_service.create_fund_event_cash_flow(fund_event.id, cash_flow_1_data, db_session)
        db_session.commit()
        
        # Verify first cash flow
        db_session.refresh(fund_event)
        assert fund_event.cash_flow_balance_amount == 120000.0
        assert fund_event.is_cash_flow_complete == False  # Not yet complete
        
        # Create second cash flow (remaining payment from account 2)
        cash_flow_2_data = {
            'bank_account_id': bank_account_2.id,
            'direction': CashFlowDirection.OUTFLOW,
            'amount': 80000.0,
            'currency': 'AUD',
            'transfer_date': date(2023, 3, 17),
            'reference': 'PART2',
            'description': 'Remaining payment from savings account'
        }
        cash_flow_2 = cash_flow_service.create_fund_event_cash_flow(fund_event.id, cash_flow_2_data, db_session)
        db_session.commit()
        
        # Verify both cash flows
        assert cash_flow_1.amount == 120000.0
        assert cash_flow_2.amount == 80000.0
        
        # Verify total cash flow balance
        db_session.refresh(fund_event)
        assert fund_event.cash_flow_balance_amount == 200000.0
        assert fund_event.is_cash_flow_complete == True  # Now complete
        
        # Verify we can retrieve all cash flows for the event
        all_cash_flows = cash_flow_service.get_fund_event_cash_flows(
            session=db_session,
            fund_event_id=fund_event.id
        )
        assert len(all_cash_flows) == 2

    def test_cash_flow_validation_errors(self, db_session):
        """Test validation errors for cash flow creation"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create entity, fund, and bank account
        entity = EntityFactory.create()
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            status=FundStatus.ACTIVE
        )
        bank = BankFactory.create()
        bank_account_service = BankAccountService()
        bank_account_data = {
            'entity_id': entity.id,
            'account_name': 'Test Account',
            'account_number': '999999999',
            'currency': 'EUR',
            'account_type': 'CHECKING'
        }
        bank_account = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_data,
            session=db_session
        )
        db_session.commit()
        
        # Create fund event
        fund_event_service = FundEventService()
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 100000.0,
            'fund_id': fund.id
        }
        fund_event = fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        cash_flow_service = FundEventCashFlowService()
        
        # Test 1: Non-existent bank account
        with pytest.raises(ValueError, match="Bank account not found"):
            cash_flow_data = {
                'bank_account_id': 99999,  # Non-existent
                'direction': CashFlowDirection.OUTFLOW,
                'amount': 50000.0,
                'currency': 'EUR',
                'transfer_date': date(2023, 1, 16)
            }
            cash_flow_service.create_fund_event_cash_flow(fund_event.id, cash_flow_data, db_session)
        
        # Test 2: Non-existent fund event
        with pytest.raises(ValueError, match="Fund event not found"):
            cash_flow_data = {
                'bank_account_id': bank_account.id,
                'direction': CashFlowDirection.OUTFLOW,
                'amount': 50000.0,
                'currency': 'EUR',
                'transfer_date': date(2023, 1, 16)
            }
            cash_flow_service.create_fund_event_cash_flow(99999, cash_flow_data, db_session)
        
        # Test 3: Cash flow amount exceeds event amount
        with pytest.raises(ValueError, match="Cash flow is too large"):
            cash_flow_data = {
                'bank_account_id': bank_account.id,
                'direction': CashFlowDirection.OUTFLOW,
                'amount': 150000.0,  # More than event amount
                'currency': 'EUR',
                'transfer_date': date(2023, 1, 16)
            }
            cash_flow_service.create_fund_event_cash_flow(fund_event.id, cash_flow_data, db_session)

    def test_cash_flow_with_unit_purchase_brokerage_fee(self, db_session):
        """Test cash flow with unit purchase event including brokerage fee"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create entity and fund
        entity = EntityFactory.create()
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2023, 1, 1)
        )
        db_session.commit()
        
        # Create bank account
        bank = BankFactory.create()
        bank_account_service = BankAccountService()
        bank_account_data = {
            'entity_id': entity.id,
            'account_name': 'Investment Account',
            'account_number': '555555555',
            'currency': 'GBP',
            'account_type': 'INVESTMENT'
        }
        bank_account = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_data,
            session=db_session
        )
        db_session.commit()
        
        # Create unit purchase event with brokerage fee
        fund_event_service = FundEventService()
        unit_purchase_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 4, 15),
            'amount': 50000.0,  # Purchase amount
            'units_purchased': 5000.0,
            'unit_price': 10.0,
            'brokerage_fee': 250.0,  # Brokerage fee
            'description': 'Unit purchase with fee',
            'fund_id': fund.id
        }
        fund_event = fund_event_service.create_fund_event(fund.id, unit_purchase_data, db_session)
        db_session.commit()
        
        # Total cash flow should be amount + brokerage fee = 50000 + 250 = 50250
        cash_flow_service = FundEventCashFlowService()
        cash_flow_data = {
            'bank_account_id': bank_account.id,
            'direction': CashFlowDirection.OUTFLOW,
            'amount': 50250.0,  # Including brokerage fee
            'currency': 'GBP',
            'transfer_date': date(2023, 4, 16),
            'description': 'Unit purchase payment including brokerage'
        }
        cash_flow = cash_flow_service.create_fund_event_cash_flow(fund_event.id, cash_flow_data, db_session)
        db_session.commit()
        
        # Verify cash flow
        assert cash_flow.amount == 50250.0
        
        # Verify cash flow balance
        db_session.refresh(fund_event)
        assert fund_event.cash_flow_balance_amount == 50250.0
        assert fund_event.is_cash_flow_complete == True

    def test_cash_flow_with_distribution_and_simple_tax_withholding(self, db_session):
        """Test cash flow with distribution event including simple tax withholding"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create entity and fund
        entity = EntityFactory.create()
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            status=FundStatus.ACTIVE,
            start_date=date(2023, 1, 1)
        )
        db_session.commit()
        
        # Create bank account
        bank = BankFactory.create()
        bank_account_service = BankAccountService()
        bank_account_data = {
            'entity_id': entity.id,
            'account_name': 'Distribution Account',
            'account_number': '777777777',
            'currency': 'CAD',
            'account_type': 'CHECKING'
        }
        bank_account = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_data,
            session=db_session
        )
        db_session.commit()
        
        # Create simple distribution event with tax withholding field
        fund_event_service = FundEventService()
        distribution_data = {
            'event_type': EventType.DISTRIBUTION,
            'event_date': date(2023, 12, 31),
            'amount': 100000.0,  # Gross distribution
            'distribution_type': DistributionType.INCOME,
            'tax_withholding': 15000.0,  # Simple tax withholding amount
            'has_withholding_tax': False,  # Not using complex withholding tax calculation
            'description': 'Year-end distribution with simple tax',
            'fund_id': fund.id
        }
        fund_event = fund_event_service.create_fund_event(fund.id, distribution_data, db_session)
        db_session.commit()
        
        # Cash flow should be net after tax: 100000 - 15000 = 85000
        cash_flow_service = FundEventCashFlowService()
        cash_flow_data = {
            'bank_account_id': bank_account.id,
            'direction': CashFlowDirection.INFLOW,
            'amount': 85000.0,  # Net after tax
            'currency': 'CAD',
            'transfer_date': date(2024, 1, 5),
            'description': 'Distribution payment after tax withholding'
        }
        cash_flow = cash_flow_service.create_fund_event_cash_flow(fund_event.id, cash_flow_data, db_session)
        db_session.commit()
        
        # Verify cash flow
        assert cash_flow.amount == 85000.0
        assert cash_flow.direction == CashFlowDirection.INFLOW
        
        # Verify event details
        db_session.refresh(fund_event)
        assert fund_event.amount == 100000.0
        
        # Verify cash flow balance (85000 is less than the 100000 event amount)
        # This demonstrates partial cash flow tracking when tax is withheld
        assert fund_event.cash_flow_balance_amount == 85000.0
        assert fund_event.is_cash_flow_complete == False  # Not complete because 85000 < 100000

    def test_cash_flow_deletion_and_balance_update(self, db_session):
        """Test cash flow deletion and event balance update"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create entity, fund, and bank account
        entity = EntityFactory.create()
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,  # Set commitment amount for validation
            status=FundStatus.ACTIVE
        )
        bank = BankFactory.create()
        bank_account_service = BankAccountService()
        bank_account_data = {
            'entity_id': entity.id,
            'account_name': 'Test Account',
            'account_number': '888888888',
            'currency': 'AUD',
            'account_type': 'CHECKING'
        }
        bank_account = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_data,
            session=db_session
        )
        db_session.commit()
        
        # Create fund event
        fund_event_service = FundEventService()
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 5, 15),
            'amount': 75000.0,
            'fund_id': fund.id
        }
        fund_event = fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Create cash flow
        cash_flow_service = FundEventCashFlowService()
        cash_flow_data = {
            'bank_account_id': bank_account.id,
            'direction': CashFlowDirection.OUTFLOW,
            'amount': 75000.0,
            'currency': 'AUD',
            'transfer_date': date(2023, 5, 16)
        }
        cash_flow = cash_flow_service.create_fund_event_cash_flow(fund_event.id, cash_flow_data, db_session)
        db_session.commit()
        
        # Verify cash flow was created and event is complete
        db_session.refresh(fund_event)
        assert fund_event.cash_flow_balance_amount == 75000.0
        assert fund_event.is_cash_flow_complete == True
        
        # Delete cash flow
        success = cash_flow_service.delete_fund_event_cash_flow(cash_flow.id, db_session)
        db_session.commit()
        
        # Verify deletion
        assert success == True
        
        # Verify event balance was updated
        db_session.refresh(fund_event)
        assert fund_event.cash_flow_balance_amount == 0.0
        assert fund_event.is_cash_flow_complete == False
        
        # Verify cash flow was removed from database
        deleted_cash_flow = cash_flow_service.get_fund_event_cash_flow_by_id(cash_flow.id, db_session)
        assert deleted_cash_flow is None

    def test_cash_flow_retrieval_with_filters(self, db_session):
        """Test retrieving cash flows with various filters"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create entities and funds
        entity_1 = EntityFactory.create(name="Entity 1")
        entity_2 = EntityFactory.create(name="Entity 2")
        fund_1 = FundFactory.create(tracking_type=FundTrackingType.COST_BASED, status=FundStatus.ACTIVE)
        fund_2 = FundFactory.create(tracking_type=FundTrackingType.NAV_BASED, status=FundStatus.ACTIVE, start_date=date(2023, 1, 1))
        db_session.commit()
        
        # Create bank accounts
        bank = BankFactory.create()
        bank_account_service = BankAccountService()
        
        account_1_data = {
            'entity_id': entity_1.id,
            'account_name': 'Account 1',
            'account_number': 'ACC001',
            'currency': 'AUD',
            'account_type': 'CHECKING'
        }
        account_1 = bank_account_service.create_bank_account(bank_id=bank.id, bank_account_data=account_1_data, session=db_session)
        
        account_2_data = {
            'entity_id': entity_2.id,
            'account_name': 'Account 2',
            'account_number': 'ACC002',
            'currency': 'USD',
            'account_type': 'SAVINGS'
        }
        account_2 = bank_account_service.create_bank_account(bank_id=bank.id, bank_account_data=account_2_data, session=db_session)
        db_session.commit()
        
        # Create fund events and cash flows
        fund_event_service = FundEventService()
        cash_flow_service = FundEventCashFlowService()
        
        # Event 1 for Fund 1
        event_1_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 100000.0,
            'fund_id': fund_1.id
        }
        event_1 = fund_event_service.create_fund_event(fund_1.id, event_1_data, db_session)
        
        cash_flow_1_data = {
            'bank_account_id': account_1.id,
            'direction': CashFlowDirection.OUTFLOW,
            'amount': 100000.0,
            'currency': 'AUD',
            'transfer_date': date(2023, 1, 16)
        }
        cash_flow_1 = cash_flow_service.create_fund_event_cash_flow(event_1.id, cash_flow_1_data, db_session)
        
        # Event 2 for Fund 2
        event_2_data = {
            'event_type': EventType.DISTRIBUTION,
            'event_date': date(2023, 6, 30),
            'amount': 50000.0,
            'distribution_type': DistributionType.INCOME,
            'has_withholding_tax': False,
            'fund_id': fund_2.id
        }
        event_2 = fund_event_service.create_fund_event(fund_2.id, event_2_data, db_session)
        
        cash_flow_2_data = {
            'bank_account_id': account_2.id,
            'direction': CashFlowDirection.INFLOW,
            'amount': 50000.0,
            'currency': 'USD',
            'transfer_date': date(2023, 7, 1)
        }
        cash_flow_2 = cash_flow_service.create_fund_event_cash_flow(event_2.id, cash_flow_2_data, db_session)
        db_session.commit()
        
        # Test retrieval by fund_id
        fund_1_cash_flows = cash_flow_service.get_fund_event_cash_flows(session=db_session, fund_id=fund_1.id)
        assert len(fund_1_cash_flows) == 1
        assert fund_1_cash_flows[0].id == cash_flow_1.id
        
        # Test retrieval by fund_event_id
        event_1_cash_flows = cash_flow_service.get_fund_event_cash_flows(session=db_session, fund_event_id=event_1.id)
        assert len(event_1_cash_flows) == 1
        assert event_1_cash_flows[0].id == cash_flow_1.id
        
        # Test retrieval by bank_account_id
        account_2_cash_flows = cash_flow_service.get_fund_event_cash_flows(session=db_session, bank_account_id=account_2.id)
        assert len(account_2_cash_flows) == 1
        assert account_2_cash_flows[0].id == cash_flow_2.id

    def test_cash_flow_transaction_integrity(self, db_session):
        """Test database transaction rollback scenarios"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create entity, fund, and bank account
        entity = EntityFactory.create()
        fund = FundFactory.create(tracking_type=FundTrackingType.COST_BASED, status=FundStatus.ACTIVE)
        bank = BankFactory.create()
        bank_account_service = BankAccountService()
        bank_account_data = {
            'entity_id': entity.id,
            'account_name': 'Test Account',
            'account_number': '666666666',
            'currency': 'AUD',
            'account_type': 'CHECKING'
        }
        bank_account = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_data,
            session=db_session
        )
        db_session.commit()
        
        # Create fund event
        fund_event_service = FundEventService()
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 2, 15),
            'amount': 50000.0,
            'fund_id': fund.id
        }
        fund_event = fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Store initial state
        db_session.refresh(fund_event)
        initial_balance = fund_event.cash_flow_balance_amount
        initial_complete_status = fund_event.is_cash_flow_complete
        
        cash_flow_repository = FundEventCashFlowRepository()
        initial_cash_flows = cash_flow_repository.get_fund_event_cash_flows(
            session=db_session,
            fund_event_id=fund_event.id
        )
        initial_cash_flow_count = len(initial_cash_flows)
        
        # Try to create invalid cash flow (exceeds event amount)
        cash_flow_service = FundEventCashFlowService()
        invalid_cash_flow_data = {
            'bank_account_id': bank_account.id,
            'direction': CashFlowDirection.OUTFLOW,
            'amount': 75000.0,  # More than event amount
            'currency': 'AUD',
            'transfer_date': date(2023, 2, 16)
        }
        
        try:
            cash_flow_service.create_fund_event_cash_flow(fund_event.id, invalid_cash_flow_data, db_session)
            db_session.commit()
            assert False, "Should have raised ValueError"
        except ValueError:
            db_session.rollback()
        
        # Verify no changes were made
        db_session.refresh(fund_event)
        assert fund_event.cash_flow_balance_amount == initial_balance
        assert fund_event.is_cash_flow_complete == initial_complete_status
        
        final_cash_flows = cash_flow_repository.get_fund_event_cash_flows(
            session=db_session,
            fund_event_id=fund_event.id
        )
        assert len(final_cash_flows) == initial_cash_flow_count

    def test_multiple_entities_and_funds_cash_flow_isolation(self, db_session):
        """Test cash flow isolation across multiple entities and funds"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create multiple entities
        entity_a = EntityFactory.create(name="Entity A", entity_type=EntityType.PERSON)
        entity_b = EntityFactory.create(name="Entity B", entity_type=EntityType.COMPANY)
        entity_c = EntityFactory.create(name="Entity C", entity_type=EntityType.TRUST)
        
        # Create multiple funds
        fund_x = FundFactory.create(tracking_type=FundTrackingType.COST_BASED, status=FundStatus.ACTIVE)
        fund_y = FundFactory.create(tracking_type=FundTrackingType.NAV_BASED, status=FundStatus.ACTIVE, start_date=date(2023, 1, 1))
        db_session.commit()
        
        # Create bank accounts for each entity
        bank = BankFactory.create()
        bank_account_service = BankAccountService()
        
        accounts = []
        for i, entity in enumerate([entity_a, entity_b, entity_c]):
            account_data = {
                'entity_id': entity.id,
                'account_name': f'{entity.name} Account',
                'account_number': f'ACC{i}00',
                'currency': 'AUD',
                'account_type': 'CHECKING'
            }
            account = bank_account_service.create_bank_account(
                bank_id=bank.id,
                bank_account_data=account_data,
                session=db_session
            )
            accounts.append(account)
        db_session.commit()
        
        # Create events and cash flows for each combination
        fund_event_service = FundEventService()
        cash_flow_service = FundEventCashFlowService()
        
        created_cash_flows = []
        
        # Fund X - Entity A
        event_xa_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 100000.0,
            'fund_id': fund_x.id
        }
        event_xa = fund_event_service.create_fund_event(fund_x.id, event_xa_data, db_session)
        
        cash_flow_xa_data = {
            'bank_account_id': accounts[0].id,
            'direction': CashFlowDirection.OUTFLOW,
            'amount': 100000.0,
            'currency': 'AUD',
            'transfer_date': date(2023, 1, 16)
        }
        cash_flow_xa = cash_flow_service.create_fund_event_cash_flow(event_xa.id, cash_flow_xa_data, db_session)
        created_cash_flows.append((cash_flow_xa, fund_x.id, accounts[0].id))
        
        # Fund Y - Entity B
        event_yb_data = {
            'event_type': EventType.DISTRIBUTION,
            'event_date': date(2023, 6, 30),
            'amount': 50000.0,
            'distribution_type': DistributionType.INCOME,
            'has_withholding_tax': False,
            'fund_id': fund_y.id
        }
        event_yb = fund_event_service.create_fund_event(fund_y.id, event_yb_data, db_session)
        
        cash_flow_yb_data = {
            'bank_account_id': accounts[1].id,
            'direction': CashFlowDirection.INFLOW,
            'amount': 50000.0,
            'currency': 'AUD',
            'transfer_date': date(2023, 7, 1)
        }
        cash_flow_yb = cash_flow_service.create_fund_event_cash_flow(event_yb.id, cash_flow_yb_data, db_session)
        created_cash_flows.append((cash_flow_yb, fund_y.id, accounts[1].id))
        
        db_session.commit()
        
        # Verify isolation - each fund only sees its own cash flows
        fund_x_flows = cash_flow_service.get_fund_event_cash_flows(session=db_session, fund_id=fund_x.id)
        assert len(fund_x_flows) == 1
        assert fund_x_flows[0].id == cash_flow_xa.id
        
        fund_y_flows = cash_flow_service.get_fund_event_cash_flows(session=db_session, fund_id=fund_y.id)
        assert len(fund_y_flows) == 1
        assert fund_y_flows[0].id == cash_flow_yb.id
        
        # Verify each account only sees its own cash flows
        account_a_flows = cash_flow_service.get_fund_event_cash_flows(session=db_session, bank_account_id=accounts[0].id)
        assert len(account_a_flows) == 1
        assert account_a_flows[0].bank_account.entity_id == entity_a.id
        
        account_b_flows = cash_flow_service.get_fund_event_cash_flows(session=db_session, bank_account_id=accounts[1].id)
        assert len(account_b_flows) == 1
        assert account_b_flows[0].bank_account.entity_id == entity_b.id

