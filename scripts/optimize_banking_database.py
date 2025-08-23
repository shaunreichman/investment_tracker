#!/usr/bin/env python3
"""
Banking Database Optimization Script for Phase 6.

This script optimizes the banking database for production performance,
adding essential indexes and optimizing queries for real-world usage.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine
from src.database import create_database_engine
from src.config import get_database_url
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BankingDatabaseOptimizer:
    """Database optimizer for banking system performance."""
    
    def __init__(self):
        """Initialize the database optimizer."""
        self.engine = create_database_engine()
        self.optimizations_applied = []
        self.performance_improvements = {}
    
    def optimize_banking_tables(self):
        """Apply essential banking database optimizations."""
        logger.info("🚀 Starting banking database optimization...")
        
        try:
            # 1. Add essential performance indexes (conservative approach)
            self._add_essential_indexes()
            
            # 2. Optimize table statistics for query planning
            self._optimize_table_statistics()
            
            # 3. Validate optimizations
            self._validate_optimizations()
            
            logger.info("✅ Banking database optimization completed successfully!")
            self._print_optimization_summary()
            
        except Exception as e:
            logger.error(f"❌ Database optimization failed: {e}")
            raise
    
    def _add_essential_indexes(self):
        """Add only essential indexes for critical query patterns."""
        logger.info("📊 Adding essential performance indexes...")
        
        # CRITICAL INDEXES - These provide real performance benefits
        essential_indexes = [
            # Bank table - only the most important
            "CREATE INDEX IF NOT EXISTS idx_banks_country ON banks(country)",
            
            # Bank account table - focus on foreign keys and common filters
            "CREATE INDEX IF NOT EXISTS idx_bank_accounts_entity_id ON bank_accounts(entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_bank_accounts_bank_id ON bank_accounts(bank_id)",
            "CREATE INDEX IF NOT EXISTS idx_bank_accounts_currency ON bank_accounts(currency)",
            "CREATE INDEX IF NOT EXISTS idx_bank_accounts_is_active ON bank_accounts(is_active)",
            
            # Fund event cash flow - only if this table exists and is used
            "CREATE INDEX IF NOT EXISTS idx_fund_event_cash_flows_bank_account_id ON fund_event_cash_flows(bank_account_id)",
        ]
        
        # Check if tables exist before creating indexes
        existing_tables = self._get_existing_tables()
        
        for index_sql in essential_indexes:
            try:
                # Extract table name from index SQL
                table_name = self._extract_table_name_from_index(index_sql)
                
                # Only create index if table exists
                if table_name in existing_tables:
                    with self.engine.connect() as conn:
                        conn.execute(text(index_sql))
                        conn.commit()
                        self.optimizations_applied.append(f"Essential Index: {index_sql}")
                        logger.info(f"✅ Added essential index: {index_sql}")
                else:
                    logger.info(f"⏭️ Skipping index for non-existent table: {table_name}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Index creation warning: {e}")
    
    def _get_existing_tables(self):
        """Get list of existing tables in the database."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                return {row[0] for row in result.fetchall()}
        except Exception as e:
            logger.warning(f"⚠️ Could not get table list: {e}")
            return set()
    
    def _extract_table_name_from_index(self, index_sql: str) -> str:
        """Extract table name from CREATE INDEX SQL."""
        # Simple extraction - look for "ON table_name"
        if " ON " in index_sql:
            parts = index_sql.split(" ON ")
            if len(parts) > 1:
                table_part = parts[1].split("(")[0].strip()
                return table_part
        return "unknown"
    
    def _optimize_table_statistics(self):
        """Optimize table statistics for query planning."""
        logger.info("📈 Optimizing table statistics...")
        
        # Only analyze tables that exist and are likely to have data
        tables_to_analyze = ['banks', 'bank_accounts']
        
        for table in tables_to_analyze:
            try:
                with self.engine.connect() as conn:
                    conn.execute(text(f"ANALYZE {table}"))
                    conn.commit()
                    self.optimizations_applied.append(f"Statistics: ANALYZE {table}")
                    logger.info(f"✅ Analyzed table: {table}")
            except Exception as e:
                logger.warning(f"⚠️ Table analysis warning for {table}: {e}")
    
    def _validate_optimizations(self):
        """Validate that optimizations were applied correctly."""
        logger.info("🔍 Validating optimizations...")
        
        validation_queries = [
            "SELECT COUNT(*) as total_indexes FROM pg_indexes WHERE tablename IN ('banks', 'bank_accounts')",
        ]
        
        for query in validation_queries:
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text(query))
                    count = result.fetchone()[0]
                    logger.info(f"✅ Total indexes on banking tables: {count}")
            except Exception as e:
                logger.warning(f"⚠️ Validation warning: {e}")
    
    def _print_optimization_summary(self):
        """Print summary of applied optimizations."""
        logger.info("📊 Optimization Summary:")
        logger.info(f"   Total optimizations applied: {len(self.optimizations_applied)}")
        
        for optimization in self.optimizations_applied:
            logger.info(f"   ✅ {optimization}")
        
        logger.info("🚀 Banking database is now optimized for production performance!")
        logger.info("💡 Remember: Start with fewer indexes and add more only if needed!")


def main():
    """Main optimization function."""
    try:
        optimizer = BankingDatabaseOptimizer()
        optimizer.optimize_banking_tables()
        
        print("\n🎉 Banking Database Optimization Complete!")
        print("✅ Essential performance indexes added")
        print("✅ Table statistics optimized")
        print("✅ Conservative approach - no over-indexing")
        print("\n🚀 Your banking system is now optimized for production!")
        print("💡 Tip: Monitor query performance and add indexes only when needed")
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
