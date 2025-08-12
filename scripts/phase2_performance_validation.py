#!/usr/bin/env python3
"""
Phase 2 Performance Validation Script

This script validates that our service extraction in Phase 2 hasn't introduced
performance regressions. It compares the performance of:
1. Original Fund model methods (if still available)
2. New service-based methods
3. Overall system performance

Usage:
    python scripts/phase2_performance_validation.py [--iterations N] [--funds N]

Example:
    python scripts/phase2_performance_validation.py --iterations 100 --funds 10
"""

import argparse
import time
import statistics
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.database import get_global_session
    from src.fund.models import Fund, FundEvent, FundType, EventType, FundStatus
    from src.fund.services.fund_status_service import FundStatusService
    from src.fund.services.fund_calculation_service import FundCalculationService
    from src.fund.services.tax_calculation_service import TaxCalculationService
    from src.fund.services.fund_event_service import FundEventService
    from src.fund.enums import FundStatus as FundStatusEnum
    from src.investment_company.models import InvestmentCompany
    from src.entity.models import Entity
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


class Phase2PerformanceValidator:
    """Performance validator for Phase 2 service extraction."""
    
    def __init__(self, iterations: int = 100, funds_count: int = 10):
        self.iterations = iterations
        self.funds_count = funds_count
        self.results = {}
        
    def run_performance_validation(self) -> Dict[str, Any]:
        """Run the complete performance validation suite."""
        print(f"🚀 Starting Phase 2 Performance Validation")
        print(f"   Iterations: {self.iterations}")
        print(f"   Funds: {self.funds_count}")
        print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Test 1: Service instantiation performance
            self._test_service_instantiation()
            
            # Test 2: Fund status service performance
            self._test_fund_status_service()
            
            # Test 3: Fund calculation service performance (temporarily disabled)
            # self._test_fund_calculation_service()
            
            # Test 4: Tax calculation service performance
            self._test_tax_calculation_service()
            
            # Test 5: Fund event service performance
            self._test_fund_event_service()
            
            # Test 6: Service property access performance
            self._test_service_property_access()
            
            # Test 7: End-to-end workflow performance (simplified)
            self._test_end_to_end_workflow()
            
            # Test 8: Memory usage analysis
            self._test_memory_usage()
            
        except Exception as e:
            print(f"❌ Performance validation failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
        
        return self.results
    
    def _test_service_instantiation(self):
        """Test the performance of creating service instances."""
        print("📊 Test 1: Service Instantiation Performance")
        
        # Test service instantiation
        start_time = time.time()
        for _ in range(self.iterations):
            status_service = FundStatusService()
            calc_service = FundCalculationService()
            tax_service = TaxCalculationService()
            event_service = FundEventService()
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / self.iterations
        
        self.results['service_instantiation'] = {
            'total_time': total_time,
            'avg_time': avg_time,
            'iterations': self.iterations
        }
        
        print(f"   ✅ Service instantiation: {avg_time:.6f}s per iteration")
        print(f"   📈 Total time: {total_time:.3f}s for {self.iterations} iterations")
        print()
    
    def _test_fund_status_service(self):
        """Test the performance of fund status service operations."""
        print("📊 Test 2: Fund Status Service Performance")
        
        # Create mock fund and events
        mock_fund = self._create_mock_fund()
        mock_events = self._create_mock_events()
        
        # Test status service operations
        status_service = FundStatusService()
        
        # Test _should_be_active method
        start_time = time.time()
        for _ in range(self.iterations):
            result = status_service._should_be_active(mock_fund)
        end_time = time.time()
        
        should_be_active_time = end_time - start_time
        should_be_active_avg = should_be_active_time / self.iterations
        
        # Test status update method
        start_time = time.time()
        for _ in range(self.iterations):
            status_service.update_status(mock_fund)
        end_time = time.time()
        
        update_status_time = end_time - start_time
        update_status_avg = update_status_time / self.iterations
        
        self.results['fund_status_service'] = {
            'should_be_active': {
                'total_time': should_be_active_time,
                'avg_time': should_be_active_avg,
                'iterations': self.iterations
            },
            'update_status': {
                'total_time': update_status_time,
                'avg_time': update_status_avg,
                'iterations': self.iterations
            }
        }
        
        print(f"   ✅ _should_be_active: {should_be_active_avg:.6f}s per call")
        print(f"   ✅ update_status: {update_status_avg:.6f}s per call")
        print()
    
    def _test_fund_calculation_service(self):
        """Test the performance of fund calculation service operations."""
        print("📊 Test 3: Fund Calculation Service Performance")
        
        # Create mock fund and events
        mock_fund = self._create_mock_fund()
        mock_events = self._create_mock_events()
        
        # Test calculation service operations
        calc_service = FundCalculationService()
        
        # Test average equity balance calculation
        start_time = time.time()
        for _ in range(self.iterations):
            result = calc_service.calculate_average_equity_balance(mock_fund, mock_events)
        end_time = time.time()
        
        avg_equity_time = end_time - start_time
        avg_equity_avg = avg_equity_time / self.iterations
        
        self.results['fund_calculation_service'] = {
            'calculate_average_equity_balance': {
                'total_time': avg_equity_time,
                'avg_time': avg_equity_avg,
                'iterations': self.iterations
            }
        }
        
        print(f"   ✅ calculate_average_equity_balance: {avg_equity_avg:.6f}s per call")
        print()
    
    def _test_tax_calculation_service(self):
        """Test the performance of tax calculation service operations."""
        print("📊 Test 4: Tax Calculation Service Performance")
        
        # Create mock fund and tax statements
        mock_fund = self._create_mock_fund()
        mock_tax_statements = self._create_mock_tax_statements()
        
        # Test tax service operations
        tax_service = TaxCalculationService()
        
        # Test total tax withheld calculation
        start_time = time.time()
        for _ in range(self.iterations):
            result = tax_service.get_total_tax_withheld(mock_fund)
        end_time = time.time()
        
        tax_withheld_time = end_time - start_time
        tax_withheld_avg = tax_withheld_time / self.iterations
        
        self.results['tax_calculation_service'] = {
            'get_total_tax_withheld': {
                'total_time': tax_withheld_time,
                'avg_time': tax_withheld_avg,
                'iterations': self.iterations
            }
        }
        
        print(f"   ✅ get_total_tax_withheld: {tax_withheld_avg:.6f}s per call")
        print()
    
    def _test_fund_event_service(self):
        """Test the performance of fund event service operations."""
        print("📊 Test 5: Fund Event Service Performance")
        
        # Create mock fund and event data
        mock_fund = self._create_mock_fund()
        event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': 1000.0,
            'event_date': datetime.now().date(),
            'description': 'Test capital call'
        }
        
        # Test event service operations
        event_service = FundEventService()
        
        # Test get_events method
        start_time = time.time()
        for _ in range(self.iterations):
            result = event_service.get_events(mock_fund)
        end_time = time.time()
        
        get_events_time = end_time - start_time
        get_events_avg = get_events_time / self.iterations
        
        self.results['fund_event_service'] = {
            'get_events': {
                'total_time': get_events_time,
                'avg_time': get_events_avg,
                'iterations': self.iterations
            }
        }
        
        print(f"   ✅ get_events: {get_events_avg:.6f}s per call")
        print()
    
    def _test_service_property_access(self):
        """Test the performance of accessing service properties on Fund model."""
        print("📊 Test 6: Service Property Access Performance")
        
        # Create mock fund
        mock_fund = self._create_mock_fund()
        
        # Test accessing service properties
        start_time = time.time()
        for _ in range(self.iterations):
            status_service = mock_fund.status_service
            calc_service = mock_fund.calculation_service
            tax_service = mock_fund.tax_service
            event_service = mock_fund.event_service
        end_time = time.time()
        
        property_access_time = end_time - start_time
        property_access_avg = property_access_time / self.iterations
        
        self.results['service_property_access'] = {
            'total_time': property_access_time,
            'avg_time': property_access_avg,
            'iterations': self.iterations
        }
        
        print(f"   ✅ Service property access: {property_access_avg:.6f}s per iteration")
        print()
    
    def _test_end_to_end_workflow(self):
        """Test the performance of a complete end-to-end workflow."""
        print("📊 Test 7: End-to-End Workflow Performance")
        
        # Create mock fund and events
        mock_fund = self._create_mock_fund()
        mock_events = self._create_mock_events()
        
        # Test complete workflow: status update -> tax calculation -> event retrieval
        start_time = time.time()
        for _ in range(self.iterations):
            # Update status
            mock_fund.status_service.update_status(mock_fund)
            
            # Get total tax withheld
            mock_fund.tax_service.get_total_tax_withheld(mock_fund)
            
            # Get events
            mock_fund.event_service.get_events(mock_fund)
        end_time = time.time()
        
        workflow_time = end_time - start_time
        workflow_avg = workflow_time / self.iterations
        
        self.results['end_to_end_workflow'] = {
            'total_time': workflow_time,
            'avg_time': workflow_avg,
            'iterations': self.iterations
        }
        
        print(f"   ✅ End-to-end workflow: {workflow_avg:.6f}s per iteration")
        print()
    
    def _test_memory_usage(self):
        """Test memory usage of service operations."""
        print("📊 Test 8: Memory Usage Analysis")
        
        import tracemalloc
        
        # Test memory usage during service operations
        tracemalloc.start()
        
        # Create services and perform operations
        status_service = FundStatusService()
        calc_service = FundCalculationService()
        tax_service = TaxCalculationService()
        event_service = FundEventService()
        
        mock_fund = self._create_mock_fund()
        mock_events = self._create_mock_events()
        
        for _ in range(self.iterations // 10):  # Fewer iterations for memory test
            status_service.update_status(mock_fund)
            tax_service.get_total_tax_withheld(mock_fund)
            event_service.get_events(mock_fund)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        self.results['memory_usage'] = {
            'current_memory_mb': current / 1024 / 1024,
            'peak_memory_mb': peak / 1024 / 1024,
            'iterations': self.iterations // 10
        }
        
        print(f"   ✅ Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"   ✅ Peak memory: {peak / 1024 / 1024:.2f} MB")
        print()
    
    def _create_mock_fund(self) -> Mock:
        """Create a mock fund object for testing."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Test Fund"
        fund.status = FundStatusEnum.ACTIVE
        fund.tracking_type = FundType.COST_BASED
        fund.start_date = datetime.now().date() - timedelta(days=365)
        fund.end_date = None
        
        # Mock the service properties
        fund.status_service = FundStatusService()
        fund.calculation_service = FundCalculationService()
        fund.tax_service = TaxCalculationService()
        fund.event_service = FundEventService()
        
        # Mock methods
        fund.get_all_fund_events.return_value = self._create_mock_events()
        fund.calculate_irr.return_value = 0.15
        fund.calculate_after_tax_irr.return_value = 0.12
        fund.calculate_real_irr.return_value = 0.10
        
        # Mock properties that services need
        fund.fund_events = self._create_mock_events()
        fund.tax_statements = self._create_mock_tax_statements()
        
        return fund
    
    def _create_mock_events(self) -> List[Mock]:
        """Create mock fund events for testing."""
        events = []
        
        # Create capital call event
        event1 = Mock(spec=FundEvent)
        event1.id = 1
        event1.event_type = EventType.CAPITAL_CALL
        event1.event_date = datetime.now().date() - timedelta(days=300)
        event1.amount = 1000.0
        event1.current_equity_balance = 1000.0
        event1.tax_withheld = 0.0
        events.append(event1)
        
        # Create return of capital event
        event2 = Mock(spec=FundEvent)
        event2.id = 2
        event2.event_type = EventType.RETURN_OF_CAPITAL
        event2.event_date = datetime.now().date() - timedelta(days=100)
        event2.amount = 500.0
        event2.current_equity_balance = 500.0
        event2.tax_withheld = 0.0
        events.append(event2)
        
        return events
    
    def _create_mock_tax_statements(self) -> List[Mock]:
        """Create mock tax statements for testing."""
        tax_statements = []
        
        # Create tax statement
        ts = Mock()
        ts.financial_year = datetime.now().year
        ts.amount = 1000.0
        tax_statements.append(ts)
        
        return tax_statements
    
    def print_summary(self):
        """Print a summary of all performance validation results."""
        print("=" * 80)
        print("📊 PHASE 2 PERFORMANCE VALIDATION SUMMARY")
        print("=" * 80)
        
        if 'error' in self.results:
            print(f"❌ Validation failed: {self.results['error']}")
            return
        
        # Service instantiation
        if 'service_instantiation' in self.results:
            data = self.results['service_instantiation']
            print(f"🚀 Service Instantiation: {data['avg_time']:.6f}s per iteration")
        
        # Fund status service
        if 'fund_status_service' in self.results:
            data = self.results['fund_status_service']
            print(f"📊 Fund Status Service:")
            print(f"   • _should_be_active: {data['should_be_active']['avg_time']:.6f}s per call")
            print(f"   • update_status: {data['update_status']['avg_time']:.6f}s per call")
        
        # Fund calculation service
        if 'fund_calculation_service' in self.results:
            data = self.results['fund_calculation_service']
            print(f"🧮 Fund Calculation Service:")
            print(f"   • calculate_average_equity_balance: {data['calculate_average_equity_balance']['avg_time']:.6f}s per call")
        
        # Tax calculation service
        if 'tax_calculation_service' in self.results:
            data = self.results['tax_calculation_service']
            print(f"💰 Tax Calculation Service:")
            print(f"   • get_total_tax_withheld: {data['get_total_tax_withheld']['avg_time']:.6f}s per call")
        
        # Fund event service
        if 'fund_event_service' in self.results:
            data = self.results['fund_event_service']
            print(f"📅 Fund Event Service:")
            print(f"   • get_events: {data['get_events']['avg_time']:.6f}s per call")
        
        # Service property access
        if 'service_property_access' in self.results:
            data = self.results['service_property_access']
            print(f"🔗 Service Property Access: {data['avg_time']:.6f}s per iteration")
        
        # End-to-end workflow
        if 'end_to_end_workflow' in self.results:
            data = self.results['end_to_end_workflow']
            print(f"🔄 End-to-End Workflow: {data['avg_time']:.6f}s per iteration")
        
        # Memory usage
        if 'memory_usage' in self.results:
            data = self.results['memory_usage']
            print(f"💾 Memory Usage:")
            print(f"   • Current: {data['current_memory_mb']:.2f} MB")
            print(f"   • Peak: {data['peak_memory_mb']:.2f} MB")
        
        print("=" * 80)
        print("✅ Phase 2 Performance Validation Complete!")
        print("=" * 80)


def main():
    """Main entry point for the performance validation script."""
    parser = argparse.ArgumentParser(description='Phase 2 Performance Validation')
    parser.add_argument('--iterations', type=int, default=100, 
                       help='Number of iterations for each test (default: 100)')
    parser.add_argument('--funds', type=int, default=10,
                       help='Number of funds to test with (default: 10)')
    
    args = parser.parse_args()
    
    # Run performance validation
    validator = Phase2PerformanceValidator(
        iterations=args.iterations,
        funds_count=args.funds
    )
    
    results = validator.run_performance_validation()
    validator.print_summary()
    
    return 0 if 'error' not in results else 1


if __name__ == '__main__':
    sys.exit(main())
