"""
Tax API Routes.

This module contains all tax-related API endpoints including
tax statement management for funds.

All endpoints use middleware validation for input data.
"""

from flask import Blueprint
from src.api.controllers.tax_controller import TaxController
from src.api.database import get_db_session
from src.api.middleware.validation import validate_tax_statement_data

# Create blueprint for tax routes
tax_bp = Blueprint('tax', __name__)

# Initialize controller
tax_controller = TaxController()


@tax_bp.route('/api/funds/<int:fund_id>/tax-statements', methods=['POST'])
@validate_tax_statement_data
def create_tax_statement(fund_id):
    """Create a new tax statement for a fund"""
    session = get_db_session()
    try:
        return tax_controller.create_tax_statement(session, fund_id)
    finally:
        session.close()


@tax_bp.route('/api/funds/<int:fund_id>/tax-statements', methods=['GET'])
def get_fund_tax_statements(fund_id):
    """Get all tax statements for a fund"""
    session = get_db_session()
    try:
        return tax_controller.get_fund_tax_statements(session, fund_id)
    finally:
        session.close()
