#!/usr/bin/env python3
"""
Test script to check for response size limits.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.api import create_app
from src.api.database import get_db_session
from src.investment_company.models import InvestmentCompany

def test_response_size():
    """Test if there are response size limits."""
    print("🚀 Testing response size limits...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        session = get_db_session()
        
        try:
            # Get all companies
            companies = session.query(InvestmentCompany).all()
            print(f"🔍 Retrieved {len(companies)} companies from database")
            
            # Create a large response
            companies_data = []
            for i, company in enumerate(companies):
                # Add some extra data to make the response larger
                company_data = {
                    "id": company.id,
                    "name": company.name,
                    "description": company.description or "",
                    "website": company.website or "",
                    "status": str(company.status) if company.status else None,
                    "created_at": company.created_at.isoformat() if company.created_at else None,
                    "extra_data": f"Extra data for company {company.id} - " + "x" * 100,  # Add 100 extra characters
                    "index": i,
                    "total_count": len(companies)
                }
                companies_data.append(company_data)
                print(f"✅ Processed company {company.id}: {company.name}")
            
            # Create response
            response_data = {
                "companies": companies_data,
                "total_count": len(companies_data),
                "metadata": {
                    "description": "Test response with all companies",
                    "extra_info": "x" * 1000  # Add 1000 extra characters
                }
            }
            
            print(f"✅ Created response with {len(companies_data)} companies")
            print(f"✅ Response data size: {len(str(response_data))} characters")
            
            # Try to return the response
            from flask import jsonify
            response = jsonify(response_data)
            print(f"✅ Created Flask response")
            print(f"✅ Response type: {type(response)}")
            
            # Check if we can access the JSON data
            if hasattr(response, 'json'):
                json_data = response.json
                print(f"✅ JSON data accessible")
                print(f"✅ Companies in response: {len(json_data.get('companies', []))}")
                print(f"✅ Total count: {json_data.get('total_count', 0)}")
            else:
                print(f"❌ Response doesn't have .json attribute")
            
        except Exception as e:
            print(f"❌ Error during response size test: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

if __name__ == "__main__":
    test_response_size()
