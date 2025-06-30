#!/usr/bin/env python3
"""
Debug script to analyze after-tax IRR calculations in detail.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType

def debug_after_tax_irr():
    """Debug after-tax IRR calculations in detail."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("DEBUG AFTER-TAX IRR CALCULATION")
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
        
        # Get all cash flow events for after-tax IRR
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
        
        print(f"\nCASH FLOW EVENTS FOR AFTER-TAX IRR:")
        print("-" * 80)
        print(f"{'Date':<12} {'Type':<15} {'Amount':<12} {'Days':<6} {'Cash Flow':<12} {'Description'}")
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
        
        cash_flows = []
        days_from_start = []
        
        for event in cash_flow_events:
            days = (event.event_date - start_date).days
            days_from_start.append(days)
            
            # Calculate cash flow based on event type
            if event.event_type == EventType.CAPITAL_CALL:
                cash_flow = -event.amount  # Cash outflow
                totals['capital_calls'] += event.amount
                cash_flow_str = f"${cash_flow:,.2f}"
            elif event.event_type == EventType.RETURN_OF_CAPITAL:
                cash_flow = event.amount  # Cash inflow
                totals['returns'] += event.amount
                cash_flow_str = f"${cash_flow:,.2f}"
            elif event.event_type == EventType.DISTRIBUTION:
                cash_flow = event.amount  # Cash inflow
                totals['distributions'] += event.amount
                cash_flow_str = f"${cash_flow:,.2f}"
            elif event.event_type == EventType.TAX_PAYMENT:
                cash_flow = -event.amount  # Cash outflow
                totals['tax_payments'] += event.amount
                cash_flow_str = f"${cash_flow:,.2f}"
            elif event.event_type in [EventType.MANAGEMENT_FEE, EventType.CARRIED_INTEREST]:
                cash_flow = -event.amount  # Cash outflow
                totals['fees'] += event.amount
                cash_flow_str = f"${cash_flow:,.2f}"
            else:
                cash_flow = event.amount
                totals['other'] += event.amount
                cash_flow_str = f"${cash_flow:,.2f}"
            
            cash_flows.append(cash_flow)
            
            print(f"{event.event_date} {event.event_type:<15} ${event.amount:<11,.2f} {days:<6} {cash_flow_str:<12} {event.description or ''}")
        
        # Add final value if fund is completed
        if not fund.should_be_active and cash_flows:
            final_value = fund.current_value or 0
            if final_value > 0:
                print(f"{end_date} FINAL_VALUE   ${final_value:<11,.2f} {(end_date - start_date).days:<6} ${final_value:,.2f}     Final value")
                cash_flows[-1] += final_value
                print(f"  -> Updated last cash flow to: ${cash_flows[-1]:,.2f}")
        
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
        
        # Show cash flows array
        print(f"\nCASH FLOWS ARRAY:")
        print(f"  Length: {len(cash_flows)}")
        print(f"  Values: {[f'${cf:,.2f}' for cf in cash_flows]}")
        
        # Show days array
        print(f"\nDAYS FROM START:")
        print(f"  Length: {len(days_from_start)}")
        print(f"  Values: {days_from_start}")
        
        # Calculate IRR manually
        print(f"\nIRR CALCULATION:")
        try:
            # Use the fund's internal method
            after_tax_irr = fund.calculate_after_tax_irr(session)
            gross_irr = fund.calculate_irr(session)
            
            print(f"  Gross IRR:         {fund.get_irr_percentage(session)}")
            print(f"  After-Tax IRR:     {fund.get_after_tax_irr_percentage(session)}")
            
            if gross_irr is not None and after_tax_irr is not None:
                difference = gross_irr - after_tax_irr
                percentage_impact = (difference / gross_irr * 100) if gross_irr != 0 else 0
                print(f"  Tax Impact:        {difference:.2f} percentage points ({percentage_impact:.1f}%)")
            
            # Debug the internal calculation
            print(f"\nINTERNAL CALCULATION DEBUG:")
            print(f"  Should be active: {fund.should_be_active}")
            print(f"  Start date: {start_date}")
            print(f"  End date: {end_date}")
            print(f"  Current value: ${fund.current_value:,.2f}")
            
            # Test the base method directly
            base_irr_gross = fund._calculate_irr_base(include_tax_payments=False, session=session)
            base_irr_after_tax = fund._calculate_irr_base(include_tax_payments=True, session=session)
            
            print(f"  Base method - Gross: {base_irr_gross:.2f}%" if base_irr_gross is not None else "  Base method - Gross: None")
            print(f"  Base method - After-tax: {base_irr_after_tax:.2f}%" if base_irr_after_tax is not None else "  Base method - After-tax: None")
            
        except Exception as e:
            print(f"  Error calculating IRR: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n{'='*80}")
    
    session.close()

def compare_gross_vs_after_tax():
    """Compare gross vs after-tax IRR calculations side by side."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f"\nCOMPARISON: GROSS VS AFTER-TAX IRR")
    print(f"{'='*80}")
    
    # Get all funds
    funds = session.query(Fund).all()
    
    for fund in funds:
        print(f"\nFUND: {fund.name}")
        print("-" * 60)
        
        # Get events for gross IRR (excluding tax payments)
        gross_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_([
                EventType.CAPITAL_CALL,
                EventType.UNIT_PURCHASE,
                EventType.RETURN_OF_CAPITAL,
                EventType.DISTRIBUTION,
                EventType.MANAGEMENT_FEE,
                EventType.CARRIED_INTEREST
            ])
        ).order_by(FundEvent.event_date).all()
        
        # Get events for after-tax IRR (including tax payments)
        after_tax_events = session.query(FundEvent).filter(
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
        
        print(f"Gross IRR Events: {len(gross_events)}")
        print(f"After-Tax IRR Events: {len(after_tax_events)}")
        
        # Count tax payment events
        tax_events = [e for e in after_tax_events if e.event_type == EventType.TAX_PAYMENT]
        print(f"Tax Payment Events: {len(tax_events)}")
        
        if tax_events:
            total_tax = sum(e.amount for e in tax_events)
            print(f"Total Tax Payments: ${total_tax:,.2f}")
            
            print(f"\nTax Payment Details:")
            for event in tax_events:
                print(f"  {event.event_date}: ${event.amount:,.2f} - {event.description}")
        
        # Calculate both IRRs
        gross_irr = fund.calculate_irr(session)
        after_tax_irr = fund.calculate_after_tax_irr(session)
        
        print(f"\nIRR Results:")
        print(f"  Gross IRR:         {fund.get_irr_percentage(session)}")
        print(f"  After-Tax IRR:     {fund.get_after_tax_irr_percentage(session)}")
        
        if gross_irr is not None and after_tax_irr is not None:
            difference = gross_irr - after_tax_irr
            percentage_impact = (difference / gross_irr * 100) if gross_irr != 0 else 0
            print(f"  Tax Impact:        {difference:.2f} percentage points ({percentage_impact:.1f}%)")
    
    session.close()

if __name__ == "__main__":
    debug_after_tax_irr()
    compare_gross_vs_after_tax() 