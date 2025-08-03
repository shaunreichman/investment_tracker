#!/usr/bin/env python3
"""
Debug script to check daily interest charges for cost-based funds.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_database_session
from src.fund.models import Fund, FundEvent, EventType
from src.fund.models import FundEvent, EventType

def debug_daily_charges():
    """Check daily interest charges for cost-based funds."""
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Get all funds
        funds = session.query(Fund).all()
        
        print("=== DAILY INTEREST CHARGES DEBUG ===")
        
        for fund in funds:
            print(f"\n--- {fund.name} (ID: {fund.id}) ---")
            print(f"Fund type: {fund.fund_type}")
            print(f"Status: {fund.status}")
            print(f"End date: {fund.end_date}")
            
            # Check daily interest charges
            daily_charges = session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id,
                FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
            ).all()
            
            print(f"Daily interest charges in database: {len(daily_charges)}")
            
            if daily_charges:
                print("Sample daily charges:")
                for i, charge in enumerate(daily_charges[:3]):
                    print(f"  {i+1}. Date: {charge.event_date}, Amount: ${charge.amount:,.2f}")
                if len(daily_charges) > 3:
                    print(f"  ... and {len(daily_charges) - 3} more")
            
            # Check tax payment events
            tax_events = session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id,
                FundEvent.event_type == EventType.TAX_PAYMENT
            ).all()
            
            print(f"Tax payment events in database: {len(tax_events)}")
            
            if tax_events:
                print("Sample tax events:")
                for i, tax_event in enumerate(tax_events[:3]):
                    print(f"  {i+1}. Date: {tax_event.event_date}, Amount: ${tax_event.amount:,.2f}")
                if len(tax_events) > 3:
                    print(f"  ... and {len(tax_events) - 3} more")
            
            # Check all fund events
            all_events = session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id
            ).order_by(FundEvent.event_date).all()
            
            print(f"Total fund events: {len(all_events)}")
            print("Event types:")
            event_types = {}
            for event in all_events:
                event_type = event.event_type.value
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            for event_type, count in sorted(event_types.items()):
                print(f"  {event_type}: {count}")
    
    finally:
        session.close()

if __name__ == "__main__":
    debug_daily_charges() 