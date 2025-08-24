#!/usr/bin/env python3
"""
Banking Performance Monitor for Phase 6.

This script helps monitor banking system performance and identify
when additional indexes or optimizations are actually needed.
"""

import sys
import os
import time
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine
from src.database import create_database_engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BankingPerformanceMonitor:
    """Monitor banking system performance and identify optimization opportunities."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.engine = create_database_engine()
        self.performance_data = {}
    
    def run_performance_analysis(self):
        """Run comprehensive performance analysis."""
        logger.info("🔍 Starting banking performance analysis...")
        
        try:
            # 1. Check current table sizes
            self._analyze_table_sizes()
            
            # 2. Check current index usage
            self._analyze_index_usage()
            
            # 3. Run sample queries to measure performance
            self._measure_query_performance()
            
            # 4. Provide optimization recommendations
            self._provide_recommendations()
            
        except Exception as e:
            logger.error(f"❌ Performance analysis failed: {e}")
            raise
    
    def _analyze_table_sizes(self):
        """Analyze current table sizes to understand data volume."""
        logger.info("📊 Analyzing table sizes...")
        
        size_query = """
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
            pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('banks', 'bank_accounts', 'fund_event_cash_flows')
        ORDER BY size_bytes DESC
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(size_query))
                rows = result.fetchall()
                
                logger.info("📈 Table Sizes:")
                for row in rows:
                    table_name = row[1]
                    size = row[2]
                    size_bytes = row[3]
                    
                    logger.info(f"   {table_name}: {size}")
                    
                    # Store for recommendations
                    self.performance_data[table_name] = {
                        'size': size,
                        'size_bytes': size_bytes
                    }
                    
        except Exception as e:
            logger.warning(f"⚠️ Could not analyze table sizes: {e}")
    
    def _analyze_index_usage(self):
        """Analyze current index usage and effectiveness."""
        logger.info("🔍 Analyzing index usage...")
        
        index_query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan as scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched
        FROM pg_stat_user_indexes 
        WHERE schemaname = 'public'
        AND tablename IN ('banks', 'bank_accounts', 'fund_event_cash_flows')
        ORDER BY tablename, idx_scan DESC
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(index_query))
                rows = result.fetchall()
                
                logger.info("📊 Index Usage:")
                for row in rows:
                    table_name = row[1]
                    index_name = row[2]
                    scans = row[3] or 0
                    tuples_read = row[4] or 0
                    tuples_fetched = row[5] or 0
                    
                    logger.info(f"   {table_name}.{index_name}: {scans} scans, {tuples_read} read, {tuples_fetched} fetched")
                    
        except Exception as e:
            logger.warning(f"⚠️ Could not analyze index usage: {e}")
    
    def _measure_query_performance(self):
        """Measure performance of common banking queries."""
        logger.info("⚡ Measuring query performance...")
        
        # Common banking queries to test
        test_queries = [
            {
                'name': 'Get all banks',
                'sql': 'SELECT * FROM banks',
                'expected_time': 0.1  # 100ms
            },
            {
                'name': 'Get bank accounts by entity',
                'sql': 'SELECT * FROM bank_accounts WHERE entity_id = 1',
                'expected_time': 0.05  # 50ms
            },
            {
                'name': 'Get active bank accounts',
                'sql': 'SELECT * FROM bank_accounts WHERE is_active = true',
                'expected_time': 0.1  # 100ms
            },
            {
                'name': 'Get bank accounts by currency',
                'sql': 'SELECT * FROM bank_accounts WHERE currency = \'AUD\'',
                'expected_time': 0.05  # 50ms
            }
        ]
        
        for query_info in test_queries:
            try:
                start_time = time.time()
                
                with self.engine.connect() as conn:
                    result = conn.execute(text(query_info['sql']))
                    rows = result.fetchall()
                
                execution_time = time.time() - start_time
                row_count = len(rows)
                
                logger.info(f"   {query_info['name']}: {execution_time:.3f}s ({row_count} rows)")
                
                # Check if performance meets expectations
                if execution_time > query_info['expected_time']:
                    logger.warning(f"   ⚠️ SLOW: {query_info['name']} took {execution_time:.3f}s (expected <{query_info['expected_time']}s)")
                
                # Store performance data
                if 'query_performance' not in self.performance_data:
                    self.performance_data['query_performance'] = {}
                
                self.performance_data['query_performance'][query_info['name']] = {
                    'execution_time': execution_time,
                    'expected_time': query_info['expected_time'],
                    'row_count': row_count,
                    'is_slow': execution_time > query_info['expected_time']
                }
                
            except Exception as e:
                logger.warning(f"   ⚠️ Query failed: {query_info['name']} - {e}")
    
    def _provide_recommendations(self):
        """Provide optimization recommendations based on analysis."""
        logger.info("💡 Performance Recommendations:")
        
        # Check table sizes for indexing strategy
        for table_name, data in self.performance_data.items():
            if isinstance(data, dict) and 'size_bytes' in data:
                size_bytes = data['size_bytes']
                
                if size_bytes < 1024 * 1024:  # Less than 1MB
                    logger.info(f"   📊 {table_name}: Small table ({data['size']}) - minimal indexing needed")
                elif size_bytes < 100 * 1024 * 1024:  # Less than 100MB
                    logger.info(f"   📊 {table_name}: Medium table ({data['size']}) - moderate indexing appropriate")
                else:
                    logger.info(f"   📊 {table_name}: Large table ({data['size']}) - aggressive indexing may be needed")
        
        # Check query performance
        if 'query_performance' in self.performance_data:
            slow_queries = [
                name for name, data in self.performance_data['query_performance'].items()
                if data.get('is_slow', False)
            ]
            
            if slow_queries:
                logger.info("   🚨 SLOW QUERIES DETECTED:")
                for query_name in slow_queries:
                    data = self.performance_data['query_performance'][query_name]
                    logger.info(f"      - {query_name}: {data['execution_time']:.3f}s (expected <{data['expected_time']}s)")
                
                logger.info("   💡 RECOMMENDATIONS:")
                logger.info("      - Consider adding indexes for slow queries")
                logger.info("      - Use EXPLAIN ANALYZE to identify bottlenecks")
                logger.info("      - Consider query optimization before adding indexes")
            else:
                logger.info("   ✅ All queries performing well - no additional indexes needed")
        
        # General recommendations
        logger.info("   💡 GENERAL OPTIMIZATION STRATEGY:")
        logger.info("      - Start with minimal indexes (what we added)")
        logger.info("      - Monitor query performance regularly")
        logger.info("      - Add indexes only when queries are slow")
        logger.info("      - Use EXPLAIN ANALYZE to understand query plans")
        logger.info("      - Consider query optimization before indexing")


def main():
    """Main performance monitoring function."""
    try:
        monitor = BankingPerformanceMonitor()
        monitor.run_performance_analysis()
        
        print("\n🎉 Banking Performance Analysis Complete!")
        print("✅ Table sizes analyzed")
        print("✅ Index usage reviewed")
        print("✅ Query performance measured")
        print("✅ Optimization recommendations provided")
        print("\n💡 Use this script regularly to monitor performance!")
        print("🚀 Add indexes only when you actually need them!")
        
    except Exception as e:
        print(f"❌ Performance analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
