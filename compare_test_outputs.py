#!/usr/bin/env python3
"""
Compare old and new system test outputs to identify differences.
"""

import re
from pathlib import Path

def parse_irr_values(text):
    """Extract IRR values from test output."""
    irr_pattern = r'IRR: ([\d.]+)%'
    after_tax_pattern = r'After-tax IRR: ([\d.]+)%'
    real_pattern = r'Real IRR: ([\d.]+)%'
    
    irr_matches = re.findall(irr_pattern, text)
    after_tax_matches = re.findall(after_tax_pattern, text)
    real_matches = re.findall(real_pattern, text)
    
    return {
        'irr': [float(x) for x in irr_matches],
        'after_tax_irr': [float(x) for x in after_tax_matches],
        'real_irr': [float(x) for x in real_matches]
    }

def parse_fund_equity(text):
    """Extract fund equity values from test output."""
    equity_pattern = r'(\w+(?:\s+\w+)*): equity=\$([\d,.-]+), avg=\$([\d,.-]+)'
    matches = re.findall(equity_pattern, text)
    
    return {name.strip(): {'equity': equity, 'avg': avg} for name, equity, avg in matches}

def parse_cash_flow_counts(text):
    """Count cash flows in each section."""
    sections = ['IRR Cash Flows', 'After-tax IRR Cash Flows', 'Real IRR Cash Flows']
    counts = {}
    
    for section in sections:
        # Find the section and count lines until next section or end
        pattern = rf'--- {section} ---\n(.*?)(?=\n\s*---|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            lines = [line.strip() for line in match.group(1).split('\n') if line.strip()]
            counts[section] = len(lines)
        else:
            counts[section] = 0
    
    return counts

def main():
    # Read the output files
    old_output = Path('system_test_output_old.txt').read_text()
    new_output = Path('system_test_output_new.txt').read_text()
    
    print("=== COMPARISON OF OLD vs NEW SYSTEM TEST OUTPUTS ===\n")
    
    # Compare IRR values
    print("1. IRR VALUES COMPARISON:")
    print("-" * 50)
    
    old_irr = parse_irr_values(old_output)
    new_irr = parse_irr_values(new_output)
    
    print("OLD SYSTEM:")
    for i, (irr, after_tax, real) in enumerate(zip(old_irr['irr'], old_irr['after_tax_irr'], old_irr['real_irr'])):
        print(f"  Fund {i+1}: IRR={irr}%, After-tax={after_tax}%, Real={real}%")
    
    print("\nNEW SYSTEM:")
    for i, (irr, after_tax, real) in enumerate(zip(new_irr['irr'], new_irr['after_tax_irr'], new_irr['real_irr'])):
        print(f"  Fund {i+1}: IRR={irr}%, After-tax={after_tax}%, Real={real}%")
    
    # Compare fund equity values
    print("\n\n2. FUND EQUITY COMPARISON:")
    print("-" * 50)
    
    old_equity = parse_fund_equity(old_output)
    new_equity = parse_fund_equity(new_output)
    
    print("OLD SYSTEM:")
    for fund_name, values in old_equity.items():
        print(f"  {fund_name}: equity=${values['equity']}, avg=${values['avg']}")
    
    print("\nNEW SYSTEM:")
    for fund_name, values in new_equity.items():
        print(f"  {fund_name}: equity=${values['equity']}, avg=${values['avg']}")
    
    # Compare cash flow counts
    print("\n\n3. CASH FLOW COUNTS COMPARISON:")
    print("-" * 50)
    
    old_counts = parse_cash_flow_counts(old_output)
    new_counts = parse_cash_flow_counts(new_output)
    
    print("OLD SYSTEM:")
    for section, count in old_counts.items():
        print(f"  {section}: {count} cash flows")
    
    print("\nNEW SYSTEM:")
    for section, count in new_counts.items():
        print(f"  {section}: {count} cash flows")
    
    # Check for key differences in cash flow amounts
    print("\n\n4. CASH FLOW AMOUNT COMPARISON:")
    print("-" * 50)
    
    # Extract first few cash flows from each system - updated pattern for new format
    old_cashflows = re.findall(r'(\d+):\s+([-\d,]+\.\d+)\s+(\w+)\s+\|', old_output)
    new_cashflows = re.findall(r'(\d+):\s+([-\d,]+\.\d+)\s+(\w+)\s+\|', new_output)
    
    print("OLD SYSTEM (first 5 cash flows):")
    for i, (num, amount, event_type) in enumerate(old_cashflows[:5]):
        print(f"  {num}: ${amount} {event_type}")
    
    print("\nNEW SYSTEM (first 5 cash flows):")
    for i, (num, amount, event_type) in enumerate(new_cashflows[:5]):
        print(f"  {num}: ${amount} {event_type}")
    
    # Check for missing FY debt cost events
    print("\n\n5. FY DEBT COST EVENTS:")
    print("-" * 50)
    
    old_fy_events = old_output.count('fy_debt_cost')
    new_fy_events = new_output.count('fy_debt_cost')
    
    print(f"OLD SYSTEM: {old_fy_events} FY debt cost events")
    print(f"NEW SYSTEM: {new_fy_events} FY debt cost events")
    
    if old_fy_events != new_fy_events:
        print("⚠️  DIFFERENCE DETECTED: FY debt cost events count mismatch!")
    
    # Check for missing daily risk-free interest charges
    print("\n\n6. DAILY RISK-FREE INTEREST CHARGES:")
    print("-" * 50)
    
    old_daily = old_output.count('daily_risk_free_interest_charge')
    new_daily = new_output.count('daily_risk_free_interest_charge')
    
    print(f"OLD SYSTEM: {old_daily} daily risk-free interest charges")
    print(f"NEW SYSTEM: {new_daily} daily risk-free interest charges")
    
    if old_daily != new_daily:
        print("⚠️  DIFFERENCE DETECTED: Daily interest charges count mismatch!")

if __name__ == '__main__':
    main() 