#!/usr/bin/env python3
"""
Simple database connection test for centralized PostgreSQL database.
"""

import psycopg2
from database_config import get_database_config

def test_database_connection():
    """Test the database connection using psycopg2."""
    try:
        # Get database configuration
        config = get_database_config()
        print(f"✅ Database config loaded: {config['host']}:{config['port']}/{config['database']}")
        
        # Test connection
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        print("✅ Database connection established")
        
        # Test simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL version: {version}")
        
        # Test if our tables exist
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'investment_tracker'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Found {len(tables)} tables in investment_tracker schema: {', '.join(tables)}")
        
        # Test a simple count query
        if 'funds' in tables:
            cursor.execute("SELECT COUNT(*) FROM investment_tracker.funds")
            fund_count = cursor.fetchone()[0]
            print(f"✅ Funds count: {fund_count}")
        
        if 'fund_events' in tables:
            cursor.execute("SELECT COUNT(*) FROM investment_tracker.fund_events")
            event_count = cursor.fetchone()[0]
            print(f"✅ Fund events count: {event_count}")
        
        cursor.close()
        conn.close()
        print("\n🎉 Database connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()
