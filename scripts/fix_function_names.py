#!/usr/bin/env python3
"""
Fix function names that were incorrectly changed by the enum script.

This script reverts function names that should not have been changed to uppercase.
"""

import os
import re
from pathlib import Path

# Define the function name mappings to revert
FUNCTION_NAME_MAPPINGS = {
    'calculate_NAV_BASED_capital_gains': 'calculate_nav_based_capital_gains',
    'calculate_cost_based_capital_gains': 'calculate_cost_based_capital_gains',
}

def fix_file(file_path: Path) -> bool:
    """Fix function names in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all mappings
        for old_name, new_name in FUNCTION_NAME_MAPPINGS.items():
            content = content.replace(old_name, new_name)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all test files."""
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / 'tests'
    
    if not tests_dir.exists():
        print(f"❌ Tests directory not found: {tests_dir}")
        return
    
    print("🔧 Fixing function names that were incorrectly changed...")
    print(f"📁 Scanning directory: {tests_dir}")
    
    # Find all Python test files
    test_files = list(tests_dir.rglob("*.py"))
    print(f"📋 Found {len(test_files)} Python files")
    
    fixed_count = 0
    for test_file in test_files:
        if fix_file(test_file):
            fixed_count += 1
    
    print(f"\n🎉 Summary:")
    print(f"   Total files processed: {len(test_files)}")
    print(f"   Files updated: {fixed_count}")
    print(f"   Files unchanged: {len(test_files) - fixed_count}")
    
    if fixed_count > 0:
        print(f"\n✅ Successfully fixed {fixed_count} test files!")
        print(f"   Function names should now be correct.")
    else:
        print(f"\n⏭️  No test files needed function name fixes.")

if __name__ == "__main__":
    main()


