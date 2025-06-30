#!/usr/bin/env python3
"""
Detailed analysis of after-tax IRR calculations showing cash flow breakdowns.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType

def analyze_after_tax_irr():
    """Analyze after-tax IRR calculations in detail."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("DETAILED AFTER-TAX IRR ANALYSIS")
    print("=" * 80)
    
    # Get all funds
    funds = session.query(Fund).all()
    
    for fund in funds:
        print(f"\n{'='*80}")
        print(f"FUND: {fund.name}")
        print(f"{'='*80}")
        
        # Get start and end dates
        start_date = fund.start_date
        end_date = fund.end_date
        
        print(f"Investment Period: {start_date} to {end_date}")
        print(f"Duration: {fund.total_investment_duration_months} months")
        print(f"Current Value: ${fund.current_value:,.2f}")
        print(f"Average Equity: ${fund.average_equity_balance:,.2f}")
        
        # Get all cash flow events
        cash_flow_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_([
                EventType.CAPITAL_CALL,
                EventType.UNIT_PURCHASE,
                EventType.RETURN_OF_CAPITAL,
                EventType.DISTRIBUTION,
                EventType.MANAGEMENT_FEE,
                EventType.CARRIED_INTEREST,
                EventType.TAX_PAYMENT
            ])
        ).order_by(FundEvent.event_date).all()
        
        if not cash_flow_events:
            print("No cash flow events found.")
            continue
        
        print(f"\nCASH FLOW BREAKDOWN:")
        print("-" * 80)
        print(f"{'Date':<12} {'Type':<15} {'Amount':<12} {'Days':<6} {'Description'}")
        print("-" * 80)
        
        # Track totals by type
        totals = {
            'capital_calls': 0,
            'returns': 0,
            'distributions': 0,
            'tax_payments': 0,
            'fees': 0,
            'other': 0
        }
        
        for event in cash_flow_events:
            days = (event.event_date - start_date).days
            
            # Format amount based on event type
            if event.event_type in [EventType.CAPITAL_CALL, EventType.UNIT_PURCHASE]:
                amount = -event.amount  # Cash outflow
                totals['capital_calls'] += event.amount
                amount_str = f"${amount:,.2f}"
            elif event.event_type == EventType.RETURN_OF_CAPITAL:
                amount = event.amount  # Cash inflow
                totals['returns'] += event.amount
                amount_str = f"${amount:,.2f}"
            elif event.event_type == EventType.DISTRIBUTION:
                amount = event.amount  # Cash inflow
                totals['distributions'] += event.amount
                amount_str = f"${amount:,.2f}"
            elif event.event_type == EventType.TAX_PAYMENT:
                amount = -event.amount  # Cash outflow
                totals['tax_payments'] += event.amount
                amount_str = f"${amount:,.2f}"
            elif event.event_type in [EventType.MANAGEMENT_FEE, EventType.CARRIED_INTEREST]:
                amount = -event.amount  # Cash outflow
                totals['fees'] += event.amount
                amount_str = f"${amount:,.2f}"
            else:
                amount = event.amount
                totals['other'] += event.amount
                amount_str = f"${amount:,.2f}"
            
            print(f"{event.event_date} {event.event_type:<15} {amount_str:<12} {days:<6} {event.description or ''}")
        
        # Show totals
        print("-" * 80)
        print(f"TOTALS:")
        print(f"  Capital Calls:     ${totals['capital_calls']:,.2f}")
        print(f"  Returns:           ${totals['returns']:,.2f}")
        print(f"  Distributions:     ${totals['distributions']:,.2f}")
        print(f"  Tax Payments:      ${totals['tax_payments']:,.2f}")
        print(f"  Fees:              ${totals['fees']:,.2f}")
        print(f"  Other:             ${totals['other']:,.2f}")
        
        # Calculate net cash flows
        gross_cash_flow = totals['returns'] + totals['distributions'] - totals['capital_calls'] - totals['fees'] - totals['other']
        after_tax_cash_flow = gross_cash_flow - totals['tax_payments']
        
        print(f"\nNET CASH FLOWS:")
        print(f"  Gross Cash Flow:   ${gross_cash_flow:,.2f}")
        print(f"  Tax Payments:      ${totals['tax_payments']:,.2f}")
        print(f"  After-Tax Cash Flow: ${after_tax_cash_flow:,.2f}")
        
        # Calculate IRRs
        gross_irr = fund.calculate_irr(session)
        after_tax_irr = fund.calculate_after_tax_irr(session)
        
        print(f"\nIRR COMPARISON:")
        print(f"  Gross IRR:         {fund.get_irr_percentage(session)}")
        print(f"  After-Tax IRR:     {fund.get_after_tax_irr_percentage(session)}")
        
        if gross_irr is not None and after_tax_irr is not None:
            difference = gross_irr - after_tax_irr
            percentage_impact = (difference / gross_irr * 100) if gross_irr != 0 else 0
            print(f"  Tax Impact:        {difference:.2f} percentage points ({percentage_impact:.1f}%)")
        
        # Show tax details
        tax_events = [e for e in cash_flow_events if e.event_type == EventType.TAX_PAYMENT]
        if tax_events:
            print(f"\nTAX PAYMENT DETAILS:")
            for event in tax_events:
                print(f"  {event.event_date}: ${event.amount:,.2f} - {event.description}")
        
        print(f"\n{'='*80}")
    
    session.close()

def show_tax_statement_summary():
    """Show summary of tax statements and their impact on after-tax IRR."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f"\nTAX STATEMENT SUMMARY")
    print(f"{'='*80}")
    
    from models import TaxStatement
    
    # Get all tax statements
    tax_statements = session.query(TaxStatement).order_by(
        TaxStatement.fund_id, TaxStatement.financial_year
    ).all()
    
    if not tax_statements:
        print("No tax statements found.")
        return
    
    current_fund = None
    for tax_statement in tax_statements:
        if current_fund != tax_statement.fund_id:
            current_fund = tax_statement.fund_id
            fund = session.query(Fund).filter(Fund.id == tax_statement.fund_id).first()
            print(f"\nFUND: {fund.name if fund else 'Unknown'}")
            print("-" * 60)
        
        print(f"\nFY {tax_statement.financial_year}:")
        print(f"  Total Income:      ${tax_statement.total_income:,.2f}")
        print(f"  Tax Withheld:      ${tax_statement.tax_withheld:,.2f}")
        print(f"  Foreign Credits:   ${tax_statement.foreign_tax_credits:,.2f}")
        print(f"  Tax Payable Rate:  {tax_statement.tax_payable_rate:.1f}%")
        print(f"  Tax Already Paid:  ${tax_statement.tax_already_paid:,.2f}")
        print(f"  Additional Tax:    ${tax_statement.tax_payable:,.2f}")
        print(f"  Tax Payment Date:  {tax_statement.get_tax_payment_date()}")
        
        # Calculate effective tax rate
        if tax_statement.total_income > 0:
            total_tax = tax_statement.tax_withheld + tax_statement.foreign_tax_credits + tax_statement.tax_payable
            effective_rate = (total_tax / tax_statement.total_income) * 100
            print(f"  Effective Tax Rate: {effective_rate:.1f}%")
    
    session.close()

if __name__ == "__main__":
    analyze_after_tax_irr()
    show_tax_statement_summary() 