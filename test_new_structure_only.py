#!/usr/bin/env python3
"""
Test script using only the new module structure.
This avoids conflicts with the old src/models.py by not importing it.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from src.rates.models import RiskFreeRate
from src.fund.models import Fund, FundEvent, FundType, EventType, DistributionType, TaxPaymentType
from src.tax.models import TaxStatement
from src.shared.utils import reset_database_for_testing
from src.database import get_database_session
from datetime import date, datetime

def test_new_structure():
    """Test that the new module structure works correctly."""
    print("Testing new module structure...")
    
    # Outermost backend layer manages the session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Reset database for clean testing - handled by domain layer
        print("Resetting database for clean test...")
        reset_database_for_testing(session)
        print("Database reset complete.")
        
        # Test creating entities using domain methods - each call accepts session parameter
        print("Creating investment company...")
        company = InvestmentCompany.create(
            name="Test Company",
            description="Test investment company",
            session=session
        )
        # Session managed by outermost layer - domain methods don't know about it
        print(f"Created company: {company.name}")
        
        print("Creating entity...")
        entity = Entity.create(
            name="Test Entity",
            description="Test entity",
            session=session
        )
        # Session managed by outermost layer - domain methods don't know about it
        print(f"Created entity: {entity.name}")
        
        # Test creating a fund using the direct object method pattern
        print("Creating fund using company.create_fund()...")
        fund = company.create_fund(
            entity=entity,  # Pass entity object, not ID
            name="Test Fund",
            fund_type="Test",
            tracking_type=FundType.COST_BASED,
            currency="AUD",
            session=session
        )
        # Session managed by @with_session decorator - consistent with fund events
        print(f"Created fund: {fund.name}")
        
        # Test domain operations on the fund
        print("Adding capital call to fund...")
        fund.add_capital_call(
            amount=100000,
            date=date(2023, 1, 1),
            description="Initial capital call",
            session=session
        )
        # Instance methods can use @with_session decorator for convenience
        print("Added capital call successfully")
        
        # Test the natural relationship - count funds in company
        print(f"Company '{company.name}' now has {len(company.funds)} fund(s)")
        
        # Commit the entire workflow
        session.commit()
        print("✅ New module structure test passed!")
        print(f"Successfully created: {company.name}, {entity.name}, {fund.name}")
        print("All operations used direct object methods with outermost layer session management.")
        print("Consistent pattern: company.create_fund() and fund.add_capital_call()")
        
    except Exception as e:
        print(f"❌ New module structure test failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    test_new_structure() 