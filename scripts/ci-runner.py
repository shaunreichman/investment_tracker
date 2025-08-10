#!/usr/bin/env python3
"""
CI Runner Script for Backend Testing Suite
Manages test execution, coverage reporting, and quality gate enforcement
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

class CIRunner:
    def __init__(self, profile: str = "fast"):
        self.profile = profile
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "profile": profile,
            "start_time": time.time(),
            "tests": {},
            "coverage": {},
            "quality_gates": {}
        }
        
    def run_tests(self, markers: Optional[str] = None, workers: Optional[int] = None) -> bool:
        """Run the test suite with specified configuration"""
        print(f"🚀 Running tests with profile: {self.profile}")
        
        # First run tests without coverage to check if they pass
        test_cmd = [
            "python", "-m", "pytest",
            "--tb=short",
            "--durations=10"
        ]
        
        if markers:
            test_cmd.extend(["-m", markers])
            self._last_markers = markers
            
        if workers and workers > 1:
            test_cmd.extend(["-n", str(workers), "--dist=loadfile"])
            
        print(f"Running tests: {' '.join(test_cmd)}")
        
        start_time = time.time()
        result = subprocess.run(test_cmd, cwd=self.project_root, capture_output=True, text=True)
        end_time = time.time()
        
        self.results["tests"] = {
            "return_code": result.returncode,
            "execution_time": end_time - start_time,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
        success = result.returncode == 0
        print(f"✅ Tests completed in {end_time - start_time:.2f}s - {'PASSED' if success else 'FAILED'}")
        
        if not success:
            print("❌ Test failures detected:")
            print(result.stdout[-1000:])  # Show last 1000 chars of output
            if result.stderr:
                print("Errors:")
                print(result.stderr[-500:])  # Show last 500 chars of stderr
        
        return success
        
    def check_coverage(self) -> bool:
        """Check coverage and generate reports"""
        print("📊 Checking coverage...")
        
        # First run coverage to collect data with the same markers as the test run
        collect_cmd = ["coverage", "run", "-m", "pytest", "-q"]
        if hasattr(self, '_last_markers') and self._last_markers:
            collect_cmd.extend(["-m", self._last_markers])
        result = subprocess.run(collect_cmd, cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Failed to collect coverage data")
            return False
        
        # Now check coverage report
        cmd = ["coverage", "report", "--show-missing"]
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse coverage output to extract percentage
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'TOTAL' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            coverage_percent = float(parts[-1].rstrip('%'))
                            self.results["coverage"]["percentage"] = coverage_percent
                            self.results["coverage"]["passed_threshold"] = coverage_percent >= 70
                            print(f"📈 Coverage: {coverage_percent:.2f}% - {'PASSED' if coverage_percent >= 70 else 'FAILED'}")
                            return coverage_percent >= 70
                        except ValueError:
                            pass
                            
        print("❌ Could not determine coverage percentage")
        return False
        
    def generate_coverage_html(self) -> bool:
        """Generate HTML coverage report"""
        print("🌐 Generating HTML coverage report...")
        
        cmd = ["coverage", "html", "--directory=htmlcov"]
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        success = result.returncode == 0
        if success:
            print("✅ HTML coverage report generated")
        else:
            print("❌ Failed to generate HTML coverage report")
            
        return success
        
    def enforce_quality_gates(self) -> bool:
        """Enforce quality gates based on test results and coverage"""
        print("🚦 Enforcing quality gates...")
        
        tests_passed = self.results["tests"]["return_code"] == 0
        coverage_passed = self.results["coverage"].get("passed_threshold", False)
        execution_time = self.results["tests"]["execution_time"]
        
        # Quality gate thresholds
        max_time_fast = 120  # 2 minutes
        max_time_full = 300  # 5 minutes
        
        time_threshold = max_time_fast if self.profile == "fast" else max_time_full
        time_passed = execution_time <= time_threshold
        
        self.results["quality_gates"] = {
            "tests_passed": tests_passed,
            "coverage_passed": coverage_passed,
            "time_passed": time_passed,
            "execution_time": execution_time,
            "time_threshold": time_threshold
        }
        
        all_gates_passed = tests_passed and coverage_passed and time_passed
        
        print(f"📋 Quality Gates:")
        print(f"  ✅ Tests: {'PASSED' if tests_passed else 'FAILED'}")
        print(f"  ✅ Coverage: {'PASSED' if coverage_passed else 'FAILED'}")
        print(f"  ✅ Time: {'PASSED' if time_passed else 'execution_time:.2f}s/{time_threshold}s'}")
        print(f"  🎯 Overall: {'PASSED' if all_gates_passed else 'FAILED'}")
        
        return all_gates_passed
        
    def save_results(self) -> None:
        """Save results to JSON file for CI artifacts"""
        results_file = self.project_root / "ci-results.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
            
        print(f"💾 Results saved to {results_file}")
        
    def run(self) -> bool:
        """Main execution flow"""
        print(f"🎯 CI Runner starting with profile: {self.profile}")
        
        # Determine test configuration based on profile
        if self.profile == "fast":
            markers = "not slow"
            workers = 4
        elif self.profile == "full":
            markers = None
            workers = 2
        else:  # nightly
            markers = None
            workers = 1
            
        # Run tests
        tests_success = self.run_tests(markers, workers)
        
        # Check coverage
        coverage_success = self.check_coverage()
        
        # Generate HTML report
        self.generate_coverage_html()
        
        # Enforce quality gates
        quality_gates_passed = self.enforce_quality_gates()
        
        # Save results
        self.save_results()
        
        # Final status
        overall_success = tests_success and coverage_success and quality_gates_passed
        
        print(f"\n🎉 CI Run Complete!")
        print(f"Profile: {self.profile}")
        print(f"Overall Status: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        
        return overall_success

def main():
    parser = argparse.ArgumentParser(description="CI Runner for Backend Testing Suite")
    parser.add_argument("--profile", choices=["fast", "full", "nightly"], default="fast",
                       help="Test profile to run")
    
    args = parser.parse_args()
    
    runner = CIRunner(args.profile)
    success = runner.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
