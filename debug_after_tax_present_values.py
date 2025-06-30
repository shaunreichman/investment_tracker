#!/usr/bin/env python3
"""
Debug script to show detailed present value calculations for after-tax IRR.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType
import math

def debug_after_tax_present_values():
    """Show detailed present value calculations for after-tax IRR."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("DETAILED AFTER-TAX IRR PRESENT VALUE CALCULATIONS")
    print("=" * 80)
    
    # Get all funds
    funds = session.query(Fund).all()
    
    for fund in funds:
        print(f"\n{'='*80}")
        print(f"FUND: {fund.name}")
        print(f"{'='*80}")
        
        # Get start and end dates
        start_date = fund.start_date
        end_date = fund.end_date
        
        print(f"Investment Period: {start_date} to {end_date}")
        print(f"Duration: {fund.total_investment_duration_months} months")
        
        # Get after-tax IRR
        after_tax_irr = fund.calculate_after_tax_irr(session)
        if after_tax_irr is None:
            print("Could not calculate after-tax IRR")
            continue
            
        print(f"After-Tax IRR: {after_tax_irr:.4f} ({after_tax_irr*100:.2f}%)")

        # Calculate monthly IRR for discounting (to match model)
        monthly_irr = (1 + after_tax_irr) ** (1/12) - 1
        
        # Get all cash flow events for after-tax IRR
        cash_flow_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_([
                EventType.CAPITAL_CALL,
                EventType.UNIT_PURCHASE,
                EventType.RETURN_OF_CAPITAL,
                EventType.DISTRIBUTION,
                EventType.MANAGEMENT_FEE,
                EventType.CARRIED_INTEREST,
                EventType.TAX_PAYMENT
            ])
        ).order_by(FundEvent.event_date).all()
        
        if not cash_flow_events:
            print("No cash flow events found.")
            continue
        
        print(f"\nDETAILED PRESENT VALUE CALCULATIONS:")
        print("-" * 100)
        print(f"{'Date':<12} {'Type':<15} {'Amount':<12} {'Days':<6} {'Cash Flow':<12} {'PV Factor':<12} {'Present Value':<15} {'Description'}")
        print("-" * 100)
        
        total_pv = 0
        cash_flows = []
        days_from_start = []
        
        for event in cash_flow_events:
            days = (event.event_date - start_date).days
            days_from_start.append(days)
            
            # Calculate cash flow based on event type
            if event.event_type == EventType.CAPITAL_CALL:
                cash_flow = -event.amount  # Cash outflow
                cash_flow_str = f"${cash_flow:,.2f}"
            elif event.event_type == EventType.RETURN_OF_CAPITAL:
                cash_flow = event.amount  # Cash inflow
                cash_flow_str = f"${cash_flow:,.2f}"
            elif event.event_type == EventType.DISTRIBUTION:
                cash_flow = event.amount  # Cash inflow
                cash_flow_str = f"${cash_flow:,.2f}"
            elif event.event_type == EventType.TAX_PAYMENT:
                cash_flow = -event.amount  # Cash outflow
                cash_flow_str = f"${cash_flow:,.2f}"
            elif event.event_type in [EventType.MANAGEMENT_FEE, EventType.CARRIED_INTEREST]:
                cash_flow = -event.amount  # Cash outflow
                cash_flow_str = f"${cash_flow:,.2f}"
            else:
                cash_flow = event.amount
                cash_flow_str = f"${cash_flow:,.2f}"
            
            cash_flows.append(cash_flow)
            
            # Calculate present value factor using monthly compounding
            if days == 0:
                pv_factor = 1.0
            else:
                pv_factor = (1 + monthly_irr) ** (days / 30.44)
            
            present_value = cash_flow / pv_factor
            total_pv += present_value
            
            print(f"{event.event_date} {event.event_type:<15} ${event.amount:<11,.2f} {days:<6} {cash_flow_str:<12} {pv_factor:<12.6f} ${present_value:<14,.2f} {event.description or ''}")
        
        # Add final value if fund is completed
        if not fund.should_be_active and cash_flows:
            final_value = fund.current_value or 0
            if final_value > 0:
                days = (end_date - start_date).days
                pv_factor = (1 + monthly_irr) ** (days / 30.44)
                present_value = final_value / pv_factor
                total_pv += present_value
                
                print(f"{end_date} FINAL_VALUE   ${final_value:<11,.2f} {days:<6} ${final_value:,.2f}     {pv_factor:<12.6f} ${present_value:<14,.2f} Final value")
                cash_flows[-1] += final_value
                print(f"  -> Updated last cash flow to: ${cash_flows[-1]:,.2f}")
        
        print("-" * 100)
        print(f"TOTAL PRESENT VALUE: ${total_pv:,.2f}")
        
        # Show summary by event type
        print(f"\nSUMMARY BY EVENT TYPE:")
        print("-" * 60)
        
        type_totals = {}
        type_pv_totals = {}
        
        for i, event in enumerate(cash_flow_events):
            event_type = event.event_type
            if event_type not in type_totals:
                type_totals[event_type] = 0
                type_pv_totals[event_type] = 0
            
            # Calculate cash flow
            if event.event_type == EventType.CAPITAL_CALL:
                cash_flow = -event.amount
            elif event.event_type == EventType.RETURN_OF_CAPITAL:
                cash_flow = event.amount
            elif event.event_type == EventType.DISTRIBUTION:
                cash_flow = event.amount
            elif event.event_type == EventType.TAX_PAYMENT:
                cash_flow = -event.amount
            elif event.event_type in [EventType.MANAGEMENT_FEE, EventType.CARRIED_INTEREST]:
                cash_flow = -event.amount
            else:
                cash_flow = event.amount
            
            type_totals[event_type] += cash_flow
            
            # Calculate present value
            days = (event.event_date - start_date).days
            if days == 0:
                pv_factor = 1.0
            else:
                pv_factor = (1 + after_tax_irr) ** (days / 365.25)
            
            present_value = cash_flow / pv_factor
            type_pv_totals[event_type] += present_value
        
        for event_type in sorted(type_totals.keys()):
            print(f"{event_type:<20} Cash Flow: ${type_totals[event_type]:<12,.2f} PV: ${type_pv_totals[event_type]:<12,.2f}")
        
        # Verify IRR calculation
        print(f"\nIRR VERIFICATION:")
        print(f"  Target NPV: $0.00")
        print(f"  Actual NPV: ${total_pv:,.2f}")
        print(f"  Difference: ${abs(total_pv):,.2f}")
        
        if abs(total_pv) < 0.01:
            print(f"  ✓ IRR calculation is accurate (NPV ≈ 0)")
        else:
            print(f"  ⚠ IRR calculation may have issues (NPV ≠ 0)")
        
        print(f"\n{'='*80}")
    
    session.close()

def compare_gross_vs_after_tax_pv():
    """Compare present value calculations for gross vs after-tax IRR."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f"\nCOMPARISON: GROSS VS AFTER-TAX PRESENT VALUES")
    print(f"{'='*80}")
    
    # Get all funds
    funds = session.query(Fund).all()
    
    for fund in funds:
        print(f"\nFUND: {fund.name}")
        print("-" * 60)
        
        # Gross IRR
        gross_irr = fund.calculate_irr(session)
        # After-tax IRR
        after_tax_irr = fund.calculate_after_tax_irr(session)
        
        if gross_irr is None or after_tax_irr is None:
            print("Could not calculate one or both IRRs")
            continue
        
        print(f"Gross IRR: {gross_irr:.4f} ({gross_irr*100:.2f}%)")
        print(f"After-Tax IRR: {after_tax_irr:.4f} ({after_tax_irr*100:.2f}%)")
        
        # Calculate monthly IRRs for discounting
        gross_monthly_irr = (1 + gross_irr) ** (1/12) - 1
        after_tax_monthly_irr = (1 + after_tax_irr) ** (1/12) - 1
        
        # Get all cash flow events for both IRRs
        event_types = [
            EventType.CAPITAL_CALL,
            EventType.UNIT_PURCHASE,
            EventType.RETURN_OF_CAPITAL,
            EventType.DISTRIBUTION,
            EventType.MANAGEMENT_FEE,
            EventType.CARRIED_INTEREST
        ]
        cash_flow_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_(event_types + [EventType.TAX_PAYMENT])
        ).order_by(FundEvent.event_date).all()
        
        start_date = fund.start_date
        end_date = fund.end_date
        
        # Calculate NPV for gross IRR (exclude tax payments)
        gross_total_pv = 0
        for event in cash_flow_events:
            if event.event_type == EventType.TAX_PAYMENT:
                continue  # Exclude tax payments for gross IRR
            days = (event.event_date - start_date).days
            if days == 0:
                pv_factor = 1.0
            else:
                pv_factor = (1 + gross_monthly_irr) ** (days / 30.44)
            # Cash flow sign
            if event.event_type == EventType.CAPITAL_CALL:
                cash_flow = -event.amount
            elif event.event_type == EventType.RETURN_OF_CAPITAL:
                cash_flow = event.amount
            elif event.event_type == EventType.DISTRIBUTION:
                cash_flow = event.amount
            elif event.event_type == EventType.MANAGEMENT_FEE:
                cash_flow = -event.amount
            elif event.event_type == EventType.CARRIED_INTEREST:
                cash_flow = -event.amount
            else:
                cash_flow = event.amount
            gross_total_pv += cash_flow / pv_factor
        # Add final value if needed
        if not fund.should_be_active:
            final_value = fund.current_value or 0
            if final_value > 0:
                days = (end_date - start_date).days
                pv_factor = (1 + gross_monthly_irr) ** (days / 30.44)
                gross_total_pv += final_value / pv_factor
        
        # Calculate NPV for after-tax IRR (include tax payments)
        after_tax_total_pv = 0
        for event in cash_flow_events:
            days = (event.event_date - start_date).days
            if days == 0:
                pv_factor = 1.0
            else:
                pv_factor = (1 + after_tax_monthly_irr) ** (days / 30.44)
            # Cash flow sign
            if event.event_type == EventType.CAPITAL_CALL:
                cash_flow = -event.amount
            elif event.event_type == EventType.RETURN_OF_CAPITAL:
                cash_flow = event.amount
            elif event.event_type == EventType.DISTRIBUTION:
                cash_flow = event.amount
            elif event.event_type == EventType.TAX_PAYMENT:
                cash_flow = -event.amount
            elif event.event_type == EventType.MANAGEMENT_FEE:
                cash_flow = -event.amount
            elif event.event_type == EventType.CARRIED_INTEREST:
                cash_flow = -event.amount
            else:
                cash_flow = event.amount
            after_tax_total_pv += cash_flow / pv_factor
        # Add final value if needed
        if not fund.should_be_active:
            final_value = fund.current_value or 0
            if final_value > 0:
                days = (end_date - start_date).days
                pv_factor = (1 + after_tax_monthly_irr) ** (days / 30.44)
                after_tax_total_pv += final_value / pv_factor
        
        print()
        print("NPV Results:")
        print(f"  Gross IRR NPV:     ${gross_total_pv:,.2f}")
        print(f"  After-Tax IRR NPV: ${after_tax_total_pv:,.2f}")
        if abs(after_tax_total_pv) < 0.01 and abs(gross_total_pv) < 0.01:
            print("  ✓ IRR calculations are accurate (NPV ≈ 0)")
        else:
            print("  ⚠ IRR calculations may have issues")
    
    session.close()

if __name__ == "__main__":
    debug_after_tax_present_values()
    compare_gross_vs_after_tax_pv() 