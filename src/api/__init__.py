from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc, create_engine, text
from sqlalchemy.orm import joinedload, sessionmaker, scoped_session
import os

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
                # Direct SQL queries to avoid model import issues
                total_funds = session.execute(text("SELECT COUNT(*) FROM funds")).scalar()
                active_funds = session.execute(text("SELECT COUNT(*) FROM funds WHERE current_equity_balance > 0")).scalar()
                total_equity = session.execute(text("SELECT SUM(current_equity_balance) FROM funds")).scalar() or 0.0
                total_avg_equity = session.execute(text("SELECT SUM(average_equity_balance) FROM funds")).scalar() or 0.0
                
                # Recent events count
                thirty_days_ago = date.today() - timedelta(days=30)
                recent_events = session.execute(
                    text("SELECT COUNT(*) FROM fund_events WHERE event_date >= :date"), 
                    {"date": thirty_days_ago}
                ).scalar()
                
                # Tax statements count
                total_tax_statements = session.execute(text("SELECT COUNT(*) FROM tax_statements")).scalar()
                
                summary = {
                    "total_funds": total_funds,
                    "active_funds": active_funds,
                    "total_equity_balance": float(total_equity),
                    "total_average_equity_balance": float(total_avg_equity),
                    "recent_events_count": recent_events,
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
                # Query funds with related data using SQL
                funds_query = text("""
                    SELECT 
                        f.id, f.name, f.fund_type, f.tracking_type, f.currency,
                        f.current_equity_balance, f.average_equity_balance, f.is_active,
                        f.created_at, ic.name as investment_company_name, e.name as entity_name
                    FROM funds f
                    JOIN investment_companies ic ON f.investment_company_id = ic.id
                    JOIN entities e ON f.entity_id = e.id
                """)
                
                funds_result = session.execute(funds_query).fetchall()
                
                fund_data = []
                for fund in funds_result:
                    # Get recent events count for this fund (excluding system events)
                    recent_events_count = session.execute(
                        text("SELECT COUNT(*) FROM fund_events WHERE fund_id = :fund_id AND event_date >= :date AND event_type != 'DAILY_RISK_FREE_INTEREST_CHARGE'"),
                        {"fund_id": fund.id, "date": date.today() - timedelta(days=30)}
                    ).scalar()
                    
                    fund_data.append({
                        "id": fund.id,
                        "name": fund.name,
                        "fund_type": fund.fund_type,
                        "tracking_type": fund.tracking_type,
                        "currency": fund.currency,
                        "current_equity_balance": float(fund.current_equity_balance) if fund.current_equity_balance else 0.0,
                        "average_equity_balance": float(fund.average_equity_balance) if fund.average_equity_balance else 0.0,
                        "is_active": fund.is_active if fund.is_active is not None else True,
                        "investment_company": fund.investment_company_name or "Unknown",
                        "entity": fund.entity_name or "Unknown",
                        "recent_events_count": recent_events_count,
                        "created_at": fund.created_at if isinstance(fund.created_at, str) else fund.created_at.isoformat() if fund.created_at else None
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
                # Get recent events with fund information (excluding system events)
                events_query = text("""
                    SELECT 
                        fe.id, fe.event_type, fe.event_date, fe.amount, 
                        fe.description, fe.reference_number, f.name as fund_name
                    FROM fund_events fe
                    JOIN funds f ON fe.fund_id = f.id
                    WHERE fe.event_type != 'DAILY_RISK_FREE_INTEREST_CHARGE'
                    ORDER BY fe.event_date DESC
                    LIMIT 10
                """)
                
                events_result = session.execute(events_query).fetchall()
                
                event_data = []
                for event in events_result:
                    event_data.append({
                        "id": event.id,
                        "fund_name": event.fund_name or "Unknown Fund",
                        "event_type": event.event_type or "unknown",
                        "event_date": event.event_date if isinstance(event.event_date, str) else event.event_date.isoformat() if event.event_date else None,
                        "amount": float(event.amount) if event.amount else None,
                        "description": event.description,
                        "reference_number": event.reference_number
                    })
                
                return jsonify({"events": event_data}), 200
                
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
                # Get performance data with fund IDs (excluding system events)
                query = text("""
                    SELECT 
                        f.id as fund_id,
                        f.name as fund_name,
                        f.current_equity_balance as current_equity,
                        f.average_equity_balance as average_equity,
                        COUNT(fe.id) as total_events,
                        MAX(fe.event_date) as last_event_date
                    FROM funds f
                    LEFT JOIN fund_events fe ON f.id = fe.fund_id AND fe.event_type != 'DAILY_RISK_FREE_INTEREST_CHARGE'
                    GROUP BY f.id, f.name, f.current_equity_balance, f.average_equity_balance
                    ORDER BY f.name
                """)
                
                result = session.execute(query).fetchall()
                
                performance_data = []
                for row in result:
                    performance_data.append({
                        "fund_id": row.fund_id,
                        "fund_name": row.fund_name,
                        "current_equity": float(row.current_equity) if row.current_equity else 0.0,
                        "average_equity": float(row.average_equity) if row.average_equity else 0.0,
                        "total_events": row.total_events,
                        "last_event_date": row.last_event_date if isinstance(row.last_event_date, str) else row.last_event_date.isoformat() if row.last_event_date else None
                    })
                
                return jsonify({"performance": performance_data}), 200
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/funds/<int:fund_id>', methods=['GET'])
    def fund_detail(fund_id):
        """Get detailed information for a specific fund"""
        try:
            session = get_db_session()
            
            try:
                # Get fund with related data
                fund_query = text("""
                    SELECT 
                        f.id, f.name, f.fund_type, f.tracking_type, f.currency,
                        f.current_equity_balance, f.average_equity_balance, f.is_active,
                        f.commitment_amount, f.expected_irr, f.expected_duration_months,
                        f.description, f.created_at, f.updated_at,
                        ic.name as investment_company_name, e.name as entity_name
                    FROM funds f
                    JOIN investment_companies ic ON f.investment_company_id = ic.id
                    JOIN entities e ON f.entity_id = e.id
                    WHERE f.id = :fund_id
                """)
                
                fund_result = session.execute(fund_query, {"fund_id": fund_id}).fetchone()
                
                if not fund_result:
                    return jsonify({"error": "Fund not found"}), 404
                
                # Get fund events with tax statement data for TAX_PAYMENT and FY_DEBT_COST events
                events_query = text("""
                    SELECT 
                        fe.id, fe.event_type, fe.event_date, fe.amount, fe.description, fe.reference_number,
                        fe.distribution_type, fe.tax_payment_type, fe.units_purchased, fe.units_sold,
                        fe.unit_price, fe.nav_per_share, fe.previous_nav_per_share, fe.nav_change_absolute, 
                        fe.nav_change_percentage, fe.brokerage_fee,
                        -- Tax statement fields for TAX_PAYMENT events
                        ts.interest_income_amount,
                        ts.interest_income_tax_rate,
                        ts.dividend_franked_income_amount,
                        ts.dividend_franked_income_tax_rate,
                        ts.dividend_unfranked_income_amount,
                        ts.dividend_unfranked_income_tax_rate,
                        ts.capital_gain_income_amount,
                        ts.capital_gain_income_tax_rate,
                        -- Tax statement fields for FY_DEBT_COST events
                        ts.fy_debt_interest_deduction_sum_of_daily_interest,
                        ts.fy_debt_interest_deduction_rate,
                        ts.fy_debt_interest_deduction_total_deduction
                    FROM fund_events fe
                    LEFT JOIN tax_statements ts ON fe.tax_statement_id = ts.id
                    WHERE fe.fund_id = :fund_id 
                    AND fe.event_type != 'DAILY_RISK_FREE_INTEREST_CHARGE'
                    ORDER BY fe.event_date ASC, fe.id ASC
                """)
                
                events_result = session.execute(events_query, {"fund_id": fund_id}).fetchall()
                
                # Get fund statistics (excluding system events)
                stats_query = text("""
                    SELECT 
                        COUNT(*) as total_events,
                        COUNT(CASE WHEN event_type = 'CAPITAL_CALL' THEN 1 END) as capital_calls,
                        COUNT(CASE WHEN event_type = 'DISTRIBUTION' THEN 1 END) as distributions,
                        COUNT(CASE WHEN event_type = 'NAV_UPDATE' THEN 1 END) as nav_updates,
                        COUNT(CASE WHEN event_type = 'UNIT_PURCHASE' THEN 1 END) as unit_purchases,
                        COUNT(CASE WHEN event_type = 'UNIT_SALE' THEN 1 END) as unit_sales,
                        SUM(CASE WHEN event_type = 'CAPITAL_CALL' THEN amount ELSE 0 END) as total_capital_called,
                        SUM(CASE WHEN event_type = 'RETURN_OF_CAPITAL' THEN amount ELSE 0 END) as total_capital_returned,
                        SUM(CASE WHEN event_type = 'DISTRIBUTION' THEN amount ELSE 0 END) as total_distributions,
                        MIN(event_date) as first_event_date,
                        MAX(event_date) as last_event_date
                    FROM fund_events 
                    WHERE fund_id = :fund_id
                    AND event_type != 'DAILY_RISK_FREE_INTEREST_CHARGE'
                """)
                
                stats_result = session.execute(stats_query, {"fund_id": fund_id}).fetchone()
                
                # Format fund data
                fund_data = {
                    "id": fund_result.id,
                    "name": fund_result.name,
                    "fund_type": fund_result.fund_type,
                    "tracking_type": fund_result.tracking_type,
                    "currency": fund_result.currency,
                    "current_equity_balance": float(fund_result.current_equity_balance) if fund_result.current_equity_balance else 0.0,
                    "average_equity_balance": float(fund_result.average_equity_balance) if fund_result.average_equity_balance else 0.0,
                    "is_active": fund_result.is_active if fund_result.is_active is not None else True,
                    "commitment_amount": float(fund_result.commitment_amount) if fund_result.commitment_amount else None,
                    "expected_irr": float(fund_result.expected_irr) if fund_result.expected_irr else None,
                    "expected_duration_months": fund_result.expected_duration_months,
                    "description": fund_result.description,
                    "investment_company": fund_result.investment_company_name or "Unknown",
                    "entity": fund_result.entity_name or "Unknown",
                    "created_at": fund_result.created_at if isinstance(fund_result.created_at, str) else fund_result.created_at.isoformat() if fund_result.created_at else None,
                    "updated_at": fund_result.updated_at if isinstance(fund_result.updated_at, str) else fund_result.updated_at.isoformat() if fund_result.updated_at else None
                }
                
                # Format events data
                events_data = []
                for event in events_result:
                    event_data = {
                        "id": event.id,
                        "event_type": event.event_type,
                        "event_date": event.event_date if isinstance(event.event_date, str) else event.event_date.isoformat() if event.event_date else None,
                        "amount": float(event.amount) if event.amount else None,
                        "description": event.description,
                        "reference_number": event.reference_number,
                        "distribution_type": event.distribution_type,
                        "tax_payment_type": event.tax_payment_type,
                        "units_purchased": float(event.units_purchased) if event.units_purchased else None,
                        "units_sold": float(event.units_sold) if event.units_sold else None,
                        "unit_price": float(event.unit_price) if event.unit_price else None,
                        "nav_per_share": float(event.nav_per_share) if event.nav_per_share else None,
                        "previous_nav_per_share": float(event.previous_nav_per_share) if event.previous_nav_per_share else None,
                        "nav_change_absolute": float(event.nav_change_absolute) if event.nav_change_absolute else None,
                        "nav_change_percentage": float(event.nav_change_percentage) if event.nav_change_percentage else None,
                        "brokerage_fee": float(event.brokerage_fee) if event.brokerage_fee else None
                    }
                    
                    # Add tax statement fields for TAX_PAYMENT events
                    if event.event_type == 'TAX_PAYMENT':
                        event_data.update({
                            "interest_income_amount": float(event.interest_income_amount) if event.interest_income_amount else None,
                            "interest_income_tax_rate": float(event.interest_income_tax_rate) if event.interest_income_tax_rate else None,
                            "dividend_franked_income_amount": float(event.dividend_franked_income_amount) if event.dividend_franked_income_amount else None,
                            "dividend_franked_income_tax_rate": float(event.dividend_franked_income_tax_rate) if event.dividend_franked_income_tax_rate else None,
                            "dividend_unfranked_income_amount": float(event.dividend_unfranked_income_amount) if event.dividend_unfranked_income_amount else None,
                            "dividend_unfranked_income_tax_rate": float(event.dividend_unfranked_income_tax_rate) if event.dividend_unfranked_income_tax_rate else None,
                            "capital_gain_income_amount": float(event.capital_gain_income_amount) if event.capital_gain_income_amount else None,
                            "capital_gain_income_tax_rate": float(event.capital_gain_income_tax_rate) if event.capital_gain_income_tax_rate else None
                        })
                    
                    # Add tax statement fields for FY_DEBT_COST events
                    if event.event_type == 'FY_DEBT_COST':
                        event_data.update({
                            "fy_debt_interest_deduction_sum_of_daily_interest": float(event.fy_debt_interest_deduction_sum_of_daily_interest) if event.fy_debt_interest_deduction_sum_of_daily_interest else None,
                            "fy_debt_interest_deduction_rate": float(event.fy_debt_interest_deduction_rate) if event.fy_debt_interest_deduction_rate else None,
                            "fy_debt_interest_deduction_total_deduction": float(event.fy_debt_interest_deduction_total_deduction) if event.fy_debt_interest_deduction_total_deduction else None
                        })
                    
                    events_data.append(event_data)
                
                # Format statistics data
                stats_data = {
                    "total_events": stats_result.total_events,
                    "capital_calls": stats_result.capital_calls,
                    "distributions": stats_result.distributions,
                    "nav_updates": stats_result.nav_updates,
                    "unit_purchases": stats_result.unit_purchases,
                    "unit_sales": stats_result.unit_sales,
                    "total_capital_called": float(stats_result.total_capital_called) if stats_result.total_capital_called else 0.0,
                    "total_capital_returned": float(stats_result.total_capital_returned) if stats_result.total_capital_returned else 0.0,
                    "total_distributions": float(stats_result.total_distributions) if stats_result.total_distributions else 0.0,
                    "first_event_date": stats_result.first_event_date if isinstance(stats_result.first_event_date, str) else stats_result.first_event_date.isoformat() if stats_result.first_event_date else None,
                    "last_event_date": stats_result.last_event_date if isinstance(stats_result.last_event_date, str) else stats_result.last_event_date.isoformat() if stats_result.last_event_date else None
                }
                
                return jsonify({
                    "fund": fund_data,
                    "events": events_data,
                    "statistics": stats_data
                }), 200
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app 