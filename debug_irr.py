#!/usr/bin/env python3
"""
Debug script to walk through IRR calculation step by step.
"""

import sys
import os
from datetime import date

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import get_database_session
from models import Fund, FundEvent, EventType

def debug_irr_calculation():
    """Debug the IRR calculation step by step."""
    
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Get the fund
        fund = session.query(Fund).filter(Fund.name == "Senior Debt Fund No.24").order_by(Fund.created_at.desc()).first()
        if not fund:
            print("Fund not found!")
            return
        
        # Show all funds first
        all_funds = session.query(Fund).all()
        print(f"All funds in database:")
        for f in all_funds:
            print(f"  {f.id}: {f.name} (created: {f.created_at})")
        
        print(f"\n" + "="*60)
        print("IRR CALCULATION DEBUG")
        print("="*60)
        
        print(f"Fund: {fund.name}")
        print(f"Start Date: {fund.start_date}")
        print(f"End Date: {fund.end_date}")
        print(f"Current Equity Balance: ${fund.current_equity_balance:,.0f}")
        print(f"Should be active: {fund.should_be_active}")
        
        # Get ALL events first
        all_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id
        ).order_by(FundEvent.event_date).all()
        
        print(f"\nAll Events in Database:")
        for event in all_events:
            print(f"  {event.event_date}: {event.event_type} ${event.amount:,.0f} - {event.description}")
        
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
        
        print(f"\nAll Cash Flow Events:")
        for event in cash_flow_events:
            flow_type = "OUTFLOW" if event.event_type in [EventType.CAPITAL_CALL, EventType.UNIT_PURCHASE, EventType.MANAGEMENT_FEE, EventType.CARRIED_INTEREST] else "INFLOW"
            print(f"  {event.event_date}: {event.event_type} ${event.amount:,.0f} ({flow_type})")
        
        # Group by month
        monthly_cash_flows = {}
        
        for event in cash_flow_events:
            month_key = (event.event_date.year, event.event_date.month)
            
            if month_key not in monthly_cash_flows:
                monthly_cash_flows[month_key] = 0
            
            amount = event.amount or 0
            
            if event.event_type in [EventType.CAPITAL_CALL, EventType.UNIT_PURCHASE, EventType.MANAGEMENT_FEE, EventType.CARRIED_INTEREST]:
                monthly_cash_flows[month_key] -= abs(amount)
            else:
                monthly_cash_flows[month_key] += abs(amount)
        
        print(f"\nMonthly Cash Flows:")
        for month_key in sorted(monthly_cash_flows.keys()):
            year, month = month_key
            amount = monthly_cash_flows[month_key]
            flow_type = "OUTFLOW" if amount < 0 else "INFLOW"
            print(f"  {year}-{month:02d}: ${amount:,.0f} ({flow_type})")
        
        # Convert to list
        cash_flows = []
        for month_key in sorted(monthly_cash_flows.keys()):
            cash_flows.append(monthly_cash_flows[month_key])
        
        print(f"\nCash Flow List for IRR:")
        print(f"  {cash_flows}")
        
        # Calculate IRR
        import numpy_financial as npf
        
        try:
            # Test the fund's new IRR method
            print(f"\nFund's New IRR Method (Daily Precision):")
            fund_irr = fund.calculate_irr(session)
            if fund_irr is not None:
                print(f"  Fund IRR: {fund_irr:.2f}%")
            else:
                print(f"  Fund IRR: None")
            
            # Get the fund's internal cash flows
            print(f"\nFund's Internal Cash Flow Generation:")
            cash_flow_events_internal = session.query(FundEvent).filter(
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
            
            start_date_internal = cash_flow_events_internal[0].event_date
            cash_flows_internal = []
            days_internal = []
            
            for event in cash_flow_events_internal:
                days = (event.event_date - start_date_internal).days
                days_internal.append(days)
                
                amount = event.amount or 0
                if event.event_type in [EventType.CAPITAL_CALL, EventType.UNIT_PURCHASE, EventType.MANAGEMENT_FEE, EventType.CARRIED_INTEREST]:
                    cash_flows_internal.append(-abs(amount))
                else:
                    cash_flows_internal.append(abs(amount))
            
            print(f"  Internal Cash Flows: {cash_flows_internal}")
            print(f"  Internal Days: {days_internal}")
            print(f"  Number of events: {len(cash_flow_events_internal)}")
            print(f"  Number of cash flows: {len(cash_flows_internal)}")
            
            # Show detailed cash flow breakdown
            print(f"\nDetailed Cash Flow Analysis:")
            start_date = cash_flow_events[0].event_date
            for i, event in enumerate(cash_flow_events):
                days = (event.event_date - start_date).days
                months = days / 30.44
                flow_type = "OUTFLOW" if event.event_type in [EventType.CAPITAL_CALL, EventType.UNIT_PURCHASE, EventType.MANAGEMENT_FEE, EventType.CARRIED_INTEREST] else "INFLOW"
                print(f"  {event.event_date}: {event.event_type} ${event.amount:,.0f} ({flow_type}) - Day {days}, Month {months:.2f}")
            
            # Manual calculation for verification
            print(f"\nManual Verification:")
            print(f"  Cash Flows: {cash_flows}")
            
            # Calculate days from start for verification
            start_date = cash_flow_events[0].event_date
            days_from_start = [(event.event_date - start_date).days for event in cash_flow_events]
            print(f"  Days from Start: {days_from_start}")
            
            # Calculate present values using the fund's IRR
            if fund_irr is not None:
                # Convert annual IRR to monthly rate
                annual_irr = fund_irr / 100  # Convert percentage to decimal
                monthly_rate = (1 + annual_irr) ** (1/12) - 1
                
                print(f"\nPresent Value Calculation (Annual IRR: {fund_irr:.2f}%, Monthly Rate: {monthly_rate:.6f}):")
                total_npv = 0
                
                # Use the fund's internal cash flows (correct ones)
                for i, (cf, days) in enumerate(zip(cash_flows_internal, days_internal)):
                    months = days / 30.44
                    discount_factor = (1 + monthly_rate) ** months
                    present_value = cf / discount_factor
                    total_npv += present_value
                    
                    flow_type = "OUTFLOW" if cf < 0 else "INFLOW"
                    event = cash_flow_events_internal[i]
                    print(f"  {event.event_date}: ${cf:,.0f} ({flow_type}) - Day {days}, Month {months:.2f}")
                    print(f"    Discount Factor: {discount_factor:.6f}")
                    print(f"    Present Value: ${present_value:,.2f}")
                
                print(f"\nTotal NPV: ${total_npv:.2f}")
                print(f"Target NPV: $0.00")
                print(f"Difference: ${abs(total_npv):.2f}")
            
        except Exception as e:
            print(f"IRR calculation failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
        scoped_session.remove()

if __name__ == "__main__":
    debug_irr_calculation() 