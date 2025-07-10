#!/usr/bin/env python3
"""
Test script to verify the new franked and unfranked dividend distribution types.
"""

import sys
import os
from datetime import date
from sqlalchemy.orm import sessionmaker

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import using absolute paths from src
from src.database import get_database_session
from src.fund.models import Fund, FundEvent, DistributionType, EventType
from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany
from test_utils import clear_database_except_rates


def test_distribution_types():
    """Test the new franked and unfranked dividend distribution types."""
    print("Testing new distribution types...")
    
    # Set up database
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Clear database
        clear_database_except_rates(session)
        
        # Create test entities
        company = InvestmentCompany.create("Test Company", session=session)
        entity = Entity.create("Test Entity", "individual", session=session)
        
        # Create a test fund
        fund = Fund.create(
            investment_company_id=company.id,
            entity_id=entity.id,
            name="Test Dividend Fund",
            fund_type="Equity",
            tracking_type="nav_based",
            session=session
        )
        
        # Test 1: Franked dividend
        print("\n1. Testing franked dividend...")
        fund.add_distribution(
            amount=1000.0,
            date=date(2024, 6, 30),
            distribution_type=DistributionType.DIVIDEND_FRANKED,
            description="Fully franked dividend",
            session=session
        )
        
        # Test 2: Unfranked dividend
        print("2. Testing unfranked dividend...")
        fund.add_distribution(
            amount=500.0,
            date=date(2024, 6, 30),
            distribution_type=DistributionType.DIVIDEND_UNFRANKED,
            description="Unfranked dividend",
            session=session
        )
        
        # Test 3: Generic dividend (legacy)
        print("3. Testing generic dividend...")
        fund.add_distribution(
            amount=750.0,
            date=date(2024, 6, 30),
            distribution_type=DistributionType.DIVIDEND,
            description="Generic dividend",
            session=session
        )
        
        # Test 4: Auto-inference from description
        print("4. Testing auto-inference from description...")
        fund.add_distribution(
            amount=300.0,
            date=date(2024, 6, 30),
            description="Fully franked dividend payment",
            session=session
        )
        
        fund.add_distribution(
            amount=200.0,
            date=date(2024, 6, 30),
            description="Unfranked dividend distribution",
            session=session
        )
        
        # Query and display results
        print("\n=== DISTRIBUTION TYPE TEST RESULTS ===")
        
        distributions = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.DISTRIBUTION
        ).order_by(FundEvent.id).all()
        
        for i, dist in enumerate(distributions, 1):
            print(f"{i}. {dist.description}")
            print(f"   Amount: ${dist.amount:,.2f}")
            print(f"   Type: {dist.distribution_type.value}")
            print(f"   Date: {dist.event_date}")
            print()
        
        # Test distribution type grouping
        print("=== DISTRIBUTION TYPE SUMMARY ===")
        type_counts = {}
        type_totals = {}
        
        for dist in distributions:
            dist_type = dist.distribution_type.value
            type_counts[dist_type] = type_counts.get(dist_type, 0) + 1
            type_totals[dist_type] = type_totals.get(dist_type, 0) + dist.amount
        
        for dist_type, count in type_counts.items():
            total = type_totals[dist_type]
            print(f"{dist_type}: {count} distributions, total ${total:,.2f}")
        
        print("\n✅ Distribution type tests completed successfully!")
        
    finally:
        session.close()


if __name__ == "__main__":
    test_distribution_types() 