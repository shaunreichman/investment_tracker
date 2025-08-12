#!/usr/bin/env python3
"""
Test categorization script to help organize tests by speed and type.
This helps developers choose the right test suite for their needs.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def categorize_tests() -> Dict[str, List[str]]:
    """Categorize tests by type and estimated speed."""
    
    categories = {
        "fast": [],      # < 1 second per test
        "medium": [],    # 1-3 seconds per test  
        "slow": [],      # > 3 seconds per test
        "unit": [],
        "integration": [],
        "performance": [],
        "api": [],
        "smoke": []
    }
    
    tests_dir = Path("tests")
    
    # Categorize by directory structure
    for test_file in tests_dir.rglob("*.py"):
        if test_file.name.startswith("test_"):
            rel_path = str(test_file.relative_to(tests_dir))
            
            # Categorize by location
            if "unit" in rel_path:
                categories["unit"].append(rel_path)
                categories["fast"].append(rel_path)
            elif "integration" in rel_path:
                categories["integration"].append(rel_path)
                categories["medium"].append(rel_path)
            elif "performance" in rel_path:
                categories["performance"].append(rel_path)
                categories["slow"].append(rel_path)
            elif "api" in rel_path:
                categories["api"].append(rel_path)
                categories["medium"].append(rel_path)
            elif "smoke" in rel_path or "factories" in rel_path:
                categories["smoke"].append(rel_path)
                categories["fast"].append(rel_path)
            else:
                # Default categorization
                if "test_" in rel_path and "test_" not in rel_path.split("/")[0]:
                    categories["unit"].append(rel_path)
                    categories["fast"].append(rel_path)
                else:
                    categories["medium"].append(rel_path)
    
    return categories

def print_test_categories():
    """Print organized test categories with recommendations."""
    
    print("🧪 TEST SUITE ORGANIZATION & RECOMMENDATIONS")
    print("=" * 60)
    
    categories = categorize_tests()
    
    print("\n🚀 FAST TESTS (< 1 second each) - Run during development:")
    print("-" * 50)
    for test in sorted(categories["fast"]):
        print(f"  ✅ {test}")
    
    print(f"\n📊 Total Fast Tests: {len(categories['fast'])}")
    
    print("\n⚡ MEDIUM TESTS (1-3 seconds each) - Run before commits:")
    print("-" * 50)
    for test in sorted(categories["medium"]):
        print(f"  🔄 {test}")
    
    print(f"\n📊 Total Medium Tests: {len(categories['medium'])}")
    
    print("\n🐌 SLOW TESTS (> 3 seconds each) - Run in CI/CD:")
    print("-" * 50)
    for test in sorted(categories["slow"]):
        print(f"  🐌 {test}")
    
    print(f"\n📊 Total Slow Tests: {len(categories['slow'])}")
    
    print("\n🎯 RECOMMENDED TEST COMMANDS:")
    print("-" * 50)
    print("  # Fast feedback during development:")
    print("  pytest -m fast -v")
    print("  pytest tests/unit/ -v")
    print("  pytest tests/test_smoke.py -v")
    
    print("\n  # Pre-commit validation:")
    print("  pytest -m 'not slow' -v")
    print("  pytest tests/unit/ tests/api/ -v")
    
    print("\n  # Full CI/CD suite:")
    print("  pytest tests/ -v")
    
    print("\n  # Performance testing only:")
    print("  pytest tests/performance/ -v")
    print("  pytest tests/integration/test_flag_based_performance.py -v")

if __name__ == "__main__":
    print_test_categories()
