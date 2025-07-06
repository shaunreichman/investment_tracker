#!/usr/bin/env python3
"""
Debug script to investigate IRR calculation issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.fund.models import Fund, FundEvent, EventType
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from src.rates.models import RiskFreeRate

def debug_irr_calculation():
    """Debug IRR calculation for a specific fund."""
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get the first fund
        fund = session.query(Fund).first()
        if not fund:
            print("No funds found in database")
            return
        
        print(f"Debugging IRR calculation for fund: {fund.name}")
        print(f"Fund type: {fund.tracking_type.value}")
        print(f"Should be active: {fund.should_be_active}")
        print(f"Is active: {fund.is_active}")
        print(f"Current equity: ${fund.current_equity_balance:,.2f}")
        
        # Get all events for this fund
        all_events = session.query(FundEvent).filter(FundEvent.fund_id == fund.id).order_by(FundEvent.event_date).all()
        print(f"\nTotal events: {len(all_events)}")
        
        # Show event types and amounts
        event_types = {}
        for event in all_events:
            event_type = event.event_type.value
            if event_type not in event_types:
                event_types[event_type] = []
            event_types[event_type].append({
                'date': event.event_date,
                'amount': event.amount,
                'description': event.description
            })
        
        print("\nEvent types found:")
        for event_type, events in event_types.items():
            print(f"  {event_type}: {len(events)} events")
            for event in events[:3]:  # Show first 3 events
                print(f"    {event['date']}: ${event['amount']:,.2f} - {event['description']}")
            if len(events) > 3:
                print(f"    ... and {len(events) - 3} more")
        
        # Test IRR calculation directly
        print(f"\nTesting IRR calculation:")
        
        # Get start and end dates
        start_date = fund.start_date
        end_date = fund.end_date
        print(f"Start date: {start_date}")
        print(f"End date: {end_date}")
        
        # Test _calculate_irr_base with different options
        print(f"\nTesting _calculate_irr_base:")
        
        # Basic IRR
        result = fund._calculate_irr_base(include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, session=session, return_cashflows=True)
        print(f"Basic IRR result: {result}")
        
        # After-tax IRR
        result = fund._calculate_irr_base(include_tax_payments=True, include_risk_free_charges=False, include_fy_debt_cost=False, session=session, return_cashflows=True)
        print(f"After-tax IRR result: {result}")
        
        # Real IRR
        result = fund._calculate_irr_base(include_tax_payments=True, include_risk_free_charges=True, include_fy_debt_cost=True, session=session, return_cashflows=True)
        print(f"Real IRR result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    debug_irr_calculation() 