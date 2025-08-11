#!/usr/bin/env python3
"""
Test script to verify database connection to centralized PostgreSQL database.
"""

from src.database import create_database_engine
from sqlalchemy import text

def test_database_connection():
    """Test the database connection and run a simple query."""
    try:
        # Create database engine
        engine = create_database_engine()
        print(f"✅ Database engine created successfully")
        print(f"   Database URL: {engine.url}")
        
        # Test connection
        with engine.connect() as conn:
            print("✅ Database connection established")
            
            # Test simple query
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL version: {version}")
            
            # Test if our tables exist
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Found {len(tables)} tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")
            
            print("\n🎉 Database connection test successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()
