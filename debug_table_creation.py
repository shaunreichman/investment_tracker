#!/usr/bin/env python3
"""
Debug script to test table creation step by step.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.shared.base import Base
from src.database import create_database_engine
from sqlalchemy import text

def debug_table_creation():
    """Debug table creation step by step."""
    try:
        print("🔧 Debugging table creation...")
        
        # Create engine
        engine = create_database_engine()
        print(f"✅ Engine created: {engine.url}")
        
        # Test connection
        with engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Check current tables
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            current_tables = [row[0] for row in result.fetchall()]
            print(f"📊 Current tables: {current_tables}")
            
            # Try to create a simple table first
            print("\n🔧 Testing simple table creation...")
            try:
                conn.execute(text("CREATE TABLE test_simple (id INTEGER PRIMARY KEY)"))
                conn.commit()
                print("✅ Simple table created successfully")
            except Exception as e:
                print(f"❌ Simple table creation failed: {e}")
            
            # Check if simple table was created
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables_after_simple = [row[0] for row in result.fetchall()]
            print(f"📊 Tables after simple creation: {tables_after_simple}")
            
            # Now try to create the domain_events table specifically
            print("\n🔧 Testing domain_events table creation...")
            try:
                # Get the CREATE TABLE SQL for domain_events
                domain_events_table = Base.metadata.tables['domain_events']
                create_sql = str(domain_events_table.compile(engine))
                print(f"📝 CREATE SQL: {create_sql}")
                
                # Execute the CREATE TABLE
                conn.execute(text(create_sql))
                conn.commit()
                print("✅ domain_events table created successfully")
                
            except Exception as e:
                print(f"❌ domain_events table creation failed: {e}")
                import traceback
                traceback.print_exc()
            
            # Check final state
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            final_tables = [row[0] for row in result.fetchall()]
            print(f"📊 Final tables: {final_tables}")
            
            if 'domain_events' in final_tables:
                print("🎉 SUCCESS: domain_events table exists!")
            else:
                print("❌ FAILED: domain_events table still missing")
                
    except Exception as e:
        print(f"❌ Error in debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_table_creation()
