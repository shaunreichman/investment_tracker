#!/usr/bin/env python3
"""
Simple script to check database schema.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from src.database import create_database_engine

def check_schema():
    """Check what tables exist in the database."""
    try:
        engine = create_database_engine()
        print(f"🔍 Checking database schema...")
        print(f"   Database: {engine.url}")
        
        with engine.connect() as conn:
            # Get all tables
            result = conn.execute(text("""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            print(f"   Found {len(tables)} tables:")
            for table_name, table_type in tables:
                print(f"     - {table_name} ({table_type})")
                
            # Check specifically for domain_events
            domain_events_exists = any(name == 'domain_events' for name, _ in tables)
            print(f"\n   Domain events table exists: {domain_events_exists}")
            
            if not domain_events_exists:
                print("   ❌ Missing domain_events table - this is why the API is failing!")
                print("   💡 Need to create the missing table for Phase 3.5 architecture completion")
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_schema()
