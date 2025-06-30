#!/usr/bin/env python3
"""
Clean up database and import real Central Bank cash rates from rfr.csv.
"""

import sys
import os
import csv
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import RiskFreeRate, FundEvent, EventType

def cleanup_and_import_real_rates():
    """Remove sample rates and import real Central Bank cash rates."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("CLEANING UP DATABASE AND IMPORTING REAL RATES")
    print("=" * 60)
    
    # Step 1: Remove all sample risk-free rates
    sample_rates_count = session.query(RiskFreeRate).filter(
        RiskFreeRate.source == 'Sample data for testing'
    ).count()
    
    if sample_rates_count > 0:
        session.query(RiskFreeRate).filter(
            RiskFreeRate.source == 'Sample data for testing'
        ).delete()
        print(f"Removed {sample_rates_count} sample risk-free rates")
    
    # Step 2: Remove all daily interest charge events (they were based on sample rates)
    interest_events_count = session.query(FundEvent).filter(
        FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
    ).count()
    
    if interest_events_count > 0:
        session.query(FundEvent).filter(
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        ).delete()
        print(f"Removed {interest_events_count} daily interest charge events")
    
    # Step 3: Import real rates from rfr.csv
    print("\nImporting real Central Bank cash rates from rfr.csv...")
    
    imported_count = 0
    with open('rfr.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        # Skip header row
        next(reader)
        
        for row in reader:
            # Skip empty rows or rows without enough data
            if len(row) < 4 or not row[0] or not row[1] or not row[2]:
                continue
            
            try:
                # Parse the data (currency, rate_date, rate, rate_type, source)
                currency = row[0]
                rate_date = datetime.strptime(row[1], '%Y-%m-%d').date()
                rate_value = float(row[2])
                rate_type = row[3] if len(row) > 3 and row[3] else 'cash_rate'
                source = row[4] if len(row) > 4 and row[4] else 'Central Bank'
                
                # Check if this rate already exists
                existing_rate = session.query(RiskFreeRate).filter(
                    RiskFreeRate.currency == currency,
                    RiskFreeRate.rate_date == rate_date
                ).first()
                
                if not existing_rate:
                    # Create new risk-free rate
                    risk_free_rate = RiskFreeRate(
                        currency=currency,
                        rate_date=rate_date,
                        rate=rate_value,
                        rate_type=rate_type,
                        source=source
                    )
                    session.add(risk_free_rate)
                    imported_count += 1
                else:
                    # Update existing rate
                    existing_rate.rate = rate_value
                    existing_rate.rate_type = rate_type
                    existing_rate.source = source
                    print(f"Updated existing rate for {currency} on {rate_date}")
                    
            except (ValueError, IndexError) as e:
                print(f"Error processing row: {row} - {e}")
                continue
    
    session.commit()
    print(f"Imported/updated {imported_count} real Central Bank cash rates")
    
    # Step 4: Show summary of rates in database
    print("\nSummary of rates in database:")
    currencies = session.query(RiskFreeRate.currency).distinct().all()
    for currency in currencies:
        currency_code = currency[0]
        count = session.query(RiskFreeRate).filter(
            RiskFreeRate.currency == currency_code
        ).count()
        print(f"  {currency_code}: {count} rates")
    
    # Show sample of AUD rates
    print("\nSample AUD rates:")
    aud_rates = session.query(RiskFreeRate).filter(
        RiskFreeRate.currency == 'AUD'
    ).order_by(RiskFreeRate.rate_date).limit(10).all()
    
    for rate in aud_rates:
        print(f"  {rate.rate_date}: {rate.rate}% ({rate.source})")
    
    session.close()
    print("\nDatabase cleanup and import completed!")

if __name__ == "__main__":
    cleanup_and_import_real_rates() 