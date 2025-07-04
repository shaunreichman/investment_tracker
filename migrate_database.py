#!/usr/bin/env python3
"""
Database migration script to make commitment_amount nullable for NAV-based funds.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def migrate_database():
    """Make commitment_amount nullable for NAV-based funds."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    
    print("MIGRATING DATABASE - Making commitment_amount nullable for NAV-based funds")
    print("=" * 70)
    
    try:
        with engine.connect() as conn:
            # Check current table structure
            result = conn.execute(text("PRAGMA table_info(funds)"))
            columns = [(row[1], row[2], row[3], row[4], row[5]) for row in result.fetchall()]
            
            print("Current funds table structure:")
            for col_name, col_type, not_null, default_val, pk in columns:
                print(f"  {col_name}: {col_type} {'NOT NULL' if not_null else 'NULL'} DEFAULT {default_val}")
            
            # SQLite doesn't support ALTER COLUMN to change nullability
            # We need to recreate the table with the new schema
            print("\nSQLite doesn't support ALTER COLUMN for nullability changes.")
            print("This migration requires manual intervention.")
            print("\nTo complete this migration:")
            print("1. Backup your database: cp data/investment_tracker.db data/investment_tracker.db.backup")
            print("2. Delete the database: rm data/investment_tracker.db")
            print("3. Run init_database.py to recreate with new schema")
            print("4. Restore your data from backup if needed")
            
            # Check if there are any NAV-based funds with commitment_amount
            result = conn.execute(text("""
                SELECT id, name, commitment_amount, tracking_type 
                FROM funds 
                WHERE tracking_type = 'nav_based' AND commitment_amount IS NOT NULL
            """))
            nav_funds = result.fetchall()
            
            if nav_funds:
                print(f"\nFound {len(nav_funds)} NAV-based funds with commitment_amount:")
                for fund_id, name, commitment, tracking_type in nav_funds:
                    print(f"  Fund ID {fund_id}: {name} - commitment_amount: ${commitment:,.2f}")
                print("\nThese funds will need their commitment_amount set to NULL after migration.")
            else:
                print("\nNo NAV-based funds with commitment_amount found.")
        
    except Exception as e:
        print(f"Migration check failed: {e}")
        raise

if __name__ == "__main__":
    migrate_database() 