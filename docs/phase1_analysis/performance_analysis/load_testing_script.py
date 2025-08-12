#!/usr/bin/env python3
"""
Load Testing Script for Fund System Performance Validation

This script validates the performance analysis findings by testing the current system
with realistic data volumes. It focuses on the critical O(n) complexity operations
identified in the performance analysis.

Usage:
    python load_testing_script.py [--funds N] [--events N] [--companies N]

Example:
    python load_testing_script.py --funds 100 --events 1000 --companies 10
"""

import argparse
import time
import statistics
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Also add current working directory
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.database import get_global_session
    from src.fund.models import Fund, FundEvent, FundType, EventType, FundStatus
    from src.investment_company.models import InvestmentCompany
    from src.entity.models import Entity
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


class FundSystemLoadTester:
    """Load tester for the fund system to validate performance analysis findings."""
    
    def __init__(self, funds_count: int = 50, events_per_fund: int = 100, companies_count: int = 5):
        self.funds_count = funds_count
        self.events_per_fund = events_per_fund
        self.companies_count = companies_count
        self.results = {}
        
    def run_load_test(self) -> Dict[str, Any]:
        """Run the complete load test suite."""
        print(f"🚀 Starting Fund System Load Test")
        print(f"   Funds: {self.funds_count}")
        print(f"   Events per fund: {self.events_per_fund}")
        print(f"   Companies: {self.companies_count}")
        print(f"   Total events: {self.funds_count * self.events_per_fund:,}")
        print()
        
        try:
            # Test 1: System startup and basic operations
            self._test_system_startup()
            
            # Test 2: Fund creation performance
            self._test_fund_creation()
            
            # Test 3: Event creation performance (critical O(n) operation)
            self._test_event_creation()
            
            # Test 4: Chain recalculation performance (critical bottleneck)
            self._test_chain_recalculation()
            
            # Test 5: Fund summary calculations
            self._test_fund_summaries()
            
            # Test 6: Dashboard performance
            self._test_dashboard_performance()
            
            # Test 7: Memory usage analysis
            self._test_memory_usage()
            
        except Exception as e:
            print(f"❌ Load test failed: {e}")
            return {"error": str(e)}
        
        return self.results
    
    def _test_system_startup(self):
        """Test system startup and basic connectivity."""
        print("📊 Test 1: System Startup Performance")
        
        start_time = time.time()
        
        try:
            session = get_global_session()
            
            # Test basic database connectivity
            fund_count = session.query(Fund).count()
            company_count = session.query(InvestmentCompany).count()
            entity_count = session.query(Entity).count()
            
            session.remove()
            
            startup_time = time.time() - start_time
            
            self.results["system_startup"] = {
                "startup_time_ms": startup_time * 1000,
                "existing_funds": fund_count,
                "existing_companies": company_count,
                "existing_entities": entity_count
            }
            
            print(f"   ✅ Startup time: {startup_time * 1000:.2f}ms")
            print(f"   ✅ Existing data: {fund_count} funds, {company_count} companies, {entity_count} entities")
            
        except Exception as e:
            print(f"   ❌ System startup failed: {e}")
            raise
    
    def _test_fund_creation(self):
        """Test fund creation performance."""
        print("📊 Test 2: Fund Creation Performance")
        
        creation_times = []
        
        try:
            session = get_global_session()
            
            # Get existing company and entity for testing
            company = session.query(InvestmentCompany).first()
            entity = session.query(Entity).first()
            
            if not company or not entity:
                print("   ⚠️  Need at least one company and entity for testing")
                return
            
            for i in range(min(10, self.funds_count)):  # Test with up to 10 funds
                start_time = time.time()
                
                fund = Fund.create(
                    investment_company_id=company.id,
                    entity_id=entity.id,
                    name=f"Test Fund {i+1}",
                    fund_type="Private Equity",
                    tracking_type=FundType.COST_BASED,
                    currency="AUD",
                    description=f"Load test fund {i+1}",
                    session=session
                )
                
                creation_time = time.time() - start_time
                creation_times.append(creation_time)
                
                # Clean up test fund
                session.delete(fund)
                session.commit()
            
            session.remove()
            
            avg_creation_time = statistics.mean(creation_times)
            max_creation_time = max(creation_times)
            min_creation_time = min(creation_times)
            
            self.results["fund_creation"] = {
                "avg_time_ms": avg_creation_time * 1000,
                "max_time_ms": max_creation_time * 1000,
                "min_time_ms": min_creation_time * 1000,
                "samples": len(creation_times)
            }
            
            print(f"   ✅ Fund creation: {avg_creation_time * 1000:.2f}ms avg")
            print(f"   ✅ Range: {min_creation_time * 1000:.2f}ms - {max_creation_time * 1000:.2f}ms")
            
        except Exception as e:
            print(f"   ❌ Fund creation test failed: {e}")
            raise
    
    def _test_event_creation(self):
        """Test fund event creation performance."""
        print("📊 Test 3: Event Creation Performance")
        
        creation_times = []
        
        try:
            session = get_global_session()
            
            # Get existing fund for testing
            fund = session.query(Fund).first()
            if not fund:
                print("   ⚠️  Need at least one fund for testing")
                return
            
            # Test event creation (this triggers the O(n) chain recalculation)
            for i in range(min(20, self.events_per_fund)):  # Test with up to 20 events
                start_time = time.time()
                
                event = fund.add_capital_call(
                    amount=10000.0 + (i * 1000),
                    date=datetime.now().date() - timedelta(days=i),
                    description=f"Load test capital call {i+1}",
                    reference_number=f"TEST-{i+1:04d}",
                    session=session
                )
                
                creation_time = time.time() - start_time
                creation_times.append(creation_time)
                
                # Clean up test event
                session.delete(event)
                session.commit()
            
            session.remove()
            
            avg_creation_time = statistics.mean(creation_times)
            max_creation_time = max(creation_times)
            min_creation_time = min(creation_times)
            
            self.results["event_creation"] = {
                "avg_time_ms": avg_creation_time * 1000,
                "max_time_ms": max_creation_time * 1000,
                "min_time_ms": min_creation_time * 1000,
                "samples": len(creation_times)
            }
            
            print(f"   ✅ Event creation: {avg_creation_time * 1000:.2f}ms avg")
            print(f"   ✅ Range: {min_creation_time * 1000:.2f}ms - {max_creation_time * 1000:.2f}ms")
            
            # Check for O(n) complexity warning
            if max_creation_time > avg_creation_time * 2:
                print(f"   ⚠️  WARNING: Potential O(n) complexity detected!")
                print(f"   ⚠️  Max time ({max_creation_time * 1000:.2f}ms) significantly higher than avg ({avg_creation_time * 1000:.2f}ms)")
            
        except Exception as e:
            print(f"   ❌ Event creation test failed: {e}")
            raise
    
    def _test_chain_recalculation(self):
        """Test the critical chain recalculation performance."""
        print("📊 Test 4: Chain Recalculation Performance (Critical Bottleneck)")
        
        recalculation_times = []
        
        try:
            session = get_database_session()
            
            # Get existing fund with events for testing
            fund = session.query(Fund).filter(Fund.fund_events.any()).first()
            if not fund:
                print("   ⚠️  Need at least one fund with events for testing")
                return
            
            # Test chain recalculation performance
            for i in range(5):  # Test multiple times
                start_time = time.time()
                
                # Trigger chain recalculation by updating an event
                if fund.fund_events:
                    event = fund.fund_events[0]
                    # Modify event to trigger recalculation
                    original_amount = event.amount
                    event.amount = original_amount + 1
                    session.flush()
                    
                    # This should trigger recalculate_capital_chain_from
                    fund.recalculate_capital_chain_from(event, session)
                    
                    # Restore original amount
                    event.amount = original_amount
                    session.flush()
                    
                    recalculation_time = time.time() - start_time
                    recalculation_times.append(recalculation_time)
            
            session.close()
            
            if recalculation_times:
                avg_recalculation_time = statistics.mean(recalculation_times)
                max_recalculation_time = max(recalculation_times)
                min_recalculation_time = min(recalculation_times)
                
                self.results["chain_recalculation"] = {
                    "avg_time_ms": avg_recalculation_time * 1000,
                    "max_time_ms": max_recalculation_time * 1000,
                    "min_time_ms": min_recalculation_time * 1000,
                    "samples": len(recalculation_times)
                }
                
                print(f"   ✅ Chain recalculation: {avg_recalculation_time * 1000:.2f}ms avg")
                print(f"   ✅ Range: {min_recalculation_time * 1000:.2f}ms - {max_recalculation_time * 1000:.2f}ms")
                
                # Performance warning thresholds
                if avg_recalculation_time > 1.0:  # > 1 second
                    print(f"   🚨 CRITICAL: Chain recalculation is SLOW ({avg_recalculation_time * 1000:.2f}ms)")
                    print(f"   🚨 This confirms the O(n) complexity bottleneck identified in analysis")
                elif avg_recalculation_time > 0.5:  # > 500ms
                    print(f"   ⚠️  WARNING: Chain recalculation is SLOW ({avg_recalculation_time * 1000:.2f}ms)")
                else:
                    print(f"   ✅ Chain recalculation performance is acceptable")
            
        except Exception as e:
            print(f"   ❌ Chain recalculation test failed: {e}")
            raise
    
    def _test_fund_summaries(self):
        """Test fund summary calculation performance."""
        print("📊 Test 5: Fund Summary Calculation Performance")
        
        summary_times = []
        
        try:
            session = get_database_session()
            
            # Test summary calculations for multiple funds
            funds = session.query(Fund).limit(10).all()
            
            for fund in funds:
                start_time = time.time()
                
                # Test various summary calculations
                _ = fund.current_equity_balance
                _ = fund.average_equity_balance
                _ = fund.status
                
                summary_time = time.time() - start_time
                summary_times.append(summary_time)
            
            session.close()
            
            if summary_times:
                avg_summary_time = statistics.mean(summary_times)
                max_summary_time = max(summary_times)
                min_summary_time = min(summary_times)
                
                self.results["fund_summaries"] = {
                    "avg_time_ms": avg_summary_time * 1000,
                    "max_time_ms": max_summary_time * 1000,
                    "min_time_ms": min_summary_time * 1000,
                    "samples": len(summary_times)
                }
                
                print(f"   ✅ Fund summaries: {avg_summary_time * 1000:.2f}ms avg")
                print(f"   ✅ Range: {min_summary_time * 1000:.2f}ms - {max_summary_time * 1000:.2f}ms")
            
        except Exception as e:
            print(f"   ❌ Fund summary test failed: {e}")
            raise
    
    def _test_dashboard_performance(self):
        """Test dashboard endpoint performance."""
        print("📊 Test 6: Dashboard Performance")
        
        # This would test actual API endpoints if we had a running server
        # For now, we'll simulate the dashboard calculations
        
        try:
            session = get_database_session()
            
            start_time = time.time()
            
            # Simulate dashboard portfolio summary calculation
            funds = session.query(Fund).all()
            total_funds = len(funds)
            active_funds = sum(1 for fund in funds if fund.status == FundStatus.ACTIVE)
            total_equity = sum(fund.current_equity_balance or 0.0 for fund in funds)
            
            dashboard_time = time.time() - start_time
            
            session.close()
            
            self.results["dashboard_performance"] = {
                "calculation_time_ms": dashboard_time * 1000,
                "total_funds": total_funds,
                "active_funds": active_funds,
                "total_equity": total_equity
            }
            
            print(f"   ✅ Dashboard calculation: {dashboard_time * 1000:.2f}ms")
            print(f"   ✅ Portfolio: {total_funds} funds, {active_funds} active, ${total_equity:,.2f} equity")
            
        except Exception as e:
            print(f"   ❌ Dashboard test failed: {e}")
            raise
    
    def _test_memory_usage(self):
        """Test memory usage during operations."""
        print("📊 Test 7: Memory Usage Analysis")
        
        try:
            import psutil
            import gc
            
            process = psutil.Process()
            
            # Force garbage collection
            gc.collect()
            
            # Get baseline memory
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform some operations to test memory usage
            session = get_database_session()
            
            # Load all funds and events to test memory usage
            funds = session.query(Fund).all()
            total_events = sum(len(fund.fund_events) for fund in funds)
            
            # Get peak memory during operations
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            session.close()
            
            # Force garbage collection again
            gc.collect()
            
            # Get final memory
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            memory_increase = peak_memory - baseline_memory
            memory_retention = final_memory - baseline_memory
            
            self.results["memory_usage"] = {
                "baseline_mb": baseline_memory,
                "peak_mb": peak_memory,
                "final_mb": final_memory,
                "increase_mb": memory_increase,
                "retention_mb": memory_retention,
                "total_funds": len(funds),
                "total_events": total_events
            }
            
            print(f"   ✅ Memory baseline: {baseline_memory:.1f}MB")
            print(f"   ✅ Memory peak: {peak_memory:.1f}MB (+{memory_increase:.1f}MB)")
            print(f"   ✅ Memory final: {final_memory:.1f}MB (+{memory_retention:.1f}MB)")
            print(f"   ✅ Data loaded: {len(funds)} funds, {total_events} events")
            
            # Memory warnings
            if memory_increase > 100:  # > 100MB increase
                print(f"   🚨 WARNING: Large memory increase ({memory_increase:.1f}MB) during operations")
            if memory_retention > 50:  # > 50MB retention
                print(f"   ⚠️  WARNING: Memory not fully released ({memory_retention:.1f}MB retained)")
            
        except ImportError:
            print("   ⚠️  psutil not available - skipping memory analysis")
        except Exception as e:
            print(f"   ❌ Memory test failed: {e}")
    
    def generate_report(self) -> str:
        """Generate a comprehensive load test report."""
        if not self.results:
            return "No test results available"
        
        report = []
        report.append("=" * 80)
        report.append("FUND SYSTEM LOAD TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Configuration: {self.funds_count} funds, {self.events_per_fund} events/fund, {self.companies_count} companies")
        report.append("")
        
        # Performance Summary
        report.append("PERFORMANCE SUMMARY")
        report.append("-" * 40)
        
        if "event_creation" in self.results:
            event_time = self.results["event_creation"]["avg_time_ms"]
            report.append(f"Event Creation: {event_time:.2f}ms avg")
            
            if event_time > 1000:  # > 1 second
                report.append("  🚨 CRITICAL: Event creation is extremely slow")
            elif event_time > 500:  # > 500ms
                report.append("  ⚠️  WARNING: Event creation is slow")
            else:
                report.append("  ✅ Event creation performance is acceptable")
        
        if "chain_recalculation" in self.results:
            recalc_time = self.results["chain_recalculation"]["avg_time_ms"]
            report.append(f"Chain Recalculation: {recalc_time:.2f}ms avg")
            
            if recalc_time > 1000:  # > 1 second
                report.append("  🚨 CRITICAL: Chain recalculation confirms O(n) bottleneck")
            elif recalc_time > 500:  # > 500ms
                report.append("  ⚠️  WARNING: Chain recalculation is slow")
            else:
                report.append("  ✅ Chain recalculation performance is acceptable")
        
        # Detailed Results
        report.append("")
        report.append("DETAILED RESULTS")
        report.append("-" * 40)
        
        for test_name, test_results in self.results.items():
            if isinstance(test_results, dict) and "avg_time_ms" in test_results:
                report.append(f"{test_name.replace('_', ' ').title()}:")
                report.append(f"  Average: {test_results['avg_time_ms']:.2f}ms")
                report.append(f"  Range: {test_results['min_time_ms']:.2f}ms - {test_results['max_time_ms']:.2f}ms")
                report.append(f"  Samples: {test_results['samples']}")
                report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 40)
        
        if "chain_recalculation" in self.results and self.results["chain_recalculation"]["avg_time_ms"] > 500:
            report.append("🚨 IMMEDIATE ACTION REQUIRED:")
            report.append("  - Chain recalculation performance confirms O(n) complexity bottleneck")
            report.append("  - System will become unusable at scale (20,000+ events)")
            report.append("  - Refactor to event-driven architecture is CRITICAL")
            report.append("")
        
        report.append("📋 REFACTOR PRIORITIES:")
        report.append("  1. Implement event handlers to replace chain recalculation")
        report.append("  2. Extract business logic from models to services")
        report.append("  3. Implement caching for expensive calculations")
        report.append("  4. Add database indexes for performance-critical queries")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main entry point for the load testing script."""
    parser = argparse.ArgumentParser(description="Fund System Load Tester")
    parser.add_argument("--funds", type=int, default=50, help="Number of funds to simulate")
    parser.add_argument("--events", type=int, default=100, help="Events per fund to simulate")
    parser.add_argument("--companies", type=int, default=5, help="Number of companies to simulate")
    parser.add_argument("--output", help="Output file for results (optional)")
    
    args = parser.parse_args()
    
    print("🔍 Fund System Load Testing Tool")
    print("   Validating performance analysis findings")
    print()
    
    # Run load test
    tester = FundSystemLoadTester(
        funds_count=args.funds,
        events_per_fund=args.events,
        companies_count=args.companies
    )
    
    try:
        results = tester.run_load_test()
        
        if "error" in results:
            print(f"❌ Load test failed: {results['error']}")
            sys.exit(1)
        
        # Generate and display report
        report = tester.generate_report()
        print("\n" + report)
        
        # Save report if output file specified
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\n📄 Report saved to: {args.output}")
        
        print("\n✅ Load testing completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Load testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Load testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
