#!/usr/bin/env python3
"""
Set up after-tax IRR calculations by configuring tax payable rates
and creating tax payment events based on tax statements.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, TaxStatement, FundEvent, EventType

def setup_after_tax_irr():
    """Set up after-tax IRR calculations for all funds."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("SETTING UP AFTER-TAX IRR CALCULATIONS")
    print("=" * 60)
    
    # Get all funds
    funds = session.query(Fund).all()
    
    for fund in funds:
        print(f"\nFUND: {fund.name}")
        print("-" * 40)
        
        # Get all tax statements for this fund
        tax_statements = session.query(TaxStatement).filter(
            TaxStatement.fund_id == fund.id
        ).order_by(TaxStatement.financial_year).all()
        
        if not tax_statements:
            print("No tax statements found for this fund.")
            continue
        
        for tax_statement in tax_statements:
            print(f"\nFinancial Year: {tax_statement.financial_year}")
            print("-" * 30)
            
            # Set tax payable rate based on non-resident status
            if tax_statement.non_resident:
                # Non-resident tax rate (typically 10% for interest income)
                tax_statement.tax_payable_rate = 10.0
                print(f"Set tax payable rate to 10.0% (non-resident)")
            else:
                # Resident tax rate (typically higher, e.g., 32.5%+)
                tax_statement.tax_payable_rate = 32.5
                print(f"Set tax payable rate to 32.5% (resident)")
            
            # Calculate tax payable
            tax_statement.calculate_tax_payable()
            
            print(f"Total Income: ${tax_statement.total_income:,.2f}")
            print(f"Tax Already Paid: ${tax_statement.tax_already_paid:,.2f}")
            print(f"Additional Tax Payable: ${tax_statement.tax_payable:,.2f}")
            
            # Create tax payment event if there's additional tax payable
            if tax_statement.tax_payable > 0.01:
                tax_payment_date = tax_statement.get_tax_payment_date()
                
                # Check if tax payment event already exists
                existing_event = session.query(FundEvent).filter(
                    FundEvent.fund_id == fund.id,
                    FundEvent.event_type == EventType.TAX_PAYMENT,
                    FundEvent.event_date == tax_payment_date,
                    FundEvent.amount == tax_statement.tax_payable
                ).first()
                
                if not existing_event:
                    # Create tax payment event
                    tax_event = FundEvent(
                        fund_id=fund.id,
                        event_type=EventType.TAX_PAYMENT,
                        event_date=tax_payment_date,
                        amount=tax_statement.tax_payable,
                        description=f"Tax payment for FY {tax_statement.financial_year}",
                        reference_number=f"TAX-{tax_statement.financial_year}"
                    )
                    session.add(tax_event)
                    print(f"Created tax payment event: ${tax_statement.tax_payable:,.2f} on {tax_payment_date}")
                else:
                    print(f"Tax payment event already exists: ${tax_statement.tax_payable:,.2f} on {tax_payment_date}")
            else:
                print("No additional tax payable - no tax payment event needed")
        
        # Commit changes for this fund
        session.commit()
    
    print(f"\nAfter-tax IRR setup completed for {len(funds)} funds!")
    session.close()

def show_after_tax_irr_comparison():
    """Show comparison between gross and after-tax IRR for all funds."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("\nAFTER-TAX IRR COMPARISON")
    print("=" * 60)
    
    # Get all funds
    funds = session.query(Fund).all()
    
    for fund in funds:
        print(f"\nFUND: {fund.name}")
        print("-" * 40)
        
        # Calculate both IRRs
        gross_irr = fund.calculate_irr(session)
        after_tax_irr = fund.calculate_after_tax_irr(session)
        
        print(f"Gross IRR: {fund.get_irr_percentage(session)}")
        print(f"After-Tax IRR: {fund.get_after_tax_irr_percentage(session)}")
        
        if gross_irr is not None and after_tax_irr is not None:
            difference = gross_irr - after_tax_irr
            print(f"Tax Impact: {difference:.2f} percentage points")
        
        # Show tax payment events
        tax_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.TAX_PAYMENT
        ).order_by(FundEvent.event_date).all()
        
        if tax_events:
            print(f"\nTax Payment Events:")
            total_tax_paid = 0
            for event in tax_events:
                print(f"  {event.event_date}: ${event.amount:,.2f} - {event.description}")
                total_tax_paid += event.amount
            print(f"  Total Tax Paid: ${total_tax_paid:,.2f}")
        else:
            print(f"\nNo tax payment events found")
    
    session.close()

if __name__ == "__main__":
    setup_after_tax_irr()
    show_after_tax_irr_comparison() 