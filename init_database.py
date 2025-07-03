#!/usr/bin/env python3
"""
Database initialization script for the investment tracker.

This script creates the SQLite database and all necessary tables.
Run this script from the project root directory.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from models import Base, InvestmentCompany, Entity, Fund, FundEvent, RiskFreeRate, TaxStatement


def init_database():
    """Initialize the database with all tables."""
    
    # Create database engine
    engine = create_engine('sqlite:///data/investment_tracker.db')
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("Database initialized successfully!")
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
    """Add sample data to the database for testing."""
    from database import get_database_session
    from datetime import datetime, date, timedelta
    
    print("\nAdding sample data...")
    
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Create sample entities
        entity1 = Entity(name="Shaun Reichman", description="Individual investor")
        entity2 = Entity(name="ShaRei Investments", description="Family investment company")
        session.add_all([entity1, entity2])
        session.commit()
        
        # Create sample investment companies
        company1 = InvestmentCompany(
            name="Blackstone Group",
            description="Global alternative asset manager",
            website="https://www.blackstone.com",
            contact_email="investor.relations@blackstone.com"
        )
        company2 = InvestmentCompany(
            name="KKR & Co.",
            description="Global investment firm",
            website="https://www.kkr.com",
            contact_email="investor.relations@kkr.com"
        )
        company3 = InvestmentCompany(
            name="Apollo Global Management",
            description="Alternative investment manager",
            website="https://www.apollo.com",
            contact_email="investor.relations@apollo.com"
        )
        session.add_all([company1, company2, company3])
        session.commit()
        
        # Create sample funds, alternating entities and fund types
        fund1 = Fund(
            investment_company_id=company1.id,
            entity_id=entity1.id,
            name="Blackstone Real Estate Partners X",
            fund_type="Real Estate",
            tracking_type=FundType.NAV_BASED,  # NAV-based fund
            current_equity_balance=750000.0,
            average_equity_balance=800000.0,
            current_units=869565.22,  # NAV-based tracking
            current_unit_price=0.86,
            expected_irr=15.5,
            expected_duration_months=120,
            is_active=True,
            currency="USD",
            description="Real estate private equity fund with NAV tracking"
        )
        fund2 = Fund(
            investment_company_id=company1.id,
            entity_id=entity2.id,
            name="Blackstone Private Equity Fund VIII",
            fund_type="Private Equity",
            tracking_type=FundType.COST_BASED,  # Cost-based fund
            current_equity_balance=1800000.0,
            average_equity_balance=1900000.0,
            total_cost_basis=1800000.0,  # Cost-based tracking
            expected_irr=18.0,
            expected_duration_months=96,
            is_active=True,
            currency="USD",
            description="Private equity buyout fund held at cost"
        )
        fund3 = Fund(
            investment_company_id=company2.id,
            entity_id=entity1.id,
            name="KKR Americas XII Fund",
            fund_type="Private Equity",
            tracking_type=FundType.NAV_BASED,  # NAV-based fund
            current_equity_balance=1200000.0,
            average_equity_balance=1300000.0,
            current_units=277777.78,  # NAV-based tracking
            current_unit_price=4.32,
            expected_irr=16.5,
            expected_duration_months=108,
            is_active=True,
            currency="USD",
            description="North American private equity fund with NAV tracking"
        )
        fund4 = Fund(
            investment_company_id=company3.id,
            entity_id=entity2.id,
            name="Apollo Investment Fund IX",
            fund_type="Private Equity",
            tracking_type=FundType.COST_BASED,  # Cost-based fund
            current_equity_balance=0.0,
            average_equity_balance=2900000.0,
            total_cost_basis=3000000.0,  # Cost-based tracking
            expected_irr=17.0,
            expected_duration_months=84,
            is_active=False,  # Fund has been exited
            currency="USD",
            description="Global private equity fund held at cost (exited)"
        )
        session.add_all([fund1, fund2, fund3, fund4])
        session.commit()
        
        # Create sample fund events
        today = date.today()
        
        # Fund 1 events (Blackstone Real Estate - NAV-based)
        events1 = [
            FundEvent(
                fund_id=fund1.id,
                event_type=EventType.UNIT_PURCHASE,  # NAV-based funds use unit purchases
                event_date=today - timedelta(days=90),
                amount=200000.0,
                units_purchased=232558.14,  # Units purchased
                unit_price=0.86,
                description="Initial unit purchase"
            ),
            FundEvent(
                fund_id=fund1.id,
                event_type=EventType.UNIT_PURCHASE,  # Second purchase
                event_date=today - timedelta(days=60),
                amount=150000.0,
                units_purchased=174418.60,  # Units purchased
                unit_price=0.86,
                description="Additional unit purchase"
            ),
            FundEvent(
                fund_id=fund1.id,
                event_type=EventType.UNIT_SALE,  # Partial sale using FIFO
                event_date=today - timedelta(days=45),
                amount=100000.0,
                units_sold=116279.07,  # Units sold (from first purchase)
                unit_price=0.86,
                description="Partial unit sale"
            ),
            FundEvent(
                fund_id=fund1.id,
                event_type=EventType.NAV_UPDATE,
                event_date=today - timedelta(days=60),
                nav_per_share=0.86,
                shares_owned=869565.22,
                unit_price=0.86,
                description="Q3 NAV update"
            ),
            FundEvent(
                fund_id=fund1.id,
                event_type=EventType.DIVIDEND,
                event_date=today - timedelta(days=30),
                amount=25000.0,
                distribution_type=DistributionType.DIVIDEND,
                description="Quarterly dividend distribution"
            ),
            FundEvent(
                fund_id=fund1.id,
                event_type=EventType.INCOME_DISTRIBUTION,
                event_date=today - timedelta(days=15),
                amount=15000.0,
                distribution_type=DistributionType.RENT,
                description="Rental income distribution"
            ),
            FundEvent(
                fund_id=fund1.id,
                event_type=EventType.NAV_UPDATE,
                event_date=today,
                nav_per_share=0.86,
                shares_owned=869565.22,
                unit_price=0.86,
                description="Q4 NAV update"
            )
        ]
        
        # Fund 2 events (Blackstone Private Equity - Cost-based)
        events2 = [
            FundEvent(
                fund_id=fund2.id,
                event_type=EventType.CAPITAL_CALL,  # Cost-based funds use capital calls
                event_date=today - timedelta(days=120),
                amount=400000.0,
                description="Capital call for new investment"
            ),
            FundEvent(
                fund_id=fund2.id,
                event_type=EventType.RETURN_OF_CAPITAL,
                event_date=today - timedelta(days=45),
                amount=150000.0,
                description="Partial exit from portfolio company"
            ),
            FundEvent(
                fund_id=fund2.id,
                event_type=EventType.CAPITAL_GAIN_INCOME,
                event_date=today - timedelta(days=45),
                amount=50000.0,
                description="Capital gains income from exit"
            ),
            FundEvent(
                fund_id=fund2.id,
                event_type=EventType.MANAGEMENT_FEE,
                event_date=today - timedelta(days=30),
                amount=-20000.0,
                description="Annual management fee"
            )
        ]
        
        # Fund 3 events (KKR - NAV-based)
        events3 = [
            FundEvent(
                fund_id=fund3.id,
                event_type=EventType.UNIT_PURCHASE,  # NAV-based funds use unit purchases
                event_date=today - timedelta(days=75),
                amount=300000.0,
                units_purchased=69444.44,  # Units purchased
                unit_price=4.32,
                description="Initial unit purchase"
            ),
            FundEvent(
                fund_id=fund3.id,
                event_type=EventType.UNIT_PURCHASE,  # Second purchase
                event_date=today - timedelta(days=50),
                amount=200000.0,
                units_purchased=46296.30,  # Units purchased
                unit_price=4.32,
                description="Additional unit purchase"
            ),
            FundEvent(
                fund_id=fund3.id,
                event_type=EventType.UNIT_SALE,  # Partial sale using FIFO
                event_date=today - timedelta(days=25),
                amount=150000.0,
                units_sold=34722.22,  # Units sold (from first purchase)
                unit_price=4.32,
                description="Partial unit sale"
            ),
            FundEvent(
                fund_id=fund3.id,
                event_type=EventType.INCOME_DISTRIBUTION,
                event_date=today - timedelta(days=45),
                amount=20000.0,
                distribution_type=DistributionType.INTEREST,
                description="Interest income distribution"
            ),
            FundEvent(
                fund_id=fund3.id,
                event_type=EventType.MANAGEMENT_FEE,
                event_date=today - timedelta(days=30),
                amount=-15000.0,
                description="Annual management fee"
            ),
            FundEvent(
                fund_id=fund3.id,
                event_type=EventType.NAV_UPDATE,
                event_date=today,
                nav_per_share=4.32,
                shares_owned=277777.78,
                unit_price=4.32,
                description="First NAV update"
            )
        ]
        
        # Fund 4 events (Apollo - Cost-based, exited)
        events4 = [
            FundEvent(
                fund_id=fund4.id,
                event_type=EventType.CAPITAL_GAIN_INCOME,
                event_date=today - timedelta(days=60),
                amount=200000.0,
                description="Capital gains income from exit"
            ),
            FundEvent(
                fund_id=fund4.id,
                event_type=EventType.CARRIED_INTEREST,
                event_date=today - timedelta(days=60),
                amount=-40000.0,
                description="Carried interest on distribution"
            ),
            FundEvent(
                fund_id=fund4.id,
                event_type=EventType.RETURN_OF_CAPITAL,
                event_date=today - timedelta(days=30),
                amount=2760000.0,  # Final capital return
                description="Final exit - remaining capital returned"
            )
        ]
        
        all_events = events1 + events2 + events3 + events4
        session.add_all(all_events)
        session.commit()
        
        print("Sample data added successfully!")
        print(f"- Created {session.query(InvestmentCompany).count()} investment companies")
        print(f"- Created {session.query(Fund).count()} funds")
        print(f"- Created {session.query(FundEvent).count()} fund events")
        
        # Show summary
        print("\nSample data summary:")
        for company in session.query(InvestmentCompany).all():
            print(f"\n{company.name}:")
            for fund in company.funds:
                print(f"  - {fund.name} (${fund.commitment_amount:,.0f} commitment)")
                event_count = len(fund.fund_events)
                print(f"    {event_count} events, Current NAV: ${fund.current_equity_balance:,.0f}")
        
    except Exception as e:
        print(f"Error adding sample data: {e}")
        session.rollback()
    finally:
        session.close()
        scoped_session.remove()


if __name__ == "__main__":
    main() 