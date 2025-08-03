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
from src.fund.models import Fund, FundType, FundEvent

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
                
                # Get tax statements for this fund
                from src.tax.models import TaxStatement
                tax_statements = session.query(TaxStatement).filter(
                    TaxStatement.fund_id == fund_id
                ).order_by(TaxStatement.financial_year.desc()).all()
                
                tax_statements_data = []
                for statement in tax_statements:
                    statement_data = {
                        "id": statement.id,
                        "entity_id": statement.entity_id,
                        "financial_year": statement.financial_year,
                        "statement_date": statement.statement_date.isoformat() if statement.statement_date else None,
                        "tax_payment_date": statement.get_tax_payment_date().isoformat() if statement.get_tax_payment_date() else None,
                        "eofy_debt_interest_deduction_rate": float(statement.eofy_debt_interest_deduction_rate) if statement.eofy_debt_interest_deduction_rate else None,
                        "interest_received_in_cash": float(statement.interest_received_in_cash) if statement.interest_received_in_cash else None,
                        "interest_receivable_this_fy": float(statement.interest_receivable_this_fy) if statement.interest_receivable_this_fy else None,
                        "interest_receivable_prev_fy": float(statement.interest_receivable_prev_fy) if statement.interest_receivable_prev_fy else None,
                        "interest_non_resident_withholding_tax_from_statement": float(statement.interest_non_resident_withholding_tax_from_statement) if statement.interest_non_resident_withholding_tax_from_statement else None,
                        "interest_income_tax_rate": float(statement.interest_income_tax_rate) if statement.interest_income_tax_rate else None,
                        "interest_income_amount": float(statement.interest_income_amount) if statement.interest_income_amount else None,
                        "interest_tax_amount": float(statement.interest_tax_amount) if statement.interest_tax_amount else None,
                        "dividend_franked_income_amount": float(statement.dividend_franked_income_amount) if statement.dividend_franked_income_amount else None,
                        "dividend_unfranked_income_amount": float(statement.dividend_unfranked_income_amount) if statement.dividend_unfranked_income_amount else None,
                        "dividend_franked_income_tax_rate": float(statement.dividend_franked_income_tax_rate) if statement.dividend_franked_income_tax_rate else None,
                        "dividend_unfranked_income_tax_rate": float(statement.dividend_unfranked_income_tax_rate) if statement.dividend_unfranked_income_tax_rate else None,
                        "dividend_franked_tax_amount": float(statement.dividend_franked_tax_amount) if statement.dividend_franked_tax_amount else None,
                        "dividend_unfranked_tax_amount": float(statement.dividend_unfranked_tax_amount) if statement.dividend_unfranked_tax_amount else None,
                        "capital_gain_income_amount": float(statement.capital_gain_income_amount) if statement.capital_gain_income_amount else None,
                        "capital_gain_income_tax_rate": float(statement.capital_gain_income_tax_rate) if statement.capital_gain_income_tax_rate else None,
                        "capital_gain_tax_amount": float(statement.capital_gain_tax_amount) if statement.capital_gain_tax_amount else None,
                        "eofy_debt_interest_deduction_sum_of_daily_interest": float(statement.eofy_debt_interest_deduction_sum_of_daily_interest) if statement.eofy_debt_interest_deduction_sum_of_daily_interest else None,
                        "eofy_debt_interest_deduction_total_deduction": float(statement.eofy_debt_interest_deduction_total_deduction) if statement.eofy_debt_interest_deduction_total_deduction else None,
                        "non_resident": statement.non_resident,
                        "accountant": statement.accountant,
                        "notes": statement.notes,
                        "created_at": statement.created_at.isoformat() if statement.created_at else None,
                        "updated_at": statement.updated_at.isoformat() if statement.updated_at else None
                    }
                    tax_statements_data.append(statement_data)
                
                # Structure response to match frontend expectations
                response_data = {
                    "fund": fund_data,
                    "events": events_data,
                    "tax_statements": tax_statements_data,
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
                        "last_event_date": max([e["event_date"] for e in events_data if e["event_date"]]) if events_data else None,
                        "total_tax_statements": len(tax_statements_data)
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

    @app.route('/api/funds/<int:fund_id>/events', methods=['POST'])
    def create_fund_event(fund_id):
        """Create a new cash flow event (capital call, distribution, unit purchase, unit sale) for a fund."""
        try:
            session = get_db_session()
            try:
                data = request.get_json()
                # Validate event_type
                event_type = data.get('event_type')
                if not event_type:
                    return jsonify({"error": "Missing required field: event_type"}), 400
                # Get fund
                fund = Fund.get_by_id(fund_id, session=session)
                if not fund:
                    return jsonify({"error": "Fund not found"}), 404
                # Parse event_date
                event_date = data.get('event_date')
                if not event_date:
                    return jsonify({"error": "Missing required field: event_date"}), 400
                from datetime import datetime
                try:
                    event_date = datetime.fromisoformat(event_date).date()
                except Exception:
                    return jsonify({"error": "Invalid event_date format. Use ISO format (YYYY-MM-DD)."}), 400
                # Route to correct domain method
                created_event = None
                if event_type.upper() == 'CAPITAL_CALL' and fund.tracking_type.value == 'cost_based':
                    amount = data.get('amount')
                    if amount is None:
                        return jsonify({"error": "Missing required field: amount for capital call"}), 400
                    created_event = fund.add_capital_call(
                        amount=amount,
                        date=event_date,
                        description=data.get('description'),
                        reference_number=data.get('reference_number'),
                        session=session
                    )
                elif event_type.upper() == 'DISTRIBUTION':
                    distribution_type = data.get('distribution_type')
                    sub_distribution_type = data.get('sub_distribution_type')

                    if distribution_type == 'INTEREST':
                        gross_interest = data.get('gross_interest')
                        net_interest = data.get('net_interest')
                        withholding_amount = data.get('withholding_amount')
                        withholding_rate = data.get('withholding_rate')
                        from src.fund.models import DistributionType
                        if (withholding_amount is not None) or (withholding_rate is not None):
                            created_event, _ = fund.add_interest_distribution_with_withholding_tax(
                                event_date=event_date,
                                gross_interest=gross_interest if gross_interest is not None else None,
                                net_interest=net_interest if net_interest is not None else None,
                                withholding_amount=withholding_amount if withholding_amount is not None else None,
                                withholding_rate=withholding_rate if withholding_rate is not None else None,
                                description=data.get('description'),
                                reference_number=data.get('reference_number'),
                                session=session
                            )
                        else:
                            # No withholding tax: use new method
                            created_event = fund.add_interest_distribution_without_withholding_tax(
                                event_date=event_date,
                                gross_interest=gross_interest if gross_interest is not None else data.get('amount'),
                                description=data.get('description'),
                                reference_number=data.get('reference_number'),
                                session=session
                            )
                    else:
                        amount = data.get('amount')
                        if amount is None:
                            return jsonify({"error": "Missing required field: amount for distribution"}), 400
                        # Enforce explicit franked/unfranked for dividends
                        if distribution_type and distribution_type.upper().startswith('DIVIDEND'):
                            if distribution_type not in ("DIVIDEND_FRANKED", "DIVIDEND_UNFRANKED"):
                                return jsonify({"error": "Dividend distributions must be either DIVIDEND_FRANKED or DIVIDEND_UNFRANKED."}), 400
                        created_event = fund.add_distribution(
                            amount=amount,
                            event_date=event_date,
                            distribution_type=distribution_type,
                            description=data.get('description'),
                            reference_number=data.get('reference_number'),
                            session=session
                        )
                elif event_type.upper() == 'UNIT_PURCHASE' and fund.tracking_type.value == 'nav_based':
                    units = data.get('units_purchased')
                    price = data.get('unit_price')
                    if units is None or price is None:
                        return jsonify({"error": "Missing required fields: units_purchased and unit_price for unit purchase"}), 400
                    created_event = fund.add_unit_purchase(
                        units=units,
                        price=price,
                        date=event_date,
                        brokerage_fee=data.get('brokerage_fee', 0.0),
                        description=data.get('description'),
                        reference_number=data.get('reference_number'),
                        session=session
                    )
                elif event_type.upper() == 'UNIT_SALE' and fund.tracking_type.value == 'nav_based':
                    units = data.get('units_sold')
                    price = data.get('unit_price')
                    if units is None or price is None:
                        return jsonify({"error": "Missing required fields: units_sold and unit_price for unit sale"}), 400
                    created_event = fund.add_unit_sale(
                        units=units,
                        price=price,
                        date=event_date,
                        brokerage_fee=data.get('brokerage_fee', 0.0),
                        description=data.get('description'),
                        reference_number=data.get('reference_number'),
                        session=session
                    )
                elif event_type.upper() == 'NAV_UPDATE' and fund.tracking_type.value == 'nav_based':
                    nav_per_share = data.get('nav_per_share')
                    if nav_per_share is None:
                        return jsonify({"error": "Missing required field: nav_per_share for NAV update"}), 400
                    created_event = fund.add_nav_update(
                        nav_per_share=nav_per_share,
                        date=event_date,
                        description=data.get('description'),
                        reference_number=data.get('reference_number'),
                        session=session
                    )
                elif event_type.upper() == 'RETURN_OF_CAPITAL' and fund.tracking_type.value == 'cost_based':
                    amount = data.get('amount')
                    if amount is None:
                        return jsonify({"error": "Missing required field: amount for return of capital"}), 400
                    created_event = fund.add_return_of_capital(
                        amount=amount,
                        date=event_date,
                        description=data.get('description'),
                        reference_number=data.get('reference_number'),
                        session=session
                    )
                else:
                    return jsonify({"error": f"Unsupported event_type '{event_type}' for fund tracking type '{fund.tracking_type.value}'"}), 400
                session.commit()
                # Serialize event for response
                event_response = {
                    "id": created_event.id,
                    "event_type": created_event.event_type.value.upper() if created_event.event_type else None,
                    "event_date": created_event.event_date.isoformat() if created_event.event_date else None,
                    "amount": float(created_event.amount) if created_event.amount is not None else None,
                    "description": created_event.description,
                    "reference_number": created_event.reference_number,
                    "distribution_type": created_event.distribution_type.value.upper() if created_event.distribution_type else None,
                    "units_purchased": float(getattr(created_event, 'units_purchased', 0.0)) if hasattr(created_event, 'units_purchased') and created_event.units_purchased is not None else None,
                    "units_sold": float(getattr(created_event, 'units_sold', 0.0)) if hasattr(created_event, 'units_sold') and created_event.units_sold is not None else None,
                    "unit_price": float(getattr(created_event, 'unit_price', 0.0)) if hasattr(created_event, 'unit_price') and created_event.unit_price is not None else None,
                    "brokerage_fee": float(getattr(created_event, 'brokerage_fee', 0.0)) if hasattr(created_event, 'brokerage_fee') and created_event.brokerage_fee is not None else None,
                    "created_at": created_event.created_at.isoformat() if created_event.created_at else None
                }
                return jsonify(event_response), 201
            finally:
                session.close()
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/funds/<int:fund_id>/events/<int:event_id>', methods=['DELETE'])
    def delete_fund_event(fund_id, event_id):
        """Delete a specific fund event."""
        try:
            session = get_db_session()
            try:
                fund = Fund.get_by_id(fund_id, session=session)
                if not fund:
                    return jsonify({"error": "Fund not found"}), 404
                # Correct event lookup
                event = session.query(FundEvent).filter_by(id=event_id, fund_id=fund_id).first()
                if not event:
                    return jsonify({"error": "Event not found"}), 404
                # Only allow deleting user-editable events
                if event.event_type.value.upper() in [
                    'TAX_PAYMENT', 'DAILY_RISK_FREE_INTEREST_CHARGE', 'EOFY_DEBT_COST', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER']:
                    return jsonify({"error": "Cannot delete system or tax events from the UI"}), 400
                fund.delete_event(event_id, session=session)
                session.commit()
                return '', 204
            finally:
                session.close()
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/funds/<int:fund_id>/events/<int:event_id>', methods=['PUT'])
    def update_fund_event(fund_id, event_id):
        """Update a specific fund event."""
        try:
            session = get_db_session()
            try:
                data = request.get_json()
                fund = Fund.get_by_id(fund_id, session=session)
                if not fund:
                    return jsonify({"error": "Fund not found"}), 404
                # Correct event lookup
                event = session.query(FundEvent).filter_by(id=event_id, fund_id=fund_id).first()
                if not event:
                    return jsonify({"error": "Event not found"}), 404
                event_type = event.event_type.value.upper() if event.event_type else None
                updated_event = None
                # Parse event_date if present
                event_date = data.get('event_date')
                if event_date:
                    from datetime import datetime
                    try:
                        event_date = datetime.fromisoformat(event_date).date()
                    except Exception:
                        return jsonify({"error": "Invalid event_date format. Use ISO format (YYYY-MM-DD)."}), 400
                else:
                    event_date = None
                # Route to correct domain method
                if event_type == 'CAPITAL_CALL' and fund.tracking_type.value == 'cost_based':
                    updated_event = fund.update_capital_call(
                        event_id=event_id,
                        amount=data.get('amount'),
                        date=event_date,
                        description=data.get('description'),
                        reference_number=data.get('reference_number'),
                        session=session
                    )
                elif event_type == 'RETURN_OF_CAPITAL' and fund.tracking_type.value == 'cost_based':
                    updated_event = fund.update_return_of_capital(
                        event_id=event_id,
                        amount=data.get('amount'),
                        date=event_date,
                        description=data.get('description'),
                        reference_number=data.get('reference_number'),
                        session=session
                    )
                elif event_type == 'UNIT_PURCHASE' and fund.tracking_type.value == 'nav_based':
                    updated_event = fund.update_unit_purchase(
                        event_id=event_id,
                        units=data.get('units_purchased'),
                        price=data.get('unit_price'),
                        date=event_date,
                        brokerage_fee=data.get('brokerage_fee'),
                        description=data.get('description'),
                        reference_number=data.get('reference_number'),
                        session=session
                    )
                elif event_type == 'UNIT_SALE' and fund.tracking_type.value == 'nav_based':
                    updated_event = fund.update_unit_sale(
                        event_id=event_id,
                        units=data.get('units_sold'),
                        price=data.get('unit_price'),
                        date=event_date,
                        brokerage_fee=data.get('brokerage_fee'),
                        description=data.get('description'),
                        reference_number=data.get('reference_number'),
                        session=session
                    )
                elif event_type == 'NAV_UPDATE' and fund.tracking_type.value == 'nav_based':
                    updated_event = fund.update_nav_update(
                        event_id=event_id,
                        nav_per_share=data.get('nav_per_share'),
                        date=event_date,
                        description=data.get('description'),
                        reference_number=data.get('reference_number'),
                        session=session
                    )
                elif event_type == 'DISTRIBUTION':
                    # Interest distribution with withholding tax
                    if event.distribution_type and event.distribution_type.value.upper() == 'INTEREST' and (
                        data.get('withholding_amount') is not None or data.get('withholding_rate') is not None):
                        updated_event = fund.update_interest_distribution_with_withholding_tax(
                            event_id=event_id,
                            gross_interest=data.get('gross_interest'),
                            net_interest=data.get('net_interest'),
                            withholding_amount=data.get('withholding_amount'),
                            withholding_rate=data.get('withholding_rate'),
                            description=data.get('description'),
                            reference_number=data.get('reference_number'),
                            session=session
                        )
                    else:
                        updated_event = fund.update_distribution(
                            event_id=event_id,
                            amount=data.get('amount'),
                            distribution_type=data.get('distribution_type'),
                            description=data.get('description'),
                            reference_number=data.get('reference_number'),
                            session=session
                        )
                else:
                    return jsonify({"error": f"Editing this event type is not supported."}), 400
                session.commit()
                # Serialize updated event for response
                event_response = {
                    "id": updated_event.id,
                    "event_type": updated_event.event_type.value.upper() if updated_event.event_type else None,
                    "event_date": updated_event.event_date.isoformat() if updated_event.event_date else None,
                    "amount": float(updated_event.amount) if updated_event.amount is not None else None,
                    "description": updated_event.description,
                    "reference_number": updated_event.reference_number,
                    "distribution_type": updated_event.distribution_type.value.upper() if updated_event.distribution_type else None,
                    "units_purchased": float(getattr(updated_event, 'units_purchased', 0.0)) if hasattr(updated_event, 'units_purchased') and updated_event.units_purchased is not None else None,
                    "units_sold": float(getattr(updated_event, 'units_sold', 0.0)) if hasattr(updated_event, 'units_sold') and updated_event.units_sold is not None else None,
                    "unit_price": float(getattr(updated_event, 'unit_price', 0.0)) if hasattr(updated_event, 'unit_price') and updated_event.unit_price is not None else None,
                    "brokerage_fee": float(getattr(updated_event, 'brokerage_fee', 0.0)) if hasattr(updated_event, 'brokerage_fee') and updated_event.brokerage_fee is not None else None,
                    "nav_per_share": float(getattr(updated_event, 'nav_per_share', 0.0)) if hasattr(updated_event, 'nav_per_share') and updated_event.nav_per_share is not None else None,
                    "created_at": updated_event.created_at.isoformat() if updated_event.created_at else None
                }
                return jsonify(event_response), 200
            finally:
                session.close()
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/funds/<int:fund_id>/tax-statements', methods=['POST'])
    def create_tax_statement(fund_id):
        """Create a new tax statement for a fund"""
        try:
            session = get_db_session()
            
            try:
                # Get fund and validate it exists
                fund = Fund.get_by_id(fund_id, session=session)
                if not fund:
                    return jsonify({"error": "Fund not found"}), 404
                
                # Get request data
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                # Extract required fields
                entity_id = data.get('entity_id')
                financial_year = data.get('financial_year')
                statement_date = data.get('statement_date')
                eofy_debt_interest_deduction_rate = data.get('eofy_debt_interest_deduction_rate')
                
                # Validate required fields
                if not entity_id:
                    return jsonify({"error": "Entity ID is required"}), 400
                if not financial_year:
                    return jsonify({"error": "Financial year is required"}), 400
                if not statement_date:
                    return jsonify({"error": "Statement date is required"}), 400
                if eofy_debt_interest_deduction_rate is None:
                    return jsonify({"error": "End of financial year debt interest deduction rate is required"}), 400
                
                # Validate entity exists
                entity = session.query(Entity).filter(Entity.id == entity_id).first()
                if not entity:
                    return jsonify({"error": "Entity not found"}), 404
                
                # Parse statement date
                try:
                    if isinstance(statement_date, str):
                        statement_date = datetime.strptime(statement_date, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({"error": "Invalid statement date format. Use YYYY-MM-DD"}), 400
                
                # Validate numeric fields
                numeric_fields = [
                    'eofy_debt_interest_deduction_rate',
                    'interest_received_in_cash',
                    'interest_receivable_this_fy',
                    'interest_receivable_prev_fy',
                    'interest_non_resident_withholding_tax_from_statement',
                    'interest_income_tax_rate',
                    'dividend_franked_income_amount',
                    'dividend_unfranked_income_amount',
                    'dividend_franked_income_tax_rate',
                    'dividend_unfranked_income_tax_rate',
                    'capital_gain_income_amount',
                    'capital_gain_income_tax_rate'
                ]
                
                for field in numeric_fields:
                    value = data.get(field)
                    if value is not None:
                        try:
                            float_value = float(value)
                            if float_value < 0:
                                return jsonify({"error": f"{field.replace('_', ' ').title()} must be non-negative"}), 400
                            data[field] = float_value
                        except (ValueError, TypeError):
                            return jsonify({"error": f"{field.replace('_', ' ').title()} must be a valid number"}), 400
                
                # Validate percentage fields (0-100%)
                percentage_fields = [
                    'eofy_debt_interest_deduction_rate',
                    'interest_income_tax_rate',
                    'dividend_franked_income_tax_rate',
                    'dividend_unfranked_income_tax_rate',
                    'capital_gain_income_tax_rate'
                ]
                
                for field in percentage_fields:
                    value = data.get(field)
                    if value is not None:
                        if not (0 <= float(value) <= 100):
                            return jsonify({"error": f"{field.replace('_', ' ').title()} must be between 0 and 100"}), 400
                
                # Create tax statement using domain method
                from src.tax.models import TaxStatement
                
                # Check for existing tax statement
                existing_statement = session.query(TaxStatement).filter(
                    TaxStatement.fund_id == fund_id,
                    TaxStatement.entity_id == entity_id,
                    TaxStatement.financial_year == financial_year
                ).first()
                
                if existing_statement:
                    return jsonify({"error": f"Tax statement already exists for fund {fund_id}, entity {entity_id}, FY {financial_year}"}), 400
                
                # Create new tax statement
                tax_statement = TaxStatement(
                    fund_id=fund_id,
                    entity_id=entity_id,
                    financial_year=financial_year,
                    statement_date=statement_date,
                    eofy_debt_interest_deduction_rate=data.get('eofy_debt_interest_deduction_rate', 0.0),
                    interest_received_in_cash=data.get('interest_received_in_cash', 0.0),
                    interest_receivable_this_fy=data.get('interest_receivable_this_fy', 0.0),
                    interest_receivable_prev_fy=data.get('interest_receivable_prev_fy', 0.0),
                    interest_non_resident_withholding_tax_from_statement=data.get('interest_non_resident_withholding_tax_from_statement', 0.0),
                    interest_income_tax_rate=data.get('interest_income_tax_rate', 0.0),
                    dividend_franked_income_amount=data.get('dividend_franked_income_amount', 0.0),
                    dividend_unfranked_income_amount=data.get('dividend_unfranked_income_amount', 0.0),
                    dividend_franked_income_tax_rate=data.get('dividend_franked_income_tax_rate', 0.0),
                    dividend_unfranked_income_tax_rate=data.get('dividend_unfranked_income_tax_rate', 0.0),
                    capital_gain_income_amount=data.get('capital_gain_income_amount', 0.0),
                    capital_gain_income_tax_rate=data.get('capital_gain_income_tax_rate', 0.0),
                    accountant=data.get('accountant'),
                    notes=data.get('notes'),
                    non_resident=data.get('non_resident', False)
                )
                
                # Calculate derived fields
                tax_statement.calculate_interest_income_amount(session=session)
                tax_statement.calculate_interest_tax_amount()
                tax_statement.calculate_dividend_totals(session=session)
                tax_statement.calculate_dividend_franked_tax_amount()
                tax_statement.calculate_dividend_unfranked_tax_amount()
                tax_statement.calculate_capital_gain_totals(session=session)
                tax_statement.calculate_capital_gain_tax_amount()
                tax_statement.calculate_eofy_debt_interest_deduction_total_deduction()
                
                # Save to database
                session.add(tax_statement)
                session.commit()
                
                # Create tax payment events
                from src.tax.events import TaxEventManager
                TaxEventManager.create_or_update_tax_events(tax_statement, session=session)
                
                # Update fund status after tax statement creation
                fund.update_status_after_tax_statement(session=session)
                
                # Return created tax statement
                response_data = {
                    "id": tax_statement.id,
                    "fund_id": tax_statement.fund_id,
                    "entity_id": tax_statement.entity_id,
                    "financial_year": tax_statement.financial_year,
                    "statement_date": tax_statement.statement_date.isoformat() if tax_statement.statement_date else None,
                    "tax_payment_date": tax_statement.get_tax_payment_date().isoformat() if tax_statement.get_tax_payment_date() else None,
                    "eofy_debt_interest_deduction_rate": float(tax_statement.eofy_debt_interest_deduction_rate) if tax_statement.eofy_debt_interest_deduction_rate else None,
                    "interest_received_in_cash": float(tax_statement.interest_received_in_cash) if tax_statement.interest_received_in_cash else None,
                    "interest_receivable_this_fy": float(tax_statement.interest_receivable_this_fy) if tax_statement.interest_receivable_this_fy else None,
                    "interest_receivable_prev_fy": float(tax_statement.interest_receivable_prev_fy) if tax_statement.interest_receivable_prev_fy else None,
                    "interest_non_resident_withholding_tax_from_statement": float(tax_statement.interest_non_resident_withholding_tax_from_statement) if tax_statement.interest_non_resident_withholding_tax_from_statement else None,
                    "interest_income_tax_rate": float(tax_statement.interest_income_tax_rate) if tax_statement.interest_income_tax_rate else None,
                    "interest_income_amount": float(tax_statement.interest_income_amount) if tax_statement.interest_income_amount else None,
                    "interest_tax_amount": float(tax_statement.interest_tax_amount) if tax_statement.interest_tax_amount else None,
                    "dividend_franked_income_amount": float(tax_statement.dividend_franked_income_amount) if tax_statement.dividend_franked_income_amount else None,
                    "dividend_unfranked_income_amount": float(tax_statement.dividend_unfranked_income_amount) if tax_statement.dividend_unfranked_income_amount else None,
                    "dividend_franked_income_tax_rate": float(tax_statement.dividend_franked_income_tax_rate) if tax_statement.dividend_franked_income_tax_rate else None,
                    "dividend_unfranked_income_tax_rate": float(tax_statement.dividend_unfranked_income_tax_rate) if tax_statement.dividend_unfranked_income_tax_rate else None,
                    "dividend_franked_tax_amount": float(tax_statement.dividend_franked_tax_amount) if tax_statement.dividend_franked_tax_amount else None,
                    "dividend_unfranked_tax_amount": float(tax_statement.dividend_unfranked_tax_amount) if tax_statement.dividend_unfranked_tax_amount else None,
                    "capital_gain_income_amount": float(tax_statement.capital_gain_income_amount) if tax_statement.capital_gain_income_amount else None,
                    "capital_gain_income_tax_rate": float(tax_statement.capital_gain_income_tax_rate) if tax_statement.capital_gain_income_tax_rate else None,
                    "capital_gain_tax_amount": float(tax_statement.capital_gain_tax_amount) if tax_statement.capital_gain_tax_amount else None,
                    "eofy_debt_interest_deduction_sum_of_daily_interest": float(tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest) if tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest else None,
                    "eofy_debt_interest_deduction_total_deduction": float(tax_statement.eofy_debt_interest_deduction_total_deduction) if tax_statement.eofy_debt_interest_deduction_total_deduction else None,
                    "non_resident": tax_statement.non_resident,
                    "accountant": tax_statement.accountant,
                    "notes": tax_statement.notes,
                    "created_at": tax_statement.created_at.isoformat() if tax_statement.created_at else None,
                    "updated_at": tax_statement.updated_at.isoformat() if tax_statement.updated_at else None
                }
                
                return jsonify(response_data), 201
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/funds/<int:fund_id>/tax-statements', methods=['GET'])
    def get_fund_tax_statements(fund_id):
        """Get all tax statements for a fund"""
        try:
            session = get_db_session()
            
            try:
                # Get fund and validate it exists
                fund = Fund.get_by_id(fund_id, session=session)
                if not fund:
                    return jsonify({"error": "Fund not found"}), 404
                
                # Get tax statements for this fund
                from src.tax.models import TaxStatement
                tax_statements = session.query(TaxStatement).filter(
                    TaxStatement.fund_id == fund_id
                ).order_by(TaxStatement.financial_year.desc()).all()
                
                statements_data = []
                for statement in tax_statements:
                    statement_data = {
                        "id": statement.id,
                        "entity_id": statement.entity_id,
                        "financial_year": statement.financial_year,
                        "statement_date": statement.statement_date.isoformat() if statement.statement_date else None,
                        "tax_payment_date": statement.get_tax_payment_date().isoformat() if statement.get_tax_payment_date() else None,
                        "eofy_debt_interest_deduction_rate": float(statement.eofy_debt_interest_deduction_rate) if statement.eofy_debt_interest_deduction_rate else None,
                        "interest_received_in_cash": float(statement.interest_received_in_cash) if statement.interest_received_in_cash else None,
                        "interest_receivable_this_fy": float(statement.interest_receivable_this_fy) if statement.interest_receivable_this_fy else None,
                        "interest_receivable_prev_fy": float(statement.interest_receivable_prev_fy) if statement.interest_receivable_prev_fy else None,
                        "interest_non_resident_withholding_tax_from_statement": float(statement.interest_non_resident_withholding_tax_from_statement) if statement.interest_non_resident_withholding_tax_from_statement else None,
                        "interest_income_tax_rate": float(statement.interest_income_tax_rate) if statement.interest_income_tax_rate else None,
                        "interest_income_amount": float(statement.interest_income_amount) if statement.interest_income_amount else None,
                        "interest_tax_amount": float(statement.interest_tax_amount) if statement.interest_tax_amount else None,
                        "dividend_franked_income_amount": float(statement.dividend_franked_income_amount) if statement.dividend_franked_income_amount else None,
                        "dividend_unfranked_income_amount": float(statement.dividend_unfranked_income_amount) if statement.dividend_unfranked_income_amount else None,
                        "dividend_franked_income_tax_rate": float(statement.dividend_franked_income_tax_rate) if statement.dividend_franked_income_tax_rate else None,
                        "dividend_unfranked_income_tax_rate": float(statement.dividend_unfranked_income_tax_rate) if statement.dividend_unfranked_income_tax_rate else None,
                        "dividend_franked_tax_amount": float(statement.dividend_franked_tax_amount) if statement.dividend_franked_tax_amount else None,
                        "dividend_unfranked_tax_amount": float(statement.dividend_unfranked_tax_amount) if statement.dividend_unfranked_tax_amount else None,
                        "capital_gain_income_amount": float(statement.capital_gain_income_amount) if statement.capital_gain_income_amount else None,
                        "capital_gain_income_tax_rate": float(statement.capital_gain_income_tax_rate) if statement.capital_gain_income_tax_rate else None,
                        "capital_gain_tax_amount": float(statement.capital_gain_tax_amount) if statement.capital_gain_tax_amount else None,
                        "eofy_debt_interest_deduction_sum_of_daily_interest": float(statement.eofy_debt_interest_deduction_sum_of_daily_interest) if statement.eofy_debt_interest_deduction_sum_of_daily_interest else None,
                        "eofy_debt_interest_deduction_total_deduction": float(statement.eofy_debt_interest_deduction_total_deduction) if statement.eofy_debt_interest_deduction_total_deduction else None,
                        "non_resident": statement.non_resident,
                        "accountant": statement.accountant,
                        "notes": statement.notes,
                        "created_at": statement.created_at.isoformat() if statement.created_at else None,
                        "updated_at": statement.updated_at.isoformat() if statement.updated_at else None
                    }
                    statements_data.append(statement_data)
                
                return jsonify({"tax_statements": statements_data}), 200
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app 