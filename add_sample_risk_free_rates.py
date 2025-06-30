#!/usr/bin/env python3
"""
Script to add sample risk-free rate data for testing real IRR calculations.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import RiskFreeRate

def add_sample_risk_free_rates():
    """Add sample risk-free rate data for AUD."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Sample risk-free rates (AUD government bond rates)
    # These are approximate rates for the period
    sample_rates = [
        # 2022 rates
        (date(2022, 11, 1), 3.5),   # November 2022
        (date(2022, 12, 1), 3.6),   # December 2022
        
        # 2023 rates
        (date(2023, 1, 1), 3.7),    # January 2023
        (date(2023, 2, 1), 3.8),    # February 2023
        (date(2023, 3, 1), 3.9),    # March 2023
        (date(2023, 4, 1), 4.0),    # April 2023
        (date(2023, 5, 1), 4.1),    # May 2023
        (date(2023, 6, 1), 4.2),    # June 2023
        (date(2023, 7, 1), 4.3),    # July 2023
        (date(2023, 8, 1), 4.4),    # August 2023
        (date(2023, 9, 1), 4.5),    # September 2023
        (date(2023, 10, 1), 4.6),   # October 2023
        (date(2023, 11, 1), 4.7),   # November 2023
        (date(2023, 12, 1), 4.8),   # December 2023
        
        # 2024 rates
        (date(2024, 1, 1), 4.9),    # January 2024
        (date(2024, 2, 1), 5.0),    # February 2024
        (date(2024, 3, 1), 5.1),    # March 2024
        (date(2024, 4, 1), 5.2),    # April 2024
        (date(2024, 5, 1), 5.3),    # May 2024
        (date(2024, 6, 1), 5.4),    # June 2024
        (date(2024, 7, 1), 5.5),    # July 2024
        (date(2024, 8, 1), 5.6),    # August 2024
    ]
    
    # Check if rates already exist
    existing_count = session.query(RiskFreeRate).filter(
        RiskFreeRate.currency == 'AUD'
    ).count()
    
    if existing_count > 0:
        print(f"Found {existing_count} existing AUD risk-free rates. Skipping.")
        session.close()
        return
    
    # Add the sample rates
    created_count = 0
    for rate_date, rate_value in sample_rates:
        risk_free_rate = RiskFreeRate(
            currency='AUD',
            rate_date=rate_date,
            rate=rate_value,
            rate_type='government_bond',
            source='Sample data for testing'
        )
        session.add(risk_free_rate)
        created_count += 1
    
    session.commit()
    print(f"Created {created_count} sample AUD risk-free rates")
    
    session.close()

if __name__ == "__main__":
    add_sample_risk_free_rates() 