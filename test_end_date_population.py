#!/usr/bin/env python3
"""
Test script to populate end_date values for all funds.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_database_session
from src.fund.models import Fund

def populate_end_dates():
    """Populate end_date values for all funds."""
    
    print("=== POPULATING END_DATES ===\n")
    
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Get all funds
        funds = session.query(Fund).all()
        
        print(f"Found {len(funds)} funds to update\n")
        
        for fund in funds:
            print(f"=== FUND: {fund.name} (ID: {fund.id}) ===")
            print(f"Current End Date: {fund.end_date}")
            
            # Calculate and set end_date
            fund.calculate_end_date(session=session)
            
            print(f"New End Date: {fund.end_date}")
            print()
        
        # Commit all changes
        session.commit()
        print("✅ All end_date values have been populated and committed!")
        
    finally:
        session.close()

if __name__ == "__main__":
    print("Starting end_date population...\n")
    
    populate_end_dates()
    
    print("Population complete!") 