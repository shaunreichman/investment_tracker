#!/usr/bin/env python3
"""
Debug script to show detailed real IRR calculation including daily interest charges.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, RiskFreeRate, EventType

def debug_real_irr(fund_name="Senior Debt Fund No.24"):
    """Debug the real IRR calculation with detailed breakdown."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Find the fund
    fund = session.query(Fund).filter(Fund.name == fund_name).first()
    if not fund:
        print(f"Fund '{fund_name}' not found!")
        return
    
    print(f"DEBUGGING REAL IRR CALCULATION FOR: {fund.name}")
    print("=" * 80)
    
    # Get fund dates and basic info
    start_date = fund.start_date
    end_date = fund.end_date
    print(f"Investment Period: {start_date} to {end_date}")
    print(f"Total Days: {(end_date - start_date).days}")
    print(f"Currency: {fund.currency}")
    print()
    
    # Get all cash flow events for IRR calculation
    cash_flow_events = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.event_type.in_([
            EventType.CAPITAL_CALL,
            EventType.UNIT_PURCHASE,
            EventType.RETURN_OF_CAPITAL,
            EventType.DISTRIBUTION,
            EventType.TAX_PAYMENT,
            EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
            EventType.FY_DEBT_COST
        ])
    ).order_by(FundEvent.event_date).all()
    
    # Calculate present values
    total_pv = 0
    total_interest_charges = 0
    interest_charges_count = 0
    total_fy_debt_cost_benefits = 0
    fy_debt_cost_count = 0
    all_cash_flows = []
    all_days_from_start = []
    
    for event in cash_flow_events:
        # Calculate days from start
        days = (event.event_date - start_date).days
        
        # Determine cash flow amount
        if event.event_type == EventType.CAPITAL_CALL:
            amount = -(event.amount or 0)  # Cash outflow (negative)
        elif event.event_type == EventType.RETURN_OF_CAPITAL:
            amount = event.amount or 0  # Cash inflow (positive)
        elif event.event_type == EventType.DISTRIBUTION:
            amount = event.amount or 0  # Cash inflow (positive)
        elif event.event_type == EventType.TAX_PAYMENT:
            amount = -(event.amount or 0)  # Cash outflow (negative)
        elif event.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE:
            amount = -(event.amount or 0)  # Cash outflow (negative)
            total_interest_charges += event.amount or 0
            interest_charges_count += 1
        elif event.event_type == EventType.FY_DEBT_COST:
            amount = event.amount or 0  # Cash inflow (positive) - tax benefit
            total_fy_debt_cost_benefits += event.amount or 0
            fy_debt_cost_count += 1
        else:
            amount = 0
        
        all_cash_flows.append(amount)
        all_days_from_start.append(days)
    
    # Print sum of all cash flows and last 10 cash flows for diagnosis
    print("CASH FLOW DIAGNOSTICS:")
    print("-" * 80)
    print(f"Sum of all cash flows: ${sum(all_cash_flows):,.2f}")
    print("Last 10 cash flows:")
    for i, (amt, day) in enumerate(zip(all_cash_flows[-10:], all_days_from_start[-10:])):
        print(f"  {i+1}. Amount: ${amt:,.2f}, Days from start: {day}")
    print()
    
    # Print all cash flows for debugging
    print("FULL CASH FLOW TABLE:")
    print("-" * 80)
    print(f"{'Date':<12} {'Type':<30} {'Amount':<15} {'Days from Start':<15}")
    print("-" * 80)
    for event, amount, days in zip(cash_flow_events, all_cash_flows, all_days_from_start):
        event_type_display = event.event_type.replace('_', ' ').title()
        if event.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE:
            event_type_display = "Daily Interest Charge"
        elif event.event_type == EventType.FY_DEBT_COST:
            event_type_display = "FY Debt Cost Benefit"
        print(f"{event.event_date} {event_type_display:<30} ${amount:>12,.2f} {days:>14d}")
    print("-" * 80)
    print()
    
    # Now try to calculate real IRR
    real_irr = fund.calculate_real_irr(session)
    if real_irr is None:
        print("ERROR: Could not calculate real IRR! (Likely due to net positive cash flows or non-convergent IRR)")
        return
    real_irr_rate = real_irr * 100  # Convert to percentage
    print(f"Real IRR Rate: {real_irr_rate:.2f}%")
    print()
    
    # If IRR is computable, print the detailed event table with present values
    print("CASH FLOW EVENTS FOR REAL IRR:")
    print("-" * 80)
    print(f"{'Date':<12} {'Type':<30} {'Amount':<15} {'Days from Start':<15} {'Present Value':<15}")
    print("-" * 80)
    total_pv = 0
    for event, amount, days in zip(cash_flow_events, all_cash_flows, all_days_from_start):
        years = days / 365.25
        pv = amount / ((1 + real_irr) ** years)
        total_pv += pv
        event_type_display = event.event_type.replace('_', ' ').title()
        if event.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE:
            event_type_display = "Daily Interest Charge"
        elif event.event_type == EventType.FY_DEBT_COST:
            event_type_display = "FY Debt Cost Benefit"
        print(f"{event.event_date} {event_type_display:<30} ${amount:>12,.2f} {days:>14d} ${pv:>12,.2f}")
    print("-" * 80)
    print(f"{'TOTAL':<42} {'':<15} ${total_pv:>12,.2f}")
    print()
    
    # Summary statistics
    print("SUMMARY STATISTICS:")
    print("-" * 80)
    print(f"Total Cash Flow Events: {len(cash_flow_events)}")
    print(f"Daily Interest Charges: {interest_charges_count}")
    print(f"Total Interest Charges: ${total_interest_charges:,.2f}")
    print(f"Average Daily Interest: ${total_interest_charges/interest_charges_count:,.4f}")
    print(f"Net Present Value: ${total_pv:,.2f}")
    print()
    
    # Compare with other IRR calculations
    print("IRR COMPARISON:")
    print("-" * 80)
    gross_irr = fund.calculate_irr(session)
    after_tax_irr = fund.calculate_after_tax_irr(session)
    
    print(f"Gross IRR:        {gross_irr * 100:>6.2f}%")
    print(f"After-Tax IRR:    {after_tax_irr * 100:>6.2f}%")
    print(f"Real IRR:         {real_irr_rate:>6.2f}%")
    print()
    print(f"Gross → After-Tax: {((gross_irr - after_tax_irr) * 100):>6.2f}%")
    print(f"After-Tax → Real:  {((after_tax_irr - real_irr) * 100):>6.2f}%")
    print(f"Gross → Real:      {((gross_irr - real_irr) * 100):>6.2f}%")
    print()
    
    # Show interest charges by period
    print("INTEREST CHARGES BY PERIOD:")
    print("-" * 80)
    
    # Group interest charges by rate
    interest_by_rate = {}
    for event in cash_flow_events:
        if event.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE:
            # Extract rate from description
            desc = event.description or ""
            if "(" in desc and "%" in desc:
                rate_str = desc.split("(")[1].split("%")[0]
                try:
                    rate = float(rate_str)
                    if rate not in interest_by_rate:
                        interest_by_rate[rate] = {'count': 0, 'total': 0, 'dates': []}
                    interest_by_rate[rate]['count'] += 1
                    interest_by_rate[rate]['total'] += event.amount or 0
                    interest_by_rate[rate]['dates'].append(event.event_date)
                except ValueError:
                    pass
    
    for rate in sorted(interest_by_rate.keys()):
        data = interest_by_rate[rate]
        start_date_rate = min(data['dates'])
        end_date_rate = max(data['dates'])
        print(f"Rate {rate:>5.2f}%: {data['count']:>4d} days, ${data['total']:>10,.2f} total")
        print(f"         Period: {start_date_rate} to {end_date_rate}")
    
    print()
    
    # Show debt cost analysis
    print("DEBT COST ANALYSIS:")
    print("-" * 80)
    debt_cost = fund.calculate_debt_cost(session)
    if debt_cost:
        print(f"Total Debt Cost: ${debt_cost['total_debt_cost']:,.2f}")
        print(f"Average Risk-Free Rate: {debt_cost['average_risk_free_rate']:.2f}%")
        print(f"Debt Cost as % of Average Equity: {debt_cost['debt_cost_percentage']:.2f}%")
        print(f"Investment Duration: {debt_cost['investment_duration_years']:.2f} years")
        print(f"Average Equity: ${debt_cost['average_equity']:,.2f}")
        if debt_cost['excess_return'] is not None:
            print(f"Excess Return: ${debt_cost['excess_return']:,.2f}")
    
    session.close()

if __name__ == "__main__":
    import sys
    fund_name = sys.argv[1] if len(sys.argv) > 1 else "Senior Debt Fund No.24"
    debug_real_irr(fund_name) 