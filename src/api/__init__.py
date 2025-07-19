from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, date, timedelta

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "ok", "message": "API is running"}), 200

    @app.route('/api/dashboard/portfolio-summary', methods=['GET'])
    def portfolio_summary():
        """Get overall portfolio summary with key metrics"""
        summary = {
            "total_funds": 5,
            "active_funds": 4,
            "total_equity_balance": 1250000.00,
            "total_average_equity_balance": 1100000.00,
            "recent_events_count": 12,
            "total_tax_statements": 8,
            "last_updated": datetime.now().isoformat()
        }
        return jsonify(summary), 200

    @app.route('/api/dashboard/funds', methods=['GET'])
    def funds_list():
        """Get list of all funds with key metrics"""
        fund_data = [
            {
                "id": 1,
                "name": "Private Debt Fund A",
                "fund_type": "Private Debt",
                "tracking_type": "cost_based",
                "currency": "AUD",
                "current_equity_balance": 500000.00,
                "average_equity_balance": 450000.00,
                "is_active": True,
                "investment_company": "ABC Investments",
                "entity": "Personal Trust",
                "recent_events_count": 3,
                "created_at": "2023-01-15T00:00:00"
            },
            {
                "id": 2,
                "name": "Venture Capital Fund B",
                "fund_type": "Venture Capital",
                "tracking_type": "nav_based",
                "currency": "AUD",
                "current_equity_balance": 750000.00,
                "average_equity_balance": 650000.00,
                "is_active": True,
                "investment_company": "XYZ Capital",
                "entity": "Personal Trust",
                "recent_events_count": 5,
                "created_at": "2023-03-20T00:00:00"
            },
            {
                "id": 3,
                "name": "Property Fund C",
                "fund_type": "Property",
                "tracking_type": "nav_based",
                "currency": "AUD",
                "current_equity_balance": 0.00,
                "average_equity_balance": 0.00,
                "is_active": False,
                "investment_company": "Property Partners",
                "entity": "Personal Trust",
                "recent_events_count": 0,
                "created_at": "2022-06-10T00:00:00"
            }
        ]
        return jsonify({"funds": fund_data}), 200

    @app.route('/api/dashboard/recent-events', methods=['GET'])
    def recent_events():
        """Get recent fund events for the dashboard"""
        event_data = [
            {
                "id": 1,
                "fund_name": "Private Debt Fund A",
                "event_type": "distribution",
                "event_date": "2024-01-15",
                "amount": 25000.00,
                "description": "Interest distribution",
                "reference_number": "DIST-001"
            },
            {
                "id": 2,
                "fund_name": "Venture Capital Fund B",
                "event_type": "nav_update",
                "event_date": "2024-01-10",
                "amount": None,
                "description": "Quarterly NAV update",
                "reference_number": "NAV-001"
            },
            {
                "id": 3,
                "fund_name": "Private Debt Fund A",
                "event_type": "capital_call",
                "event_date": "2024-01-05",
                "amount": 100000.00,
                "description": "Additional capital call",
                "reference_number": "CALL-001"
            }
        ]
        return jsonify({"events": event_data}), 200

    @app.route('/api/dashboard/performance', methods=['GET'])
    def performance_data():
        """Get performance data for charts"""
        performance_data = [
            {
                "fund_name": "Private Debt Fund A",
                "current_equity": 500000.00,
                "average_equity": 450000.00,
                "total_events": 15,
                "last_event_date": "2024-01-15"
            },
            {
                "fund_name": "Venture Capital Fund B",
                "current_equity": 750000.00,
                "average_equity": 650000.00,
                "total_events": 22,
                "last_event_date": "2024-01-10"
            }
        ]
        return jsonify({"performance": performance_data}), 200

    return app 