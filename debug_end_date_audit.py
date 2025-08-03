#!/usr/bin/env python3
"""
Debug script to audit end_date calculation logic and identify issues.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date
from src.database import get_database_session
from src.fund.models import Fund, FundEvent, EventType, FundType, FundStatus
from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany

def audit_end_date_logic():
    """Audit the current end_date calculation logic and identify issues."""
    
    print("=== END_DATE AUDIT ===\n")
    
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Get all funds
        funds = session.query(Fund).all()
        
        print(f"Found {len(funds)} funds to audit\n")
        
        for fund in funds:
            print(f"=== FUND: {fund.name} (ID: {fund.id}) ===")
            print(f"Tracking Type: {fund.tracking_type.value}")
            print(f"Current Status: {fund.status.value}")
            print(f"Current Equity Balance: {fund.current_equity_balance}")
            print(f"Current End Date: {fund.end_date}")
            
            # Get all events for this fund
            events = session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id
            ).order_by(FundEvent.event_date, FundEvent.id).all()
            
            print(f"Total Events: {len(events)}")
            
            # Analyze equity events
            equity_events = [e for e in events if e.event_type in [
                EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL,
                EventType.UNIT_PURCHASE, EventType.UNIT_SALE
            ]]
            
            print(f"Equity Events: {len(equity_events)}")
            for event in equity_events:
                print(f"  - {event.event_type.value}: {event.event_date}, Amount: {event.amount}, Equity Balance: {event.current_equity_balance}")
            
            # Analyze distribution events
            distribution_events = [e for e in events if e.event_type == EventType.DISTRIBUTION]
            print(f"Distribution Events: {len(distribution_events)}")
            for event in distribution_events:
                print(f"  - {event.event_type.value}: {event.event_date}, Amount: {event.amount}")
            
            # Test current calculate_end_date logic
            print("\n--- Testing Current calculate_end_date Logic ---")
            
            # Save current end_date
            original_end_date = fund.end_date
            
            # Call calculate_end_date
            fund.calculate_end_date(session=session)
            new_end_date = fund.end_date
            
            print(f"Original End Date: {original_end_date}")
            print(f"Calculated End Date: {new_end_date}")
            
            # Analyze the logic step by step
            print("\n--- Step-by-Step Analysis ---")
            
            # Check if fund has equity balance > 0
            has_equity = False
            if fund.tracking_type == FundType.NAV_BASED:
                has_equity = fund.current_units is not None and fund.current_units > 0
            elif fund.tracking_type == FundType.COST_BASED:
                has_equity = fund.current_equity_balance is not None and fund.current_equity_balance > 0
            
            print(f"Fund has equity balance > 0: {has_equity}")
            
            if has_equity:
                print("  → End date should be None (fund still active)")
            else:
                print("  → Fund is realized, should find final equity/distribution event")
                
                # Get relevant events (equity + distribution)
                relevant_events = [e for e in events if e.event_type in [
                    EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL,
                    EventType.UNIT_PURCHASE, EventType.UNIT_SALE, EventType.DISTRIBUTION
                ]]
                
                print(f"  Relevant events: {len(relevant_events)}")
                
                # Find events after equity balance reached zero
                events_after_zero = []
                for event in relevant_events:
                    if event.current_equity_balance is not None and event.current_equity_balance == 0:
                        events_after_zero.append(event)
                
                print(f"  Events after equity balance reached zero: {len(events_after_zero)}")
                for event in events_after_zero:
                    print(f"    - {event.event_type.value}: {event.event_date}")
                
                if events_after_zero:
                    expected_end_date = events_after_zero[-1].event_date
                    print(f"  Expected end date: {expected_end_date}")
                else:
                    # Fallback to last equity event
                    equity_events_only = [e for e in relevant_events if e.event_type in [
                        EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL,
                        EventType.UNIT_PURCHASE, EventType.UNIT_SALE
                    ]]
                    if equity_events_only:
                        expected_end_date = equity_events_only[-1].event_date
                        print(f"  Fallback end date (last equity event): {expected_end_date}")
                    else:
                        expected_end_date = None
                        print("  No equity events found")
            
            print("\n" + "="*50 + "\n")
            
    finally:
        session.close()

def test_proposed_logic():
    """Test the proposed end_date calculation logic."""
    
    print("=== TESTING PROPOSED END_DATE LOGIC ===\n")
    
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        funds = session.query(Fund).all()
        
        for fund in funds:
            print(f"=== FUND: {fund.name} ===")
            
            # Proposed logic:
            # 1. Check if equity balance is 0
            # 2. If yes, find the final equity or distribution event
            # 3. That should be the end_date
            
            has_equity = False
            if fund.tracking_type == FundType.NAV_BASED:
                has_equity = fund.current_units is not None and fund.current_units > 0
            elif fund.tracking_type == FundType.COST_BASED:
                has_equity = fund.current_equity_balance is not None and fund.current_equity_balance > 0
            
            print(f"Has equity balance > 0: {has_equity}")
            
            if has_equity:
                proposed_end_date = None
                print("  → Fund still active, end_date should be None")
            else:
                # Find final equity or distribution event
                events = session.query(FundEvent).filter(
                    FundEvent.fund_id == fund.id,
                    FundEvent.event_type.in_([
                        EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL,
                        EventType.UNIT_PURCHASE, EventType.UNIT_SALE, EventType.DISTRIBUTION
                    ])
                ).order_by(FundEvent.event_date.desc(), FundEvent.id.desc()).all()
                
                if events:
                    proposed_end_date = events[0].event_date
                    print(f"  → Final equity/distribution event: {events[0].event_type.value} on {proposed_end_date}")
                else:
                    proposed_end_date = None
                    print("  → No equity or distribution events found")
            
            print(f"  Proposed end_date: {proposed_end_date}")
            print(f"  Current end_date: {fund.end_date}")
            
            if proposed_end_date != fund.end_date:
                print("  ⚠️  MISMATCH DETECTED!")
            else:
                print("  ✅ Match")
            
            print()
            
    finally:
        session.close()

if __name__ == "__main__":
    print("Starting end_date audit...\n")
    
    audit_end_date_logic()
    test_proposed_logic()
    
    print("Audit complete!") 