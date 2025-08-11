#!/usr/bin/env python3
"""
Script to check the complete database schema and verify all tables are present.
"""

from src.database import create_database_engine
from sqlalchemy import text

def check_database_schema():
    """Check the complete database schema."""
    try:
        # Create database engine
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
            
            print(f"\n📊 Found {len(tables)} tables:")
            for table_name, table_type in tables:
                print(f"   • {table_name} ({table_type})")
            
            # Get table counts
            print(f"\n📈 Table record counts:")
            for table_name, _ in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    print(f"   • {table_name}: {count:,} records")
                except Exception as e:
                    print(f"   • {table_name}: Error getting count - {e}")
            
            # Check if this matches expected schema
            expected_tables = [
                'entities', 'investment_companies', 'funds', 'fund_events', 
                'fund_event_types', 'fund_statuses', 'risk_free_rates', 
                'tax_statements', 'fund_tax_statements', 'fund_performance_metrics',
                'fund_irr_calculations'
            ]
            
            actual_table_names = [table[0] for table in tables]
            missing_tables = set(expected_tables) - set(actual_table_names)
            extra_tables = set(actual_table_names) - set(expected_tables)
            
            print(f"\n🔍 Schema Analysis:")
            if missing_tables:
                print(f"   ❌ Missing tables: {', '.join(missing_tables)}")
            else:
                print(f"   ✅ All expected tables present")
                
            if extra_tables:
                print(f"   ⚠️  Extra tables: {', '.join(extra_tables)}")
            
            print(f"\n🎯 Schema Status: {len(actual_table_names)}/{len(expected_tables)} tables present")
            
    except Exception as e:
        print(f"❌ Error checking database schema: {e}")

if __name__ == "__main__":
    check_database_schema()
