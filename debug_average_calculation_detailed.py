#!/usr/bin/env python3
"""
Debug script to test calculate_average_equity_balance method with detailed step-by-step output.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from datetime import date, timedelta
from src.database import get_database_session
from src.fund.models import Fund, FundEvent, EventType, FundType, FundStatus
from src.entity.models import Entity, InvestmentCompany

def test_average_calculation_detailed():
    """Test the average equity balance calculation with detailed output."""
    
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Create test fund (same as in test_main.py)
        company = InvestmentCompany.create(name="Alceon", session=session)
        entity = Entity.create(name="Test Entity", session=session)
        fund = company.create_fund(
            entity=entity,
            name="Senior Debt Fund No.24",
            fund_type="Private Debt",
            tracking_type=FundType.COST_BASED,
            currency="AUD",
            description="Test fund for debugging",
            session=session
        )
        
        print(f"Created fund: {fund.name}")
        print(f"Fund ID: {fund.id}")
        print()
        
        # Add the exact same events as in test_main.py
        events_data = [
            {
                'event_type': EventType.CAPITAL_CALL,
                'event_date': date(2023, 6, 23),
                'amount': 100000.0,
                'description': 'Initial capital call'
            },
            {
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': date(2023, 12, 8),
                'amount': 7000.0,
                'description': 'Return of capital 1'
            },
            {
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': date(2024, 3, 26),
                'amount': 45000.0,
                'description': 'Return of capital 2'
            },
            {
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': date(2024, 8, 2),
                'amount': 48000.0,
                'description': 'Return of capital 3'
            }
        ]
        
        print("Adding events:")
        for i, event_data in enumerate(events_data, 1):
            event = fund.add_capital_call(
                amount=event_data['amount'],
                date=event_data['event_date'],
                description=event_data['description'],
                session=session
            ) if event_data['event_type'] == EventType.CAPITAL_CALL else fund.add_return_of_capital(
                amount=event_data['amount'],
                date=event_data['event_date'],
                description=event_data['description'],
                session=session
            )
            
            print(f"  {i}. {event.event_date} - {event.event_type.value} - ${event.amount:,.2f}")
        
        print()
        
        # Refresh fund to get latest data
        session.refresh(fund)
        
        print(f"Final fund state:")
        print(f"  Current equity balance: ${fund.current_equity_balance:,.2f}")
        print(f"  Average equity balance: ${fund.average_equity_balance:,.2f}")
        print()
        
        # Test the calculation method directly
        print("Testing calculate_average_equity_balance method:")
        calculated_avg = fund.calculate_average_equity_balance(session=session)
        print(f"  Calculated average: ${calculated_avg:,.2f}")
        print(f"  Stored average: ${fund.average_equity_balance:,.2f}")
        print(f"  Difference: ${calculated_avg - fund.average_equity_balance:,.2f}")
        print()
        
        # Manual calculation
        print("Manual calculation:")
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_([EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL])
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        print(f"  Found {len(events)} capital events:")
        for i, event in enumerate(events, 1):
            equity_str = f"${event.current_equity_balance:,.2f}" if event.current_equity_balance is not None else "None"
            print(f"    {i}. {event.event_date} - {event.event_type.value:20s} - Amount: ${event.amount:10,.2f} - Current Equity: {equity_str:>15}")
        
        print()
        
        # Step-by-step manual calculation
        print("Step-by-step manual calculation:")
        total_weighted_equity = 0.0
        total_days = 0
        
        for i in range(len(events)):
            event = events[i]
            equity = event.current_equity_balance if event.current_equity_balance is not None else 0.0
            
            # Calculate days for this period
            if i == 0:
                # First event: from event date to next event date (or end_date/today)
                if i + 1 < len(events):
                    next_event = events[i + 1]
                    days = (next_event.event_date - event.event_date).days
                else:
                    # Last event: to end_date or today
                    period_end = fund.end_date if fund.end_date else date.today()
                    days = (period_end - event.event_date).days
            else:
                # Not first event: from this event to next event (or end_date/today)
                if i + 1 < len(events):
                    next_event = events[i + 1]
                    days = (next_event.event_date - event.event_date).days
                else:
                    # Last event: to end_date or today
                    period_end = fund.end_date if fund.end_date else date.today()
                    days = (period_end - event.event_date).days
            
            weighted_equity = equity * days
            total_weighted_equity += weighted_equity
            total_days += days
            
            print(f"  Period {i+1}: {event.event_date} to {event.event_date + timedelta(days=days)}")
            print(f"    Equity: ${equity:,.2f}")
            print(f"    Days: {days}")
            print(f"    Weighted: ${weighted_equity:,.2f}")
            print()
        
        if total_days > 0:
            manual_average = total_weighted_equity / total_days
            print(f"Total weighted equity: ${total_weighted_equity:,.2f}")
            print(f"Total days: {total_days}")
            print(f"Manual average: ${manual_average:,.2f}")
            print()
            print(f"Method result: ${calculated_avg:,.2f}")
            print(f"Manual result: ${manual_average:,.2f}")
            print(f"Difference: ${calculated_avg - manual_average:,.2f}")
        else:
            print("No days calculated!")
        
    finally:
        session.close()

if __name__ == "__main__":
    test_average_calculation_detailed() 