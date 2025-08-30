#!/usr/bin/env python3
"""
Test script to check database connection differences.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.api.database import get_db_session
from src.investment_company.models import InvestmentCompany
from sqlalchemy import text

def test_database_connection():
    """Test database connection and query differences."""
    print("🚀 Testing database connection...")
    
    session = get_db_session()
    
    try:
        # Test 1: Direct query
        print("\n🔍 Test 1: Direct SQLAlchemy query")
        companies = session.query(InvestmentCompany).all()
        print(f"✅ Direct query returned {len(companies)} companies")
        for company in companies:
            print(f"  - ID: {company.id}, Name: {company.name}")
        
        # Test 2: Raw SQL query
        print("\n🔍 Test 2: Raw SQL query")
        result = session.execute(text("SELECT id, name FROM investment_companies ORDER BY id"))
        raw_companies = result.fetchall()
        print(f"✅ Raw SQL query returned {len(raw_companies)} companies")
        for company in raw_companies:
            print(f"  - ID: {company.id}, Name: {company.name}")
        
        # Test 3: Check database URL
        print("\n🔍 Test 3: Database connection info")
        engine = session.bind
        print(f"✅ Database URL: {engine.url}")
        print(f"✅ Database name: {engine.url.database}")
        print(f"✅ Database host: {engine.url.host}")
        print(f"✅ Database port: {engine.url.port}")
        
        # Test 4: Check if there are any active transactions
        print("\n🔍 Test 4: Transaction status")
        print(f"✅ Session autocommit: {session.autocommit}")
        print(f"✅ Session is active: {session.is_active}")
        
    except Exception as e:
        print(f"❌ Error during database test: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    test_database_connection()
