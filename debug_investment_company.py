#!/usr/bin/env python3
"""Debug script to test investment company domain methods"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_db_session
from src.investment_company.models import InvestmentCompany
from src.fund.models import Fund, FundStatus
from src.entity.models import Entity

def test_investment_company_methods():
    """Test the domain methods that are failing in the API"""
    try:
        print("Testing investment company domain methods...")
        
        # Test imports
        print("✓ Imports successful")
        
        # Test session creation
        session = get_db_session()
        print("✓ Session created successfully")
        
        # Test model instantiation
        company = InvestmentCompany(
            name="Test Company",
            description="Test Description",
            website="https://test.com"
        )
        print("✓ InvestmentCompany model instantiated")
        
        # Test if methods exist
        if hasattr(company, 'get_total_funds_under_management'):
            print("✓ get_total_funds_under_management method exists")
        else:
            print("✗ get_total_funds_under_management method missing")
            
        if hasattr(company, 'get_total_commitments'):
            print("✓ get_total_commitments method exists")
        else:
            print("✗ get_total_commitments method missing")
            
        # Test if FundStatus enum exists
        try:
            active_status = FundStatus.ACTIVE
            print("✓ FundStatus.ACTIVE exists:", active_status)
        except Exception as e:
            print("✗ FundStatus.ACTIVE error:", e)
            
        print("✓ All basic tests passed")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_investment_company_methods()
