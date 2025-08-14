#!/usr/bin/env python3
"""
Script to manually create the domain_events table.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import create_database_engine
from sqlalchemy import text

def create_domain_events_table():
    """Manually create the domain_events table."""
    try:
        print("🔧 Creating domain_events table manually...")
        
        # Create engine
        engine = create_database_engine()
        print(f"✅ Engine created: {engine.url}")
        
        # Create the domain_events table manually
        create_sql = """
        CREATE TABLE IF NOT EXISTS domain_events (
            id SERIAL PRIMARY KEY,
            event_id VARCHAR(36) UNIQUE NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            fund_id INTEGER NOT NULL,
            event_date DATE NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            event_metadata JSON,
            CONSTRAINT fk_domain_events_fund_id FOREIGN KEY (fund_id) REFERENCES funds(id)
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_domain_events_event_id ON domain_events(event_id);
        CREATE INDEX IF NOT EXISTS idx_domain_events_event_type ON domain_events(event_type);
        CREATE INDEX IF NOT EXISTS idx_domain_events_fund_id ON domain_events(fund_id);
        CREATE INDEX IF NOT EXISTS idx_domain_events_event_date ON domain_events(event_date);
        CREATE INDEX IF NOT EXISTS idx_domain_events_timestamp ON domain_events(timestamp);
        """
        
        with engine.connect() as conn:
            # Execute the CREATE TABLE
            conn.execute(text(create_sql))
            conn.commit()
            print("✅ domain_events table created successfully!")
            
            # Verify the table exists
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'domain_events'"))
            if result.fetchone():
                print("✅ Table verification successful!")
            else:
                print("❌ Table verification failed!")
                
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_domain_events_table()
