#!/usr/bin/env python3
"""
Migration script to update bank_accounts table from is_active boolean to status enum.

This script:
1. Adds a new 'status' column with AccountStatus enum
2. Migrates existing data (True -> ACTIVE, False -> SUSPENDED)
3. Drops the old 'is_active' column
4. Updates any foreign key constraints if needed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, MetaData, Table, Column, Enum
from sqlalchemy.orm import sessionmaker
from src.database import create_database_engine
from src.banking.enums import AccountStatus

def migrate_bank_account_status():
    """Migrate bank_accounts table from is_active to status."""
    try:
        engine = create_database_engine()
        print(f"🔄 Starting bank account status migration...")
        print(f"   Database: {engine.url}")
        
        with engine.connect() as conn:
            # Check if migration is needed
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'bank_accounts' 
                AND table_schema = 'public'
                ORDER BY column_name
            """))
            
            columns = {row[0]: row[1] for row in result.fetchall()}
            print(f"   Current columns: {list(columns.keys())}")
            
            # Check if migration is already done
            if 'status' in columns and 'is_active' not in columns:
                print("   ✅ Migration already completed - status column exists, is_active column removed")
                return
            
            # Check if both columns exist (migration in progress)
            if 'status' in columns and 'is_active' in columns:
                print("   ⚠️  Migration partially completed - both columns exist")
                print("   💡 Dropping old is_active column...")
                
                conn.execute(text("ALTER TABLE bank_accounts DROP COLUMN is_active"))
                conn.commit()
                print("   ✅ Old is_active column removed")
                return
            
            # Check if only is_active exists (needs migration)
            if 'is_active' in columns and 'status' not in columns:
                print("   🔄 Starting migration...")
                
                # Step 1: Add new status column
                print("   📝 Adding status column...")
                conn.execute(text("""
                    ALTER TABLE bank_accounts 
                    ADD COLUMN status VARCHAR(50) DEFAULT 'ACTIVE' NOT NULL
                """))
                
                # Step 2: Migrate existing data
                print("   🔄 Migrating existing data...")
                conn.execute(text("""
                    UPDATE bank_accounts 
                    SET status = CASE 
                        WHEN is_active = true THEN 'ACTIVE'
                        WHEN is_active = false THEN 'SUSPENDED'
                        ELSE 'ACTIVE'
                    END
                """))
                
                # Step 3: Drop old column
                print("   🗑️  Dropping old is_active column...")
                conn.execute(text("ALTER TABLE bank_accounts DROP COLUMN is_active"))
                
                # Step 4: Commit changes
                conn.commit()
                print("   ✅ Migration completed successfully!")
                
                # Verify migration
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'bank_accounts' 
                    AND table_schema = 'public'
                    ORDER BY column_name
                """))
                
                new_columns = {row[0]: row[1] for row in result.fetchall()}
                print(f"   📊 New columns: {list(new_columns.keys())}")
                
                # Check data integrity
                result = conn.execute(text("SELECT COUNT(*) FROM bank_accounts WHERE status IS NULL"))
                null_count = result.scalar()
                if null_count == 0:
                    print("   ✅ Data integrity verified - no null status values")
                else:
                    print(f"   ⚠️  Warning: {null_count} accounts have null status values")
                
            else:
                print("   ❌ Unexpected column state - cannot determine migration path")
                print(f"   Columns found: {list(columns.keys())}")
                return
                
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def rollback_migration():
    """Rollback the migration if needed."""
    try:
        engine = create_database_engine()
        print(f"🔄 Rolling back bank account status migration...")
        print(f"   Database: {engine.url}")
        
        with engine.connect() as conn:
            # Check current state
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'bank_accounts' 
                AND table_schema = 'public'
                ORDER BY column_name
            """))
            
            columns = {row[0]: row[1] for row in result.fetchall()}
            
            if 'is_active' in columns:
                print("   ✅ Rollback not needed - is_active column still exists")
                return
            
            if 'status' not in columns:
                print("   ❌ Cannot rollback - status column does not exist")
                return
            
            print("   🔄 Rolling back...")
            
            # Step 1: Add back is_active column
            conn.execute(text("""
                ALTER TABLE bank_accounts 
                ADD COLUMN is_active BOOLEAN DEFAULT true NOT NULL
            """))
            
            # Step 2: Migrate data back
            conn.execute(text("""
                UPDATE bank_accounts 
                SET is_active = CASE 
                    WHEN status = 'ACTIVE' THEN true
                    ELSE false
                END
            """))
            
            # Step 3: Drop status column
            conn.execute(text("ALTER TABLE bank_accounts DROP COLUMN status"))
            
            # Step 4: Commit rollback
            conn.commit()
            print("   ✅ Rollback completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during rollback: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate bank_accounts table from is_active to status")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback_migration()
    else:
        success = migrate_bank_account_status()
    
    if success:
        print("\n🎉 Operation completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Operation failed!")
        sys.exit(1)
