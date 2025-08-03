#!/usr/bin/env python3
"""
Debug script to check fund status logic.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_database_session
from src.fund.models import Fund
from src.tax.models import TaxStatement
from datetime import date

def debug_fund_status():
    """Debug fund status logic."""
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Get all funds
        funds = session.query(Fund).all()
        
        for fund in funds:
            print(f"\n=== {fund.name} ===")
            print(f"Status: {fund.status.value}")
            print(f"End date: {fund.end_date}")
            print(f"Current equity: {fund.current_equity_balance}")
            
            # Get tax statements
            tax_statements = session.query(TaxStatement).filter(
                TaxStatement.fund_id == fund.id
            ).all()
            
            print(f"Tax statements: {len(tax_statements)}")
            for ts in tax_statements:
                print(f"  - {ts.financial_year}: {ts.statement_date}")
            
            # Check if final tax statement received
            is_final = fund.is_final_tax_statement_received(session=session)
            print(f"Is final tax statement received: {is_final}")
            
            # Check each tax statement
            if fund.end_date:
                for ts in tax_statements:
                    if ts.statement_date:
                        is_after_end = ts.statement_date > fund.end_date
                        print(f"  {ts.financial_year} ({ts.statement_date}) > {fund.end_date}: {is_after_end}")
            
            # Manually trigger status update
            print(f"\nTriggering status update...")
            old_status = fund.status
            fund.update_status(session=session)
            new_status = fund.status
            print(f"Status changed: {old_status.value} → {new_status.value}")
    
    finally:
        session.close()

if __name__ == "__main__":
    debug_fund_status() 