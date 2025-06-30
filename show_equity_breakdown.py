#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType, FundType

def show_equity_breakdown(fund_name=None):
    """Show detailed equity balance breakdown for a fund.
    
    Args:
        fund_name (str): Name of the fund to analyze. If None, will list available funds.
    """
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # If no fund name provided, list available funds
        if fund_name is None:
            print("=" * 80)
            print("AVAILABLE FUNDS")
            print("=" * 80)
            funds = session.query(Fund).all()
            if not funds:
                print("No funds found in database!")
                return
            
            for i, fund in enumerate(funds, 1):
                print(f"{i:2d}. {fund.name} ({fund.tracking_type.value})")
                print(f"    Investment Company: {fund.investment_company.name}")
                print(f"    Entity: {fund.entity.name}")
                print(f"    Status: {'Active' if fund.is_active else 'Exited'}")
                print(f"    Average Equity: ${fund.average_equity_balance:,.0f}")
                print()
            
            print("Usage: python show_equity_breakdown.py 'Fund Name'")
            print("Example: python show_equity_breakdown.py '3PG Finance'")
            return
        
        # Get the specified fund
        fund = session.query(Fund).filter(Fund.name == fund_name).first()
        if not fund:
            print(f"Fund '{fund_name}' not found!")
            print("\nAvailable funds:")
            funds = session.query(Fund).all()
            for fund in funds:
                print(f"  - {fund.name}")
            return
        
        print("=" * 80)
        print("EQUITY BALANCE BREAKDOWN")
        print("=" * 80)
        print(f"Fund: {fund.name}")
        print(f"Fund Type: {fund.tracking_type.value}")
        print(f"Investment Company: {fund.investment_company.name}")
        print(f"Entity: {fund.entity.name}")
        print(f"Start Date: {fund.start_date}")
        print(f"End Date: {fund.end_date}")
        print(f"Total Duration: {fund.total_investment_duration_months} months")
        print(f"Status: {'Active' if fund.is_active else 'Exited'}")
        print()
        
        # Get system's calculated average
        system_average = fund.calculate_average_equity_balance(session)
        print(f"SYSTEM CALCULATED AVERAGE: ${system_average:,.0f}")
        print(f"STORED AVERAGE: ${fund.average_equity_balance:,.0f}")
        print()
        
        # Get all equity-changing events in chronological order
        if fund.tracking_type == FundType.COST_BASED:
            equity_events = session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id,
                FundEvent.event_type.in_([EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL])
            ).order_by(FundEvent.event_date).all()
        else:
            # For NAV-based funds, use unit purchase/sale events
            equity_events = session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id,
                FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
            ).order_by(FundEvent.event_date).all()
        
        if not equity_events:
            print("No equity-changing events found for this fund!")
            return
        
        print("EQUITY-CHANGING EVENTS:")
        print("-" * 80)
        current_equity = 0
        
        for i, event in enumerate(equity_events):
            equity_change = fund._get_equity_change_for_event(event)
            current_equity += equity_change
            
            if equity_change > 0:
                print(f"{event.event_date}: +${event.amount:>8,.0f} ({event.event_type}) -> ${current_equity:>8,.0f}")
            else:
                print(f"{event.event_date}: -${abs(event.amount):>8,.0f} ({event.event_type}) -> ${current_equity:>8,.0f}")
        
        print()
        print("PERIOD-BASED CALCULATION BREAKDOWN")
        print("-" * 80)
        print("Period | Equity Balance | Start Date  | End Date    | Days | Months | Weighted Equity")
        print("-" * 80)
        
        # Calculate periods between events
        periods = []
        current_equity = 0
        current_date = fund.start_date
        
        for i, event in enumerate(equity_events):
            # Calculate duration of current period
            if i > 0:
                duration_days = (event.event_date - current_date).days
                duration_months = duration_days / 30.44
                periods.append({
                    'start_date': current_date,
                    'end_date': event.event_date,
                    'equity': current_equity,
                    'duration_days': duration_days,
                    'duration_months': duration_months
                })
            
            # Update equity for next period
            equity_change = fund._get_equity_change_for_event(event)
            current_equity += equity_change
            current_date = event.event_date
        
        # Add final period if fund has exited
        if not fund.should_be_active and current_date <= fund.end_date:
            # Don't include the final day with $0 equity (match system method)
            if current_equity > 0:  # Only add if there's still equity
                duration_days = (fund.end_date - current_date).days + 1  # Include final day
                duration_months = duration_days / 30.44
                periods.append({
                    'start_date': current_date,
                    'end_date': fund.end_date,
                    'equity': current_equity,
                    'duration_days': duration_days,
                    'duration_months': duration_months
                })
        
        # Display periods
        total_weighted_equity = 0
        total_days = 0
        
        for i, period in enumerate(periods):
            weighted_equity = period['equity'] * period['duration_days']
            total_weighted_equity += weighted_equity
            total_days += period['duration_days']
            
            print(f"  {i+1:2d}   | ${period['equity']:>8,.0f} | {period['start_date']} | {period['end_date']} | {period['duration_days']:4d} | {period['duration_months']:6.2f} | ${weighted_equity:>12,.0f}")
        
        print("-" * 80)
        print(f"TOTAL: | {'':>8} | {'':>10} | {'':>10} | {total_days:4d} | {total_days/30.44:6.2f} | ${total_weighted_equity:>12,.0f}")
        
        # Calculate average
        calculated_average = total_weighted_equity / total_days if total_days > 0 else 0
        
        print()
        print("CALCULATION SUMMARY:")
        print("-" * 80)
        print(f"Total Weighted Equity: ${total_weighted_equity:,.0f}")
        print(f"Total Days: {total_days}")
        print(f"Calculated Average: ${calculated_average:,.0f}")
        print(f"System Average: ${system_average:,.0f}")
        print(f"Stored Average: ${fund.average_equity_balance:,.0f}")
        
        # Show any differences
        if abs(calculated_average - system_average) > 0.01:
            print(f"\nNOTE: Calculated average differs from system average by ${abs(calculated_average - system_average):,.2f}")
        
        if abs(system_average - fund.average_equity_balance) > 0.01:
            print(f"NOTE: System average differs from stored average by ${abs(system_average - fund.average_equity_balance):,.2f}")
        
        print()
        print("DETAILED EQUITY BALANCE PERIODS:")
        print("-" * 80)
        print("Period | Equity Balance | Duration | Days | Months | Weighted Equity | % of Total")
        print("-" * 80)
        
        for i, period in enumerate(periods):
            weighted_equity = period['equity'] * period['duration_days']
            percentage = (weighted_equity / total_weighted_equity * 100) if total_weighted_equity > 0 else 0
            
            print(f"  {i+1:2d}   | ${period['equity']:>8,.0f} | {period['start_date']} to {period['end_date']} | {period['duration_days']:4d} | {period['duration_months']:6.2f} | ${weighted_equity:>12,.0f} | {percentage:5.1f}%")
        
        print("-" * 80)
        print(f"TOTAL: | {'':>8} | {'':>25} | {total_days:4d} | {total_days/30.44:6.2f} | ${total_weighted_equity:>12,.0f} | 100.0%")
        
        print()
        print("EQUITY BALANCE ANALYSIS:")
        print("-" * 80)
        
        # Group by equity balance to show total time at each level
        equity_periods = {}
        for period in periods:
            equity = period['equity']
            if equity not in equity_periods:
                equity_periods[equity] = {'days': 0, 'weighted_equity': 0}
            equity_periods[equity]['days'] += period['duration_days']
            equity_periods[equity]['weighted_equity'] += period['equity'] * period['duration_days']
        
        print("Equity Balance | Total Days | Months | Weighted Equity | % of Total")
        print("-" * 80)
        for equity in sorted(equity_periods.keys(), reverse=True):
            data = equity_periods[equity]
            months = data['days'] / 30.44
            percentage = (data['weighted_equity'] / total_weighted_equity * 100) if total_weighted_equity > 0 else 0
            
            print(f"${equity:>10,.0f} | {data['days']:>9d} | {months:>6.2f} | ${data['weighted_equity']:>12,.0f} | {percentage:5.1f}%")
        
        print()
        print("VERIFICATION CALCULATION:")
        print("-" * 80)
        print("Manual calculation check:")
        for equity in sorted(equity_periods.keys(), reverse=True):
            data = equity_periods[equity]
            print(f"${equity:>10,.0f} × {data['days']:>3d} days = ${data['weighted_equity']:>12,.0f}")
        
        print(f"{'':>13} {'='*40}")
        print(f"{'TOTAL':>13} {total_days:>3d} days = ${total_weighted_equity:>12,.0f}")
        print(f"Average = ${total_weighted_equity:,.0f} ÷ {total_days} days = ${calculated_average:,.0f}")
        
        print()
        print("METHOD EXPLANATION:")
        print("-" * 80)
        print("This breakdown shows how the average equity balance is calculated using weighted periods:")
        print("1. Each period represents the time between equity-changing events")
        print("2. For each period: Weighted Equity = Equity Balance × Number of Days")
        print("3. Average = Total Weighted Equity ÷ Total Days")
        print()
        print("The system uses this same methodology but may include/exclude the final day differently.")
        
    finally:
        session.close()

if __name__ == "__main__":
    # Get fund name from command line argument, or show available funds
    if len(sys.argv) > 1:
        fund_name = sys.argv[1]
        show_equity_breakdown(fund_name)
    else:
        show_equity_breakdown()  # Will show available funds 