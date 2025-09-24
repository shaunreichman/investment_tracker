#!/usr/bin/env python3
"""
Database initialization script for the investment tracker.

This script creates the PostgreSQL database and all necessary tables.
Run this script from the project root directory.
"""

import sys
import os

# Ensure project root is on the Python path so `src` package can be imported
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from src.investment_company.models import InvestmentCompany
from src.rates.models import RiskFreeRate
from src.entity.models import Entity
from src.fund.models import Fund, FundEvent, FundTrackingType, EventType, DomainEvent
from src.tax.models import TaxStatement
from src.shared.base import Base
from src.fund.models import DistributionType
from datetime import date, timedelta


def init_database():
    """Initialize the database with all tables."""
    
    # Create database engine using centralized PostgreSQL configuration
    from src.database import create_database_engine
    engine = create_database_engine()
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("Database initialized successfully!")
    print(f"Database URL: {engine.url}")
    print("Created tables:")
    print("- investment_companies")
    print("- entities") 
    print("- funds")
    print("- fund_events")
    print("- risk_free_rates")
    print("- tax_statements")


def main():
    """Initialize the database and optionally add sample data."""
    print("Initializing investment tracker database...")
    
    try:
        # Initialize the database
        init_database()
        
        print("\nDatabase tables created:")
        print("- investment_companies")
        print("- entities")
        print("- funds")
        print("- fund_events")
        print("- risk_free_rates")
        print("- tax_statements")
        
        print("\nDatabase is ready to use!")
        print("You can now start adding investment companies, funds, and fund events.")
        
        # Optionally add some sample data
        add_sample_data = input("\nWould you like to add some sample data? (y/n): ").lower().strip()
        
        if add_sample_data in ['y', 'yes']:
            add_sample_data_to_database()
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


def add_sample_data_to_database():
    """Add sample data to the database using domain methods."""
    print("Adding sample data to database...")
    
    # Get database session
    from src.database import get_database_session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Create sample entities using domain methods
        entity1 = Entity.create(
            name="Shaun Reichman", 
            description="Individual investor",
            session=session
        )
        entity2 = Entity.create(
            name="ShaRei Investments", 
            description="Family investment company",
            session=session
        )
        
        # Create sample investment companies using domain methods
        company1 = InvestmentCompany.create(
            name="Blackstone Group",
            description="Global alternative asset manager",
            website="https://www.blackstone.com",
            contact_email="investor.relations@blackstone.com",
            session=session
        )
        company2 = InvestmentCompany.create(
            name="KKR & Co.",
            description="Global investment firm",
            website="https://www.kkr.com",
            contact_email="investor.relations@kkr.com",
            session=session
        )
        company3 = InvestmentCompany.create(
            name="Apollo Global Management",
            description="Alternative investment manager",
            website="https://www.apollo.com",
            contact_email="investor.relations@apollo.com",
            session=session
        )
        
        # Create sample funds using domain methods
        fund1 = company1.create_fund(
            entity=entity1,
            name="Blackstone Real Estate Partners X",
            fund_type="Real Estate",
            tracking_type=FundTrackingType.NAV_BASED,
            expected_irr=15.5,
            expected_duration_months=120,
            currency="USD",
            description="Real estate private equity fund with NAV tracking",
            session=session
        )
        
        fund2 = company1.create_fund(
            entity=entity2,
            name="Blackstone Private Equity Fund VIII",
            fund_type="Private Equity",
            tracking_type=FundTrackingType.COST_BASED,
            expected_irr=18.0,
            expected_duration_months=96,
            currency="USD",
            description="Private equity buyout fund held at cost",
            session=session
        )
        
        fund3 = company2.create_fund(
            entity=entity1,
            name="KKR Americas XII Fund",
            fund_type="Private Equity",
            tracking_type=FundTrackingType.NAV_BASED,
            expected_irr=16.5,
            expected_duration_months=108,
            currency="USD",
            description="North American private equity fund with NAV tracking",
            session=session
        )
        
        fund4 = company3.create_fund(
            entity=entity2,
            name="Apollo Investment Fund IX",
            fund_type="Private Equity",
            tracking_type=FundTrackingType.COST_BASED,
            expected_irr=17.0,
            expected_duration_months=84,
            currency="USD",
            description="Global private equity fund held at cost (exited)",
            session=session
        )
        
        # Add sample fund events using domain methods
        # Note: Calculated fields will be set by the domain methods
        # We'll add some sample events to demonstrate the system
        
        # Add capital call to fund1 (NAV-based)
        fund1.create_capital_call(
            amount=1000000.0,
            date=date(2023, 1, 15),
            description="Initial capital call",
            session=session
        )
        
        # Add NAV update to fund1
        fund1.create_nav_update(
            nav_per_share=0.86,
            date=date(2023, 6, 30),
            description="Q2 NAV update",
            session=session
        )
        
        # Add capital call to fund2 (cost-based)
        fund2.create_capital_call(
            amount=2000000.0,
            date=date(2023, 2, 1),
            description="Initial capital call",
            session=session
        )
        
        # Add distribution to fund2
        fund2.create_distribution(
            amount=200000.0,
            event_date=date(2023, 12, 31),
            distribution_type=DistributionType.INTEREST,
            description="Annual interest distribution",
            session=session
        )
        
        # Add capital call to fund3 (NAV-based)
        fund3.create_capital_call(
            amount=1500000.0,
            date=date(2023, 3, 1),
            description="Initial capital call",
            session=session
        )
        
        # Add NAV update to fund3
        fund3.create_nav_update(
            nav_per_share=4.32,
            date=date(2023, 9, 30),
            description="Q3 NAV update",
            session=session
        )
        
        # Add capital call to fund4 (cost-based, exited fund)
        fund4.create_capital_call(
            amount=3000000.0,
            date=date(2022, 1, 1),
            description="Initial capital call",
            session=session
        )
        
        # Add return of capital to fund4 (exited)
        fund4.create_return_of_capital(
            amount=3000000.0,
            date=date(2023, 12, 31),
            description="Fund exit - return of all capital",
            session=session
        )
        
        session.commit()
        print("Sample data added successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error adding sample data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main() 