#!/usr/bin/env python3
"""
Database migration script to add after-tax IRR fields to TaxStatement table.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def migrate_database():
    """Add after-tax IRR fields to TaxStatement table."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    
    print("MIGRATING DATABASE - Adding After-Tax IRR Fields")
    print("=" * 60)
    
    try:
        # Check if columns already exist
        with engine.connect() as conn:
            # Get table info
            result = conn.execute(text("PRAGMA table_info(tax_statements)"))
            columns = [row[1] for row in result.fetchall()]
            
            print(f"Existing columns: {columns}")
            
            # Add new columns if they don't exist
            new_columns = [
                ('tax_already_paid', 'REAL DEFAULT 0.0'),
                ('tax_payable', 'REAL DEFAULT 0.0'),
                ('tax_payable_rate', 'REAL DEFAULT 0.0'),
                ('tax_payment_date', 'DATE')
            ]
            
            for column_name, column_def in new_columns:
                if column_name not in columns:
                    print(f"Adding column: {column_name}")
                    conn.execute(text(f"ALTER TABLE tax_statements ADD COLUMN {column_name} {column_def}"))
                    conn.commit()
                else:
                    print(f"Column {column_name} already exists")
        
        print("\nMigration completed successfully!")
        
        # Show final table structure
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(tax_statements)"))
            columns = [(row[1], row[2]) for row in result.fetchall()]
            
            print("\nFinal table structure:")
            print("-" * 40)
            for col_name, col_type in columns:
                print(f"{col_name}: {col_type}")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_database() 