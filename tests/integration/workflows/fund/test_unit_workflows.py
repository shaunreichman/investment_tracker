"""
Integration tests for complete unit purchase and sale workflows.

This file focuses ONLY on unit purchase and sale workflow testing, consolidating
all unit purchase/sale related integration tests into a single, focused location.

Filename: test_unit_workflows.py

Tests end-to-end unit purchase and sale processes including:
- Unit purchase workflow with NAV updates
- Unit sale workflow with NAV updates and capital gains
- Cash flow integration for unit operations
- Event system coordination
- Business rule enforcement
- Tax implications and calculations

IMPORTANT: This file tests WORKFLOWS, not individual components.
Individual component testing is already covered in:
- Unit tests: test_fund_models.py, test_fund_event_service.py
- Service tests: test_fund_incremental_calculation_service.py
- Calculation tests: test_fifo_calculations.py, test_nav_calculations.py
- Basic integration: test_fund_flows.py
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from tests.factories import (
    FundFactory, EntityFactory, InvestmentCompanyFactory,
    BankFactory, BankAccountFactory, FundEventCashFlowFactory,
    TaxStatementFactory
)
from src.fund.models import (
    Fund, FundType, EventType, CashFlowDirection,
    FundEvent, FundEventCashFlow
)
from src.fund.enums import DistributionType, TaxPaymentType
from src.fund.events.orchestrator import FundUpdateOrchestrator


class TestUnitPurchaseWorkflow:
    """Test complete unit purchase workflows from creation to completion"""

    def test_basic_unit_purchase_workflow(self, db_session):
        """Test basic unit purchase workflow with NAV updates"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Initial state validation
        assert fund.current_units == 0.0
        assert fund.current_unit_price == 0.0
        assert fund.current_nav_total == 0.0
        
        # Execute unit purchase
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        event = fund_event_service.add_unit_purchase(
            fund=fund,
            units=1000.0,
            price=25.50,
            date=date(2023, 1, 15),
            description="Initial unit purchase",
            session=db_session
        )
        db_session.commit()
        
        # Verify fund state updates
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 1000.0
        assert fund.current_unit_price == 25.50
        assert fund.current_nav_total == 25500.0
        
        # Verify event creation
        assert event is not None
        assert event.event_type == EventType.UNIT_PURCHASE
        assert event.units_purchased == 1000.0
        assert event.unit_price == 25.50
        assert event.event_date == date(2023, 1, 15)
        assert event.description == "Initial unit purchase"

    def test_unit_purchase_with_cash_flow_integration(self, db_session):
        """Test unit purchase workflow with cash flow creation and reconciliation"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, 
                       BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund and bank account
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(
            entity=entity,
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0,
            currency="AUD"
        )
        db_session.commit()
        
        # Create unit purchase event
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        event = fund_event_service.add_unit_purchase(
            fund=fund,
            units=500.0,
            price=30.00,
            date=date(2023, 2, 1),
            description="Unit purchase with cash flow",
            session=db_session
        )
        db_session.commit()
        
        # Add cash flow for the unit purchase
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=15000.0,  # 500 units * $30.00
            currency="AUD",
            transfer_date=date(2023, 2, 2),
            direction=CashFlowDirection.OUTFLOW
        )
        db_session.commit()
        
        # Verify fund state after cash flow
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 500.0
        assert fund.current_unit_price == 30.00
        assert fund.current_nav_total == 15000.0
        
        # Verify cash flow integration
        assert cash_flow.fund_event_id == event.id
        assert cash_flow.amount == 15000.0
        assert cash_flow.direction == CashFlowDirection.OUTFLOW

    def test_multiple_unit_purchases_workflow(self, db_session):
        """Test workflow with multiple unit purchases and NAV averaging"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=200000.0
        )
        db_session.commit()
        
        # First unit purchase
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        fund_event_service.add_unit_purchase(
            fund=fund,
            units=1000.0,
            price=20.00,
            date=date(2023, 1, 1),
            description="First purchase",
            session=db_session
        )
        db_session.commit()
        
        # Second unit purchase
        fund_event_service.add_unit_purchase(
            fund=fund,
            units=500.0,
            price=25.00,
            date=date(2023, 2, 1),
            description="Second purchase",
            session=db_session
        )
        db_session.commit()
        
        # Verify final fund state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 1500.0
        
        # Verify weighted average unit price calculation
        # (1000 * 20 + 500 * 25) / 1500 = 21.67
        expected_avg_price = (1000.0 * 20.00 + 500.0 * 25.00) / 1500.0
        assert abs(fund.current_unit_price - expected_avg_price) < 0.01
        assert fund.current_nav_total == 1500.0 * expected_avg_price
        
        # Verify all events created
        events = fund.get_all_fund_events(session=db_session)
        unit_purchase_events = [e for e in events if e.event_type == EventType.UNIT_PURCHASE]
        assert len(unit_purchase_events) == 2


class TestUnitSaleWorkflow:
    """Test complete unit sale workflows from creation to completion"""

    def test_basic_unit_sale_workflow(self, db_session):
        """Test basic unit sale workflow with NAV updates"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund with existing units
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add initial unit purchase
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        fund_event_service.add_unit_purchase(
            fund=fund,
            units=1000.0,
            price=25.00,
            date=date(2023, 1, 1),
            description="Initial purchase",
            session=db_session
        )
        db_session.commit()
        
        # Verify initial state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 1000.0
        assert fund.current_unit_price == 25.00
        
        # Execute unit sale
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        event = fund_event_service.add_unit_sale(
            fund=fund,
            units=400.0,
            price=30.00,
            date=date(2023, 6, 1),
            description="Partial unit sale",
            session=db_session
        )
        db_session.commit()
        
        # Verify fund state updates
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 600.0
        # Unit price should remain the same for remaining units
        assert fund.current_unit_price == 25.00
        assert fund.current_nav_total == 600.0 * 25.00
        
        # Verify event creation
        assert event is not None
        assert event.event_type == EventType.UNIT_SALE
        assert event.units_sold == 400.0
        assert event.unit_price == 30.00
        assert event.event_date == date(2023, 6, 1)

    def test_unit_sale_with_cash_flow_integration(self, db_session):
        """Test unit sale workflow with cash flow creation and reconciliation"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, 
                       BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund and bank account
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(
            entity=entity,
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0,
            currency="AUD"
        )
        db_session.commit()
        
        # Add initial unit purchase
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        fund_event_service.add_unit_purchase(
            fund=fund,
            units=1000.0,
            price=20.00,
            date=date(2023, 1, 1),
            description="Initial purchase",
            session=db_session
        )
        db_session.commit()
        
        # Create unit sale event
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        event = fund_event_service.add_unit_sale(
            fund=fund,
            units=300.0,
            price=25.00,
            date=date(2023, 3, 1),
            description="Unit sale with cash flow",
            session=db_session
        )
        db_session.commit()
        
        # Add cash flow for the unit sale
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=7500.0,  # 300 units * $25.00
            currency="AUD",
            transfer_date=date(2023, 3, 2),
            direction=CashFlowDirection.INFLOW
        )
        db_session.commit()
        
        # Verify fund state after sale and cash flow
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 700.0
        assert fund.current_unit_price == 20.00  # Should remain unchanged
        assert fund.current_nav_total == 700.0 * 20.00
        
        # Verify cash flow integration
        assert cash_flow.fund_event_id == event.id
        assert cash_flow.amount == 7500.0
        assert cash_flow.direction == CashFlowDirection.INFLOW

    def test_unit_sale_insufficient_units_workflow(self, db_session):
        """Test unit sale workflow when attempting to sell more units than available"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund with limited units
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=50000.0
        )
        db_session.commit()
        
        # Add unit purchase
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        fund_event_service.add_unit_purchase(
            fund=fund,
            units=500.0,
            price=20.00,
            date=date(2023, 1, 1),
            description="Limited purchase",
            session=db_session
        )
        db_session.commit()
        
        # Verify initial state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 500.0
        
        # Attempt to sell more units than available
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        with pytest.raises(ValueError, match="Insufficient units"):
            fund_event_service.add_unit_sale(
                fund=fund,
                units=600.0,  # More than available
                price=25.00,
                date=date(2023, 6, 1),
                description="Excessive sale",
                session=db_session
            )
        
        # Verify fund state unchanged
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 500.0
        assert fund.current_unit_price == 20.00


class TestUnitPurchaseSaleCombinedWorkflow:
    """Test combined unit purchase and sale workflows"""

    def test_complete_unit_lifecycle_workflow(self, db_session):
        """Test complete unit lifecycle from purchase to sale to repurchase"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=150000.0
        )
        db_session.commit()
        
        # Phase 1: Initial unit purchase
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        fund_event_service.add_unit_purchase(
            fund=fund,
            units=1000.0,
            price=20.00,
            date=date(2023, 1, 1),
            description="Initial purchase",
            session=db_session
        )
        db_session.commit()
        
        # Phase 2: Additional unit purchase
        fund_event_service.add_unit_purchase(
            fund=fund,
            units=500.0,
            price=25.00,
            date=date(2023, 2, 1),
            description="Additional purchase",
            session=db_session
        )
        db_session.commit()
        
        # Phase 3: Partial unit sale
        fund_event_service.add_unit_sale(
            fund=fund,
            units=300.0,
            price=30.00,
            date=date(2023, 3, 1),
            description="Partial sale",
            session=db_session
        )
        db_session.commit()
        
        # Phase 4: Repurchase after sale
        fund_event_service.add_unit_purchase(
            fund=fund,
            units=200.0,
            price=22.00,
            date=date(2023, 4, 1),
            description="Repurchase",
            session=db_session
        )
        db_session.commit()
        
        # Verify final fund state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 1400.0  # 1000 + 500 - 300 + 200
        
        # Verify all events created
        events = fund.get_all_fund_events(session=db_session)
        unit_purchase_events = [e for e in events if e.event_type == EventType.UNIT_PURCHASE]
        unit_sale_events = [e for e in events if e.event_type == EventType.UNIT_SALE]
        
        assert len(unit_purchase_events) == 3
        assert len(unit_sale_events) == 1
        
        # Verify event ordering
        event_dates = [e.event_date for e in events]
        assert event_dates == sorted(event_dates)

    def test_unit_workflow_with_tax_implications(self, db_session):
        """Test unit purchase/sale workflow with tax statement integration"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, 
                       TaxStatementFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund and tax statement
        entity = EntityFactory.create()
        fund = FundFactory.create(
            entity=entity,
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        
        tax_statement = TaxStatementFactory.create(
            fund=fund,
            entity=entity,
            financial_year=2024
        )
        db_session.commit()
        
        # Execute unit purchase
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        purchase_event = fund_event_service.add_unit_purchase(
            fund=fund,
            units=1000.0,
            price=25.00,
            date=date(2023, 1, 1),
            description="Purchase for tax year",
            session=db_session
        )
        db_session.commit()
        
        # Execute unit sale
        sale_event = fund_event_service.add_unit_sale(
            fund=fund,
            units=400.0,
            price=30.00,
            date=date(2023, 6, 30),  # End of financial year
            description="Sale in tax year",
            session=db_session
        )
        db_session.commit()
        
        # Verify both events created and linked to fund
        assert purchase_event.fund_id == fund.id
        assert sale_event.fund_id == fund.id
        
        # Verify fund state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 600.0
        
        # Verify tax statement integration
        assert tax_statement.fund_id == fund.id
        assert tax_statement.entity_id == entity.id
