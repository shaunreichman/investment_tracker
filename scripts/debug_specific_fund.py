#!/usr/bin/env python3
"""
Debug script to investigate specific fund ID 2 that's causing the mismatch.
"""

import psycopg2
from database_config import get_database_config

def debug_specific_fund():
    """Debug the specific fund ID 2 that's causing the mismatch."""
    
    try:
        # Get database configuration
        config = get_database_config()
        print(f"🔍 Connecting to database: {config['host']}:{config['port']}/{config['database']}")
        
        # Connect to database
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        
        cursor = conn.cursor()
        
        print("✅ Database connection established")
        print("🔍 Investigating Fund ID 2 specifically...")
        print("=" * 60)
        
        # Check what fund ID 2 actually is
        cursor.execute("""
            SELECT f.id, f.name, f.investment_company_id, ic.name as company_name
            FROM investment_tracker.funds f
            LEFT JOIN investment_tracker.investment_companies ic ON f.investment_company_id = ic.id
            WHERE f.id = 2
        """)
        
        fund_2 = cursor.fetchone()
        if fund_2:
            fund_id, fund_name, company_id, company_name = fund_2
            print(f"🏦 Fund ID 2 Details:")
            print(f"   Name: {fund_name}")
            print(f"   Company: {company_name} (ID: {company_id})")
        else:
            print("❌ Fund ID 2 not found!")
        
        print()
        
        # Check what fund ID 3 actually is
        cursor.execute("""
            SELECT f.id, f.name, f.investment_company_id, ic.name as company_name
            FROM investment_tracker.funds f
            LEFT JOIN investment_tracker.investment_companies ic ON f.investment_company_id = ic.id
            WHERE f.id = 3
        """)
        
        fund_3 = cursor.fetchone()
        if fund_3:
            fund_id, fund_name, company_id, company_name = fund_3
            print(f"🏦 Fund ID 3 Details:")
            print(f"   Name: {fund_name}")
            print(f"   Company: {company_name} (ID: {company_id})")
        else:
            print("❌ Fund ID 3 not found!")
        
        print()
        
        # Check if there are any duplicate fund names or other issues
        cursor.execute("""
            SELECT f.id, f.name, f.investment_company_id, ic.name as company_name
            FROM investment_tracker.funds f
            LEFT JOIN investment_tracker.investment_companies ic ON f.investment_company_id = ic.id
            WHERE f.name LIKE '%ABC%' OR f.name LIKE '%Senior Debt%' OR f.name LIKE '%3PG%'
            ORDER BY f.id
        """)
        
        specific_funds = cursor.fetchall()
        print("🔍 All funds with names mentioned in the issue:")
        for fund_id, fund_name, company_id, company_name in specific_funds:
            print(f"   ID {fund_id}: {fund_name} → {company_name}")
        
        print()
        
        # Check for any potential ID conflicts or data issues
        cursor.execute("""
            SELECT COUNT(*) as total_funds, 
                   COUNT(DISTINCT name) as unique_names,
                   COUNT(DISTINCT investment_company_id) as unique_companies
            FROM investment_tracker.funds
        """)
        
        stats = cursor.fetchone()
        total_funds, unique_names, unique_companies = stats
        print(f"📊 Database Statistics:")
        print(f"   Total funds: {total_funds}")
        print(f"   Unique fund names: {unique_names}")
        print(f"   Unique companies: {unique_companies}")
        
        if total_funds != unique_names:
            print("   ⚠️  Potential duplicate fund names detected!")
        
        cursor.close()
        conn.close()
        print("✅ Database connection closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_specific_fund()
