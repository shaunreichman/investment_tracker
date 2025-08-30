#!/usr/bin/env python3
"""
Test script to check which specific companies are causing issues.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.api.database import get_db_session
from src.investment_company.models import InvestmentCompany
from src.investment_company.services import CompanyPortfolioService

def test_specific_companies():
    """Test specific companies to see which ones cause issues."""
    print("🚀 Testing specific companies...")
    
    session = get_db_session()
    portfolio_service = CompanyPortfolioService()
    
    try:
        # Get all companies
        companies = session.query(InvestmentCompany).order_by(InvestmentCompany.id).all()
        print(f"🔍 Found {len(companies)} companies in database")
        
        # Test each company individually
        for company in companies:
            print(f"\n🔍 Testing company ID {company.id}: {company.name}")
            
            try:
                # Test portfolio service calls
                total_funds = portfolio_service.get_total_funds_under_management(company, session)
                total_commitments = portfolio_service.get_total_commitments(company, session)
                
                print(f"✅ Company {company.id}: Portfolio data retrieved successfully")
                print(f"   - Total funds: {total_funds}")
                print(f"   - Total commitments: {total_commitments}")
                
                # Test fund access
                if company.funds:
                    print(f"   - Has {len(company.funds)} funds")
                    for fund in company.funds:
                        print(f"     - Fund {fund.id}: {fund.name}, Status: {fund.status}")
                else:
                    print(f"   - No funds")
                
            except Exception as e:
                print(f"❌ Company {company.id}: Error during processing")
                print(f"   - Error: {str(e)}")
                import traceback
                traceback.print_exc()
                
    finally:
        session.close()

if __name__ == "__main__":
    test_specific_companies()
