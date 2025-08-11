#!/usr/bin/env python3
"""
Test script to verify database connectivity and queries work
"""

from src.database import create_database_engine
from sqlalchemy import text

def test_database_query():
    """Test a simple database query."""
    try:
        # Create database engine
        engine = create_database_engine()
        print("✅ Database engine created successfully")
        
        # Test connection and query
        with engine.connect() as conn:
            # First, let's see what schemas exist
            result = conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
            schemas = [row[0] for row in result.fetchall()]
            print(f"✅ Available schemas: {schemas}")
            
            # Check what tables exist in the public schema
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            public_tables = [row[0] for row in result.fetchall()]
            print(f"✅ Tables in public schema: {public_tables}")
            
            # Check what tables exist in the investment_tracker schema
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'investment_tracker'"))
            it_tables = [row[0] for row in result.fetchall()]
            print(f"✅ Tables in investment_tracker schema: {it_tables}")
            
            # Test queries with correct table names
            if 'funds' in it_tables:
                result = conn.execute(text("SELECT COUNT(*) FROM investment_tracker.funds"))
                fund_count = result.fetchone()[0]
                print(f"✅ Query successful! Funds count: {fund_count}")
            else:
                print("❌ Funds table not found in investment_tracker schema")
                
            if 'fund_events' in it_tables:
                result = conn.execute(text("SELECT COUNT(*) FROM investment_tracker.fund_events"))
                event_count = result.fetchone()[0]
                print(f"✅ Query successful! Fund events count: {event_count}")
            else:
                print("❌ Fund events table not found in investment_tracker schema")
                
            if 'investment_companies' in it_tables:
                result = conn.execute(text("SELECT COUNT(*) FROM investment_tracker.investment_companies"))
                company_count = result.fetchone()[0]
                print(f"✅ Query successful! Investment companies count: {company_count}")
            else:
                print("❌ Investment companies table not found in investment_tracker schema")
            
        print("🎉 Database connectivity test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database_query()
