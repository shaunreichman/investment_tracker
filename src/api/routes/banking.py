"""
Banking API Routes.

This module contains all banking-related API endpoints including
bank management and bank account operations.
"""

from flask import Blueprint, jsonify, request
from src.api.controllers import BankingController
from src.api.database import get_db_session

# Create blueprint for banking routes
banking_bp = Blueprint('banking', __name__)

# Initialize controller
banking_controller = BankingController()


@banking_bp.route('/api/banks', methods=['GET'])
def get_banks():
    """Get list of all banks with summary data"""
    try:
        session = get_db_session()
        try:
            return banking_controller.get_banks(session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@banking_bp.route('/api/banks', methods=['POST'])
def create_bank():
    """Create a new bank"""
    try:
        session = get_db_session()
        try:
            return banking_controller.create_bank(session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@banking_bp.route('/api/banks/<int:bank_id>', methods=['PUT'])
def update_bank(bank_id):
    """Update a bank"""
    try:
        session = get_db_session()
        try:
            return banking_controller.update_bank(bank_id, session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@banking_bp.route('/api/banks/<int:bank_id>', methods=['DELETE'])
def delete_bank(bank_id):
    """Delete a bank"""
    try:
        session = get_db_session()
        try:
            return banking_controller.delete_bank(bank_id, session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@banking_bp.route('/api/bank-accounts', methods=['GET'])
def get_bank_accounts():
    """Get list of all bank accounts with summary data"""
    try:
        session = get_db_session()
        try:
            return banking_controller.get_bank_accounts(session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@banking_bp.route('/api/bank-accounts', methods=['POST'])
def create_bank_account():
    """Create a new bank account"""
    try:
        session = get_db_session()
        try:
            return banking_controller.create_bank_account(session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@banking_bp.route('/api/bank-accounts/<int:account_id>', methods=['PUT'])
def update_bank_account(account_id):
    """Update a bank account"""
    try:
        session = get_db_session()
        try:
            return banking_controller.update_bank_account(account_id, session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@banking_bp.route('/api/bank-accounts/<int:account_id>', methods=['DELETE'])
def delete_bank_account(account_id):
    """Delete a bank account"""
    try:
        session = get_db_session()
        try:
            return banking_controller.delete_bank_account(account_id, session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
