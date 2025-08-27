#!/usr/bin/env python3
"""
Simple database connection test script.
Tests the PostgreSQL connection using the centralized configuration.
"""

import sys
import os

# Ensure project root is on the Python path so `src` package can be imported
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_database_connection():
    """Test the database connection."""
    try:
        from src.database import create_database_engine
        from src.config import get_database_url
        from sqlalchemy import text
        
        print("Testing database connection...")
        print(f"Database URL: {get_database_url()}")
        
        # Create engine
        engine = create_database_engine()
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Test if our database exists
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"Connected to database: {db_name}")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the project root directory and src package is available")
        return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check if database 'investment_tracker' exists")
        print("3. Verify user 'postgres' with password 'development_password' exists")
        print("4. Check environment variables or use defaults")
        return False

def test_basic_queries():
    """Test basic database queries."""
    try:
        from src.database import create_database_engine
        from sqlalchemy import text
        
        print("\nTesting basic database queries...")
        engine = create_database_engine()
        
        with engine.connect() as connection:
            # Test if tables exist (check both public and investment_tracker schemas)
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema IN ('public', 'investment_tracker')
                ORDER BY table_schema, table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("⚠️  No tables found. Run 'python scripts/init_database.py' to create tables.")
                
        return True
        
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 50)
    print("Database Connection Test")
    print("=" * 50)
    
    # Test connection
    if test_database_connection():
        # Test basic queries
        test_basic_queries()
        
        print("\n" + "=" * 50)
        print("✅ Database connection test completed successfully!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ Database connection test failed!")
        print("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main()
