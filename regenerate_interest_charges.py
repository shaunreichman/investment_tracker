#!/usr/bin/env python3
"""
Delete all old DAILY_RISK_FREE_INTEREST_CHARGE events and regenerate them using the real rates for all funds.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType

def regenerate_interest_charges():
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    funds = session.query(Fund).all()
    for fund in funds:
        # Delete old daily interest charge events
        deleted = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        ).delete()
        session.commit()
        print(f"Deleted {deleted} old daily interest charges for {fund.name}")
        # Regenerate new ones
        created = fund.create_daily_risk_free_interest_charges(session)
        print(f"Regenerated {len(created)} new daily interest charges for {fund.name}")
    session.close()
    print("All funds updated.")

if __name__ == "__main__":
    regenerate_interest_charges() 