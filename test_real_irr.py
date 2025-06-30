#!/usr/bin/env python3
"""
Test script for real IRR calculation including debt cost.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType, RiskFreeRate

def test_real_irr():
    """Test the real IRR calculation."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("REAL IRR CALCULATION TEST")
    print("=" * 60)
    
    # Get all funds
    funds = session.query(Fund).all()
    
    for fund in funds:
        print(f"\nFUND: {fund.name}")
        print("-" * 40)
        
        # Check if fund is completed
        if fund.should_be_active:
            print("Fund is still active - cannot calculate IRR")
            continue
        
        # Calculate all three IRRs
        gross_irr = fund.calculate_irr(session)
        after_tax_irr = fund.calculate_after_tax_irr(session)
        real_irr = fund.calculate_real_irr(session)
        
        print(f"Gross IRR:        {fund.get_irr_percentage(session)}")
        print(f"After-Tax IRR:    {fund.get_after_tax_irr_percentage(session)}")
        print(f"Real IRR:         {fund.get_real_irr_percentage(session)}")
        
        # Show debt cost analysis
        debt_cost_analysis = fund.calculate_debt_cost(session)
        if debt_cost_analysis:
            print(f"\nDebt Cost Analysis:")
            print(f"  Total Debt Cost: ${debt_cost_analysis['total_debt_cost']:,.2f}")
            print(f"  Average RFR:     {debt_cost_analysis['average_risk_free_rate']:.2f}%")
            print(f"  Debt Cost %:     {debt_cost_analysis['debt_cost_percentage']:.2f}%")
            if debt_cost_analysis['excess_return'] is not None:
                print(f"  Excess Return:   ${debt_cost_analysis['excess_return']:,.2f}")
        
        # Show the difference between after-tax and real IRR
        if after_tax_irr is not None and real_irr is not None:
            difference = after_tax_irr - real_irr
            print(f"\nAfter-Tax vs Real IRR Difference: {difference*100:.2f}%")
            print(f"This represents the impact of debt cost on returns")
    
    session.close()

if __name__ == "__main__":
    test_real_irr() 