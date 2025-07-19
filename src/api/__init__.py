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
                    # Get recent events count for this fund
                    recent_events_count = session.execute(
                        text("SELECT COUNT(*) FROM fund_events WHERE fund_id = :fund_id AND event_date >= :date"),
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
                # Get recent events with fund information
                events_query = text("""
                    SELECT 
                        fe.id, fe.event_type, fe.event_date, fe.amount, 
                        fe.description, fe.reference_number, f.name as fund_name
                    FROM fund_events fe
                    JOIN funds f ON fe.fund_id = f.id
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
    def performance_data():
        """Get performance data for charts"""
        try:
            session = get_db_session()
            
            try:
                # Get all funds
                funds_query = text("SELECT id, name, current_equity_balance, average_equity_balance FROM funds")
                funds_result = session.execute(funds_query).fetchall()
                
                performance_data = []
                for fund in funds_result:
                    # Get total events for this fund
                    total_events = session.execute(
                        text("SELECT COUNT(*) FROM fund_events WHERE fund_id = :fund_id"),
                        {"fund_id": fund.id}
                    ).scalar()
                    
                    # Get last event date
                    last_event = session.execute(
                        text("SELECT event_date FROM fund_events WHERE fund_id = :fund_id ORDER BY event_date DESC LIMIT 1"),
                        {"fund_id": fund.id}
                    ).fetchone()
                    
                    performance_data.append({
                        "fund_name": fund.name,
                        "current_equity": float(fund.current_equity_balance) if fund.current_equity_balance else 0.0,
                        "average_equity": float(fund.average_equity_balance) if fund.average_equity_balance else 0.0,
                        "total_events": total_events,
                        "last_event_date": last_event.event_date if isinstance(last_event.event_date, str) else last_event.event_date.isoformat() if last_event and last_event.event_date else None
                    })
                
                return jsonify({"performance": performance_data}), 200
                
            finally:
                session.close()
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app 