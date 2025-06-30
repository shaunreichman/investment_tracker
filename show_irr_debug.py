#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType, FundType

def show_irr_debug(fund_name="3PG Finance"):
    """Show detailed IRR calculation with present values for debugging."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get the fund
    fund = session.query(Fund).filter(Fund.name == fund_name).first()
    if not fund:
        print(f"Fund '{fund_name}' not found!")
        return
    
    print(f"IRR DEBUG ANALYSIS FOR: {fund.name}")
    print("=" * 80)
    
    # Get start and end dates
    start_date = fund.start_date
    end_date = fund.end_date
    print(f"Investment Period: {start_date} to {end_date}")
    print(f"Total Days: {(end_date - start_date).days}")
    print(f"Total Years: {(end_date - start_date).days / 365.25:.2f}")
    print()
    
    # Calculate IRR using the fund's method
    irr_percentage = fund.calculate_irr(session)
    print(f"Calculated IRR: {irr_percentage:.2f}%")
    print()
    
    # Get all cash flow events
    cash_flow_events = session.query(FundEvent).filter(
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
    
    print("CASH FLOW ANALYSIS:")
    print("-" * 100)
    print("Date       | Event Type        | Amount    | Cash Flow | Days | Months | Rate | PV Factor | Present Value")
    print("-" * 100)
    
    cash_flows = []
    days_from_start = []
    
    for event in cash_flow_events:
        # Calculate days from start
        days = (event.event_date - start_date).days
        days_from_start.append(days)
        
        # Calculate cash flow
        if event.event_type == EventType.CAPITAL_CALL:
            cash_flow = -event.amount  # Outflow
        elif event.event_type == EventType.RETURN_OF_CAPITAL:
            cash_flow = event.amount   # Inflow
        elif event.event_type == EventType.DISTRIBUTION:
            cash_flow = event.amount   # Inflow
        elif event.event_type == EventType.MANAGEMENT_FEE:
            cash_flow = -event.amount  # Outflow
        elif event.event_type == EventType.CARRIED_INTEREST:
            cash_flow = -event.amount  # Outflow
        else:
            equity_change = fund._get_equity_change_for_event(event)
            cash_flow = -equity_change
        
        cash_flows.append(cash_flow)
        
        # Calculate present value using the IRR
        months = days / 30.44
        if irr_percentage is not None:
            monthly_rate = (1 + irr_percentage/100) ** (1/12) - 1
            pv_factor = (1 + monthly_rate) ** months
            present_value = cash_flow / pv_factor
        else:
            monthly_rate = 0
            pv_factor = 1.0
            present_value = cash_flow
        
        print(f"{event.event_date} | {event.event_type:<16} | ${event.amount:>8,.0f} | ${cash_flow:>9,.0f} | {days:>4} | {months:>6.1f} | {monthly_rate*100:>4.1f}% | {pv_factor:>9.4f} | ${present_value:>12,.2f}")
    
    print("-" * 100)
    
    # Show summary
    total_investment = sum(cf for cf in cash_flows if cf < 0)
    total_return = sum(cf for cf in cash_flows if cf > 0)
    net_cash_flow = sum(cash_flows)
    
    print(f"Total Investment (outflows): ${abs(total_investment):,.0f}")
    print(f"Total Return (inflows):      ${total_return:,.0f}")
    print(f"Net Cash Flow:               ${net_cash_flow:,.0f}")
    print()
    
    # Calculate NPV at the IRR
    if irr_percentage is not None:
        npv = 0
        for cf, days in zip(cash_flows, days_from_start):
            months = days / 30.44
            monthly_rate = (1 + irr_percentage/100) ** (1/12) - 1
            pv_factor = (1 + monthly_rate) ** months
            npv += cf / pv_factor
        
        print(f"NPV at {irr_percentage:.2f}% IRR: ${npv:.2f}")
        print()
    
    # Show alternative IRR calculations
    print("ALTERNATIVE CALCULATIONS:")
    print("-" * 100)
    
    # Simple return
    if abs(total_investment) > 0:
        simple_return = (total_return - abs(total_investment)) / abs(total_investment)
        print(f"Simple Return: {simple_return:.2%}")
        
        # Time-weighted return approximation
        years = (end_date - start_date).days / 365.25
        if years > 0:
            time_weighted_return = (total_return / abs(total_investment)) ** (1/years) - 1
            print(f"Time-weighted Return: {time_weighted_return:.2%}")
    
    # Test different IRR rates
    print("\nNPV AT DIFFERENT RATES:")
    print("-" * 100)
    print("Rate  | NPV")
    print("-" * 100)
    
    for test_rate in [0, 5, 10, 15, 20, 25, 30]:
        npv = 0
        for cf, days in zip(cash_flows, days_from_start):
            months = days / 30.44
            monthly_rate = (1 + test_rate/100) ** (1/12) - 1
            pv_factor = (1 + monthly_rate) ** months
            npv += cf / pv_factor
        print(f"{test_rate:>5.0f}% | ${npv:>8,.2f}")
    
    print()
    print("VERIFICATION:")
    print("-" * 100)
    print("The IRR should result in NPV ≈ 0. If NPV is significantly different from 0,")
    print("there may be an issue with the IRR calculation.")
    print()
    print("The 'Rate' column shows the monthly rate used for discounting.")
    print("The 'PV Factor' is (1 + monthly_rate)^months")
    print("The 'Present Value' is cash_flow / pv_factor")
    
    session.close()

if __name__ == "__main__":
    fund_name = sys.argv[1] if len(sys.argv) > 1 else "3PG Finance"
    show_irr_debug(fund_name) 