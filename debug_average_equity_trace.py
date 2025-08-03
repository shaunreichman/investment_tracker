#!/usr/bin/env python3
"""
Debug script to trace when average equity balance is being updated during the test.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from src.database import get_database_session
from src.fund.models import Fund, FundEvent, EventType, FundType, DistributionType
from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany

def trace_average_equity_updates():
    """Trace when average equity balance is being updated."""
    
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Get the first fund
        fund = session.query(Fund).first()
        if not fund:
            print("No funds found")
            return
            
        print(f"=== TRACING AVERAGE EQUITY UPDATES FOR {fund.name} ===")
        
        # Store original value
        original_avg = fund.average_equity_balance
        print(f"Original average equity balance: ${original_avg:,.2f}")
        
        # Create a test distribution event to see if it triggers recalculation
        print("\n--- Creating test distribution event ---")
        event = fund.add_interest_distribution_with_withholding_tax(
            event_date=date(2024, 6, 30),
            gross_interest=1000.0,
            withholding_rate=10.0,
            description="Test distribution",
            session=session
        )
        
        # Check if average equity balance changed
        session.refresh(fund)
        new_avg = fund.average_equity_balance
        print(f"After distribution event: ${new_avg:,.2f}")
        
        if abs(new_avg - original_avg) > 0.01:
            print("⚠️  WARNING: Average equity balance changed after distribution event!")
        else:
            print("✅ Average equity balance unchanged after distribution event")
        
        # Now test the recalculate_everything methods
        print("\n--- Testing recalculate_everything methods ---")
        
        # Test create_tax_payment_events
        print("Testing create_tax_payment_events...")
        tax_events = fund.create_tax_payment_events(session=session)
        session.refresh(fund)
        avg_after_tax = fund.average_equity_balance
        print(f"After create_tax_payment_events: ${avg_after_tax:,.2f}")
        
        if abs(avg_after_tax - new_avg) > 0.01:
            print("⚠️  WARNING: Average equity balance changed after create_tax_payment_events!")
        else:
            print("✅ Average equity balance unchanged after create_tax_payment_events")
        
        # Test create_daily_risk_free_interest_charges
        print("Testing create_daily_risk_free_interest_charges...")
        daily_events = fund.create_daily_risk_free_interest_charges(session=session)
        session.refresh(fund)
        avg_after_daily = fund.average_equity_balance
        print(f"After create_daily_risk_free_interest_charges: ${avg_after_daily:,.2f}")
        
        if abs(avg_after_daily - avg_after_tax) > 0.01:
            print("⚠️  WARNING: Average equity balance changed after create_daily_risk_free_interest_charges!")
        else:
            print("✅ Average equity balance unchanged after create_daily_risk_free_interest_charges")
        
        # Test create_eofy_debt_cost_events
        print("Testing create_eofy_debt_cost_events...")
        eofy_events = fund.create_eofy_debt_cost_events(session=session)
        session.refresh(fund)
        avg_after_eofy = fund.average_equity_balance
        print(f"After create_eofy_debt_cost_events: ${avg_after_eofy:,.2f}")
        
        if abs(avg_after_eofy - avg_after_daily) > 0.01:
            print("⚠️  WARNING: Average equity balance changed after create_eofy_debt_cost_events!")
        else:
            print("✅ Average equity balance unchanged after create_eofy_debt_cost_events")
        
        print(f"\n=== SUMMARY ===")
        print(f"Original: ${original_avg:,.2f}")
        print(f"After distribution: ${new_avg:,.2f}")
        print(f"After tax events: ${avg_after_tax:,.2f}")
        print(f"After daily events: ${avg_after_daily:,.2f}")
        print(f"After EOFY events: ${avg_after_eofy:,.2f}")
        
    finally:
        session.close()

if __name__ == "__main__":
    trace_average_equity_updates() 