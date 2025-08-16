#!/usr/bin/env python3
"""
Debug script to understand why Enum columns are not being recognized properly.
"""

import sys
import os

# Ensure project root is on the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.fund.models import Fund, FundType, FundStatus
from src.shared.base import Base
from sqlalchemy import create_engine, text

def debug_enum_columns():
    """Debug the enum column definitions."""
    print("=== Debugging Enum Columns ===")
    
    # Check the model definition
    print(f"✅ Fund model imported: {Fund}")
    print(f"✅ FundType enum: {FundType}")
    print(f"✅ FundStatus enum: {FundStatus}")
    
    # Check the table definition
    print(f"\n✅ Table name: {Fund.__tablename__}")
    print(f"✅ Table columns count: {len(Fund.__table__.columns)}")
    
    # Check specific columns
    tracking_type_col = Fund.__table__.columns['tracking_type']
    status_col = Fund.__table__.columns['status']
    
    print(f"\n✅ tracking_type column:")
    print(f"   - Type: {tracking_type_col.type}")
    print(f"   - Type class: {type(tracking_type_col.type)}")
    print(f"   - Nullable: {tracking_type_col.nullable}")
    print(f"   - Default: {tracking_type_col.default}")
    
    print(f"\n✅ status column:")
    print(f"   - Type: {status_col.type}")
    print(f"   - Type class: {type(status_col.type)}")
    print(f"   - Nullable: {status_col.nullable}")
    print(f"   - Default: {status_col.default}")
    
    # Check if it's an Enum type
    print(f"\n✅ Is tracking_type Enum? {hasattr(tracking_type_col.type, 'enums')}")
    print(f"✅ Is status Enum? {hasattr(status_col.type, 'enums')}")
    
    # Try to get the enum values
    if hasattr(tracking_type_col.type, 'enums'):
        print(f"✅ tracking_type enum values: {tracking_type_col.type.enums}")
    if hasattr(status_col.type, 'enums'):
        print(f"✅ status enum values: {status_col.type.enums}")

def test_table_creation():
    """Test table creation to see what SQL is generated."""
    print("\n=== Testing Table Creation ===")
    
    try:
        # Create a test engine
        engine = create_engine('sqlite:///:memory:')
        
        # Try to create the table
        print("✅ Creating table in memory database...")
        Base.metadata.create_all(bind=engine)
        print("✅ Table created successfully!")
        
        # Check what tables were created
        inspector = engine.inspect(engine)
        tables = inspector.get_table_names()
        print(f"✅ Tables created: {tables}")
        
        # Check the funds table structure
        if 'funds' in tables:
            columns = inspector.get_columns('funds')
            print(f"\n✅ Funds table columns:")
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_enum_columns()

