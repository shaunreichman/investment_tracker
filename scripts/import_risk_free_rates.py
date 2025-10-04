#!/usr/bin/env python3

import sys
import os
import csv
from datetime import datetime
# Ensure project root on path for `src` imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database import create_database_engine, create_session_factory
from src.rates.services.risk_free_rate_service import RiskFreeRateService
from src.shared.enums.shared_enums import Currency
from src.rates.enums.risk_free_rate_enums import RiskFreeRateType

def import_risk_free_rates(csv_file='scripts/rfr.csv'):
    """Import risk-free rates from CSV file into database."""
    
    # Create database connection using centralized PostgreSQL configuration
    engine = create_database_engine()
    Session = create_session_factory(engine)
    session = Session()
    
    # Initialize the service
    risk_free_rate_service = RiskFreeRateService()
    
    print(f"Importing risk-free rates from {csv_file}...")
    
    # Clear existing sample data (optional - comment out if you want to keep it)
    print("Clearing existing sample data...")
    # Note: We'll need to implement a method to clear by source in the service
    # For now, we'll skip this step and let the script handle duplicates
    
    imported_count = 0
    skipped_count = 0
    updated_count = 0
    
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
                    currency_str = row['currency'].strip()
                    rate_date_str = row['rate_date'].strip()
                    rate = float(row['rate'].strip())
                    rate_type_str = row.get('rate_type', 'cash_rate').strip()
                    source = row.get('source', '').strip()
                    
                    # Convert currency string to enum
                    try:
                        currency = Currency.from_string(currency_str)
                    except ValueError:
                        print(f"Invalid currency '{currency_str}' in row {row_num}")
                        skipped_count += 1
                        continue
                    
                    # Parse date
                    try:
                        rate_date = datetime.strptime(rate_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        print(f"Invalid date format '{rate_date_str}' in row {row_num}")
                        skipped_count += 1
                        continue
                    
                    # Map rate_type from CSV to enum
                    # CSV uses 'cash_rate' but enum expects 'GOVERNMENT_BOND', 'LIBOR', or 'SOFR'
                    # We'll map 'cash_rate' to 'GOVERNMENT_BOND' as it's the closest equivalent
                    rate_type_mapping = {
                        'cash_rate': RiskFreeRateType.GOVERNMENT_BOND,
                        'government_bond': RiskFreeRateType.GOVERNMENT_BOND,
                        'libor': RiskFreeRateType.LIBOR,
                        'sofr': RiskFreeRateType.SOFR
                    }
                    
                    rate_type = rate_type_mapping.get(rate_type_str.lower(), RiskFreeRateType.GOVERNMENT_BOND)
                    
                    # Check if this rate already exists by querying through the service
                    existing_rates = risk_free_rate_service.get_risk_free_rates(
                        session=session,
                        currency=currency,
                        rate_type=rate_type
                    )
                    
                    # Filter by date to find exact match
                    existing = None
                    for existing_rate in existing_rates:
                        if existing_rate.date == rate_date:
                            existing = existing_rate
                            break
                    
                    if existing:
                        # Update existing record
                        existing.rate = rate
                        existing.source = source
                        print(f"Updated {currency_str} rate: {rate_date} - {rate}%")
                        updated_count += 1
                    else:
                        # Create new record using the service
                        risk_free_rate_data = {
                            'currency': currency,
                            'date': rate_date,  # Note: field name changed from 'rate_date' to 'date'
                            'rate': rate,
                            'rate_type': rate_type,
                            'source': source
                        }
                        
                        risk_free_rate = risk_free_rate_service.create_risk_free_rate(
                            risk_free_rate_data, session
                        )
                        print(f"Added {currency_str} rate: {rate_date} - {rate}%")
                        imported_count += 1
                    
                except (ValueError, KeyError) as e:
                    print(f"Error processing row {row_num}: {row} - {e}")
                    skipped_count += 1
                    continue
        
        session.commit()
        print(f"\nImport completed!")
        print(f"Successfully imported: {imported_count} rates")
        print(f"Updated: {updated_count} rates")
        print(f"Skipped: {skipped_count} rows")
        
        # Show summary by currency using the service
        print("\nSummary by currency:")
        for currency_str in ['AUD', 'USD', 'EUR']:
            try:
                currency = Currency.from_string(currency_str)
                rates = risk_free_rate_service.get_risk_free_rates(
                    session=session,
                    currency=currency
                )
                count = len(rates)
                if count > 0:
                    # Sort by date to get min/max
                    sorted_rates = sorted(rates, key=lambda x: x.date)
                    min_date = sorted_rates[0].date
                    max_date = sorted_rates[-1].date
                    print(f"  {currency_str}: {count} rates from {min_date} to {max_date}")
            except ValueError:
                print(f"  {currency_str}: Invalid currency")
        
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