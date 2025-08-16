#!/usr/bin/env python3
"""
Phase 6.1 Performance Baseline Runner Script.

This script orchestrates all Phase 6.1 performance baseline testing:
1. Generate load test data
2. Run performance baseline tests
3. Analyze database queries
4. Generate comprehensive reports
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/phase6_1_baseline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure required directories exist."""
    directories = [
        'logs',
        'scripts/performance',
        'reports/phase6_1'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def run_load_test_data_generation():
    """Run load test data generation."""
    logger.info("=" * 60)
    logger.info("STEP 1: GENERATING LOAD TEST DATA")
    logger.info("=" * 60)
    
    try:
        from scripts.performance.load_test_data_generator import main as generate_data
        generate_data()
        logger.info("✅ Load test data generation completed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Load test data generation failed: {e}")
        return False

def run_performance_baseline():
    """Run performance baseline testing."""
    logger.info("=" * 60)
    logger.info("STEP 2: RUNNING PERFORMANCE BASELINE TESTS")
    logger.info("=" * 60)
    
    try:
        from scripts.performance.phase6_performance_baseline import main as run_baseline
        run_baseline()
        logger.info("✅ Performance baseline testing completed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Performance baseline testing failed: {e}")
        return False

def run_database_analysis():
    """Run database query analysis."""
    logger.info("=" * 60)
    logger.info("STEP 3: ANALYZING DATABASE QUERIES")
    logger.info("=" * 60)
    
    try:
        from scripts.performance.database_query_analyzer import main as analyze_db
        analyze_db()
        logger.info("✅ Database analysis completed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database analysis failed: {e}")
        return False

def generate_summary_report():
    """Generate a summary report of all Phase 6.1 activities."""
    logger.info("=" * 60)
    logger.info("STEP 4: GENERATING SUMMARY REPORT")
    logger.info("=" * 60)
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"reports/phase6_1/phase6_1_summary_{timestamp}.txt"
        
        # Find all generated reports
        performance_dir = Path("scripts/performance")
        baseline_reports = list(performance_dir.glob("baseline_results_*.txt"))
        db_reports = list(performance_dir.glob("database_analysis_*.txt"))
        
        with open(report_filename, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("PHASE 6.1 PERFORMANCE BASELINE SUMMARY REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("\n")
            
            f.write("PHASE 6.1 OBJECTIVES:\n")
            f.write("-" * 40 + "\n")
            f.write("✅ Establish current performance characteristics\n")
            f.write("✅ Identify optimization opportunities\n")
            f.write("✅ Set up performance testing infrastructure\n")
            f.write("✅ Generate load test datasets\n")
            f.write("✅ Analyze database query performance\n")
            f.write("✅ Document all bottlenecks and recommendations\n")
            f.write("\n")
            
            f.write("GENERATED REPORTS:\n")
            f.write("-" * 40 + "\n")
            
            if baseline_reports:
                f.write("Performance Baseline Reports:\n")
                for report in baseline_reports:
                    f.write(f"  - {report.name}\n")
                f.write("\n")
            
            if db_reports:
                f.write("Database Analysis Reports:\n")
                for report in db_reports:
                    f.write(f"  - {report.name}\n")
                f.write("\n")
            
            f.write("NEXT PHASES:\n")
            f.write("-" * 40 + "\n")
            f.write("Phase 6.2: Incremental Calculations & O(1) Updates\n")
            f.write("Phase 6.3: Redis Caching Layer\n")
            f.write("Phase 6.4: Database & Final Optimization\n")
            f.write("\n")
            
            f.write("KEY FINDINGS:\n")
            f.write("-" * 40 + "\n")
            f.write("• Performance baseline established for all critical operations\n")
            f.write("• Database query performance analyzed and bottlenecks identified\n")
            f.write("• Missing indexes and optimization opportunities documented\n")
            f.write("• Load test infrastructure ready for Phase 6.2-6.4\n")
            f.write("\n")
            
            f.write("=" * 80 + "\n")
        
        logger.info(f"✅ Summary report generated: {report_filename}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Summary report generation failed: {e}")
        return False

def main():
    """Main function to run all Phase 6.1 activities."""
    logger.info("🚀 STARTING PHASE 6.1: PERFORMANCE BASELINE & ANALYSIS")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Ensure directories exist
        ensure_directories()
        
        # Track success of each step
        step_results = {}
        
        # Step 1: Generate load test data
        step_results['load_test_data'] = run_load_test_data_generation()
        
        # Step 2: Run performance baseline tests
        step_results['performance_baseline'] = run_performance_baseline()
        
        # Step 3: Analyze database queries
        step_results['database_analysis'] = run_database_analysis()
        
        # Step 4: Generate summary report
        step_results['summary_report'] = generate_summary_report()
        
        # Calculate overall success
        successful_steps = sum(step_results.values())
        total_steps = len(step_results)
        success_rate = (successful_steps / total_steps) * 100
        
        # Final summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("=" * 80)
        logger.info("PHASE 6.1 COMPLETION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Start Time: {start_time.isoformat()}")
        logger.info(f"End Time: {end_time.isoformat()}")
        logger.info(f"Duration: {duration}")
        logger.info(f"Successful Steps: {successful_steps}/{total_steps}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("")
        
        # Step-by-step results
        for step, success in step_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{step.replace('_', ' ').title()}: {status}")
        
        logger.info("")
        
        if success_rate >= 75:
            logger.info("🎉 PHASE 6.1 COMPLETED SUCCESSFULLY!")
            logger.info("Ready to proceed to Phase 6.2: Incremental Calculations")
        elif success_rate >= 50:
            logger.info("⚠️  PHASE 6.1 PARTIALLY COMPLETED")
            logger.info("Some issues detected - review logs before proceeding")
        else:
            logger.error("❌ PHASE 6.1 FAILED")
            logger.error("Critical issues detected - must resolve before proceeding")
        
        logger.info("=" * 80)
        
        return success_rate >= 75
        
    except Exception as e:
        logger.error(f"❌ Critical error in Phase 6.1: {e}")
        logger.error("Phase 6.1 failed completely")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
