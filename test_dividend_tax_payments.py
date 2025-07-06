#!/usr/bin/env python3
"""
Test script for franked/unfranked dividend tax payment logic.
"""
import sys
import os
from datetime import date
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_database_session
from src.fund.models import Fund, FundEvent, DistributionType, EventType, TaxPaymentType
from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany
from src.tax.models import TaxStatement
from test_utils import clear_database_except_rates

def test_dividend_tax_payments():
    print("Testing franked/unfranked dividend tax payment logic...")
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    try:
        clear_database_except_rates(session)
        # Create company/entity/fund
        company = InvestmentCompany.create("DivCo", session=session)
        entity = Entity.create("DivEntity", "individual", session=session)
        fund = Fund.create(
            investment_company_id=company.id,
            entity_id=entity.id,
            name="Dividend Fund",
            fund_type="Equity",
            tracking_type="nav_based",
            session=session
        )
        # Add franked and unfranked dividends
        fund.add_distribution(
            amount=1000.0,
            date=date(2024, 1, 30),
            distribution_type=DistributionType.DIVIDEND_FRANKED,
            description="Fully franked dividend",
            session=session
        )
        fund.add_distribution(
            amount=500.0,
            date=date(2024, 2, 28),
            distribution_type=DistributionType.DIVIDEND_UNFRANKED,
            description="Unfranked dividend",
            session=session
        )
        fund.add_distribution(
            amount=2000.0,
            date=date(2024, 5, 20),
            distribution_type=DistributionType.DIVIDEND_FRANKED,
            description="Fully franked dividend",
            session=session
        )
        fund.add_distribution(
            amount=750.0,
            date=date(2024, 5, 25),
            distribution_type=DistributionType.DIVIDEND_UNFRANKED,
            description="Unfranked dividend",
            session=session
        )
        # Create tax statement for FY 2023-24
        tax_statement = TaxStatement(
            fund_id=fund.id,
            entity_id=entity.id,
            financial_year="2023-24",
            dividends_franked_taxable_rate=30.0,   # 30% tax rate
            dividends_unfranked_taxable_rate=10.0  # 10% tax rate
        )
        session.add(tax_statement)
        session.commit()
        # Call create_tax_payment_events
        fund.create_tax_payment_events(session=session)
        # Query tax payment events
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.TAX_PAYMENT
        ).all()
        print("\n=== TAX PAYMENT EVENTS CREATED ===")
        for e in events:
            print(f"Type: {e.tax_payment_type.value}, Amount: {e.amount}, Desc: {e.description}")
        # Check for correct events
        franked = [e for e in events if e.tax_payment_type == TaxPaymentType.DIVIDENDS_FRANKED_TAX]
        unfranked = [e for e in events if e.tax_payment_type == TaxPaymentType.DIVIDENDS_UNFRANKED_TAX]
        assert len(franked) == 1, "Should be one franked dividend tax event"
        assert len(unfranked) == 1, "Should be one unfranked dividend tax event"
        assert abs(franked[0].amount - 900.0) < 0.01, f"Franked tax should be 900.0, got {franked[0].amount}"
        assert abs(unfranked[0].amount - 125.0) < 0.01, f"Unfranked tax should be 125.0, got {unfranked[0].amount}"
        print("\n✅ Dividend tax payment logic works as expected!")
    finally:
        session.close()

if __name__ == "__main__":
    test_dividend_tax_payments() 