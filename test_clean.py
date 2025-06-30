#!/usr/bin/env python3
"""
Clean test script that resets the database before each test run.
This ensures consistent results without data duplication.
"""

import sys
import os
from datetime import datetime, date

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    Base, InvestmentCompany, Entity, Fund, FundEvent, 
    TaxStatement, EventType, DistributionType, FundType
)


def reset_database():
    """Reset the database by dropping and recreating all tables."""
    engine = create_engine('sqlite:///data/investment_tracker.db')
    
    # Drop all tables
    Base.metadata.drop_all(engine)
    print("Dropped all existing tables")
    
    # Recreate all tables
    Base.metadata.create_all(engine)
    print("Recreated all tables")
    
    return engine


def run_clean_test():
    """Run a clean test with fresh database."""
    
    print("CLEAN INVESTMENT TRACKER TEST")
    print("=" * 50)
    print("Resetting database...")
    
    # Reset database
    engine = reset_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create entities
        shaun = Entity(
            name="Shaun Reichman",
            description="Individual investor",
            tax_jurisdiction="AU"
        )
        session.add(shaun)
        
        # Create investment company
        alceon = InvestmentCompany(
            name="Alceon",
            description="Australian private debt investment manager",
            website="https://www.alceon.com.au",
            contact_email="investor.relations@alceon.com.au"
        )
        session.add(alceon)
        session.commit()
        
        # Create funds
        senior_debt_fund = Fund(
            investment_company_id=alceon.id,
            entity_id=shaun.id,
            name='Senior Debt Fund No.24',
            fund_type='Private Debt',
            vintage_year=2023,
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0,
            currency='AUD',
            description='Senior debt fund with quarterly distributions'
        )
        session.add(senior_debt_fund)
        
        three_pg_fund = Fund(
            investment_company_id=alceon.id,
            entity_id=shaun.id,
            name='3PG Finance',
            fund_type='Private Debt',
            vintage_year=2022,
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0,
            currency='AUD',
            description='3PG Finance debt fund'
        )
        session.add(three_pg_fund)
        session.commit()
        
        print("Created entities, companies, and funds")
        
        # Add events for Senior Debt Fund
        senior_debt_events = [
            (date(2023, 6, 23), EventType.CAPITAL_CALL, 100000.0, "Initial capital call"),
            (date(2023, 10, 20), EventType.DISTRIBUTION, 3031.0, "Interest distribution", DistributionType.INTEREST),
            (date(2023, 12, 8), EventType.RETURN_OF_CAPITAL, 7000.0, "Return of capital"),
            (date(2024, 1, 16), EventType.DISTRIBUTION, 2837.0, "Interest distribution", DistributionType.INTEREST),
            (date(2024, 3, 26), EventType.RETURN_OF_CAPITAL, 45000.0, "Partial exit distribution"),
            (date(2024, 7, 9), EventType.DISTRIBUTION, 1392.0, "Interest distribution", DistributionType.INTEREST),
            (date(2024, 8, 2), EventType.DISTRIBUTION, 510.0, "Interest distribution", DistributionType.INTEREST),
            (date(2024, 8, 2), EventType.RETURN_OF_CAPITAL, 48000.0, "Final return of capital"),
        ]
        
        for event_data in senior_debt_events:
            if len(event_data) == 5:  # Distribution event
                event_date, event_type, amount, description, distribution_type = event_data
                event = FundEvent(
                    fund_id=senior_debt_fund.id,
                    event_type=event_type,
                    event_date=event_date,
                    amount=amount,
                    description=description,
                    distribution_type=distribution_type,
                    tax_withheld=0.0,
                    tax_withholding_rate=0.0
                )
            else:  # Capital event
                event_date, event_type, amount, description = event_data
                event = FundEvent(
                    fund_id=senior_debt_fund.id,
                    event_type=event_type,
                    event_date=event_date,
                    amount=amount,
                    description=description
                )
            session.add(event)
        
        session.commit()
        print("Added Senior Debt Fund events")
        
        # Update fund calculations
        senior_debt_fund.update_current_equity_balance(session)
        senior_debt_fund.update_average_equity_balance(session)
        senior_debt_fund.update_active_status(session)
        
        # Analysis
        print(f"\nSenior Debt Fund Analysis:")
        print(f"Current Equity: ${senior_debt_fund.current_equity_balance:,.0f}")
        print(f"Average Equity: ${senior_debt_fund.average_equity_balance:,.0f}")
        print(f"IRR: {senior_debt_fund.get_irr_percentage(session)}")
        
        print("\n" + "=" * 50)
        print("CLEAN TEST COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error during test: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_clean_test()
