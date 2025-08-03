#!/usr/bin/env python3
"""
Script to fix all stored average equity balance values by recalculating them.
This version commits the changes to the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_database_session
from src.fund.models import Fund

def fix_all_average_equity_balances():
    """Fix all stored average equity balance values by recalculating them."""
    
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        funds = session.query(Fund).all()
        
        print(f"=== FIXING AVERAGE EQUITY BALANCES FOR {len(funds)} FUNDS ===")
        
        for fund in funds:
            print(f"\n--- {fund.name} (ID: {fund.id}) ---")
            print(f"Type: {fund.tracking_type.value}")
            
            # Get current values
            old_average = fund.average_equity_balance
            calculated_average = fund.calculate_average_equity_balance(session=session)
            
            print(f"Old average: ${old_average:,.2f}")
            print(f"Calculated average: ${calculated_average:,.2f}")
            
            # Update the stored value
            fund.average_equity_balance = calculated_average
            
            print(f"Updated to: ${fund.average_equity_balance:,.2f}")
        
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
    fix_all_average_equity_balances() 