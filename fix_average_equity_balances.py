#!/usr/bin/env python3
"""
Script to fix average equity balance calculations for all funds.
Recalculates and updates the stored average equity balance values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_database_session
from src.fund.models import Fund

def fix_average_equity_balances():
    """Recalculate and update average equity balances for all funds."""
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        funds = session.query(Fund).all()
        
        print(f"Fixing average equity balances for {len(funds)} funds...")
        
        for fund in funds:
            print(f"\nProcessing {fund.name} (ID: {fund.id})...")
            print(f"  Current average: ${fund.average_equity_balance:,.2f}")
            
            # Recalculate the average equity balance
            new_average = fund.calculate_average_equity_balance(session=session)
            
            print(f"  New average: ${new_average:,.2f}")
            print(f"  Difference: ${new_average - fund.average_equity_balance:,.2f}")
            
            # Update the stored value
            fund.average_equity_balance = new_average
        
        # Commit all changes
        session.commit()
        print(f"\n✅ Successfully updated average equity balances for {len(funds)} funds")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_average_equity_balances() 