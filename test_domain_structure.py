#!/usr/bin/env python3
"""
Test script to verify the new domain structure works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_domain_imports():
    """Test that all domain modules can be imported correctly."""
    print("Testing domain imports...")
    
    try:
        # Test shared domain
        from src.shared.base import Base
        from src.shared.calculations import calculate_irr, get_equity_change_for_event
        from src.shared.utils import with_session
        print("✅ Shared domain imports successful")
        
        # Test fund domain
        from src.fund.models import Fund, FundEvent, EventType, FundType, DistributionType
        from src.fund.calculations import calculate_average_equity_balance_nav
        from src.fund.creation import FundCreationMixin, FundUpdateMixin
        from src.fund.queries import FundQueryMixin
        print("✅ Fund domain imports successful")
        
        # Test fund domain init
        from src.fund import Fund, FundEvent, EventType, FundType, DistributionType
        print("✅ Fund domain __init__ imports successful")
        
        # Test entity domain
        from src.entity.models import Entity, InvestmentCompany, RiskFreeRate, EntityType
        from src.entity import Entity, InvestmentCompany, RiskFreeRate
        print("✅ Entity domain imports successful")
        
        # Test tax domain
        from src.tax.models import TaxStatement
        from src.tax import TaxStatement
        print("✅ Tax domain imports successful")
        
        print("\n🎉 All domain imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_domain_imports()
    sys.exit(0 if success else 1) 