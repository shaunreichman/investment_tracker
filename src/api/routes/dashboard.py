"""
Dashboard API Routes.

This module contains all dashboard-related API endpoints including
portfolio summary, funds list, recent events, and performance data.
"""

from flask import Blueprint, jsonify, request
from datetime import date, timedelta
from src.fund.models import Fund
from src.fund.enums import FundStatus
from src.tax.models import TaxStatement

# Create blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "API is running"}), 200


@dashboard_bp.route('/api/dashboard/portfolio-summary', methods=['GET'])
def portfolio_summary():
    """Get overall portfolio summary with key metrics"""
    try:
        from src.api import get_db_session
        session = get_db_session()
        
        try:
            # Use domain methods to get all funds
            funds = Fund.get_all(session=session)
            
            # Calculate summary metrics using domain data
            total_funds = len(funds)
            active_funds = sum(1 for fund in funds if fund.status == FundStatus.ACTIVE)
            total_equity = sum(fund.current_equity_balance or 0.0 for fund in funds)
            total_avg_equity = sum(fund.average_equity_balance or 0.0 for fund in funds)
            
            # Get recent events count across all funds
            recent_events_count = 0
            thirty_days_ago = date.today() - timedelta(days=30)
            for fund in funds:
                recent_events = fund.get_recent_events(limit=1000, session=session)
                recent_events_count += len([e for e in recent_events if e.event_date and e.event_date >= thirty_days_ago])
            
            # Get tax statements count using domain method
            total_tax_statements = session.query(TaxStatement).count()
            
            summary = {
                "total_funds": total_funds,
                "active_funds": active_funds,
                "total_equity_balance": float(total_equity),
                "total_average_equity_balance": float(total_avg_equity),
                "recent_events_count": recent_events_count,
                "total_tax_statements": total_tax_statements,
                "last_updated": date.today().isoformat()
            }
            return jsonify(summary), 200
            
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/api/dashboard/funds', methods=['GET'])
def funds_list():
    """Get list of all funds with key metrics"""
    try:
        from src.api import get_db_session
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
                    "status": fund.status.value if fund.status else None,
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


@dashboard_bp.route('/api/dashboard/recent-events', methods=['GET'])
def recent_events():
    """Get recent fund events for the dashboard"""
    try:
        from src.api import get_db_session
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


@dashboard_bp.route('/api/dashboard/performance', methods=['GET'])
def dashboard_performance():
    """Get performance data for all funds"""
    try:
        from src.api import get_db_session
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
