"""
Dashboard API Routes.

This module contains all dashboard-related API endpoints including
portfolio summary, funds list, recent events, and performance data.
"""

from flask import Blueprint, jsonify, request
from src.api.controllers import DashboardController
from src.api.database import get_db_session

# Create blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

# Initialize controller
dashboard_controller = DashboardController()


@dashboard_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return dashboard_controller.health_check()


@dashboard_bp.route('/api/dashboard/portfolio-summary', methods=['GET'])
def portfolio_summary():
    """Get overall portfolio summary with key metrics"""
    try:
        session = get_db_session()
        try:
            return dashboard_controller.portfolio_summary(session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/api/dashboard/funds', methods=['GET'])
def funds_list():
    """Get list of all funds with key metrics"""
    try:
        session = get_db_session()
        try:
            return dashboard_controller.funds_list(session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/api/dashboard/recent-events', methods=['GET'])
def recent_events():
    """Get recent fund events for the dashboard"""
    try:
        session = get_db_session()
        try:
            return dashboard_controller.recent_events(session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/api/dashboard/performance', methods=['GET'])
def dashboard_performance():
    """Get performance data for all funds"""
    try:
        session = get_db_session()
        try:
            return dashboard_controller.dashboard_performance(session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
