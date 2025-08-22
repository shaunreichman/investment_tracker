#!/usr/bin/env python3
"""
Test runner script that runs the main test and compares output with baseline.
"""

import os
import sys
import subprocess
import difflib
from pathlib import Path

def run_test_and_compare():
    """Run the main test and compare with baseline."""
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"
    output_dir = tests_dir / "output"
    
    # Define file paths
    baseline_file = output_dir / "test_main_output_baseline.txt"
    new_output_file = output_dir / "test_main_output_new.txt"
    
    print("🧪 Running system test and comparing with baseline...")
    print(f"Baseline file: {baseline_file}")
    print(f"New output file: {new_output_file}")
    
    # Check if baseline exists
    if not baseline_file.exists():
        print("❌ Error: Baseline file not found!")
        print(f"Please ensure {baseline_file} exists.")
        return False
    
    # Run the test and save output
    print("\n📝 Running test and saving output...")
    try:
        # Set PYTHONPATH to include the project root
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root)
        
        result = subprocess.run([
            sys.executable, 
            str(tests_dir / "test_main.py"),
            "--output-file", str(new_output_file)
        ], capture_output=True, text=True, cwd=project_root, env=env)
        
        if result.returncode != 0:
            print("❌ Test failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False
    
    # Compare with baseline
    print("\n🔍 Comparing with baseline...")
    try:
        with open(baseline_file, 'r') as f:
            baseline_content = f.readlines()
        
        with open(new_output_file, 'r') as f:
            new_content = f.readlines()
        
        # Compare files
        if baseline_content == new_content:
            print("✅ Test output matches baseline exactly!")
            return True
        else:
            print("⚠️  Test output differs from baseline!")
            print("\n📊 Differences found:")
            
            # Show a summary of differences
            diff = list(difflib.unified_diff(
                baseline_content, new_content,
                fromfile=str(baseline_file),
                tofile=str(new_output_file),
                lineterm=''
            ))
            
            # Print first 20 lines of diff
            for i, line in enumerate(diff[:20]):
                print(line)
            
            if len(diff) > 20:
                print(f"... and {len(diff) - 20} more lines")
            
            print(f"\n💡 To see full diff: diff {baseline_file} {new_output_file}")
            return False
            
    except Exception as e:
        print(f"❌ Error comparing files: {e}")
        return False

def main():
    """Main function."""
    success = run_test_and_compare()
    
    if success:
        print("\n🎉 All tests passed! System is working as expected.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Please investigate the differences.")
        sys.exit(1)

if __name__ == "__main__":
    main() 