#!/usr/bin/env python3
"""
Debug script to test company retrieval logic step by step.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.api.database import get_db_session
from src.investment_company.models import InvestmentCompany
from src.investment_company.services import CompanyService
from src.investment_company.api.company_controller import CompanyController

def test_direct_database_query():
    """Test direct database query."""
    print("🔍 Testing direct database query...")
    session = get_db_session()
    try:
        companies = session.query(InvestmentCompany).all()
        print(f"✅ Direct query returned {len(companies)} companies")
        for company in companies:
            print(f"  - ID: {company.id}, Name: {company.name}")
        return companies
    finally:
        session.close()

def test_company_service():
    """Test company service."""
    print("\n🔍 Testing company service...")
    session = get_db_session()
    try:
        service = CompanyService()
        companies = service.get_all_companies(session)
        print(f"✅ Service returned {len(companies)} companies")
        for company in companies:
            print(f"  - ID: {company.id}, Name: {company.name}")
        return companies
    finally:
        session.close()

def test_company_controller():
    """Test company controller."""
    print("\n🔍 Testing company controller...")
    session = get_db_session()
    try:
        controller = CompanyController()
        companies = controller.company_service.get_all_companies(session)
        print(f"✅ Controller service returned {len(companies)} companies")
        
        # Test the processing logic
        companies_data = []
        for i, company in enumerate(companies):
            print(f"🔍 Processing company {i+1}/{len(companies)}: ID={company.id}, Name={company.name}")
            
            try:
                # Get fund count and summary data using services directly
                total_funds = controller.portfolio_service.get_total_funds_under_management(company, session)
                total_commitments = controller.portfolio_service.get_total_commitments(company, session)
                print(f"✅ Got portfolio data for company {company.id}: funds={total_funds}, commitments={total_commitments}")
                
                # Extract fund data while session is still active
                active_funds = 0
                total_equity = 0.0
                if company.funds:
                    for fund in company.funds:
                        if fund.status == 'active':  # Use string since it might be stored as string
                            active_funds += 1
                        total_equity += fund.current_equity_balance or 0.0
                
                company_data = {
                    "id": company.id,
                    "name": company.name,
                    "description": company.description,
                    "website": company.website,
                    "company_type": company.company_type,
                    "status": company.status,
                    "business_address": company.business_address,
                    "fund_count": total_funds,
                    "active_funds": active_funds,
                    "total_commitments": float(total_commitments) if total_commitments else 0.0,
                    "total_equity_balance": float(total_equity),
                    "created_at": company.created_at.isoformat() if company.created_at else None,
                    "updated_at": company.updated_at.isoformat() if company.updated_at else None
                }
                
                companies_data.append(company_data)
                print(f"✅ Successfully processed company {company.id}")
                
            except Exception as e:
                print(f"❌ Error processing company {company.id}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"✅ Successfully processed {len(companies_data)} out of {len(companies)} companies")
        return companies_data
        
    finally:
        session.close()

def test_api_simulation():
    """Test simulating the exact API call flow."""
    print("\n🔍 Testing API simulation...")
    
    # Create a controller instance directly (avoiding Flask context issues)
    controller = CompanyController()
    
    session = get_db_session()
    try:
        print("🔍 Calling controller.get_investment_companies(session)...")
        
        # Get companies from service first
        companies = controller.company_service.get_all_companies(session)
        print(f"✅ Service returned {len(companies)} companies")
        
        # Now test the exact processing logic from the controller
        companies_data = []
        for i, company in enumerate(companies):
            print(f"🔍 Processing company {i+1}/{len(companies)}: ID={company.id}, Name={company.name}")
            
            try:
                # Get fund count and summary data using services directly
                total_funds = controller.portfolio_service.get_total_funds_under_management(company, session)
                total_commitments = controller.portfolio_service.get_total_commitments(company, session)
                print(f"✅ Got portfolio data for company {company.id}: funds={total_funds}, commitments={total_commitments}")
                
                # Extract fund data while session is still active
                active_funds = 0
                total_equity = 0.0
                if company.funds:
                    for fund in company.funds:
                        if fund.status == 'active':  # Use string since it might be stored as string
                            active_funds += 1
                        total_equity += fund.current_equity_balance or 0.0
                
                # Handle company_type safely - it might be a string from old data or an enum
                company_type_value = None
                if company.company_type:
                    if hasattr(company.company_type, 'value'):
                        company_type_value = company.company_type.value
                    else:
                        company_type_value = str(company.company_type)
                
                # Handle status safely
                status_value = None
                if company.status:
                    if hasattr(company.status, 'value'):
                        status_value = company.status.value
                    else:
                        status_value = str(company.status)
                
                company_data = {
                    "id": company.id,
                    "name": company.name,
                    "description": company.description,
                    "website": company.website,
                    "company_type": company_type_value,
                    "status": status_value,
                    "business_address": company.business_address,
                    "fund_count": total_funds,
                    "active_funds": active_funds,
                    "total_commitments": float(total_commitments) if total_commitments else 0.0,
                    "total_equity_balance": float(total_equity),
                    "created_at": company.created_at.isoformat() if company.created_at else None,
                    "updated_at": company.updated_at.isoformat() if company.updated_at else None
                }
                
                companies_data.append(company_data)
                print(f"✅ Successfully processed company {company.id}")
                
            except Exception as e:
                print(f"❌ Error processing company {company.id}: {str(e)}")
                import traceback
                traceback.print_exc()
                # Continue processing other companies instead of failing completely
                continue
        
        print(f"✅ Successfully processed {len(companies_data)} out of {len(companies)} companies")
        
        # Check if we have the same issue as the API
        if len(companies_data) != len(companies):
            print(f"⚠️  WARNING: Processing mismatch! Got {len(companies)} companies but only processed {len(companies_data)}")
            print(f"🔍 Checking which companies were processed:")
            processed_ids = [c['id'] for c in companies_data]
            all_ids = [c.id for c in companies]
            missing_ids = [id for id in all_ids if id not in processed_ids]
            print(f"❌ Missing companies: {missing_ids}")
        else:
            print(f"✅ All companies processed successfully")
            
        return companies_data
        
    finally:
        session.close()

def main():
    """Main test function."""
    print("🚀 Starting company retrieval debug...")
    
    # Test 1: Direct database query
    db_companies = test_direct_database_query()
    
    # Test 2: Company service
    service_companies = test_company_service()
    
    # Test 3: Company controller
    controller_companies = test_company_controller()
    
    # Test 4: API simulation
    api_companies = test_api_simulation()
    
    print(f"\n📊 Summary:")
    print(f"  - Direct DB query: {len(db_companies)} companies")
    print(f"  - Company service: {len(service_companies)} companies")
    print(f"  - Controller processing: {len(controller_companies)} companies")
    print(f"  - API simulation: {len(api_companies) if api_companies else 0} companies")
    
    if len(db_companies) != len(service_companies):
        print(f"⚠️  WARNING: Database query vs Service mismatch!")
    
    if len(service_companies) != len(controller_companies):
        print(f"⚠️  WARNING: Service vs Controller processing mismatch!")
    
    if api_companies and len(service_companies) != len(api_companies):
        print(f"⚠️  WARNING: Service vs API simulation mismatch!")

if __name__ == "__main__":
    main()
