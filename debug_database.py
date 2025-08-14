#!/usr/bin/env python3
"""
Debug script to understand the database connection issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import create_database_engine
from sqlalchemy import text

def debug_database():
    """Debug the database connection and schema."""
    try:
        print("🔍 Debugging database connection...")
        
        # Create engine
        engine = create_database_engine()
        print(f"✅ Engine created: {engine.url}")
        
        # Test connection and get database info
        with engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Get current database and schema
            result = conn.execute(text("SELECT current_database(), current_schema()"))
            db_info = result.fetchone()
            print(f"📊 Current database: {db_info[0]}")
            print(f"📊 Current schema: {db_info[1]}")
            
            # List all schemas
            result = conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
            schemas = [row[0] for row in result.fetchall()]
            print(f"📊 Available schemas: {schemas}")
            
            # Check tables in public schema
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            public_tables = [row[0] for row in result.fetchall()]
            print(f"📊 Tables in public schema: {public_tables}")
            
            # Check tables in all schemas
            result = conn.execute(text("SELECT table_schema, table_name FROM information_schema.tables ORDER BY table_schema, table_name"))
            all_tables = [(row[0], row[1]) for row in result.fetchall()]
            print(f"📊 All tables in all schemas: {all_tables}")
            
            # Try to create a test table in public schema
            print("\n🔧 Testing table creation in public schema...")
            try:
                conn.execute(text("CREATE TABLE IF NOT EXISTS test_debug (id INTEGER PRIMARY KEY)"))
                conn.commit()
                print("✅ Test table created successfully")
                
                # Check if it appears in public schema
                result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'test_debug'"))
                if result.fetchone():
                    print("✅ Test table visible in public schema")
                else:
                    print("❌ Test table NOT visible in public schema")
                    
            except Exception as e:
                print(f"❌ Test table creation failed: {e}")
                
    except Exception as e:
        print(f"❌ Error in debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_database()
