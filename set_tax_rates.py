#!/usr/bin/env python3
"""
Script to manually set tax payable rates for specific tax statements.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, TaxStatement, FundEvent, EventType

def list_tax_statements():
    """List all tax statements with their current settings."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("CURRENT TAX STATEMENTS")
    print("=" * 80)
    
    # Get all tax statements
    tax_statements = session.query(TaxStatement).order_by(
        TaxStatement.fund_id, TaxStatement.financial_year
    ).all()
    
    if not tax_statements:
        print("No tax statements found.")
        return
    
    for i, tax_statement in enumerate(tax_statements, 1):
        fund = session.query(Fund).filter(Fund.id == tax_statement.fund_id).first()
        
        print(f"\n{i}. FUND: {fund.name if fund else 'Unknown'}")
        print(f"   Financial Year: {tax_statement.financial_year}")
        print(f"   Total Income: ${tax_statement.total_income:,.2f}")
        print(f"   Tax Withheld: ${tax_statement.tax_withheld:,.2f}")
        print(f"   Non-Resident: {tax_statement.non_resident}")
        print(f"   Current Tax Rate: {tax_statement.tax_payable_rate:.1f}%")
        print(f"   Tax Already Paid: ${tax_statement.tax_already_paid:,.2f}")
        print(f"   Additional Tax: ${tax_statement.tax_payable:,.2f}")
    
    session.close()
    return tax_statements

def set_tax_rate(tax_statement_id, tax_rate, non_resident=None):
    """Set tax payable rate for a specific tax statement."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get the tax statement
    tax_statement = session.query(TaxStatement).filter(TaxStatement.id == tax_statement_id).first()
    if not tax_statement:
        print(f"Tax statement with ID {tax_statement_id} not found.")
        session.close()
        return
    
    fund = session.query(Fund).filter(Fund.id == tax_statement.fund_id).first()
    
    print(f"UPDATING TAX STATEMENT")
    print(f"Fund: {fund.name if fund else 'Unknown'}")
    print(f"Financial Year: {tax_statement.financial_year}")
    print(f"Current Tax Rate: {tax_statement.tax_payable_rate:.1f}%")
    print(f"New Tax Rate: {tax_rate:.1f}%")
    
    # Update the tax rate
    tax_statement.tax_payable_rate = tax_rate
    
    # Update non-resident status if provided
    if non_resident is not None:
        tax_statement.non_resident = non_resident
        print(f"Non-Resident Status: {non_resident}")
    
    # Recalculate tax payable
    tax_statement.calculate_tax_payable()
    
    print(f"Updated Tax Already Paid: ${tax_statement.tax_already_paid:,.2f}")
    print(f"Updated Additional Tax: ${tax_statement.tax_payable:,.2f}")
    
    # Remove existing tax payment event if tax payable is now zero
    if tax_statement.tax_payable <= 0.01:
        existing_event = session.query(FundEvent).filter(
            FundEvent.fund_id == tax_statement.fund_id,
            FundEvent.event_type == EventType.TAX_PAYMENT,
            FundEvent.event_date == tax_statement.get_tax_payment_date(),
            FundEvent.description == f"Tax payment for FY {tax_statement.financial_year}"
        ).first()
        
        if existing_event:
            session.delete(existing_event)
            print(f"Removed existing tax payment event: ${existing_event.amount:,.2f}")
    
    # Create new tax payment event if there's additional tax payable
    elif tax_statement.tax_payable > 0.01:
        # Remove any existing tax payment event for this FY
        existing_event = session.query(FundEvent).filter(
            FundEvent.fund_id == tax_statement.fund_id,
            FundEvent.event_type == EventType.TAX_PAYMENT,
            FundEvent.description == f"Tax payment for FY {tax_statement.financial_year}"
        ).first()
        
        if existing_event:
            session.delete(existing_event)
        
        # Create new tax payment event
        tax_event = FundEvent(
            fund_id=tax_statement.fund_id,
            event_type=EventType.TAX_PAYMENT,
            event_date=tax_statement.get_tax_payment_date(),
            amount=tax_statement.tax_payable,
            description=f"Tax payment for FY {tax_statement.financial_year}",
            reference_number=f"TAX-{tax_statement.financial_year}"
        )
        session.add(tax_event)
        print(f"Created new tax payment event: ${tax_statement.tax_payable:,.2f} on {tax_statement.get_tax_payment_date()}")
    
    session.commit()
    session.close()
    
    print("Tax statement updated successfully!")

def interactive_setup():
    """Interactive setup for tax rates."""
    
    tax_statements = list_tax_statements()
    if not tax_statements:
        return
    
    print(f"\nINTERACTIVE TAX RATE SETUP")
    print(f"=" * 80)
    
    while True:
        try:
            choice = input(f"\nEnter tax statement number (1-{len(tax_statements)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                break
            
            statement_num = int(choice)
            if statement_num < 1 or statement_num > len(tax_statements):
                print(f"Please enter a number between 1 and {len(tax_statements)}")
                continue
            
            tax_statement = tax_statements[statement_num - 1]
            fund = session.query(Fund).filter(Fund.id == tax_statement.fund_id).first()
            
            print(f"\nUpdating: {fund.name} - FY {tax_statement.financial_year}")
            
            # Get new tax rate
            tax_rate = float(input(f"Enter new tax rate (current: {tax_statement.tax_payable_rate:.1f}%): "))
            
            # Get non-resident status
            non_resident_input = input(f"Non-resident? (y/n, current: {tax_statement.non_resident}): ").strip().lower()
            non_resident = None
            if non_resident_input in ['y', 'yes']:
                non_resident = True
            elif non_resident_input in ['n', 'no']:
                non_resident = False
            
            # Update the tax statement
            set_tax_rate(tax_statement.id, tax_rate, non_resident)
            
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Command line usage: python set_tax_rates.py <tax_statement_id> <tax_rate>
        tax_statement_id = int(sys.argv[1])
        tax_rate = float(sys.argv[2])
        set_tax_rate(tax_statement_id, tax_rate)
    else:
        # Interactive mode
        interactive_setup() 