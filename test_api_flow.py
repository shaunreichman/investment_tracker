#!/usr/bin/env python3
"""
Minimal test script to simulate the exact API call flow with Flask context.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.api import create_app
from src.api.database import get_db_session
from src.investment_company.api.company_controller import CompanyController

def test_api_flow():
    """Test the exact API call flow with Flask context."""
    print("🚀 Testing API call flow with Flask context...")
    
    # Create Flask app and context
    app = create_app()
    
    with app.app_context():
        # Create controller instance
        controller = CompanyController()
        
        # Get database session
        session = get_db_session()
        
        try:
            print("🔍 Calling controller.get_investment_companies(session)...")
            
            # Call the exact method that the API calls
            result = controller.get_investment_companies(session)
            
            print(f"✅ Controller returned: {type(result)}")
            
            if isinstance(result, tuple) and len(result) == 2:
                response_data, status_code = result
                print(f"✅ Status code: {status_code}")
                print(f"✅ Response data type: {type(response_data)}")
                
                # Check if it's a Flask response object
                if hasattr(response_data, 'json'):
                    json_data = response_data.json
                    print(f"✅ JSON data: {json_data}")
                    if 'companies' in json_data:
                        companies = json_data['companies']
                        print(f"✅ Companies count in response: {len(companies)}")
                        for company in companies:
                            print(f"  - ID: {company['id']}, Name: {company['name']}")
                    else:
                        print(f"❌ No 'companies' key in response")
                else:
                    print(f"❌ Response data doesn't have .json attribute")
                    print(f"🔍 Response data: {response_data}")
            else:
                print(f"❌ Unexpected result format: {result}")
                
        except Exception as e:
            print(f"❌ Error during API flow test: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

if __name__ == "__main__":
    test_api_flow()
