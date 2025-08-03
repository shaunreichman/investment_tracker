#!/usr/bin/env python3
"""
Test script to verify fund status update logic.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_database_session
from src.fund.models import Fund, FundStatus

def test_status_update():
    """Test the status update logic for the Senior Debt Fund."""
    
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Get the Senior Debt Fund (ID 1)
        fund = session.query(Fund).filter_by(id=1).first()
        if not fund:
            print("❌ Fund not found")
            return
        
        print(f"📊 Testing Fund: {fund.name}")
        print(f"   Current Status: {fund.status.value}")
        print(f"   Equity Balance: {fund.current_equity_balance}")
        print(f"   End Date: {fund.end_date}")
        
        # Test the update_status method
        print("\n🔄 Running update_status()...")
        fund.update_status(session=session)
        
        print(f"   New Status: {fund.status.value}")
        
        # Verify the logic worked
        if fund.current_equity_balance == 0.0 and fund.status == FundStatus.REALIZED:
            print("✅ SUCCESS: Fund correctly transitioned to REALIZED")
        else:
            print("❌ FAILURE: Fund status not updated correctly")
            
    finally:
        session.close()

if __name__ == "__main__":
    test_status_update() 