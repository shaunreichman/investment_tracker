#!/usr/bin/env python3
"""
Debug script to test the enhanced funds endpoint and identify the 500 error
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_database_session
from src.investment_company.models import InvestmentCompany
from src.fund.models import Fund, FundStatus
from src.tax.models import TaxStatement
from datetime import date

def debug_enhanced_funds_endpoint():
    """Debug the enhanced funds endpoint to find the 500 error"""
    engine, session_factory, session = get_database_session()
    
    try:
        # Get the first company
        company = session.query(InvestmentCompany).first()
        if not company:
            print("No companies found in database")
            return
        
        print(f"Testing company: {company.name} (ID: {company.id})")
        print(f"Company has {len(company.funds)} funds")
        
        # Test the enhanced funds endpoint logic step by step
        for fund in company.funds:
            print(f"\n--- Testing Fund: {fund.name} ---")
            print(f"Status: {fund.status}")
            print(f"Tracking type: {fund.tracking_type}")
            print(f"Current equity balance: {fund.current_equity_balance}")
            
            try:
                # Test get_enhanced_fund_metrics
                print("Testing fund.get_enhanced_fund_metrics...")
                enhanced_metrics = fund.get_enhanced_fund_metrics(session=session)
                print(f"Enhanced metrics: {enhanced_metrics}")
            except Exception as e:
                print(f"Error in fund.get_enhanced_fund_metrics: {e}")
                import traceback
                traceback.print_exc()
            
            try:
                # Test get_distribution_summary
                print("Testing fund.get_distribution_summary...")
                distribution_summary = fund.get_distribution_summary(session=session)
                print(f"Distribution summary: {distribution_summary}")
            except Exception as e:
                print(f"Error in fund.get_distribution_summary: {e}")
                import traceback
                traceback.print_exc()
            
            try:
                # Test status filtering logic
                print("Testing status filtering...")
                if fund.status == FundStatus.ACTIVE:
                    print("Fund is ACTIVE - should pass filter")
                elif fund.status == FundStatus.COMPLETED:
                    print("Fund is COMPLETED - should pass filter")
                elif fund.status == FundStatus.REALIZED:
                    print("Fund is REALIZED - should pass filter")
            except Exception as e:
                print(f"Error in status filtering: {e}")
                import traceback
                traceback.print_exc()
        
        # Test the specific filtering logic from the endpoint
        print("\n--- Testing Endpoint Filtering Logic ---")
        status_filter = 'active'
        print(f"Testing status filter: {status_filter}")
        
        from src.fund.models import FundStatus
        status_map = {
            'active': FundStatus.ACTIVE,
            'completed': FundStatus.COMPLETED,
            'suspended': FundStatus.SUSPENDED
        }
        
        if status_filter in status_map:
            target_status = status_map[status_filter]
            print(f"Target status: {target_status}")
            
            filtered_funds = [f for f in company.funds if f.status == target_status]
            print(f"Found {len(filtered_funds)} funds with status {target_status}")
            
            for fund in filtered_funds:
                print(f"  - {fund.name}: {fund.status}")
        
    except Exception as e:
        print(f"Error in debug: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    debug_enhanced_funds_endpoint()
