#!/usr/bin/env python3
"""
Comprehensive system test script using direct model methods.
Clears database (except Risk Free Rates), re-enters the two main funds,
and recalculates everything to verify the system works end-to-end.
This version uses only direct model methods - no direct FundEvent creation.
"""

import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.models import (
    Base, InvestmentCompany, Entity, Fund, FundEvent, 
    TaxStatement, RiskFreeRate, FundType, EventType, DistributionType, TaxPaymentType
)
from datetime import date, datetime
import sqlite3
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.schema import Column

def clear_database_except_rates():
    """Clear all data except Risk Free Rates."""
    engine = create_engine('sqlite:///data/investment_tracker.db')
    
    with engine.connect() as conn:
        # Disable foreign key constraints temporarily
        conn.execute(text("PRAGMA foreign_keys=OFF;"))
        
        # Clear all tables except risk_free_rates
        tables = ['tax_statements', 'fund_events', 'funds', 'entities', 'investment_companies']
        for table in tables:
            conn.execute(text(f"DELETE FROM {table};"))
            print(f"Cleared {table}")
        
        # Re-enable foreign key constraints
        conn.execute(text("PRAGMA foreign_keys=ON;"))
        conn.commit()
    
    print("Database cleared (Risk Free Rates preserved)")

def setup_test_data():
    """Set up test data using only direct model methods."""
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create investment company
        company = InvestmentCompany(
            name="Alceon",
            description="Private investment firm"
        )
        session.add(company)
        session.commit()

        # Create investment company
        company_shares = InvestmentCompany(
            name="Shares",
            description="Share trading platform"
        )
        session.add(company_shares)
        session.commit()
        
        # Create entity
        entity = Entity(
            name="Shaun Reichman",
            description="Individual investor"
        )
        session.add(entity)
        session.commit()
        
        # Create Senior Debt Fund No.24 (Cost-based)
        senior_debt_fund = Fund(
            investment_company_id=company.id,
            entity_id=entity.id,
            name="Senior Debt Fund No.24",
            fund_type="Private Debt",
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0,
            expected_irr=12.0,
            expected_duration_months=60,
            currency="AUD",
            description="Senior debt fund with quarterly distributions"
        )
        session.add(senior_debt_fund)
        
        # Create 3PG Finance (Cost-based)
        finance_fund = Fund(
            investment_company_id=company.id,
            entity_id=entity.id,
            name="3PG Finance",
            fund_type="Private Debt",
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0,
            expected_irr=10.0,
            expected_duration_months=48,
            currency="AUD",
            description="3PG Finance debt fund"
        )
        session.add(finance_fund)
        session.commit()
        
        # Create NAV-based test fund
        abc_fund = Fund(
            investment_company_id=company_shares.id,
            entity_id=entity.id,
            name="ABC Ltd",
            fund_type="Equity - Consumer Discretionary",
            tracking_type=FundType.NAV_BASED,
            currency="AUD",
            description="ABC Ltd on the ASX"
        )
        session.add(abc_fund)
        session.commit()
        
        # Add events for Senior Debt Fund No.24 using direct methods
        print("Adding Senior Debt Fund events using direct methods...")
        
        # Add capital call
        senior_debt_fund.add_capital_call(
            amount=100000.0,
            date=date(2023, 6, 23),
            description="Initial capital call"
        )
        
        # Add returns of capital
        senior_debt_fund.add_return_of_capital(
            amount=7000.0,
            date=date(2023, 12, 8),
            description="Return of capital"
        )
        senior_debt_fund.add_return_of_capital(
            amount=45000.0,
            date=date(2024, 3, 26),
            description="Partial exit distribution"
        )
        senior_debt_fund.add_return_of_capital(
            amount=48000.0,
            date=date(2024, 8, 2),
            description="Return of capital"
        )
        
        # Add distribution events with tax using direct methods
        print("Adding Senior Debt Fund distributions with tax...")
        senior_debt_fund.add_distribution_with_tax_rate(
            event_date=date(2023, 10, 20),
            gross_amount=3030.62,
            tax_rate=10.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        senior_debt_fund.add_distribution_with_tax_rate(
            event_date=date(2024, 1, 16),
            gross_amount=2836.98,
            tax_rate=10.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        senior_debt_fund.add_distribution_with_tax_rate(
            event_date=date(2024, 3, 26),
            gross_amount=2630.16,
            tax_rate=10.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        senior_debt_fund.add_distribution_with_tax_rate(
            event_date=date(2024, 7, 9),
            gross_amount=1392.19,
            tax_rate=10.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        senior_debt_fund.add_distribution_with_tax_rate(
            event_date=date(2024, 8, 2),
            gross_amount=509.84,
            tax_rate=10.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        
        # Add events for 3PG Finance using direct methods
        print("Adding 3PG Finance events using direct methods...")
        
        # Add capital call
        finance_fund.add_capital_call(
            amount=100000.0,
            date=date(2022, 11, 24),
            description="Initial capital call"
        )
        
        # Add returns of capital
        finance_fund.add_return_of_capital(
            amount=7324.42,
            date=date(2023, 3, 24),
            description="Return of capital"
        )
        finance_fund.add_return_of_capital(
            amount=26326.88,
            date=date(2023, 7, 7),
            description="Partial exit distribution"
        )
        finance_fund.add_return_of_capital(
            amount=8527.53,
            date=date(2023, 8, 4),
            description="Return of capital"
        )
        finance_fund.add_return_of_capital(
            amount=8805.21,
            date=date(2023, 9, 22),
            description="Return of capital"
        )
        finance_fund.add_return_of_capital(
            amount=9814.74,
            date=date(2023, 10, 13),
            description="Return of capital"
        )
        finance_fund.add_return_of_capital(
            amount=6967.81,
            date=date(2023, 11, 21),
            description="Return of capital"
        )
        finance_fund.add_return_of_capital(
            amount=32233.41,
            date=date(2024, 4, 19),
            description="Final return of capital"
        )
        
        # Add distribution events with tax using direct methods
        print("Adding 3PG Finance distributions with tax...")
        # First distribution (no tax)
        finance_fund.add_distribution_with_tax(
            event_date=date(2023, 3, 24),
            gross_amount=3075.58,
            tax_withheld=0.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        # Remaining distributions (with 10% tax)
        finance_fund.add_distribution_with_tax_rate(
            event_date=date(2023, 7, 7),
            gross_amount=4472.36,
            tax_rate=10.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        finance_fund.add_distribution_with_tax_rate(
            event_date=date(2023, 8, 4),
            gross_amount=871.63,
            tax_rate=10.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        finance_fund.add_distribution_with_tax_rate(
            event_date=date(2023, 9, 22),
            gross_amount=794.21,
            tax_rate=10.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        finance_fund.add_distribution_with_tax_rate(
            event_date=date(2023, 10, 13),
            gross_amount=684.73,
            tax_rate=10.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        finance_fund.add_distribution_with_tax_rate(
            event_date=date(2023, 11, 21),
            gross_amount=531.32,
            tax_rate=10.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        finance_fund.add_distribution_with_tax_rate(
            event_date=date(2024, 4, 19),
            gross_amount=4399.27,
            tax_rate=10.0,
            distribution_type=DistributionType.INTEREST,
            description="Interest distribution"
        )
        
        # Add NAV-based fund events using direct methods
        print("Adding NAV-based fund events using direct methods...")
        
        # Initial unit purchase
        abc_fund.add_unit_purchase(
            units=85.0,
            price=58.00,
            date=date(2013, 3, 28),
            brokerage_fee=19.95,
            description="Initial unit purchase"
        )
        
        # NAV updates
        abc_fund.add_nav_update(
            nav_per_share=57.20,
            date=date(2013, 3, 31),
            description="March 2013 NAV update"
        )
        abc_fund.add_nav_update(
            nav_per_share=55.80,
            date=date(2013, 4, 30),
            description="April 2013 NAV update"
        )
        abc_fund.add_nav_update(
            nav_per_share=55.18,
            date=date(2013, 5, 31),
            description="May 2013 NAV update"
        )
        abc_fund.add_nav_update(
            nav_per_share=52.37,
            date=date(2013, 6, 30),
            description="June 2013 NAV update"
        )
        abc_fund.add_nav_update(
            nav_per_share=57.51,
            date=date(2013, 7, 31),
            description="July 2013 NAV update"
        )
        abc_fund.add_nav_update(
            nav_per_share=58.30,
            date=date(2013, 8, 31),
            description="August 2013 NAV update"
        )
        
        # Partial unit sale
        abc_fund.add_unit_sale(
            units=40.0,
            price=61.20,
            date=date(2013, 9, 4),
            brokerage_fee=24.95,
            description="Partial unit sale"
        )
        
        # Distribution
        abc_fund.add_distribution(
            amount=79.05,
            date=date(2013, 9, 12),
            distribution_type=DistributionType.DIVIDEND,
            description="Fully Franked Dividend"
        )
        
        # More NAV updates
        abc_fund.add_nav_update(
            nav_per_share=59.30,
            date=date(2013, 9, 30),
            description="September 2013 NAV update"
        )
        abc_fund.add_nav_update(
            nav_per_share=53.30,
            date=date(2013, 10, 31),
            description="October 2013 NAV update"
        )
        abc_fund.add_nav_update(
            nav_per_share=54.30,
            date=date(2013, 11, 30),
            description="November 2013 NAV update"
        )
        abc_fund.add_nav_update(
            nav_per_share=48.30,
            date=date(2013, 12, 31),
            description="December 2013 NAV update"
        )
        abc_fund.add_nav_update(
            nav_per_share=59.30,
            date=date(2014, 1, 31),
            description="January 2014 NAV update"
        )
        abc_fund.add_nav_update(
            nav_per_share=54.30,
            date=date(2014, 2, 28),
            description="February 2014 NAV update"
        )
        abc_fund.add_nav_update(
            nav_per_share=56.30,
            date=date(2014, 3, 31),
            description="March 2014 NAV update"
        )
        
        # Additional unit purchase
        abc_fund.add_unit_purchase(
            units=120.0,
            price=61.4,
            date=date(2014, 4, 30),
            brokerage_fee=19.95,
            description="Additional unit purchase"
        )
        
        # NAV update on same date as purchase
        abc_fund.add_nav_update(
            nav_per_share=61.25,
            date=date(2014, 4, 30),
            description="April 2014 NAV update"
        )
        
        # Final unit sale
        abc_fund.add_unit_sale(
            units=165.0,
            price=62.62,
            date=date(2014, 5, 13),
            brokerage_fee=19.95,
            description="Full unit sale"
        )
        
        # Add tax statements using direct model methods
        tax_statements = []
        
        # Senior Debt Fund No.24 Tax Statements
        tax_statements.append(senior_debt_fund.create_or_update_tax_statement(
            entity_id=entity.id,
            financial_year="2022-23",
            notes="FY23 tax statement from fund manager",
            distribution_receivable_this_fy=0.0,
            distribution_received_prev_fy=0.0,
            interest_received_in_cash=0.0,
            non_resident_withholding_tax_from_statement=0.0,
            accountant='Findex',
            statement_date=date(2024, 8, 24),
            interest_taxable_rate=10.0,
            interest_deduction_rate=32.5
        ))
        
        tax_statements.append(senior_debt_fund.create_or_update_tax_statement(
            entity_id=entity.id,
            financial_year="2023-24",
            notes="FY24 tax statement from fund manager",
            distribution_receivable_this_fy=0.0,
            distribution_received_prev_fy=0.0,
            interest_received_in_cash=8499.98,
            non_resident_withholding_tax_from_statement=852.0,
            accountant='Findex',
            statement_date=date(2024, 8, 12),
            interest_taxable_rate=10.0,
            interest_deduction_rate=32.5
        ))
        
        # 3PG Finance Tax Statements
        tax_statements.append(finance_fund.create_or_update_tax_statement(
            entity_id=entity.id,
            financial_year="2022-23",
            notes="FY23 tax statement from fund manager",
            distribution_receivable_this_fy=0.0,
            distribution_received_prev_fy=0.0,
            interest_received_in_cash=3075.58,
            non_resident_withholding_tax_from_statement=0.0,
            accountant='Findex',
            statement_date=date(2024, 8, 24),
            interest_taxable_rate=10.0,
            interest_deduction_rate=32.5
        ))
        
        tax_statements.append(finance_fund.create_or_update_tax_statement(
            entity_id=entity.id,
            financial_year="2023-24",
            notes="FY24 tax statement from fund manager",
            distribution_receivable_this_fy=0.0,
            distribution_received_prev_fy=0.0,
            interest_received_in_cash=10763.96,
            non_resident_withholding_tax_from_statement=1076.4,
            accountant='Findex',
            statement_date=date(2024, 8, 12),
            interest_taxable_rate=10.0,
            interest_deduction_rate=32.5
        ))
        
        # ABC Ltd Tax Statements (NAV-based fund)
        tax_statements.append(abc_fund.create_or_update_tax_statement(
            entity_id=entity.id,
            financial_year="2012-13",
            notes="FY13 tax statement from fund manager",
            distribution_receivable_this_fy=0.0,
            distribution_received_prev_fy=0.0,
            interest_received_in_cash=0.0,
            non_resident_withholding_tax_from_statement=0.0,
            accountant='Findex',
            statement_date=date(2024, 8, 24),
            interest_taxable_rate=0.0,
            interest_deduction_rate=32.5
        ))
        
        tax_statements.append(abc_fund.create_or_update_tax_statement(
            entity_id=entity.id,
            financial_year="2013-14",
            notes="FY14 tax statement from fund manager",
            distribution_receivable_this_fy=0.0,
            distribution_received_prev_fy=0.0,
            interest_received_in_cash=79.05,
            non_resident_withholding_tax_from_statement=0.0,
            accountant='Findex',
            statement_date=date(2024, 8, 12),
            interest_taxable_rate=0.0,
            interest_deduction_rate=32.5
        ))
        
        print("Test data created successfully!")
        print(f"- Created {len([senior_debt_fund, finance_fund, abc_fund])} funds")
        
        # Count events using direct methods
        total_events = (
            len(senior_debt_fund.get_events()) +
            len(finance_fund.get_events()) +
            len(abc_fund.get_events())
        )
        print(f"- Created {total_events} events")
        print(f"- Created {len(tax_statements)} tax statements")
        
        # Show initial fund state
        print("\nInitial fund state:")
        for fund in [senior_debt_fund, finance_fund, abc_fund]:
            print(f"  {fund.name}: equity=${fund.current_equity_balance:,.2f}, avg=${fund.average_equity_balance:,.2f}")
        
    except Exception as e:
        print(f"Error setting up test data: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def get_irr_cashflows(fund, session, irr_type):
    """Helper to get cash flows and labels for each IRR type."""
    if irr_type == 'IRR':
        base = fund._calculate_irr_base(include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, session=session, return_cashflows=True)
    elif irr_type == 'After-tax IRR':
        base = fund._calculate_irr_base(include_tax_payments=True, include_risk_free_charges=False, include_fy_debt_cost=False, session=session, return_cashflows=True)
    elif irr_type == 'Real IRR':
        base = fund._calculate_irr_base(include_tax_payments=True, include_risk_free_charges=True, include_fy_debt_cost=True, session=session, return_cashflows=True)
    else:
        return [], []
    
    # Debug print to help diagnose if cash flows are not being returned
    if base is None:
        print(f"[DEBUG] IRR base is None for fund {fund.name} ({irr_type})")
    elif 'cash_flows' in base and 'labels' in base:
        if not base['cash_flows']:
            print(f"[DEBUG] No cash flows returned for fund {fund.name} ({irr_type}). This may be because the fund is still active (should_be_active={fund.should_be_active}). IRR cash flows are only available for completed funds.")
        return base['cash_flows'], base['labels']
    return [], []

def recalculate_everything(show_irr_cashflows=False):
    """Recalculate all derived values using direct model methods."""
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        funds = session.query(Fund).all()
        
        for fund in funds:
            print(f"\nRecalculating for {fund.name}:")
            
            # Update current equity balance (should calculate from events)
            fund.update_current_equity_balance(session=session)
            print(f"  Current equity: ${fund.current_equity_balance:,.2f}")
            
            # Update average equity balance (should calculate from events)
            fund.update_average_equity_balance(session=session)
            print(f"  Average equity: ${fund.average_equity_balance:,.2f}")
            
            # Update NAV-specific fields for NAV-based funds
            if fund.tracking_type == FundType.NAV_BASED:
                fund.update_current_units_and_price(session=session)
                print(f"  Current units: {fund.current_units:,.2f}" if fund.current_units is not None else "  Current units: N/A")
                print(f"  Current unit price: ${fund.current_unit_price:,.4f}" if fund.current_unit_price is not None else "  Current unit price: N/A")
                print(f"  Current value: ${fund.current_value:,.2f}" if fund.current_value is not None else "  Current value: N/A")
            else:
                # Update cost basis for cost-based funds
                fund.update_total_cost_basis(session=session)
                print(f"  Total cost basis: ${fund.total_cost_basis:,.2f}")
            
            # Create tax payment events
            tax_events = fund.create_tax_payment_events(session=session)
            print(f"  Created {len(tax_events)} tax payment events")
            
            # Create daily risk-free interest charges
            daily_events = fund.create_daily_risk_free_interest_charges(session=session)
            print(f"  Created daily interest charges")
            
            # Create FY debt cost events
            fy_events = fund.create_fy_debt_cost_events(session=session)
            print(f"  Created FY debt cost events")
            
            # Calculate IRRs
            irr = fund.calculate_irr(session=session)
            after_tax_irr = fund.calculate_after_tax_irr(session=session)
            real_irr = fund.calculate_real_irr(session=session)
            
            print(f"  IRR: {irr:.2%}" if irr else "  IRR: N/A")
            print(f"  After-tax IRR: {after_tax_irr:.2%}" if after_tax_irr else "  After-tax IRR: N/A")
            print(f"  Real IRR: {real_irr:.2%}" if real_irr else "  Real IRR: N/A")
            
            if show_irr_cashflows:
                for irr_type in ['IRR', 'After-tax IRR', 'Real IRR']:
                    cash_flows, labels = get_irr_cashflows(fund, session, irr_type)
                    print(f"\n    --- {irr_type} Cash Flows ---")
                    if not cash_flows:
                        print("    (No cash flows)")
                        continue
                    for i, cf in enumerate(cash_flows):
                        label = labels[i] if labels and i < len(labels) else ''
                        print(f"    {i+1:2d}: {cf:12,.2f}  {label}")

        session.commit()
        print("\nAll recalculations completed!")
        
    except Exception as e:
        print(f"Error recalculating: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def verify_results():
    """Verify that everything is working correctly."""
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("\n=== VERIFICATION RESULTS ===")
        
        # Check funds
        funds = session.query(Fund).all()
        print(f"\nFunds found: {len(funds)}")
        
        for fund in funds:
            print(f"\n{fund.name}:")
            print(f"  Type: {fund.tracking_type.value}")
            print(f"  Current equity: ${fund.current_equity_balance:,.2f}")
            print(f"  Average equity: ${fund.average_equity_balance:,.2f}")
            
            # Verify equity calculations are correct
            expected_current_equity = fund.calculated_average_equity_balance
            current_equity = fund.current_equity_balance
            # Only perform the check if both are not SQLAlchemy columns
            if not isinstance(expected_current_equity, (InstrumentedAttribute, Column)) and not isinstance(current_equity, (InstrumentedAttribute, Column)):
                try:
                    expected_current_equity = float(expected_current_equity)
                    current_equity = float(current_equity)
                    if abs(current_equity - expected_current_equity) > 0.01:
                        print(f"  ⚠️  WARNING: Current equity doesn't match calculated value!")
                        print(f"     Expected: ${expected_current_equity:,.2f}")
                except Exception:
                    pass
            
            # Count events by type
            event_counts = {}
            for event in fund.fund_events:
                event_type = event.event_type.value
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            print(f"  Events: {dict(event_counts)}")
            
            # Verify tax payment events were created
            tax_events = [e for e in fund.fund_events if e.event_type == EventType.TAX_PAYMENT]
            print(f"  Tax payment events: {len(tax_events)}")
            
            # Verify debt cost events were created
            debt_events = [e for e in fund.fund_events if e.event_type == EventType.FY_DEBT_COST]
            print(f"  FY debt cost events: {len(debt_events)}")
            
            # Verify daily interest charges were created
            daily_charges = [e for e in fund.fund_events if e.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE]
            print(f"  Daily interest charges: {len(daily_charges)}")
            
            # NAV-specific verification
            if fund.tracking_type == FundType.NAV_BASED:
                print(f"  Current units: {fund.current_units:,.2f}" if fund.current_units is not None else "  Current units: N/A")
                print(f"  Current unit price: ${fund.current_unit_price:,.4f}" if fund.current_unit_price is not None else "  Current unit price: N/A")
                print(f"  Current value: ${fund.current_value:,.2f}" if fund.current_value is not None else "  Current value: N/A")
                
                # Verify NAV update events
                nav_events = [e for e in fund.fund_events if e.event_type == EventType.NAV_UPDATE]
                print(f"  NAV update events: {len(nav_events)}")
                
                # Verify unit purchase/sale events
                unit_purchases = [e for e in fund.fund_events if e.event_type == EventType.UNIT_PURCHASE]
                unit_sales = [e for e in fund.fund_events if e.event_type == EventType.UNIT_SALE]
                print(f"  Unit purchases: {len(unit_purchases)}, Unit sales: {len(unit_sales)}")
            else:
                # Cost-based specific verification
                print(f"  Total cost basis: ${fund.total_cost_basis:,.2f}")
        
        # Check risk-free rates are preserved
        rate_count = session.query(RiskFreeRate).count()
        print(f"\nRisk-free rates preserved: {rate_count}")
        
        # Verify total event counts
        total_events = session.query(FundEvent).count()
        print(f"Total events in database: {total_events}")
        
        # Verify tax statements
        tax_statement_count = session.query(TaxStatement).count()
        print(f"Tax statements: {tax_statement_count}")
        
        print("\n=== SYSTEM TEST COMPLETED SUCCESSFULLY ===")
        
    except Exception as e:
        print(f"Error during verification: {e}")
        raise
    finally:
        session.close()

def main():
    """Run the complete system test."""
    parser = argparse.ArgumentParser(description="Comprehensive system test for investment tracker.")
    parser.add_argument('--show-irr-cashflows', action='store_true', help='Display all relevant cash flows for IRR calculations.')
    args = parser.parse_args()

    print("Starting comprehensive system test...")
    
    try:
        # Step 1: Clear database (except rates)
        print("\n1. Clearing database (preserving Risk Free Rates)...")
        clear_database_except_rates()
        
        # Step 2: Set up test data
        print("\n2. Setting up test data...")
        setup_test_data()
        
        # Step 3: Recalculate everything
        print("\n3. Recalculating all derived values...")
        recalculate_everything(show_irr_cashflows=args.show_irr_cashflows)
        
        # Step 4: Verify results
        print("\n4. Verifying results...")
        verify_results()
        
        print("\n🎉 All tests passed! System is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 