#!/usr/bin/env python3

import sys
import os
import csv
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.rates.models import RiskFreeRate

def import_risk_free_rates(csv_file='rfr.csv'):
    """Import risk-free rates from CSV file into database."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f"Importing risk-free rates from {csv_file}...")
    
    # Clear existing sample data (optional - comment out if you want to keep it)
    print("Clearing existing sample data...")
    session.query(RiskFreeRate).filter(RiskFreeRate.source == 'Sample data').delete()
    
    imported_count = 0
    skipped_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            # Normalize fieldnames to remove BOM and strip whitespace
            fieldnames = [fn.strip().replace('\ufeff', '') for fn in reader.fieldnames]
            reader.fieldnames = fieldnames
            print(f"Normalized CSV headers: {reader.fieldnames}")
            
            for row_num, row in enumerate(reader, 1):
                # Normalize row keys
                row = {k.strip().replace('\ufeff', ''): v for k, v in row.items()}
                if row_num <= 3:
                    print(f"Row {row_num}: {row}")
                
                # Skip empty rows
                if not row.get('currency') or not row.get('rate_date') or not row.get('rate'):
                    if row_num <= 5:
                        print(f"Skipping row {row_num} - missing required fields")
                    continue
                
                try:
                    # Parse the data
                    currency = row['currency'].strip()
                    rate_date = datetime.strptime(row['rate_date'].strip(), '%Y-%m-%d').date()
                    rate = float(row['rate'].strip())
                    rate_type = row.get('rate_type', 'cash_rate').strip()
                    source = row.get('source', '').strip()
                    
                    # Check if this rate already exists
                    existing = session.query(RiskFreeRate).filter(
                        RiskFreeRate.currency == currency,
                        RiskFreeRate.rate_date == rate_date,
                        RiskFreeRate.rate_type == rate_type
                    ).first()
                    
                    if existing:
                        # Update existing record
                        existing.rate = rate
                        existing.source = source
                        print(f"Updated {currency} rate: {rate_date} - {rate}%")
                    else:
                        # Create new record
                        risk_free_rate = RiskFreeRate(
                            currency=currency,
                            rate_date=rate_date,
                            rate=rate,
                            rate_type=rate_type,
                            source=source
                        )
                        session.add(risk_free_rate)
                        print(f"Added {currency} rate: {rate_date} - {rate}%")
                    
                    imported_count += 1
                    
                except (ValueError, KeyError) as e:
                    print(f"Error processing row: {row} - {e}")
                    skipped_count += 1
                    continue
        
        session.commit()
        print(f"\nImport completed!")
        print(f"Successfully imported: {imported_count} rates")
        print(f"Skipped: {skipped_count} rows")
        
        # Show summary by currency
        print("\nSummary by currency:")
        for currency in ['AUD', 'USD', 'EUR']:
            count = session.query(RiskFreeRate).filter(RiskFreeRate.currency == currency).count()
            if count > 0:
                min_date = session.query(RiskFreeRate.rate_date).filter(
                    RiskFreeRate.currency == currency
                ).order_by(RiskFreeRate.rate_date).first()[0]
                max_date = session.query(RiskFreeRate.rate_date).filter(
                    RiskFreeRate.currency == currency
                ).order_by(RiskFreeRate.rate_date.desc()).first()[0]
                print(f"  {currency}: {count} rates from {min_date} to {max_date}")
        
    except FileNotFoundError:
        print(f"Error: File {csv_file} not found!")
        return
    except Exception as e:
        print(f"Error importing data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    import_risk_free_rates() 