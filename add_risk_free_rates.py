#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import RiskFreeRate

def add_sample_risk_free_rates():
    """Add sample risk-free rate data for testing."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Sample AUD risk-free rates (approximate historical data)
    aud_rates = [
        # 2023 rates (approximate)
        ('2023-01-01', 3.5),
        ('2023-02-01', 3.6),
        ('2023-03-01', 3.7),
        ('2023-04-01', 3.8),
        ('2023-05-01', 3.9),
        ('2023-06-01', 4.0),
        ('2023-07-01', 4.1),
        ('2023-08-01', 4.2),
        ('2023-09-01', 4.3),
        ('2023-10-01', 4.4),
        ('2023-11-01', 4.5),
        ('2023-12-01', 4.6),
        
        # 2024 rates (approximate)
        ('2024-01-01', 4.7),
        ('2024-02-01', 4.8),
        ('2024-03-01', 4.9),
        ('2024-04-01', 5.0),
        ('2024-05-01', 5.1),
        ('2024-06-01', 5.2),
        ('2024-07-01', 5.3),
        ('2024-08-01', 5.4),
    ]
    
    # Sample USD risk-free rates (approximate historical data)
    usd_rates = [
        # 2023 rates (approximate)
        ('2023-01-01', 4.0),
        ('2023-02-01', 4.1),
        ('2023-03-01', 4.2),
        ('2023-04-01', 4.3),
        ('2023-05-01', 4.4),
        ('2023-06-01', 4.5),
        ('2023-07-01', 4.6),
        ('2023-08-01', 4.7),
        ('2023-09-01', 4.8),
        ('2023-10-01', 4.9),
        ('2023-11-01', 5.0),
        ('2023-12-01', 5.1),
        
        # 2024 rates (approximate)
        ('2024-01-01', 5.2),
        ('2024-02-01', 5.3),
        ('2024-03-01', 5.4),
        ('2024-04-01', 5.5),
        ('2024-05-01', 5.6),
        ('2024-06-01', 5.7),
        ('2024-07-01', 5.8),
        ('2024-08-01', 5.9),
    ]
    
    print("Adding sample risk-free rates...")
    
    # Add AUD rates
    for rate_date_str, rate in aud_rates:
        rate_date = date.fromisoformat(rate_date_str)
        
        # Check if rate already exists
        existing = session.query(RiskFreeRate).filter(
            RiskFreeRate.currency == 'AUD',
            RiskFreeRate.rate_date == rate_date
        ).first()
        
        if not existing:
            risk_free_rate = RiskFreeRate(
                currency='AUD',
                rate_date=rate_date,
                rate=rate,
                rate_type='government_bond',
                source='Sample data'
            )
            session.add(risk_free_rate)
            print(f"Added AUD rate: {rate_date} - {rate}%")
    
    # Add USD rates
    for rate_date_str, rate in usd_rates:
        rate_date = date.fromisoformat(rate_date_str)
        
        # Check if rate already exists
        existing = session.query(RiskFreeRate).filter(
            RiskFreeRate.currency == 'USD',
            RiskFreeRate.rate_date == rate_date
        ).first()
        
        if not existing:
            risk_free_rate = RiskFreeRate(
                currency='USD',
                rate_date=rate_date,
                rate=rate,
                rate_type='government_bond',
                source='Sample data'
            )
            session.add(risk_free_rate)
            print(f"Added USD rate: {rate_date} - {rate}%")
    
    session.commit()
    session.close()
    
    print("Sample risk-free rates added successfully!")

if __name__ == "__main__":
    add_sample_risk_free_rates() 