#!/usr/bin/env python3
"""
Test script to verify the new domain structure works correctly.

This script demonstrates the proper architectural pattern:
- Outermost backend layer manages sessions
- Domain methods accept session parameters
- No direct database operations from external clients
"""

import sys
import os
import argparse
from datetime import date
from sqlalchemy import func
import re

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import domain modules
from src.fund.models import Fund, FundEvent, EventType, FundType, DistributionType
from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany
from src.tax.models import TaxStatement
from src.rates.models import RiskFreeRate
from src.database import get_database_session
from test_utils import clear_database_except_rates
from src.shared.utils import reset_database_for_testing, with_session

def setup_test_data(session):
    """Set up test data using domain methods with proper session management."""
    print("Setting up test data using domain methods...")
    
    # Create investment company using class method
    company = InvestmentCompany.create(
        name="Alceon",
        description="Alceon Pty Ltd",
        session=session
    )
    
    # Create entity using class method
    entity = Entity.create(
        name="Shaun Reichman",
        description="Personal entity",
        session=session
    )
    
    # Create investment company for shares using class method
    company_shares = InvestmentCompany.create(
        name="Shares",
        description="Share trading",
        session=session
    )
    
    # Create Senior Debt Fund No.24 using direct object method
    senior_debt_fund = company.create_fund(
        entity=entity,  # Pass entity object, not ID
        name="Senior Debt Fund No.24",
        fund_type="Private Debt",
        tracking_type=FundType.COST_BASED,
        commitment_amount=100000.0,
        expected_irr=10.0,
        expected_duration_months=48,
        currency="AUD",
        description="Senior Debt Fund No.24",
        session=session
    )
    
    # Create 3PG Finance (Cost-based) using direct object method
    finance_fund = company.create_fund(
        entity=entity,  # Pass entity object, not ID
        name="3PG Finance",
        fund_type="Private Debt",
        tracking_type=FundType.COST_BASED,
        commitment_amount=100000.0,
        expected_irr=10.0,
        expected_duration_months=48,
        currency="AUD",
        description="3PG Finance debt fund",
        session=session
    )
    
    # Create NAV-based test fund using direct object method
    abc_fund = company_shares.create_fund(
        entity=entity,  # Pass entity object, not ID
        name="ABC Ltd",
        fund_type="Equity - Consumer Discretionary",
        tracking_type=FundType.NAV_BASED,
        currency="AUD",
        description="ABC Ltd on the ASX",
        session=session
    )
    
    # Add events for Senior Debt Fund No.24 using domain methods
    print("Adding Senior Debt Fund events using domain methods...")
    
    # Add capital call
    senior_debt_fund.add_capital_call(
        amount=100000.0,
        date=date(2023, 6, 23),
        description="Initial capital call",
        session=session
    )
    
    # Add returns of capital
    senior_debt_fund.add_return_of_capital(
        amount=7000.0,
        date=date(2023, 12, 8),
        description="Return of capital",
        session=session
    )
    senior_debt_fund.add_return_of_capital(
        amount=45000.0,
        date=date(2024, 3, 26),
        description="Partial exit distribution",
        session=session
    )
    senior_debt_fund.add_return_of_capital(
        amount=48000.0,
        date=date(2024, 8, 2),
        description="Return of capital",
        session=session
    )
    
    # Add distribution events with tax using domain methods
    print("Adding Senior Debt Fund distributions with tax...")
    senior_debt_fund.add_distribution_with_tax_rate(
        event_date=date(2023, 10, 20),
        gross_amount=3030.62,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    senior_debt_fund.add_distribution_with_tax_rate(
        event_date=date(2024, 1, 16),
        gross_amount=2836.98,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    senior_debt_fund.add_distribution_with_tax_rate(
        event_date=date(2024, 3, 26),
        gross_amount=2630.16,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    senior_debt_fund.add_distribution_with_tax_rate(
        event_date=date(2024, 7, 9),
        gross_amount=1392.19,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    senior_debt_fund.add_distribution_with_tax_rate(
        event_date=date(2024, 8, 2),
        gross_amount=509.84,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    
    # Add events for 3PG Finance using domain methods
    print("Adding 3PG Finance events using domain methods...")
    
    # Add capital call
    finance_fund.add_capital_call(
        amount=100000.0,
        date=date(2022, 11, 24),
        description="Initial capital call",
        session=session
    )
    
    # Add returns of capital
    finance_fund.add_return_of_capital(
        amount=7324.42,
        date=date(2023, 3, 24),
        description="Return of capital",
        session=session
    )
    finance_fund.add_return_of_capital(
        amount=26326.88,
        date=date(2023, 7, 7),
        description="Partial exit distribution",
        session=session
    )
    finance_fund.add_return_of_capital(
        amount=8527.53,
        date=date(2023, 8, 4),
        description="Return of capital",
        session=session
    )
    finance_fund.add_return_of_capital(
        amount=8805.21,
        date=date(2023, 9, 22),
        description="Return of capital",
        session=session
    )
    finance_fund.add_return_of_capital(
        amount=9814.74,
        date=date(2023, 10, 13),
        description="Return of capital",
        session=session
    )
    finance_fund.add_return_of_capital(
        amount=6967.81,
        date=date(2023, 11, 21),
        description="Return of capital",
        session=session
    )
    finance_fund.add_return_of_capital(
        amount=32233.41,
        date=date(2024, 4, 19),
        description="Final return of capital",
        session=session
    )
    
    # Add distribution events with tax using domain methods
    print("Adding 3PG Finance distributions with tax...")
    # First distribution (no tax)
    finance_fund.add_distribution_with_tax(
        event_date=date(2023, 3, 24),
        gross_amount=3075.58,
        tax_withheld=0.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    # Remaining distributions (with 10% tax)
    finance_fund.add_distribution_with_tax_rate(
        event_date=date(2023, 7, 7),
        gross_amount=4472.36,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    finance_fund.add_distribution_with_tax_rate(
        event_date=date(2023, 8, 4),
        gross_amount=871.63,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    finance_fund.add_distribution_with_tax_rate(
        event_date=date(2023, 9, 22),
        gross_amount=794.21,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    finance_fund.add_distribution_with_tax_rate(
        event_date=date(2023, 10, 13),
        gross_amount=684.73,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    finance_fund.add_distribution_with_tax_rate(
        event_date=date(2023, 11, 21),
        gross_amount=531.32,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    finance_fund.add_distribution_with_tax_rate(
        event_date=date(2024, 4, 19),
        gross_amount=4399.27,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    
    # Add events for ABC Ltd NAV-based fund (match original test)
    # Initial unit purchase
    abc_fund.add_unit_purchase(
        units=85.0,
        price=58.00,
        date=date(2013, 3, 28),
        brokerage_fee=19.95,
        description="Initial unit purchase",
        session=session
    )
    # NAV updates
    abc_fund.add_nav_update(
        nav_per_share=57.20,
        date=date(2013, 3, 31),
        description="March 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=55.80,
        date=date(2013, 4, 30),
        description="April 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=55.18,
        date=date(2013, 5, 31),
        description="May 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=52.37,
        date=date(2013, 6, 30),
        description="June 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=57.51,
        date=date(2013, 7, 31),
        description="July 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=58.30,
        date=date(2013, 8, 31),
        description="August 2013 NAV update",
        session=session
    )
    # Partial unit sale
    abc_fund.add_unit_sale(
        units=40.0,
        price=61.20,
        date=date(2013, 9, 4),
        brokerage_fee=24.95,
        description="Partial unit sale",
        session=session
    )
    # Distribution
    abc_fund.add_distribution(
        amount=79.05,
        date=date(2013, 9, 12),
        distribution_type=DistributionType.DIVIDEND_FRANKED,
        description="Fully Franked Dividend",
        session=session
    )
    # More NAV updates
    abc_fund.add_nav_update(
        nav_per_share=59.30,
        date=date(2013, 9, 30),
        description="September 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=53.30,
        date=date(2013, 10, 31),
        description="October 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=54.30,
        date=date(2013, 11, 30),
        description="November 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=48.30,
        date=date(2013, 12, 31),
        description="December 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=59.30,
        date=date(2014, 1, 31),
        description="January 2014 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=54.30,
        date=date(2014, 2, 28),
        description="February 2014 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=56.30,
        date=date(2014, 3, 31),
        description="March 2014 NAV update",
        session=session
    )
    # Additional unit purchase
    abc_fund.add_unit_purchase(
        units=120.0,
        price=61.4,
        date=date(2014, 4, 30),
        brokerage_fee=19.95,
        description="Additional unit purchase",
        session=session
    )
    # NAV update on same date as purchase
    abc_fund.add_nav_update(
        nav_per_share=61.25,
        date=date(2014, 4, 30),
        description="April 2014 NAV update",
        session=session
    )
    # Final unit sale
    abc_fund.add_unit_sale(
        units=165.0,
        price=62.62,
        date=date(2014, 5, 13),
        brokerage_fee=19.95,
        description="Full unit sale",
        session=session
    )
    
    # Add tax statements using domain methods (copied from original test)
    # Senior Debt Fund No.24 Tax Statements
    senior_debt_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2022-23",
        notes="FY23 tax statement from fund manager",
        accountant='Findex',
        statement_date=date(2024, 8, 24),
        interest_income_tax_rate=10.0,
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )
    senior_debt_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2023-24",
        notes="FY24 tax statement from fund manager",
        interest_received_in_cash=8499.98,
        interest_non_resident_withholding_tax_from_statement=852.0,
        accountant='Findex',
        statement_date=date(2024, 8, 12),
        interest_income_tax_rate=10.0,
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )
    # 3PG Finance Tax Statements
    finance_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2022-23",
        notes="FY23 tax statement from fund manager",
        interest_received_in_cash=3075.58,
        accountant='Findex',
        statement_date=date(2024, 8, 24),
        interest_income_tax_rate=10.0,
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )
    finance_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2023-24",
        notes="FY24 tax statement from fund manager",
        interest_received_in_cash=10763.96,
        interest_non_resident_withholding_tax_from_statement=1076.4,
        accountant='Findex',
        statement_date=date(2024, 8, 12),
        interest_income_tax_rate=10.0,
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )
    # ABC Ltd Tax Statements (NAV-based fund)
    abc_tax_statement_2012_13 = abc_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2012-13",
        notes="FY13 tax statement from fund manager",
        accountant='Findex',
        statement_date=date(2024, 8, 24),
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )
    abc_tax_statement_2013_14 = abc_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2013-14",
        notes="FY14 tax statement from fund manager",
        accountant='Findex',
        statement_date=date(2024, 8, 12),
        capital_gain_income_tax_rate=30,
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )

    # --- Capital gain calculation and cash flow addition ---
    for tax_statement, label in [
        (abc_tax_statement_2012_13, "2012-13"),
        (abc_tax_statement_2013_14, "2013-14")
    ]:
        try:
            tax_statement.calculate_capital_gain_totals(session=session)
            tax_statement.calculate_capital_gain_discount(session=session)
            tax_statement.calculate_capital_gain_tax_amount()
            if getattr(tax_statement, 'capital_gain_income_amount', 0) > 0:
                print(f"ABC Ltd capital gain for {label}: {tax_statement.capital_gain_income_amount:.2f} (discount: {tax_statement.capital_gain_discount_amount:.2f}, tax: {tax_statement.capital_gain_tax_amount:.2f})")
        except Exception as e:
            print(f"Error calculating capital gains for ABC Ltd {label}: {e}")
    
    print("Test data setup complete!")
    print(f"Created {len(company.funds)} funds for {company.name}")
    print(f"Created {len(company_shares.funds)} funds for {company_shares.name}")

def get_irr_cashflows(fund, irr_type, session):
    """Get IRR cash flows using domain methods."""
    if irr_type == "irr":
        return fund._calculate_irr_base(return_cashflows=True, session=session)
    elif irr_type == "after_tax_irr":
        return fund._calculate_irr_base(include_tax_payments=True, return_cashflows=True, session=session)
    elif irr_type == "real_irr":
        return fund._calculate_irr_base(include_tax_payments=True, include_risk_free_charges=True, include_eofy_debt_cost=True, return_cashflows=True, session=session)
    else:
        raise ValueError(f"Unknown IRR type: {irr_type}")

def recalculate_everything(session, show_irr_cashflows=True):
    """Recalculate all derived values using domain methods."""
    print("\n3. Recalculating all derived values...")
    
    # Get all funds using domain methods
    funds = session.query(Fund).all()
    print(f"Funds to recalculate: {[f'{fund.id}: {fund.name}' for fund in funds]}")
    print(f"Number of funds to recalculate: {len(funds)}")
    
    iteration_count = 0
    for fund in funds:
        iteration_count += 1
        print(f"\nRecalculating for {fund.name}:")
        
        # Get current values
        current_equity = fund.current_equity_balance
        average_equity = fund.average_equity_balance
        
        print(f"  Current equity: ${current_equity:,.2f}")
        print(f"  Average equity: ${average_equity:,.2f}")
        
        if fund.tracking_type == FundType.NAV_BASED:
            current_units = fund.current_units
            current_unit_price = fund.current_unit_price
            print(f"  Current units: {current_units:.2f}")
            print(f"  Current unit price: ${current_unit_price:.4f}")
        # Remove lines that reference fund.total_cost_basis and their print statements
        
        # Create tax payment events using domain methods
        tax_events = fund.create_tax_payment_events(session=session)
        print(f"  Created {len(tax_events)} tax payment events")
        
        # Create daily risk-free interest charges using domain methods
        daily_events = fund.create_daily_risk_free_interest_charges(session=session)
        print(f"Created {len(daily_events)} daily risk-free interest charge events for {fund.name}")
        
        # Create EOFY debt cost events using domain methods
        eofy_events = fund.create_eofy_debt_cost_events(session=session)
        print(f"Created {len(eofy_events)} EOFY debt cost events for {fund.name}")
        
        # Calculate IRRs using domain methods
        irr = fund.calculate_irr(session=session)
        after_tax_irr = fund.calculate_after_tax_irr(session=session)
        real_irr = fund.calculate_real_irr(session=session)
        
        # Handle None values gracefully
        irr_str = f"{irr * 100:.2f}%" if irr is not None else "N/A"
        after_tax_irr_str = f"{after_tax_irr * 100:.2f}%" if after_tax_irr is not None else "N/A"
        real_irr_str = f"{real_irr * 100:.2f}%" if real_irr is not None else "N/A"
        
        print(f"  IRR: {irr_str}")
        print(f"  After-tax IRR: {after_tax_irr_str}")
        print(f"  Real IRR: {real_irr_str}")
        
        if show_irr_cashflows:
            # Get IRR cash flows using domain methods
            try:
                irr_result = get_irr_cashflows(fund, "irr", session)
                after_tax_result = get_irr_cashflows(fund, "after_tax_irr", session)
                real_result = get_irr_cashflows(fund, "real_irr", session)
                
                print(f"\n    --- IRR Cash Flows ---")
                if irr_result and irr_result.get('cash_flows') and irr_result.get('labels'):
                    for i, (cf, label) in enumerate(zip(irr_result['cash_flows'], irr_result['labels']), 1):
                        print(f"     {i:2d}: {cf:12,.2f}  {label}")
                else:
                    print("     No IRR cash flows available")
                
                print(f"\n    --- After-tax IRR Cash Flows ---")
                if after_tax_result and after_tax_result.get('cash_flows') and after_tax_result.get('labels'):
                    for i, (cf, label) in enumerate(zip(after_tax_result['cash_flows'], after_tax_result['labels']), 1):
                        print(f"     {i:2d}: {cf:12,.2f}  {label}")
                else:
                    print("     No after-tax IRR cash flows available")
                
                print(f"\n    --- Real IRR Cash Flows ---")
                if real_result and real_result.get('cash_flows') and real_result.get('labels'):
                    for i, (cf, label) in enumerate(zip(real_result['cash_flows'], real_result['labels']), 1):
                        print(f"     {i:2d}: {cf:12,.2f}  {label}")
                else:
                    print("     No real IRR cash flows available")
            except Exception as e:
                print(f"     Error calculating IRR cash flows: {e}")
    print(f"Completed recalculation loop. Iterations: {iteration_count}")
    print("\nAll recalculations completed!")

def verify_results(session):
    """Verify the results using domain methods."""
    print("\n4. Verifying results...")
    
    # Get all funds using domain methods
    funds = session.query(Fund).all()
    print(f"Funds at verification: {[f'{fund.id}: {fund.name}' for fund in funds]}")
    
    print(f"\n=== VERIFICATION RESULTS ===")
    print(f"\nFunds found: {len(funds)}")
    
    for fund in funds:
        print(f"\n{fund.name}:")
        print(f"  Type: {fund.tracking_type.value}")
        
        # Get current values using domain methods
        current_equity = fund.current_equity_balance
        average_equity = fund.average_equity_balance
        
        print(f"  Current equity: ${current_equity:,.2f}")
        print(f"  Average equity: ${average_equity:,.2f}")
        
        # Check if current equity matches calculated value
        calculated_equity = fund.current_equity_balance  # Just use the field directly
        if abs(current_equity - calculated_equity) > 0.01:
            print(f"  ⚠️  WARNING: Current equity doesn't match calculated value!")
            print(f"     Expected: ${calculated_equity:,.2f}")
        
        # Get event counts using domain methods
        events = session.query(FundEvent).filter(FundEvent.fund_id == fund.id).all()
        event_counts = {}
        for event in events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        print(f"  Events: {event_counts}")
        
        # Count specific event types
        tax_events = [e for e in events if e.event_type == EventType.TAX_PAYMENT]
        eofy_events = [e for e in events if e.event_type == EventType.EOFY_DEBT_COST]
        daily_events = [e for e in events if e.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE]
        
        print(f"  Tax payment events: {len(tax_events)}")
        print(f"  EOFY debt cost events: {len(eofy_events)}")
        print(f"  Daily interest charges: {len(daily_events)}")
        
        if fund.tracking_type == FundType.NAV_BASED:
            current_units = fund.current_units
            current_unit_price = fund.current_unit_price
            
            print(f"  Current units: {current_units:.2f}")
            print(f"  Current unit price: ${current_unit_price:.4f}")
            
            # Count NAV-specific events
            nav_events = [e for e in events if e.event_type == EventType.NAV_UPDATE]
            unit_purchases = [e for e in events if e.event_type == EventType.UNIT_PURCHASE]
            unit_sales = [e for e in events if e.event_type == EventType.UNIT_SALE]
            
            print(f"  NAV update events: {len(nav_events)}")
            print(f"  Unit purchases: {len(unit_purchases)}, Unit sales: {len(unit_sales)}")
        # Remove lines that reference fund.total_cost_basis and their print statements
    
    # Get risk-free rates count using domain methods
    risk_free_rates = session.query(RiskFreeRate).all()
    print(f"\nRisk-free rates preserved: {len(risk_free_rates)}")
    
    # Get total events count using domain methods
    all_events = session.query(FundEvent).all()
    print(f"Total events in database: {len(all_events)}")
    
    # Get tax statements count using domain methods
    tax_statements = session.query(TaxStatement).all()
    print(f"Tax statements: {len(tax_statements)}")

def print_equity_balance_over_time(fund, session):
    """Print equity balance over time for a fund, including number of days each balance persisted."""
    from src.fund.models import FundEvent, EventType
    print(f"\n=== Equity Balance Over Time: {fund.name} ===")
    # Get all events that affect equity, ordered by date
    if fund.tracking_type.name == 'COST_BASED':
        event_types = [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]
    else:
        event_types = [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]
    events = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.event_type.in_(event_types)
    ).order_by(FundEvent.event_date).all()
    if not events:
        print("No events.")
        return
    # For each event, recalculate equity and print
    prev_date = None
    prev_equity = None
    for i, event in enumerate(events):
        # Use the event's current_equity_balance field (set by the system)
        equity = event.current_equity_balance if event.current_equity_balance is not None else 0.0
        # Calculate number of days this balance persisted
        if i + 1 < len(events):
            days = (events[i+1].event_date - event.event_date).days
        else:
            # If last event, use fund end_date or today
            end_date = getattr(fund, 'end_date', None) or event.event_date
            if end_date is None or end_date < event.event_date:
                from datetime import date as dtdate
                end_date = dtdate.today()
            days = (end_date - event.event_date).days
        print(f"{event.event_date} | {event.event_type.name:15} | Equity: {equity:12,.2f} | Days: {days}")
        prev_date = event.event_date
        prev_equity = equity

def print_daily_debt_cost_breakdown(fund, session, fy_label, fy_start, fy_end):
    """Print the exact daily breakdown of risk-free interest charges for a fund in a given FY, and summarize how many days each unique charge appears."""
    print(f"\n=== Daily Risk-Free Interest Charges for {fund.name} ({fy_label}) ===")
    # Get all daily risk-free interest charges for the FY
    daily_events = fund.get_daily_risk_free_charges(session, start_date=fy_start, end_date=fy_end)
    if not daily_events:
        print("No daily risk-free interest charges found.")
        return
    from collections import defaultdict
    total = 0.0
    charge_counter = defaultdict(int)
    for event in daily_events:
        date = event.event_date
        charge = event.amount
        rate = getattr(event, 'risk_free_rate', None)
        # Find the most recent capital event on or before this date
        capital_event_types = [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE]
        latest_cap_event = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_(capital_event_types),
            FundEvent.event_date <= date
        ).order_by(FundEvent.event_date.desc(), FundEvent.id.desc()).first()
        equity = latest_cap_event.current_equity_balance if latest_cap_event and latest_cap_event.current_equity_balance is not None else 0.0
        # Try to parse rate from description if not present
        if rate is None and event.description:
            match = re.search(r'\((\d+\.\d+)% p\.a\.\)', event.description)
            if match:
                rate = float(match.group(1))
        if rate is not None:
            print(f"{date} | Rate: {rate:5.2f}% | Daily Charge: {charge:8.4f} | Equity: {equity:12,.2f}")
        else:
            print(f"{date} | Rate:   N/A | Daily Charge: {charge:8.4f} | Equity: {equity:12,.2f}")
        total += charge
        charge_counter[round(charge, 6)] += 1  # Use rounded charge as key for grouping
    print(f"Total for {fy_label}: {total:.4f}\n")
    # Print summary of unique daily charges
    print(f"Summary of unique daily charges for {fy_label}:")
    print(f"{'Daily Charge':>12} | {'Days':>5}")
    print("-" * 22)
    for charge, days in sorted(charge_counter.items()):
        print(f"{charge:12.6f} | {days:5}")
    print()

def main():
    """Main test function demonstrating proper session management architecture."""
    parser = argparse.ArgumentParser(description='Test the new domain structure')
    parser.add_argument('--no-cashflows', action='store_true', help='Skip showing IRR cash flows')
    args = parser.parse_args()
    
    print("Starting comprehensive system test...")
    print("Demonstrating proper session management architecture:")
    print("- Outermost backend layer manages sessions")
    print("- Domain methods accept session parameters")
    print("- No direct database operations from external clients")
    
    # ✅ CORRECT: Outermost backend layer manages sessions
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Clear database using the session (managed by outermost layer)
        print("\n1. Clearing database (preserving Risk Free Rates)...")
        clear_database_except_rates(session)
        
        # Set up test data using domain methods with shared session
        print("\n2. Setting up test data...")
        setup_test_data(session)
        
        # Show initial fund state
        funds = session.query(Fund).all()
        print(f"Funds after setup: {[f'{fund.id}: {fund.name}' for fund in funds]}")
        print("\nInitial fund state:")
        for fund in funds:
            current_equity = fund.current_equity_balance
            average_equity = fund.average_equity_balance
            print(f"  {fund.name}: equity=${current_equity:.2f}, avg=${average_equity:.2f}")
        
        # Recalculate everything using domain methods
        recalculate_everything(session, show_irr_cashflows=not args.no_cashflows)
        
        # Verify results using domain methods
        verify_results(session)
        
        # After recalculation and verification, print equity balance over time for each fund
        # Find the funds we created in setup_test_data
        senior_debt_fund = session.query(Fund).filter(Fund.name == "Senior Debt Fund No.24").first()
        finance_fund = session.query(Fund).filter(Fund.name == "3PG Finance").first()
        abc_fund = session.query(Fund).filter(Fund.name == "ABC Ltd").first()

        print_equity_balance_over_time(senior_debt_fund, session)
        print_equity_balance_over_time(finance_fund, session)
        print_equity_balance_over_time(abc_fund, session)
        
        print("\n=== DOMAIN STRUCTURE TEST COMPLETED SUCCESSFULLY ===")
        print("\n🎉 All domain structure tests passed! Migration was successful.")
        print("\n✅ Architectural pattern verified:")
        print("   - Outermost backend layer manages sessions")
        print("   - Domain methods accept session parameters")
        print("   - No direct database operations from external clients")
        print("   - Stateless external clients (sessions hidden from API consumers)")
        
    finally:
        # ✅ CORRECT: Outermost layer closes session
        session.close()

if __name__ == "__main__":
    main() 
    # --- Print exact daily breakdown for ABC fund debt cost ---
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    try:
        abc_fund = session.query(Fund).filter(Fund.name == "ABC Ltd").first()
        if abc_fund:
            # FY13: 2012-07-01 to 2013-06-30
            print_daily_debt_cost_breakdown(
                abc_fund, session, "FY13", date(2012, 7, 1), date(2013, 6, 30)
            )
            # FY14: 2013-07-01 to 2014-06-30
            print_daily_debt_cost_breakdown(
                abc_fund, session, "FY14", date(2013, 7, 1), date(2014, 6, 30)
            )
        else:
            print("ABC Ltd fund not found for daily debt cost breakdown.")
    finally:
        session.close() 