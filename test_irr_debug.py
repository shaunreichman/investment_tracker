#!/usr/bin/env python3
"""
Debug script to test IRR calculation for both funds.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund

FUND_NAMES = ["Senior Debt Fund No.24", "3PG Finance"]

def debug_irr_for_funds():
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    for fund_name in FUND_NAMES:
        fund = session.query(Fund).filter(Fund.name == fund_name).first()
        print(f"\n=== {fund_name} ===")
        print(f"Current Equity Balance: {fund.current_equity_balance}")
        print(f"Should be active: {fund.should_be_active}")
        print(f"Start date: {fund.start_date}")
        print(f"End date: {fund.end_date}")
        
        gross_irr = fund.calculate_irr(session)
        after_tax_irr = fund.calculate_after_tax_irr(session)
        print(f"Gross IRR:        {gross_irr*100:.2f}%" if gross_irr is not None else "Gross IRR:        N/A")
        print(f"After-Tax IRR:    {after_tax_irr*100:.2f}%" if after_tax_irr is not None else "After-Tax IRR:    N/A")
    
    session.close()

if __name__ == "__main__":
    debug_irr_for_funds() 