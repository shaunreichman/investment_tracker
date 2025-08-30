#!/usr/bin/env python3
"""
Minimal Flask app to test company retrieval without middleware.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, jsonify
from src.api.database import get_db_session
from src.investment_company.models import InvestmentCompany

def create_minimal_app():
    """Create a minimal Flask app without middleware."""
    app = Flask(__name__)
    
    @app.route('/test/companies')
    def test_companies():
        """Simple endpoint to test company retrieval."""
        try:
            session = get_db_session()
            try:
                # Direct database query
                companies = session.query(InvestmentCompany).all()
                print(f"🔍 Minimal app: Retrieved {len(companies)} companies from database")
                
                # Simple processing
                companies_data = []
                for company in companies:
                    company_data = {
                        "id": company.id,
                        "name": company.name,
                        "description": company.description or "",
                        "website": company.website or "",
                        "status": str(company.status) if company.status else None,
                        "created_at": company.created_at.isoformat() if company.created_at else None
                    }
                    companies_data.append(company_data)
                    print(f"✅ Minimal app: Processed company {company.id}: {company.name}")
                
                print(f"✅ Minimal app: Returning {len(companies_data)} companies")
                return jsonify({"companies": companies_data, "count": len(companies_data)})
                
            finally:
                session.close()
        except Exception as e:
            print(f"❌ Minimal app: Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
    
    return app

if __name__ == "__main__":
    app = create_minimal_app()
    print("🚀 Starting minimal Flask app on port 5002...")
    app.run(debug=True, host='0.0.0.0', port=5002)
