import sys
import os
from datetime import datetime, date, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import text, func, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import joinedload

# Add the project root to Python path to enable domain method imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import domain models and methods
from src.database import get_database_session
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from src.fund.models import Fund, FundType

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Direct database setup to avoid import issues
    def get_db_session():
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'investment_tracker.db')
        engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=engine)
        return scoped_session(Session)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "ok", "message": "API is running"}), 200

    @app.route('/api/dashboard/portfolio-summary', methods=['GET'])
    def portfolio_summary():
        """Get overall portfolio summary with key metrics"""
        try:
            session = get_db_session()
            
            try:
                # Use domain methods to get all funds
                funds = Fund.get_all(session=session)
                
                # Calculate summary metrics using domain data
                total_funds = len(funds)
                active_funds = sum(1 for fund in funds if fund.is_active)
                total_equity = sum(fund.current_equity_balance or 0.0 for fund in funds)
                total_avg_equity = sum(fund.average_equity_balance or 0.0 for fund in funds)
                
                # Get recent events count across all funds
                recent_events_count = 0
                thirty_days_ago = date.today() - timedelta(days=30)
                for fund in funds:
                    recent_events = fund.get_recent_events(limit=1000, session=session)
                    recent_events_count += len([e for e in recent_events if e.event_date and e.event_date >= thirty_days_ago])
                
                # Get tax statements count using domain method
                from src.tax.models import TaxStatement
                total_tax_statements = session.query(TaxStatement).count()
                
                summary = {
                    "total_funds": total_funds,
                    "active_funds": active_funds,
                    "total_equity_balance": float(total_equity),
                    "total_average_equity_balance": float(total_avg_equity),
                    "recent_events_count": recent_events_count,
                    "total_tax_statements": total_tax_statements,
                    "last_updated": datetime.now().isoformat()
                }
                return jsonify(summary), 200
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/dashboard/funds', methods=['GET'])
    def funds_list():
        """Get list of all funds with key metrics"""
        try:
            session = get_db_session()
            
            try:
                # Use domain methods to get all funds
                funds = Fund.get_all(session=session)
                
                fund_data = []
                for fund in funds:
                    # Get recent events count using domain method
                    recent_events = fund.get_recent_events(limit=100, session=session)
                    recent_events_count = len(recent_events)
                    
                    fund_data.append({
                        "id": fund.id,
                        "name": fund.name,
                        "fund_type": fund.fund_type,
                        "tracking_type": fund.tracking_type.value if fund.tracking_type else None,
                        "currency": fund.currency,
                        "current_equity_balance": float(fund.current_equity_balance) if fund.current_equity_balance else 0.0,
                        "average_equity_balance": float(fund.average_equity_balance) if fund.average_equity_balance else 0.0,
                        "is_active": fund.is_active if fund.is_active is not None else True,
                        "investment_company": fund.investment_company.name if fund.investment_company else "Unknown",
                        "entity": fund.entity.name if fund.entity else "Unknown",
                        "recent_events_count": recent_events_count,
                        "created_at": fund.created_at.isoformat() if fund.created_at else None
                    })
                
                return jsonify({"funds": fund_data}), 200
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/dashboard/recent-events', methods=['GET'])
    def recent_events():
        """Get recent fund events for the dashboard"""
        try:
            session = get_db_session()
            
            try:
                # Get all funds and their recent events using domain methods
                funds = Fund.get_all(session=session)
                
                all_events = []
                for fund in funds:
                    # Get recent events for this fund using domain method
                    recent_events = fund.get_recent_events(limit=5, session=session)
                    
                    for event in recent_events:
                        all_events.append({
                            "id": event.id,
                            "fund_name": fund.name,
                            "event_type": event.event_type.value if event.event_type else "unknown",
                            "event_date": event.event_date.isoformat() if event.event_date else None,
                            "amount": float(event.amount) if event.amount else None,
                            "description": event.description,
                            "reference_number": event.reference_number
                        })
                
                # Sort by event date (most recent first) and limit to 10
                all_events.sort(key=lambda x: x['event_date'] if x['event_date'] else '', reverse=True)
                all_events = all_events[:10]
                
                return jsonify({"events": all_events}), 200
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/dashboard/performance', methods=['GET'])
    def dashboard_performance():
        """Get performance data for all funds"""
        try:
            session = get_db_session()
            
            try:
                # Get all funds using domain methods
                funds = Fund.get_all(session=session)
                
                performance_data = []
                for fund in funds:
                    # Get recent events using domain method
                    recent_events = fund.get_recent_events(limit=1000, session=session)
                    total_events = len(recent_events)
                    
                    # Get last event date
                    last_event_date = None
                    if recent_events:
                        last_event = max(recent_events, key=lambda x: x.event_date if x.event_date else date.min)
                        last_event_date = last_event.event_date.isoformat() if last_event.event_date else None
                    
                    performance_data.append({
                        "fund_id": fund.id,
                        "fund_name": fund.name,
                        "current_equity": float(fund.current_equity_balance) if fund.current_equity_balance else 0.0,
                        "average_equity": float(fund.average_equity_balance) if fund.average_equity_balance else 0.0,
                        "total_events": total_events,
                        "last_event_date": last_event_date
                    })
                
                # Sort by fund name
                performance_data.sort(key=lambda x: x['fund_name'])
                
                return jsonify({"performance": performance_data}), 200
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/investment-companies', methods=['GET'])
    def investment_companies():
        """Get list of all investment companies with summary data"""
        try:
            session = get_db_session()
            try:
                # Eagerly load funds relationship
                companies = session.query(InvestmentCompany).options(joinedload(InvestmentCompany.funds)).all()
                companies_data = []
                for company in companies:
                    # Get fund count and summary data using domain methods
                    total_funds = company.get_total_funds_under_management(session)
                    total_commitments = company.get_total_commitments(session)
                    active_funds = 0
                    for fund in company.funds:
                        if fund.is_active:
                            active_funds += 1
                    total_equity = sum(fund.current_equity_balance or 0.0 for fund in company.funds)
                    companies_data.append({
                        "id": company.id,
                        "name": company.name,
                        "description": company.description,
                        "website": company.website,
                        "contact_email": company.contact_email,
                        "contact_phone": company.contact_phone,
                        "fund_count": total_funds,  # Match frontend expectation
                        "active_funds": active_funds,
                        "total_commitments": float(total_commitments) if total_commitments else 0.0,
                        "total_equity_balance": float(total_equity),
                        "created_at": company.created_at.isoformat() if company.created_at else None,
                        "updated_at": company.updated_at.isoformat() if company.updated_at else None
                    })
                # Serialize all data before closing session
                return jsonify({"companies": companies_data}), 200
            finally:
                session.close()
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/investment-companies', methods=['POST'])
    def create_investment_company():
        """Create a new investment company using domain methods"""
        try:
            session = get_db_session()
            
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['name']
                for field in required_fields:
                    if not data.get(field):
                        return jsonify({"error": f"Missing required field: {field}"}), 400
                
                # Validate name length
                if len(data['name'].strip()) < 2:
                    return jsonify({"error": "Company name must be at least 2 characters"}), 400
                
                if len(data['name'].strip()) > 255:
                    return jsonify({"error": "Company name must be less than 255 characters"}), 400
                
                # Check for duplicate names
                existing_company = session.query(InvestmentCompany).filter(InvestmentCompany.name == data['name'].strip()).first()
                if existing_company:
                    return jsonify({"error": "Investment company with this name already exists"}), 400
                
                # Create company using domain method
                company = InvestmentCompany.create(
                    name=data['name'].strip(),
                    description=data.get('description', ''),
                    website=data.get('website', ''),
                    contact_email=data.get('contact_email', ''),
                    contact_phone=data.get('contact_phone', ''),
                    session=session
                )
                
                session.commit()
                
                # Return company data
                company_data = {
                    "id": company.id,
                    "name": company.name,
                    "description": company.description,
                    "website": company.website,
                    "contact_email": company.contact_email,
                    "contact_phone": company.contact_phone,
                    "created_at": company.created_at.isoformat() if company.created_at else None,
                    "updated_at": company.updated_at.isoformat() if company.updated_at else None
                }
                
                return jsonify(company_data), 201
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/companies/<int:company_id>/funds', methods=['GET'])
    def company_funds(company_id):
        """Get list of funds for a specific investment company"""
        try:
            session = get_db_session()
            
            try:
                # Use domain methods to get company
                company = InvestmentCompany.get_by_id(company_id, session=session)
                
                if not company:
                    return jsonify({"error": "Investment company not found"}), 404
                
                # Get funds with summary data using domain methods
                funds_data = company.get_funds_with_summary(session=session)
                
                # Include company information
                company_data = {
                    "id": company.id,
                    "name": company.name,
                    "description": company.description,
                    "website": company.website,
                    "contact_email": company.contact_email,
                    "contact_phone": company.contact_phone
                }
                
                return jsonify({
                    "company": company_data,
                    "funds": funds_data
                }), 200
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/funds/<int:fund_id>', methods=['GET'])
    def fund_detail(fund_id):
        """Get detailed information about a specific fund"""
        try:
            session = get_db_session()
            
            try:
                # Use domain methods to get fund
                fund = Fund.get_by_id(fund_id, session=session)
                
                if not fund:
                    return jsonify({"error": "Fund not found"}), 404
                
                # Get fund summary data using domain methods
                fund_data = fund.get_summary_data(session=session)
                
                # Get all events using domain methods (excluding system events)
                all_events = fund.get_all_fund_events(exclude_system_events=True, session=session)
                
                events_data = []
                for event in all_events:
                    event_data = {
                        "id": event.id,
                        "event_type": event.event_type.value.upper() if event.event_type else None,
                        "event_date": event.event_date.isoformat() if event.event_date else None,
                        "amount": float(event.amount) if event.amount else None,
                        "description": event.description,
                        "reference_number": event.reference_number,
                        "distribution_type": event.distribution_type.value.upper() if event.distribution_type else None,
                        "tax_payment_type": event.tax_payment_type.value.upper() if event.tax_payment_type else None,
                        "units_purchased": float(event.units_purchased) if event.units_purchased else None,
                        "units_sold": float(event.units_sold) if event.units_sold else None,
                        "unit_price": float(event.unit_price) if event.unit_price else None,
                        "nav_per_share": float(event.nav_per_share) if event.nav_per_share else None,
                        "previous_nav_per_share": float(event.previous_nav_per_share) if event.previous_nav_per_share else None,
                        "nav_change_absolute": float(event.nav_change_absolute) if event.nav_change_absolute else None,
                        "nav_change_percentage": float(event.nav_change_percentage) if event.nav_change_percentage else None,
                        "brokerage_fee": float(event.brokerage_fee) if event.brokerage_fee else None,
                        "created_at": event.created_at.isoformat() if event.created_at else None
                    }
                    
                    # Add tax statement fields for TAX_PAYMENT and EOFY_DEBT_COST events
                    if event.event_type.value in ['tax_payment', 'eofy_debt_cost'] and event.tax_statement_id:
                        from src.tax.models import TaxStatement
                        tax_statement = session.query(TaxStatement).filter(TaxStatement.id == event.tax_statement_id).first()
                        if tax_statement:
                            # Add tax statement fields for TAX_PAYMENT events
                            if event.event_type.value == 'tax_payment':
                                event_data.update({
                                    "interest_income_amount": float(tax_statement.interest_income_amount) if tax_statement.interest_income_amount else None,
                                    "interest_income_tax_rate": float(tax_statement.interest_income_tax_rate) if tax_statement.interest_income_tax_rate else None,
                                    "dividend_franked_income_amount": float(tax_statement.dividend_franked_income_amount) if tax_statement.dividend_franked_income_amount else None,
                                    "dividend_franked_income_tax_rate": float(tax_statement.dividend_franked_income_tax_rate) if tax_statement.dividend_franked_income_tax_rate else None,
                                    "dividend_unfranked_income_amount": float(tax_statement.dividend_unfranked_income_amount) if tax_statement.dividend_unfranked_income_amount else None,
                                    "dividend_unfranked_income_tax_rate": float(tax_statement.dividend_unfranked_income_tax_rate) if tax_statement.dividend_unfranked_income_tax_rate else None,
                                    "capital_gain_income_amount": float(tax_statement.capital_gain_income_amount) if tax_statement.capital_gain_income_amount else None,
                                    "capital_gain_income_tax_rate": float(tax_statement.capital_gain_income_tax_rate) if tax_statement.capital_gain_income_tax_rate else None,
                                })
                            # Add tax statement fields for EOFY_DEBT_COST events
                            elif event.event_type.value == 'eofy_debt_cost':
                                event_data.update({
                                    "eofy_debt_interest_deduction_sum_of_daily_interest": float(tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest) if tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest else None,
                                    "eofy_debt_interest_deduction_rate": float(tax_statement.eofy_debt_interest_deduction_rate) if tax_statement.eofy_debt_interest_deduction_rate else None,
                                    "eofy_debt_interest_deduction_total_deduction": float(tax_statement.eofy_debt_interest_deduction_total_deduction) if tax_statement.eofy_debt_interest_deduction_total_deduction else None,
                                })
                    
                    events_data.append(event_data)
                
                # Structure response to match frontend expectations
                response_data = {
                    "fund": fund_data,
                    "events": events_data,
                    "statistics": {
                        "total_events": len(events_data),
                        "capital_calls": len([e for e in events_data if e["event_type"] == "CAPITAL_CALL"]),
                        "distributions": len([e for e in events_data if e["event_type"] == "DISTRIBUTION"]),
                        "nav_updates": len([e for e in events_data if e["event_type"] == "NAV_UPDATE"]),
                        "unit_purchases": len([e for e in events_data if e["event_type"] == "UNIT_PURCHASE"]),
                        "unit_sales": len([e for e in events_data if e["event_type"] == "UNIT_SALE"]),
                        "total_capital_called": sum([e["amount"] for e in events_data if e["event_type"] == "CAPITAL_CALL" and e["amount"] is not None]),
                        "total_capital_returned": sum([e["amount"] for e in events_data if e["event_type"] == "RETURN_OF_CAPITAL" and e["amount"] is not None]),
                        "total_distributions": sum([e["amount"] for e in events_data if e["event_type"] == "DISTRIBUTION" and e["amount"] is not None]),
                        "first_event_date": min([e["event_date"] for e in events_data if e["event_date"]]) if events_data else None,
                        "last_event_date": max([e["event_date"] for e in events_data if e["event_date"]]) if events_data else None
                    }
                }
                
                return jsonify(response_data), 200
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/entities', methods=['GET'])
    def entities():
        """Get list of all entities"""
        try:
            session = get_db_session()
            
            try:
                # Use domain methods to get entities
                entities = Entity.get_all(session=session)
                
                entities_data = []
                for entity in entities:
                    entities_data.append({
                        "id": entity.id,
                        "name": entity.name,
                        "description": entity.description,
                        "tax_jurisdiction": entity.tax_jurisdiction,
                        "created_at": entity.created_at.isoformat() if entity.created_at else None,
                        "updated_at": entity.updated_at.isoformat() if entity.updated_at else None
                    })
                
                return jsonify({"entities": entities_data}), 200
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/entities', methods=['POST'])
    def create_entity():
        """Create a new entity using domain methods"""
        try:
            session = get_db_session()
            
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['name']
                for field in required_fields:
                    if not data.get(field):
                        return jsonify({"error": f"Missing required field: {field}"}), 400
                
                # Validate name length
                if len(data['name'].strip()) < 2:
                    return jsonify({"error": "Entity name must be at least 2 characters"}), 400
                
                if len(data['name'].strip()) > 255:
                    return jsonify({"error": "Entity name must be less than 255 characters"}), 400
                
                # Check for duplicate names
                existing_entity = session.query(Entity).filter(Entity.name == data['name'].strip()).first()
                if existing_entity:
                    return jsonify({"error": "Entity with this name already exists"}), 400
                
                # Create entity using domain method
                entity = Entity.create(
                    name=data['name'].strip(),
                    description=data.get('description', ''),
                    tax_jurisdiction=data.get('tax_jurisdiction', 'AU'),
                    session=session
                )
                
                session.commit()
                
                # Return entity data
                entity_data = {
                    "id": entity.id,
                    "name": entity.name,
                    "description": entity.description,
                    "tax_jurisdiction": entity.tax_jurisdiction,
                    "created_at": entity.created_at.isoformat() if entity.created_at else None,
                    "updated_at": entity.updated_at.isoformat() if entity.updated_at else None
                }
                
                return jsonify(entity_data), 201
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/funds', methods=['POST'])
    def create_fund():
        """Create a new fund using domain methods"""
        try:
            session = get_db_session()
            
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['investment_company_id', 'entity_id', 'name', 'fund_type', 'tracking_type']
                for field in required_fields:
                    if not data.get(field):
                        return jsonify({"error": f"Missing required field: {field}"}), 400
                
                # Validate tracking type
                valid_tracking_types = ['nav_based', 'cost_based']
                if data['tracking_type'] not in valid_tracking_types:
                    return jsonify({"error": f"Invalid tracking_type: {data['tracking_type']}. Must be one of: {valid_tracking_types}"}), 400
                
                # Get investment company and entity using domain methods
                company = InvestmentCompany.get_by_id(data['investment_company_id'], session=session)
                if not company:
                    return jsonify({"error": "Investment company not found"}), 404
                
                entity = Entity.get_by_id(data['entity_id'], session=session)
                if not entity:
                    return jsonify({"error": "Entity not found"}), 404
                
                # Create fund using domain method
                fund = company.create_fund(
                    entity=entity,
                    name=data['name'],
                    fund_type=data['fund_type'],
                    tracking_type=data['tracking_type'],
                    currency=data.get('currency', 'AUD'),
                    description=data.get('description'),
                    commitment_amount=data.get('commitment_amount'),
                    expected_irr=data.get('expected_irr'),
                    expected_duration_months=data.get('expected_duration_months'),
                    session=session
                )
                
                session.commit()
                
                # Return fund data
                fund_data = {
                    "id": fund.id,
                    "name": fund.name,
                    "fund_type": fund.fund_type,
                    "tracking_type": fund.tracking_type.value if fund.tracking_type else None,
                    "currency": fund.currency,
                    "description": fund.description,
                    "commitment_amount": fund.commitment_amount,
                    "expected_irr": fund.expected_irr,
                    "expected_duration_months": fund.expected_duration_months,
                    "investment_company_id": fund.investment_company_id,
                    "entity_id": fund.entity_id,
                    "created_at": fund.created_at.isoformat() if fund.created_at else None
                }
                
                return jsonify(fund_data), 201
                
            finally:
                session.close()
                
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app 