#!/usr/bin/env python3
"""
Test script using only the new module structure.
This avoids conflicts with the old src/models.py by not importing it.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.shared.base import Base
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from src.rates.models import RiskFreeRate
from src.fund.models import Fund, FundEvent, FundType, EventType, DistributionType, TaxPaymentType
from src.tax.models import TaxStatement
from datetime import date, datetime

def test_new_structure():
    """Test that the new module structure works correctly."""
    print("Testing new module structure...")
    
    try:
        # Test creating entities using domain methods - each call is its own transaction
        company = InvestmentCompany.create(
            name="Test Company",
            description="Test investment company"
        )
        # Session managed by @with_class_session decorator - client doesn't know about it
        company_id = company.id  # Store ID before object becomes detached
        
        entity = Entity.create(
            name="Test Entity",
            description="Test entity"
        )
        # Session managed by @with_class_session decorator - client doesn't know about it
        entity_id = entity.id  # Store ID before object becomes detached
        
        # Test creating a fund using domain method
        fund = Fund.create(
            investment_company_id=company_id,  # Use stored ID
            entity_id=entity_id,  # Use stored ID
            name="Test Fund",
            fund_type="Test",
            tracking_type=FundType.COST_BASED,
            currency="AUD"
        )
        # Session managed by @with_class_session decorator - client doesn't know about it
        
        print("✅ New module structure test passed!")
        print(f"Created: Company ID {company_id}, Entity ID {entity_id}, Fund ID {fund.id}")
        
    except Exception as e:
        print(f"❌ New module structure test failed: {e}")
        raise

if __name__ == "__main__":
    test_new_structure() 