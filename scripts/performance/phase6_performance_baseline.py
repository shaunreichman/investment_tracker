#!/usr/bin/env python3
"""
Phase 6.1 Performance Baseline Testing Script.

This script establishes performance baselines for the current system to identify
optimization opportunities for Phase 6 performance improvements.

Targets:
- Single event creation performance
- Fund summary update performance  
- API response times
- Database query performance
- Memory usage patterns
- Event processing pipeline performance
"""

import time
import psutil
import statistics
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database imports
from sqlalchemy.orm import Session
from src.database_config import get_database_session
from src.fund.models import Fund, FundEvent, FundStatus
from src.fund.enums import FundType, EventType
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from src.tax.models import TaxStatement

# Performance testing utilities
class PerformanceTimer:
    """Utility class for measuring performance of operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        return False
    
    def get_duration_ms(self) -> float:
        """Get duration in milliseconds."""
        return self.duration * 1000 if self.duration else 0

class PerformanceBaseline:
    """Main class for establishing performance baselines."""
    
    def __init__(self):
        self.results = {}
        self.memory_baseline = None
        
    def measure_memory_usage(self) -> Dict[str, float]:
        """Measure current memory usage."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
            'percent': process.memory_percent()
        }
    
    def baseline_memory(self):
        """Establish memory baseline."""
        self.memory_baseline = self.measure_memory_usage()
        logger.info(f"Memory baseline established: {self.memory_baseline}")
    
    def measure_event_creation_performance(self, session: Session, iterations: int = 100) -> Dict[str, Any]:
        """Measure performance of fund event creation."""
        logger.info(f"Measuring event creation performance with {iterations} iterations...")
        
        # Get a test fund
        test_fund = session.query(Fund).first()
        if not test_fund:
            logger.error("No test fund found for performance testing")
            return {}
        
        durations = []
        memory_usage = []
        
        for i in range(iterations):
            # Measure memory before
            mem_before = self.measure_memory_usage()
            
            # Create a test event
            with PerformanceTimer("event_creation") as timer:
                event = FundEvent(
                    fund_id=test_fund.id,
                    event_type=EventType.CAPITAL_CALL,
                    event_date=datetime.now().date(),
                    amount=Decimal('10000.00'),
                    description=f"Performance test event {i}",
                    reference_number=f"PERF-{i:03d}"
                )
                session.add(event)
                session.flush()  # Don't commit to avoid database growth
            
            # Measure memory after
            mem_after = self.measure_memory_usage()
            
            durations.append(timer.get_duration_ms())
            memory_usage.append(mem_after['rss_mb'] - mem_before['rss_mb'])
            
            # Clean up
            session.rollback()
        
        # Calculate statistics
        stats = {
            'iterations': iterations,
            'mean_duration_ms': statistics.mean(durations),
            'median_duration_ms': statistics.median(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
            'std_deviation_ms': statistics.stdev(durations) if len(durations) > 1 else 0,
            'mean_memory_delta_mb': statistics.mean(memory_usage),
            'total_memory_delta_mb': sum(memory_usage)
        }
        
        logger.info(f"Event creation performance: {stats['mean_duration_ms']:.2f}ms average")
        return stats
    
    def measure_fund_summary_update_performance(self, session: Session, iterations: int = 50) -> Dict[str, Any]:
        """Measure performance of fund summary updates."""
        logger.info(f"Measuring fund summary update performance with {iterations} iterations...")
        
        # Get a test fund with events
        test_fund = session.query(Fund).first()
        if not test_fund:
            logger.error("No test fund found for performance testing")
            return {}
        
        durations = []
        
        for i in range(iterations):
            with PerformanceTimer("fund_summary_update") as timer:
                # Trigger a summary update by adding a temporary event
                temp_event = FundEvent(
                    fund_id=test_fund.id,
                    event_type=EventType.CAPITAL_CALL,
                    event_date=datetime.now().date(),
                    amount=Decimal('1000.00'),
                    description=f"Temp performance test {i}",
                    reference_number=f"TEMP-{i:03d}"
                )
                session.add(temp_event)
                session.flush()
                
                # This would normally trigger summary updates
                # For baseline, we'll measure the event addition time
                
                # Clean up
                session.rollback()
            
            durations.append(timer.get_duration_ms())
        
        # Calculate statistics
        stats = {
            'iterations': iterations,
            'mean_duration_ms': statistics.mean(durations),
            'median_duration_ms': statistics.median(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
            'std_deviation_ms': statistics.stdev(durations) if len(durations) > 1 else 0
        }
        
        logger.info(f"Fund summary update performance: {stats['mean_duration_ms']:.2f}ms average")
        return stats
    
    def measure_database_query_performance(self, session: Session, iterations: int = 100) -> Dict[str, Any]:
        """Measure performance of common database queries."""
        logger.info(f"Measuring database query performance with {iterations} iterations...")
        
        query_results = {}
        
        # Test 1: Simple fund lookup
        durations = []
        for i in range(iterations):
            with PerformanceTimer("fund_lookup") as timer:
                fund = session.query(Fund).filter(Fund.id == 1).first()
            durations.append(timer.get_duration_ms())
        
        query_results['fund_lookup'] = {
            'iterations': iterations,
            'mean_duration_ms': statistics.mean(durations),
            'median_duration_ms': statistics.median(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations)
        }
        
        # Test 2: Fund events query
        durations = []
        for i in range(iterations):
            with PerformanceTimer("fund_events_query") as timer:
                events = session.query(FundEvent).filter(FundEvent.fund_id == 1).limit(100).all()
            durations.append(timer.get_duration_ms())
        
        query_results['fund_events_query'] = {
            'iterations': iterations,
            'mean_duration_ms': statistics.mean(durations),
            'median_duration_ms': statistics.median(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations)
        }
        
        # Test 3: Complex join query
        durations = []
        for i in range(iterations):
            with PerformanceTimer("complex_join_query") as timer:
                result = session.query(Fund, InvestmentCompany).join(
                    InvestmentCompany, Fund.investment_company_id == InvestmentCompany.id
                ).filter(Fund.status == FundStatus.ACTIVE).limit(50).all()
            durations.append(timer.get_duration_ms())
        
        query_results['complex_join_query'] = {
            'iterations': iterations,
            'mean_duration_ms': statistics.mean(durations),
            'median_duration_ms': statistics.median(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations)
        }
        
        logger.info("Database query performance measured")
        return query_results
    
    def measure_api_endpoint_performance(self, session: Session, iterations: int = 50) -> Dict[str, Any]:
        """Measure performance of API-like operations."""
        logger.info(f"Measuring API endpoint performance with {iterations} iterations...")
        
        # Simulate API operations by calling domain methods
        api_results = {}
        
        # Test 1: Get fund details
        durations = []
        for i in range(iterations):
            with PerformanceTimer("get_fund_details") as timer:
                fund = session.query(Fund).first()
                if fund:
                    # Simulate API response preparation
                    fund_data = {
                        'id': fund.id,
                        'name': fund.name,
                        'status': fund.status.value if fund.status else None,
                        'current_equity_balance': float(fund.current_equity_balance) if fund.current_equity_balance else 0.0
                    }
            durations.append(timer.get_duration_ms())
        
        api_results['get_fund_details'] = {
            'iterations': iterations,
            'mean_duration_ms': statistics.mean(durations),
            'median_duration_ms': statistics.median(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations)
        }
        
        # Test 2: Get fund events
        durations = []
        for i in range(iterations):
            with PerformanceTimer("get_fund_events") as timer:
                fund = session.query(Fund).first()
                if fund:
                    events = session.query(FundEvent).filter(
                        FundEvent.fund_id == fund.id
                    ).order_by(FundEvent.event_date.desc()).limit(50).all()
                    
                    # Simulate API response preparation
                    events_data = [{
                        'id': event.id,
                        'event_type': event.event_type.value if event.event_type else None,
                        'amount': float(event.amount) if event.amount else 0.0,
                        'event_date': event.event_date.isoformat() if event.event_date else None
                    } for event in events]
            durations.append(timer.get_duration_ms())
        
        api_results['get_fund_events'] = {
            'iterations': iterations,
            'mean_duration_ms': statistics.mean(durations),
            'median_duration_ms': statistics.median(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations)
        }
        
        logger.info("API endpoint performance measured")
        return api_results
    
    def run_comprehensive_baseline(self) -> Dict[str, Any]:
        """Run comprehensive performance baseline testing."""
        logger.info("Starting comprehensive performance baseline testing...")
        
        # Establish memory baseline
        self.baseline_memory()
        
        # Get database session
        engine, session_factory, scoped_session = get_database_session()
        session = scoped_session()
        
        try:
            # Run all performance tests
            self.results = {
                'timestamp': datetime.now().isoformat(),
                'memory_baseline': self.memory_baseline,
                'event_creation': self.measure_event_creation_performance(session),
                'fund_summary_updates': self.measure_fund_summary_update_performance(session),
                'database_queries': self.measure_database_query_performance(session),
                'api_endpoints': self.measure_api_endpoint_performance(session),
                'final_memory': self.measure_memory_usage()
            }
            
            logger.info("Comprehensive performance baseline completed successfully")
            return self.results
            
        except Exception as e:
            logger.error(f"Error during performance baseline testing: {e}")
            raise
        finally:
            session.close()
    
    def generate_report(self) -> str:
        """Generate a comprehensive performance baseline report."""
        if not self.results:
            return "No performance baseline results available. Run run_comprehensive_baseline() first."
        
        report = []
        report.append("=" * 80)
        report.append("PHASE 6.1 PERFORMANCE BASELINE REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {self.results['timestamp']}")
        report.append("")
        
        # Memory baseline
        report.append("MEMORY BASELINE:")
        report.append(f"  Initial RSS: {self.results['memory_baseline']['rss_mb']:.2f} MB")
        report.append(f"  Initial VMS: {self.results['memory_baseline']['vms_mb']:.2f} MB")
        report.append(f"  Initial %: {self.results['memory_baseline']['percent']:.2f}%")
        report.append("")
        
        # Event creation performance
        if 'event_creation' in self.results:
            ec = self.results['event_creation']
            report.append("EVENT CREATION PERFORMANCE:")
            report.append(f"  Iterations: {ec['iterations']}")
            report.append(f"  Mean Duration: {ec['mean_duration_ms']:.2f} ms")
            report.append(f"  Median Duration: {ec['median_duration_ms']:.2f} ms")
            report.append(f"  Min Duration: {ec['min_duration_ms']:.2f} ms")
            report.append(f"  Max Duration: {ec['max_duration_ms']:.2f} ms")
            report.append(f"  Std Deviation: {ec['std_deviation_ms']:.2f} ms")
            report.append("")
        
        # Fund summary updates
        if 'fund_summary_updates' in self.results:
            fsu = self.results['fund_summary_updates']
            report.append("FUND SUMMARY UPDATE PERFORMANCE:")
            report.append(f"  Iterations: {fsu['iterations']}")
            report.append(f"  Mean Duration: {fsu['mean_duration_ms']:.2f} ms")
            report.append(f"  Median Duration: {fsu['median_duration_ms']:.2f} ms")
            report.append(f"  Min Duration: {fsu['min_duration_ms']:.2f} ms")
            report.append(f"  Max Duration: {fsu['max_duration_ms']:.2f} ms")
            report.append("")
        
        # Database queries
        if 'database_queries' in self.results:
            report.append("DATABASE QUERY PERFORMANCE:")
            for query_name, query_stats in self.results['database_queries'].items():
                report.append(f"  {query_name.replace('_', ' ').title()}:")
                report.append(f"    Mean Duration: {query_stats['mean_duration_ms']:.2f} ms")
                report.append(f"    Median Duration: {query_stats['median_duration_ms']:.2f} ms")
                report.append(f"    Min Duration: {query_stats['min_duration_ms']:.2f} ms")
                report.append(f"    Max Duration: {query_stats['max_duration_ms']:.2f} ms")
            report.append("")
        
        # API endpoints
        if 'api_endpoints' in self.results:
            report.append("API ENDPOINT PERFORMANCE:")
            for endpoint_name, endpoint_stats in self.results['api_endpoints'].items():
                report.append(f"  {endpoint_name.replace('_', ' ').title()}:")
                report.append(f"    Mean Duration: {endpoint_stats['mean_duration_ms']:.2f} ms")
                report.append(f"    Median Duration: {endpoint_stats['median_duration_ms']:.2f} ms")
                report.append(f"    Min Duration: {endpoint_stats['min_duration_ms']:.2f} ms")
                report.append(f"    Max Duration: {endpoint_stats['max_duration_ms']:.2f} ms")
            report.append("")
        
        # Final memory
        if 'final_memory' in self.results:
            final_mem = self.results['final_memory']
            report.append("FINAL MEMORY USAGE:")
            report.append(f"  Final RSS: {final_mem['rss_mb']:.2f} MB")
            report.append(f"  Final VMS: {final_mem['vms_mb']:.2f} MB")
            report.append(f"  Final %: {final_mem['percent']:.2f}%")
            report.append("")
        
        # Performance analysis and recommendations
        report.append("PERFORMANCE ANALYSIS:")
        report.append("  This baseline establishes current performance characteristics")
        report.append("  for Phase 6 optimization planning.")
        report.append("")
        report.append("NEXT STEPS:")
        report.append("  1. Analyze bottlenecks identified in this baseline")
        report.append("  2. Plan Phase 6.2 incremental calculation optimizations")
        report.append("  3. Design Redis caching strategy for slow operations")
        report.append("  4. Identify database query optimization opportunities")
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Main function to run performance baseline testing."""
    logger.info("Starting Phase 6.1 Performance Baseline Testing")
    
    try:
        # Create performance baseline instance
        baseline = PerformanceBaseline()
        
        # Run comprehensive baseline
        results = baseline.run_comprehensive_baseline()
        
        # Generate and display report
        report = baseline.generate_report()
        print(report)
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scripts/performance/baseline_results_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(report)
        
        logger.info(f"Performance baseline report saved to {filename}")
        logger.info("Phase 6.1 Performance Baseline Testing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in performance baseline testing: {e}")
        raise

if __name__ == "__main__":
    main()
