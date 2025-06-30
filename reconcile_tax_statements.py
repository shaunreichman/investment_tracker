#!/usr/bin/env python3
"""
Reconcile tax statements with actual distributions for each fund and financial year.
Shows differences and provides suggestions for handling discrepancies.
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
    # Australian financial year runs from July 1 to June 30
    start_year = int(financial_year.split('-')[0])
    start_date = date(start_year, 7, 1)
    end_date = date(start_year + 1, 6, 30)
    return start_date, end_date

def reconcile_tax_statements():
    """Reconcile tax statements with actual distributions."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("TAX STATEMENT RECONCILIATION")
    print("=" * 80)
    
    # Get all funds
    funds = session.query(Fund).all()
    
    for fund in funds:
        print(f"\nFUND: {fund.name}")
        print("-" * 80)
        
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
            
            # Display reconciliation
            print(f"PERIOD: {fy_start} to {fy_end}")
            print()
            
            print("ACTUAL DISTRIBUTIONS:")
            print("-" * 30)
            if distributions:
                for dist in distributions:
                    print(f"  {dist.event_date}: ${dist.amount:,.2f} (Tax: ${dist.tax_withheld:,.2f})")
            else:
                print("  No distributions in this period")
            
            print()
            print("RECONCILIATION SUMMARY:")
            print("-" * 30)
            print(f"Actual Gross Income:     ${actual_gross_income:>10,.2f}")
            print(f"Statement Gross Income:  ${statement_gross_income:>10,.2f}")
            print(f"Difference:              ${gross_diff:>10,.2f}")
            print()
            print(f"Actual Tax Withheld:     ${actual_tax_withheld:>10,.2f}")
            print(f"Statement Tax Withheld:  ${statement_tax_withheld:>10,.2f}")
            print(f"Difference:              ${tax_diff:>10,.2f}")
            print()
            print(f"Actual Net Income:       ${actual_net_income:>10,.2f}")
            print(f"Statement Net Income:    ${statement_net_income:>10,.2f}")
            print(f"Difference:              ${net_diff:>10,.2f}")
            
            # Analyze differences
            print()
            print("ANALYSIS:")
            print("-" * 30)
            
            if abs(gross_diff) < 0.01 and abs(tax_diff) < 0.01:
                print("✓ PERFECT MATCH - No reconciliation needed")
            else:
                print("⚠ DIFFERENCES FOUND - Reconciliation required")
                
                if abs(gross_diff) > 0.01:
                    print(f"  • Gross income difference: ${gross_diff:,.2f}")
                    if gross_diff > 0:
                        print("    → Actual distributions exceed tax statement")
                    else:
                        print("    → Tax statement exceeds actual distributions")
                
                if abs(tax_diff) > 0.01:
                    print(f"  • Tax withheld difference: ${tax_diff:,.2f}")
                    if tax_diff > 0:
                        print("    → Actual tax withheld exceeds statement")
                    else:
                        print("    → Statement tax withheld exceeds actual")
                
                # Provide suggestions
                print()
                print("SUGGESTIONS FOR HANDLING DIFFERENCES:")
                print("-" * 40)
                
                if abs(gross_diff) > 0.01:
                    print("1. TIMING DIFFERENCES:")
                    print("   • Check if distributions were received in different FY")
                    print("   • Verify distribution dates vs. payment dates")
                    print("   • Consider accrual vs. cash basis differences")
                
                if abs(tax_diff) > 0.01:
                    print("2. TAX WITHHOLDING DIFFERENCES:")
                    print("   • Verify tax withholding rates applied")
                    print("   • Check for additional tax credits/refunds")
                    print("   • Consider foreign tax credits or offsets")
                
                print("3. GENERAL RECONCILIATION OPTIONS:")
                print("   • Use tax statement figures for tax reporting")
                print("   • Use actual distributions for cash flow tracking")
                print("   • Create adjustment entries to reconcile differences")
                print("   • Document differences in notes for future reference")
                
                # Check for common patterns
                print()
                print("COMMON PATTERNS:")
                print("-" * 20)
                
                if gross_diff > 0 and abs(gross_diff) < 100:
                    print("• Small positive difference - likely rounding differences")
                elif gross_diff < 0 and abs(gross_diff) < 100:
                    print("• Small negative difference - likely rounding differences")
                elif abs(gross_diff) > 1000:
                    print("• Large difference - investigate timing or missing distributions")
                
                if tax_diff > 0 and abs(tax_diff) < 50:
                    print("• Small tax difference - likely rate calculation differences")
                elif abs(tax_diff) > 500:
                    print("• Large tax difference - investigate withholding rates")
    
    session.close()

if __name__ == "__main__":
    reconcile_tax_statements() 