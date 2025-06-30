#!/usr/bin/env python3
"""
Analyze tax statement differences in detail and provide specific recommendations
for handling discrepancies between actual distributions and tax statements.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, TaxStatement, EventType, DistributionType

def get_financial_year_dates(financial_year):
    """Convert financial year string to start and end dates (Australian FY)."""
    start_year = int(financial_year.split('-')[0])
    start_date = date(start_year, 7, 1)
    end_date = date(start_year + 1, 6, 30)
    return start_date, end_date

def analyze_tax_differences():
    """Analyze tax differences and provide specific recommendations."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("DETAILED TAX DIFFERENCE ANALYSIS")
    print("=" * 80)
    
    # Get all funds
    funds = session.query(Fund).all()
    
    for fund in funds:
        print(f"\nFUND: {fund.name}")
        print("=" * 80)
        
        # Get all tax statements for this fund
        tax_statements = session.query(TaxStatement).filter(
            TaxStatement.fund_id == fund.id
        ).order_by(TaxStatement.financial_year).all()
        
        if not tax_statements:
            print("No tax statements found for this fund.")
            continue
        
        for tax_statement in tax_statements:
            print(f"\nFINANCIAL YEAR: {tax_statement.financial_year}")
            print("-" * 50)
            
            # Get financial year dates
            fy_start, fy_end = get_financial_year_dates(tax_statement.financial_year)
            
            # Get actual distributions for this financial year
            distributions = session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id,
                FundEvent.event_type == EventType.DISTRIBUTION,
                FundEvent.event_date >= fy_start,
                FundEvent.event_date <= fy_end
            ).order_by(FundEvent.event_date).all()
            
            # Calculate totals from actual distributions
            actual_gross_income = sum(d.amount for d in distributions)
            actual_tax_withheld = sum(d.tax_withheld for d in distributions)
            actual_net_income = actual_gross_income - actual_tax_withheld
            
            # Get tax statement values
            statement_gross_income = tax_statement.gross_interest_income
            statement_tax_withheld = tax_statement.tax_withheld
            statement_net_income = tax_statement.net_interest_income
            
            # Calculate differences
            gross_diff = actual_gross_income - statement_gross_income
            tax_diff = actual_tax_withheld - statement_tax_withheld
            net_diff = actual_net_income - statement_net_income
            
            # Display detailed analysis
            print(f"PERIOD: {fy_start} to {fy_end}")
            print()
            
            print("DETAILED BREAKDOWN:")
            print("-" * 30)
            print(f"Tax Statement Gross:     ${statement_gross_income:>10,.2f}")
            print(f"Actual Distributions:    ${actual_gross_income:>10,.2f}")
            print(f"Difference:              ${gross_diff:>10,.2f}")
            print(f"Difference %:            {(gross_diff/statement_gross_income*100 if statement_gross_income > 0 else 0):>10.2f}%")
            print()
            print(f"Tax Statement Tax:       ${statement_tax_withheld:>10,.2f}")
            print(f"Actual Tax Withheld:     ${actual_tax_withheld:>10,.2f}")
            print(f"Difference:              ${tax_diff:>10,.2f}")
            print(f"Difference %:            {(tax_diff/statement_tax_withheld*100 if statement_tax_withheld > 0 else 0):>10.2f}%")
            
            # Analyze the type of difference
            print()
            print("DIFFERENCE ANALYSIS:")
            print("-" * 30)
            
            if abs(gross_diff) < 0.01:
                print("✓ PERFECT MATCH - No action needed")
            elif abs(gross_diff) < 10:
                print("⚠ MINOR DIFFERENCE - Likely rounding or timing")
                print("   Recommendation: Use tax statement figures for tax reporting")
                print("   Reason: Small differences are common due to rounding")
            elif abs(gross_diff) < 100:
                print("⚠ MODERATE DIFFERENCE - Investigate timing or rates")
                print("   Recommendation: Check distribution dates and tax rates")
                print("   Possible causes: Different tax rates, timing differences")
            else:
                print("⚠ SIGNIFICANT DIFFERENCE - Requires investigation")
                print("   Recommendation: Contact fund manager for clarification")
                print("   Possible causes: Missing distributions, incorrect tax rates")
            
            # Check for specific patterns
            print()
            print("SPECIFIC PATTERNS:")
            print("-" * 30)
            
            # Pattern 1: Tax statement higher than actual
            if gross_diff < 0:
                print("• Tax statement exceeds actual distributions")
                print("  Possible reasons:")
                print("    - Accrued income not yet distributed")
                print("    - Fund includes income from other sources")
                print("    - Timing differences in distribution dates")
                print("    - Fund manager uses different calculation method")
            
            # Pattern 2: Actual higher than tax statement
            elif gross_diff > 0:
                print("• Actual distributions exceed tax statement")
                print("  Possible reasons:")
                print("    - Distributions received in different FY")
                print("    - Fund manager hasn't updated tax statement")
                print("    - Different income classification")
                print("    - Timing differences in payment vs. accrual")
            
            # Pattern 3: Tax withholding differences
            if abs(tax_diff) > 0.01:
                print()
                print("• Tax withholding differences detected")
                print("  Possible reasons:")
                print("    - Different withholding rates applied")
                print("    - Additional tax credits or offsets")
                print("    - Foreign tax credits")
                print("    - Fund manager adjustments")
            
            # Provide specific recommendations
            print()
            print("RECOMMENDED ACTIONS:")
            print("-" * 30)
            
            if abs(gross_diff) < 10:
                print("1. ACCEPT DIFFERENCE:")
                print("   • Use tax statement figures for tax reporting")
                print("   • Document difference in notes")
                print("   • No further action required")
            elif abs(gross_diff) < 100:
                print("1. INVESTIGATE DIFFERENCE:")
                print("   • Check distribution dates vs. financial year")
                print("   • Verify tax withholding rates")
                print("   • Review fund manager's calculation method")
                print("2. DECISION POINT:")
                print("   • If timing difference: Use tax statement")
                print("   • If rate difference: Use actual distributions")
                print("   • Document reasoning in notes")
            else:
                print("1. IMMEDIATE ACTION REQUIRED:")
                print("   • Contact fund manager for clarification")
                print("   • Request detailed breakdown of tax statement")
                print("   • Check for missing or incorrect distributions")
                print("2. DOCUMENTATION:")
                print("   • Record all communications with fund manager")
                print("   • Note any explanations provided")
                print("   • Decide on approach based on fund manager response")
            
            # Show individual distribution analysis
            if distributions:
                print()
                print("INDIVIDUAL DISTRIBUTION ANALYSIS:")
                print("-" * 40)
                print("Date       | Amount    | Tax Rate | Tax Amount | Tax %")
                print("-" * 40)
                
                for dist in distributions:
                    tax_rate = (dist.tax_withheld / dist.amount * 100) if dist.amount > 0 else 0
                    print(f"{dist.event_date} | ${dist.amount:>8,.2f} | {dist.tax_withholding_rate:>8.1f}% | ${dist.tax_withheld:>9,.2f} | {tax_rate:>5.1f}%")
                
                # Check for consistency in tax rates
                tax_rates = [d.tax_withholding_rate for d in distributions if d.amount > 0]
                if len(set(tax_rates)) > 1:
                    print()
                    print("⚠ INCONSISTENT TAX RATES DETECTED:")
                    for rate in sorted(set(tax_rates)):
                        count = tax_rates.count(rate)
                        print(f"  • {rate}% rate used in {count} distribution(s)")
    
    session.close()

if __name__ == "__main__":
    analyze_tax_differences() 