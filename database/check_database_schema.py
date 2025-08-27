#!/usr/bin/env python3
"""
Database schema verification script.
Checks the database schema integrity and table structure.
"""

import sys
import os

# Ensure project root is on the Python path so `src` package can be imported
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_database_schema():
    """Check the database schema integrity."""
    try:
        from src.database import create_database_engine
        from src.config import get_database_url
        from sqlalchemy import text
        
        print("Checking database schema...")
        print(f"Database URL: {get_database_url()}")
        
        engine = create_database_engine()
        
        with engine.connect() as connection:
            # Check if tables exist (check both public and investment_tracker schemas)
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema IN ('public', 'investment_tracker')
                ORDER BY table_schema, table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if not tables:
                print("❌ No tables found in database!")
                print("Run 'python scripts/init_database.py' to create tables.")
                return False
            
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")
            
            # Check expected tables
            expected_tables = [
                'investment_companies',
                'entities', 
                'funds',
                'fund_events',
                'risk_free_rates',
                'tax_statements'
            ]
            
            missing_tables = [table for table in expected_tables if table not in tables]
            if missing_tables:
                print(f"\n⚠️  Missing expected tables: {missing_tables}")
            else:
                print("\n✅ All expected tables are present!")
            
            # Check table structure for key tables
            check_table_structure(connection, tables)
            
            # Check record counts
            check_record_counts(connection, tables)
            
            # Check foreign key integrity
            check_foreign_key_integrity(connection, tables)
            
        return True
        
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        return False

def check_table_structure(connection, tables):
    """Check the structure of key tables."""
    from sqlalchemy import text
    
    print("\n" + "=" * 50)
    print("Table Structure Check")
    print("=" * 50)
    
    key_tables = ['funds', 'fund_events', 'entities', 'investment_companies']
    
    for table in key_tables:
        if table in tables:
            print(f"\n📋 Table: {table}")
            
            # Get columns
            result = connection.execute(text(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            print(f"  Columns ({len(columns)}):")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"    - {col[0]}: {col[1]} {nullable}{default}")
            
            # Get constraints
            result = connection.execute(text(f"""
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints 
                WHERE table_name = '{table}'
                ORDER BY constraint_type, constraint_name;
            """))
            
            constraints = result.fetchall()
            if constraints:
                print(f"  Constraints ({len(constraints)}):")
                for constraint in constraints:
                    print(f"    - {constraint[0]}: {constraint[1]}")

def check_record_counts(connection, tables):
    """Check record counts in tables."""
    from sqlalchemy import text
    
    print("\n" + "=" * 50)
    print("Record Counts")
    print("=" * 50)
    
    for table in tables:
        try:
            result = connection.execute(text(f"SELECT COUNT(*) FROM {table};"))
            count = result.fetchone()[0]
            print(f"  {table}: {count} records")
        except Exception as e:
            print(f"  {table}: Error counting records - {e}")

def check_foreign_key_integrity(connection, tables):
    """Check foreign key integrity."""
    from sqlalchemy import text
    
    print("\n" + "=" * 50)
    print("Foreign Key Integrity Check")
    print("=" * 50)
    
    try:
        # Check for orphaned records
        checks = [
            ("fund_events", "fund_id", "funds", "id", "Fund events with invalid fund_id"),
            ("tax_statements", "fund_id", "funds", "id", "Tax statements with invalid fund_id"),
        ]
        
        for child_table, fk_column, parent_table, pk_column, description in checks:
            if child_table in tables and parent_table in tables:
                result = connection.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM {child_table} 
                    WHERE {fk_column} NOT IN (SELECT {pk_column} FROM {parent_table});
                """))
                orphaned_count = result.fetchone()[0]
                
                if orphaned_count == 0:
                    print(f"✅ {description}: No orphaned records")
                else:
                    print(f"❌ {description}: {orphaned_count} orphaned records found")
                    
    except Exception as e:
        print(f"⚠️  Foreign key check failed: {e}")

def main():
    """Main schema check function."""
    print("=" * 60)
    print("Database Schema Verification")
    print("=" * 60)
    
    if check_database_schema():
        print("\n" + "=" * 60)
        print("✅ Database schema verification completed!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Database schema verification failed!")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
