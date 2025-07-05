#!/usr/bin/env python3
"""
Migration script to add units_owned and cost_of_units columns to fund_events table.
This migration supports the new NAV-based fund tracking with FIFO cost basis.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate the database to add new columns for NAV-based fund tracking."""
    
    db_path = 'data/investment_tracker.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. Please run init_database.py first.")
        return False
    
    print("Starting database migration...")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(fund_events)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_applied = []
        
        # Add units_owned column if it doesn't exist
        if 'units_owned' not in columns:
            print("Adding units_owned column...")
            cursor.execute("ALTER TABLE fund_events ADD COLUMN units_owned REAL")
            migrations_applied.append("units_owned")
        
        # Add cost_of_units column if it doesn't exist
        if 'cost_of_units' not in columns:
            print("Adding cost_of_units column...")
            cursor.execute("ALTER TABLE fund_events ADD COLUMN cost_of_units REAL")
            migrations_applied.append("cost_of_units")
        
        # Commit the changes
        conn.commit()
        
        if migrations_applied:
            print(f"Migration completed successfully. Added columns: {', '.join(migrations_applied)}")
        else:
            print("No migration needed - all columns already exist.")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("Database migration completed successfully!")
    else:
        print("Database migration failed!")
        exit(1) 