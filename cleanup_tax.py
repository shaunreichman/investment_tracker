#!/usr/bin/env python3
"""
Quick script to remove tax statements for testing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.database import get_db_session
from src.tax.models import TaxStatement
from src.fund.models import FundEvent

def cleanup():
    session = get_db_session()
    
    try:
        print("🔍 Cleaning up tax statements for fund ID 2...")
        
        # First, remove any events that reference tax statements (due to foreign key constraints)
        referenced_events = session.query(FundEvent).filter(
            FundEvent.fund_id == 2,
            FundEvent.tax_statement_id.isnot(None)
        ).all()
        for event in referenced_events:
            session.delete(event)
            print(f"🗑️  Deleted referenced fund event ID: {event.id}")
        
        # Remove any tax-related events
        tax_events = session.query(FundEvent).filter(
            FundEvent.fund_id == 2,
            FundEvent.event_type.in_(['TAX_PAYMENT', 'EOFY_DEBT_COST'])
        ).all()
        for event in tax_events:
            session.delete(event)
            print(f"🗑️  Deleted fund event ID: {event.id}")
        
        # Now remove tax statements
        tax_statements = session.query(TaxStatement).filter(TaxStatement.fund_id == 2).all()
        for ts in tax_statements:
            session.delete(ts)
            print(f"🗑️  Deleted tax statement ID: {ts.id}")
        
        session.commit()
        print(f"✅ Cleaned up {len(tax_statements)} tax statements and {len(tax_events) + len(referenced_events)} events")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    cleanup()
