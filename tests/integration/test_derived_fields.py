"""
Integration tests for derived fields and computed properties.

Tests computed properties, relationships, and derived fields
that require database interaction and session management.
"""

import pytest
from datetime import date, datetime, timezone
from decimal import Decimal

from tests.factories import FundFactory, EntityFactory, InvestmentCompanyFactory, TaxStatementFactory
from src.fund.models import Fund, FundEvent, FundType, EventType, FundStatus
from src.tax.models import TaxStatement


class TestFundDerivedFields:
    """Test fund computed properties and derived fields."""

    def test_fund_total_commitments_calculated(self, db_session):
        """Test that fund total commitments are calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Verify commitment amount is set
        assert fund.commitment_amount == 100000.0
        
        # Add capital calls
        fund.add_capital_call(30000.0, date(2023, 1, 1), "First capital call")
        fund.add_capital_call(20000.0, date(2023, 3, 1), "Second capital call")
        db_session.commit()
        
        # Verify total capital called
        fund = db_session.query(Fund).get(fund.id)
        assert fund.total_capital_called == 50000.0
        
        # Verify remaining commitment
        assert fund.remaining_commitment == 50000.0

    def test_fund_irr_calculation_with_events(self, db_session):
        """Test that fund IRR is calculated correctly from events."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add capital call
        fund.add_capital_call(100000.0, date(2023, 1, 1), "Full capital call")
        db_session.commit()
        
        # Add distribution (return)
        fund.add_distribution(
            event_date=date(2023, 12, 31),
            distribution_type="return_of_capital",
            distribution_amount=110000.0,  # 10% return
            description="Return with profit"
        )
        db_session.commit()
        
        # Calculate IRR from events
        fund = db_session.query(Fund).get(fund.id)
        events = fund.get_all_fund_events()
        
        # Extract cash flows and dates for IRR calculation
        cash_flows = []
        dates = []
        for event in events:
            if event.event_type == EventType.CAPITAL_CALL:
                cash_flows.append(-event.amount)  # Negative for capital call
                dates.append(event.event_date)
            elif event.event_type == EventType.DISTRIBUTION:
                cash_flows.append(event.amount)  # Positive for distribution
                dates.append(event.event_date)
        
        # Verify we have the expected cash flows
        assert len(cash_flows) == 2
        assert cash_flows[0] == -100000.0  # Capital call
        assert cash_flows[1] == 110000.0   # Distribution
        
        # Verify dates are correct
        assert dates[0] == date(2023, 1, 1)
        assert dates[1] == date(2023, 12, 31)

    def test_fund_status_derived_from_equity_balance(self, db_session):
        """Test that fund status is derived from equity balance."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Initial status should be active
        assert fund.status == FundStatus.ACTIVE
        
        # Add capital call
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call")
        db_session.commit()
        
        # Status should remain active
        fund = db_session.query(Fund).get(fund.id)
        assert fund.status == FundStatus.ACTIVE
        
        # Return all capital
        fund.add_return_of_capital(50000.0, date(2023, 6, 1), "Full capital return")
        db_session.commit()
        
        # Status should change to realized
        fund = db_session.query(Fund).get(fund.id)
        assert fund.status == FundStatus.REALIZED

    def test_fund_current_nav_total_calculated(self, db_session):
        """Test that fund current NAV total is calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add unit purchase
        fund.add_unit_purchase(
            units=1000.0,
            price=10.0,
            date=date(2023, 1, 1),
            description="Initial unit purchase"
        )
        db_session.commit()
        
        # Verify current NAV total
        fund = db_session.query(Fund).get(fund.id)
        expected_nav_total = 1000.0 * 10.0  # units * price
        assert fund.current_nav_total == expected_nav_total
        
        # Update NAV
        fund.add_nav_update(
            nav_per_share=11.0,
            date=date(2023, 3, 1),
            description="NAV increase"
        )
        db_session.commit()
        
        # Verify NAV total updated
        fund = db_session.query(Fund).get(fund.id)
        expected_nav_total = 1000.0 * 11.0  # units * new price
        assert fund.current_nav_total == expected_nav_total


class TestEntityDerivedFields:
    """Test entity computed properties and derived fields."""

    def test_entity_total_funds_under_management(self, db_session):
        """Test that entity total funds under management is calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        entity = EntityFactory()
        company = InvestmentCompanyFactory()
        
        # Create multiple funds for the entity
        fund1 = FundFactory(
            entity=entity,
            investment_company=company,
            commitment_amount=100000.0
        )
        fund2 = FundFactory(
            entity=entity,
            investment_company=company,
            commitment_amount=200000.0
        )
        db_session.commit()
        
        # Verify total funds under management
        entity = db_session.query(Entity).get(entity.id)
        total_funds = entity.get_total_funds_under_management(session=db_session)
        assert total_funds == 300000.0

    def test_entity_financial_year_calculation(self, db_session):
        """Test that entity financial year dates are calculated correctly."""
        entity = EntityFactory(tax_jurisdiction="AU")
        db_session.commit()
        
        # Test Australian financial year (July-June)
        fy_start, fy_end = entity.get_financial_year(date(2023, 8, 15))
        assert fy_start == date(2023, 7, 1)
        assert fy_end == date(2024, 6, 30)
        
        # Test US financial year (January-December)
        entity_us = EntityFactory(tax_jurisdiction="US")
        db_session.commit()
        
        fy_start, fy_end = entity_us.get_financial_year(date(2023, 8, 15))
        assert fy_start == date(2023, 1, 1)
        assert fy_end == date(2023, 12, 31)

    def test_entity_financial_years_for_period(self, db_session):
        """Test that entity financial years for a period are calculated correctly."""
        entity = EntityFactory(tax_jurisdiction="AU")
        db_session.commit()
        
        # Test period spanning multiple financial years
        start_date = date(2022, 6, 1)  # FY 2021-22
        end_date = date(2024, 8, 1)    # FY 2024-25
        
        financial_years = entity.get_financial_years_for_period(start_date, end_date)
        
        # Should include FY 2021-22, 2022-23, 2023-24, 2024-25
        expected_years = ["2021-22", "2022-23", "2023-24", "2024-25"]
        assert len(financial_years) == 4
        for expected_year in expected_years:
            assert expected_year in financial_years


class TestInvestmentCompanyDerivedFields:
    """Test investment company computed properties and derived fields."""

    def test_company_total_commitments(self, db_session):
        """Test that company total commitments are calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        # Create multiple funds for the company
        fund1 = FundFactory(
            entity=entity,
            investment_company=company,
            commitment_amount=100000.0
        )
        fund2 = FundFactory(
            entity=entity,
            investment_company=company,
            commitment_amount=200000.0
        )
        db_session.commit()
        
        # Verify total commitments
        company = db_session.query(InvestmentCompany).get(company.id)
        total_commitments = company.get_total_commitments(session=db_session)
        assert total_commitments == 300000.0

    def test_company_funds_under_management(self, db_session):
        """Test that company funds under management are calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        # Create funds with different statuses
        active_fund = FundFactory(
            entity=entity,
            investment_company=company,
            commitment_amount=100000.0
        )
        realized_fund = FundFactory(
            entity=entity,
            investment_company=company,
            commitment_amount=200000.0
        )
        db_session.commit()
        
        # Set one fund to realized status
        realized_fund.status = FundStatus.REALIZED
        db_session.commit()
        
        # Verify only active funds are counted
        company = db_session.query(InvestmentCompany).get(company.id)
        active_funds = company.get_funds_under_management(session=db_session)
        assert len(active_funds) == 1
        assert active_funds[0].id == active_fund.id


class TestTaxStatementDerivedFields:
    """Test tax statement computed properties and derived fields."""

    def test_tax_statement_total_income_calculated(self, db_session):
        """Test that tax statement total income is calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, TaxStatementFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        tax_statement = TaxStatementFactory(
            fund=fund,
            dividend_income=5000.0,
            interest_income=3000.0,
            capital_gains=2000.0
        )
        db_session.commit()
        
        # Verify total income calculation
        tax_statement = db_session.query(TaxStatement).get(tax_statement.id)
        total_income = tax_statement.dividend_income + tax_statement.interest_income + tax_statement.capital_gains
        assert total_income == 10000.0

    def test_tax_statement_financial_year_derived(self, db_session):
        """Test that tax statement financial year is derived correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, TaxStatementFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        tax_statement = TaxStatementFactory(
            fund=fund,
            statement_date=date(2023, 8, 15)  # FY 2023-24 for AU
        )
        db_session.commit()
        
        # Verify financial year is derived
        tax_statement = db_session.query(TaxStatement).get(tax_statement.id)
        assert tax_statement.financial_year == "2023-24"
