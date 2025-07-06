#!/usr/bin/env python3
"""
Test script using only the new module structure.
This avoids conflicts with the old src/models.py by not importing it.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
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
    
    # Create engine and tables
    engine = create_engine('sqlite:///data/investment_tracker_new.db')
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Test creating entities
        company = InvestmentCompany(
            name="Test Company",
            description="Test investment company"
        )
        session.add(company)
        session.flush()  # Get the ID
        
        entity = Entity(
            name="Test Entity",
            description="Test entity"
        )
        session.add(entity)
        session.flush()  # Get the ID
        
        # Test creating a fund
        fund = Fund(
            investment_company_id=company.id,
            entity_id=entity.id,
            name="Test Fund",
            fund_type="Test",
            tracking_type=FundType.COST_BASED,
            currency="AUD"
        )
        session.add(fund)
        
        session.commit()
        
        print("✅ New module structure test passed!")
        print(f"Created: {company.name}, {entity.name}, {fund.name}")
        
    except Exception as e:
        print(f"❌ New module structure test failed: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    test_new_structure() 