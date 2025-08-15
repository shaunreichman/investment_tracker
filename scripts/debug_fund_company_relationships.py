#!/usr/bin/env python3
"""
Debug script to investigate fund-company relationships.
This will help us understand why ABC Fund is showing the wrong company in breadcrumbs.
"""

import psycopg2
from database_config import get_database_config

def debug_fund_company_relationships():
    """Debug fund-company relationships to find data inconsistencies."""
    
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
        print("🔍 Investigating Fund-Company Relationships...")
        print("=" * 60)
        
        # Get all funds with their company relationships
        cursor.execute("""
            SELECT f.id, f.name, f.investment_company_id, ic.name as company_name
            FROM investment_tracker.funds f
            LEFT JOIN investment_tracker.investment_companies ic ON f.investment_company_id = ic.id
            ORDER BY f.id
        """)
        
        funds = cursor.fetchall()
        print(f"📊 Found {len(funds)} funds in database:")
        print()
        
        for fund_id, fund_name, company_id, company_name in funds:
            print(f"🏦 Fund: {fund_name} (ID: {fund_id})")
            print(f"   📍 Company: {company_name or 'None'} (ID: {company_id})")
            print()
        
        # Look specifically for ABC Fund and Senior Debt Fund
        print("🎯 Looking for specific funds mentioned in the issue:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT f.id, f.name, f.investment_company_id, ic.name as company_name
            FROM investment_tracker.funds f
            LEFT JOIN investment_tracker.investment_companies ic ON f.investment_company_id = ic.id
            WHERE f.name LIKE '%ABC%' OR f.name LIKE '%Senior Debt%'
        """)
        
        specific_funds = cursor.fetchall()
        
        abc_fund = None
        senior_debt_fund = None
        
        for fund_id, fund_name, company_id, company_name in specific_funds:
            if 'ABC' in fund_name:
                abc_fund = (fund_id, fund_name, company_id, company_name)
                print(f"✅ Found ABC Fund: {fund_name}")
                print(f"   Company: {company_name or 'None'}")
                print(f"   Company ID: {company_id}")
            elif 'Senior Debt' in fund_name:
                senior_debt_fund = (fund_id, fund_name, company_id, company_name)
                print(f"✅ Found Senior Debt Fund: {fund_name}")
                print(f"   Company: {company_name or 'None'}")
                print(f"   Company ID: {company_id}")
        
        if not abc_fund:
            print("❌ ABC Fund not found")
        if not senior_debt_fund:
            print("❌ Senior Debt Fund not found")
        
        # Check for any funds with the same company ID
        print("\n🔍 Checking for potential company ID conflicts:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT f.investment_company_id, ic.name as company_name, 
                   COUNT(*) as fund_count,
                   STRING_AGG(f.name, ', ' ORDER BY f.name) as fund_names
            FROM investment_tracker.funds f
            LEFT JOIN investment_tracker.investment_companies ic ON f.investment_company_id = ic.id
            GROUP BY f.investment_company_id, ic.name
            HAVING COUNT(*) > 1
            ORDER BY fund_count DESC
        """)
        
        company_fund_counts = cursor.fetchall()
        
        for company_id, company_name, fund_count, fund_names in company_fund_counts:
            print(f"⚠️  Company '{company_name}' (ID: {company_id}) has {fund_count} funds:")
            for fund_name in fund_names.split(', '):
                print(f"   - {fund_name}")
            print()
        
        # Check investment companies
        print("🏢 Investment Companies:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT ic.id, ic.name, COUNT(f.id) as fund_count
            FROM investment_tracker.investment_companies ic
            LEFT JOIN investment_tracker.funds f ON ic.id = f.investment_company_id
            GROUP BY ic.id, ic.name
            ORDER BY ic.id
        """)
        
        companies = cursor.fetchall()
        for company_id, company_name, fund_count in companies:
            print(f"Company: {company_name} (ID: {company_id}) - {fund_count} funds")
            
            # Get funds for this company
            cursor.execute("""
                SELECT name FROM investment_tracker.funds 
                WHERE investment_company_id = %s 
                ORDER BY name
            """, (company_id,))
            
            company_funds = [row[0] for row in cursor.fetchall()]
            if company_funds:
                print(f"  Funds: {', '.join(company_funds)}")
            else:
                print("  Funds: None")
            print()
        
        cursor.close()
        conn.close()
        print("✅ Database connection closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_fund_company_relationships()
