#!/usr/bin/env python3
"""
Debug script to investigate why daily interest charges are not being created.
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

def debug_daily_charges():
    """Debug daily interest charge creation."""
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get the first fund
        fund = session.query(Fund).first()
        if not fund:
            print("No funds found in database")
            return
        
        print(f"Debugging daily interest charges for fund: {fund.name}")
        print(f"Fund currency: {fund.currency}")
        print(f"Start date: {fund.start_date}")
        print(f"End date: {fund.end_date}")
        
        # Check risk-free rates
        risk_free_rates = session.query(RiskFreeRate).filter(
            RiskFreeRate.currency == fund.currency,
            RiskFreeRate.rate_date <= fund.end_date
        ).order_by(RiskFreeRate.rate_date).all()
        
        print(f"\nRisk-free rates found: {len(risk_free_rates)}")
        if risk_free_rates:
            print(f"First rate: {risk_free_rates[0].rate_date} - {risk_free_rates[0].rate}%")
            print(f"Last rate: {risk_free_rates[-1].rate_date} - {risk_free_rates[-1].rate}%")
        
        # Check existing daily interest charges
        existing_charges = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        ).all()
        print(f"\nExisting daily interest charges: {len(existing_charges)}")
        
        # Check cash flow events for equity tracking
        cash_flow_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_([
                EventType.CAPITAL_CALL,
                EventType.UNIT_PURCHASE,
                EventType.RETURN_OF_CAPITAL,
                EventType.UNIT_SALE
            ])
        ).order_by(FundEvent.event_date).all()
        
        print(f"\nCash flow events for equity tracking: {len(cash_flow_events)}")
        for event in cash_flow_events:
            print(f"  {event.event_date}: {event.event_type} - ${event.amount:,.2f}")
        
        # Try to create daily interest charges
        print(f"\nAttempting to create daily interest charges...")
        daily_events = fund.create_daily_risk_free_interest_charges(session=session)
        print(f"Created {len(daily_events)} daily interest charge events")
        
        # Check if any were actually created
        new_charges = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        ).all()
        print(f"Total daily interest charges after creation: {len(new_charges)}")
        
        if new_charges:
            print("Sample daily interest charges:")
            for event in new_charges[:5]:
                print(f"  {event.event_date}: ${event.amount:,.2f} - {event.description}")
        
    finally:
        session.close()

if __name__ == "__main__":
    debug_daily_charges() 