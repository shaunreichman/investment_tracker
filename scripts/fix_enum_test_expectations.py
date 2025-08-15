#!/usr/bin/env python3
"""
Fix enum test expectations script.

This script updates all test files to expect uppercase enum values (e.g., 'ACTIVE' instead of 'active')
to match the new enum architecture.
"""

import os
import re
from pathlib import Path

# Define the enum value mappings
ENUM_VALUE_MAPPINGS = {
    # Fund Status
    "'active'": "'ACTIVE'",
    "'suspended'": "'SUSPENDED'", 
    "'realized'": "'REALIZED'",
    "'completed'": "'COMPLETED'",
    
    # Fund Type
    "'cost_based'": "'COST_BASED'",
    "'nav_based'": "'NAV_BASED'",
    
    # Event Type
    "'capital_call'": "'CAPITAL_CALL'",
    "'return_of_capital'": "'RETURN_OF_CAPITAL'",
    "'distribution'": "'DISTRIBUTION'",
    "'unit_purchase'": "'UNIT_PURCHASE'",
    "'unit_sale'": "'UNIT_SALE'",
    "'nav_update'": "'NAV_UPDATE'",
    
    # Distribution Type
    "'income'": "'INCOME'",
    "'dividend_franked'": "'DIVIDEND_FRANKED'",
    "'dividend_unfranked'": "'DIVIDEND_UNFRANKED'",
    "'interest'": "'INTEREST'",
    "'rent'": "'RENT'",
    "'capital_gain'": "'CAPITAL_GAIN'",
    
    # Cash Flow Direction
    "'inflow'": "'INFLOW'",
    "'outflow'": "'OUTFLOW'",
    
    # Tax Payment Type
    "'interest'": "'INTEREST'",
    "'capital_gains_tax'": "'CAPITAL_GAINS_TAX'",
    "'dividend'": "'DIVIDEND'",
    "'dividends_franked_tax'": "'DIVIDENDS_FRANKED_TAX'",
    "'non_resident_interest_withholding'": "'NON_RESIDENT_INTEREST_WITHHOLDING'",
    
    # Group Type
    "'interest_withholding'": "'INTEREST_WITHHOLDING'",
    "'tax_statement'": "'TAX_STATEMENT'",
    
    # String literals without quotes (for regex patterns)
    'active': 'ACTIVE',
    'cost_based': 'COST_BASED',
    'capital_call': 'CAPITAL_CALL',
    'inflow': 'INFLOW',
    'outflow': 'OUTFLOW',
    'nav_based': 'NAV_BASED',
    'nav_based fund': 'NAV_BASED fund',
    'cost_based fund': 'COST_BASED fund',
}

def fix_file(file_path: Path) -> bool:
    """Fix enum values in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all mappings
        for old_value, new_value in ENUM_VALUE_MAPPINGS.items():
            content = content.replace(old_value, new_value)
        
        # Additional regex-based fixes for more complex patterns
        # Fix regex patterns in test assertions
        content = re.sub(r"match=\"Event requires (\w+)_based fund\"", r"match=\"Event requires \1_BASED fund\"", content)
        content = re.sub(r"match=\"Event requires (\w+)_based fund\"", r"match=\"Event requires \1_BASED fund\"", content)
        
        # Fix test data creation
        content = re.sub(r"'event_type': '(\w+)'", r"'event_type': '\1'", content)
        
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
    
    print("🔧 Fixing enum test expectations...")
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
        print(f"\n✅ Successfully updated {fixed_count} test files to use uppercase enum values!")
        print(f"   The new enum architecture should now work correctly with all tests.")
    else:
        print(f"\n⏭️  No test files needed updates.")

if __name__ == "__main__":
    main()
