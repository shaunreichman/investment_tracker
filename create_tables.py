#!/usr/bin/env python3
"""
Simple script to create database tables.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.shared.base import Base
from src.database import create_database_engine
from sqlalchemy import text

def create_tables():
    """Create all database tables."""
    try:
        print("🔧 Creating database tables...")
        
        # Create engine
        engine = create_database_engine()
        print(f"✅ Engine created: {engine.url}")
        
        # Show what tables should be created
        print(f"📋 Tables to create: {list(Base.metadata.tables.keys())}")
        
        # Create all tables
        Base.metadata.create_all(engine)
        print("✅ Tables created successfully!")
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"📊 Actual tables in database: {tables}")
            
            # Check specifically for domain_events
            if 'domain_events' in tables:
                print("✅ domain_events table created successfully!")
            else:
                print("❌ domain_events table NOT created!")
                
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_tables()
