#!/usr/bin/env python3
"""
Recalculate all daily risk-free interest charges and FY debt cost events for both funds.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund

FUND_NAMES = ["Senior Debt Fund No.24", "3PG Finance"]

def main():
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    for fund_name in FUND_NAMES:
        fund = session.query(Fund).filter(Fund.name == fund_name).first()
        if fund:
            fund.recalculate_debt_costs(session)
        else:
            print(f"Fund not found: {fund_name}")
    session.close()

if __name__ == "__main__":
    main() 