"""
Company API Routes.

This module contains all company-related API endpoints including
investment company management and company-specific fund operations.
"""

from flask import Blueprint, jsonify, request
from src.investment_company.api import CompanyController
from src.api.database import get_db_session
from src.api.middleware.validation import validate_investment_company_data

# Create blueprint for company routes
company_bp = Blueprint('company', __name__)

# Initialize controller
company_controller = CompanyController()


@company_bp.route('/api/investment-companies', methods=['GET'])
def investment_companies():
    """Get list of all investment companies with summary data"""
    try:
        session = get_db_session()
        try:
            return company_controller.get_investment_companies(session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/api/investment-companies', methods=['POST'])
@validate_investment_company_data
def create_investment_company():
    """Create a new investment company using domain methods"""
    try:
        session = get_db_session()
        try:
            # Use validated data from middleware
            validated_data = request.validated_data
            return company_controller.create_investment_company_with_data(session, validated_data)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/api/companies/<int:company_id>/funds', methods=['GET'])
def company_funds(company_id):
    """Get list of funds for a specific investment company"""
    try:
        session = get_db_session()
        try:
            return company_controller.get_company_funds(company_id, session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/api/companies/<int:company_id>/overview', methods=['GET'])
def company_overview(company_id):
    """Get company overview with portfolio summary for the Overview tab"""
    try:
        session = get_db_session()
        try:
            return company_controller.get_company_overview(company_id, session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/api/companies/<int:company_id>/details', methods=['GET'])
def company_details(company_id):
    """Get company details information for the Company Details tab"""
    try:
        session = get_db_session()
        try:
            return company_controller.get_company_details(company_id, session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/api/companies/<int:company_id>/funds/enhanced', methods=['GET'])
def company_enhanced_funds(company_id):
    """Get enhanced fund comparison data for the Funds tab with sorting, filtering, and pagination"""
    try:
        session = get_db_session()
        try:
            return company_controller.get_company_funds_enhanced(company_id, session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
