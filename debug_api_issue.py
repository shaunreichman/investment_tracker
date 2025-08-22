#!/usr/bin/env python3
"""
Debug script to isolate the API issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api import create_app
from src.fund.models import Fund
from sqlalchemy.orm import sessionmaker, scoped_session
from src.database import create_database_engine

def debug_api_issue():
    """Debug the API issue step by step."""
    print("🔍 Debugging API issue...")
    
    # Create the app
    app = create_app()
    print("✅ App created successfully")
    
    # Get a database session
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    session = scoped_session(Session)
    print("✅ Database session created")
    
    try:
        # Try to get a fund
        funds = Fund.get_all(session=session)
        if not funds:
            print("❌ No funds found in database")
            return
        
        fund = funds[0]
        print(f"✅ Found fund: {fund.id}")
        
        # Try to get summary data
        print("🔍 Testing fund.get_summary_data...")
        try:
            fund_data = fund.get_summary_data(session=session)
            print("✅ fund.get_summary_data succeeded")
            print(f"   Summary data keys: {list(fund_data.keys())}")
        except Exception as e:
            print(f"❌ fund.get_summary_data failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Try to get all events
        print("🔍 Testing fund.get_all_fund_events...")
        try:
            all_events = fund.get_all_fund_events(exclude_system_events=True, session=session)
            print(f"✅ fund.get_all_fund_events succeeded: {len(all_events)} events")
            
            if all_events:
                event = all_events[0]
                print(f"   First event: id={event.id}, type={event.event_type}")
                print(f"   Event type value: {event.event_type.value if event.event_type else None}")
                
                # Test the specific field access that's failing in the API
                try:
                    event_type_upper = event.event_type.value.upper() if event.event_type else None
                    print(f"✅ event.event_type.value.upper() succeeded: {event_type_upper}")
                except Exception as e:
                    print(f"❌ event.event_type.value.upper() failed: {e}")
                    import traceback
                    traceback.print_exc()
            
        except Exception as e:
            print(f"❌ fund.get_all_fund_events failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print("✅ All tests passed - API should work")
        
    finally:
        session.close()
        print("✅ Database session closed")

if __name__ == "__main__":
    debug_api_issue()
