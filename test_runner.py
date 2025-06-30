#!/usr/bin/env python3
"""
Test runner that runs the comprehensive investment tracker test.
The comprehensive test already handles existing data properly.
"""
import subprocess
import sys

# Run the comprehensive test (it handles existing data properly)
print("\n=== RUNNING COMPREHENSIVE TEST ===\n")
subprocess.run([sys.executable, 'test_investment_tracker.py'], check=True) 