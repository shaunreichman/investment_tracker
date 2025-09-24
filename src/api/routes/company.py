"""
Company API Routes.

This module contains all company-related API endpoints including
investment company management and company-specific fund operations.
"""

from flask import Blueprint, jsonify, request
from src.api.middleware.validation import validate_investment_company_data
from src.api.controllers.company_controller import CompanyController
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response

# Create blueprint for company routes
company_bp = Blueprint('company', __name__)

# Initialize controller
company_controller = CompanyController()


################################################################################
# COMPANY ENDPOINTS
################################################################################

###############################################
# Get companies
###############################################

@company_bp.route('/api/companies', methods=['GET'])
def get_companies():
    """
    Get list of all companies with summary data
    """
    try:
        dto = company_controller.get_companies(include_contacts=True)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting companies: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@company_bp.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company_by_id(company_id):
    """
    Get a specific company by ID
    """
    try:
        dto = company_controller.get_company_by_id(company_id, include_contacts=True)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting company {company_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create company
###############################################

@company_bp.route('/api/companies', methods=['POST'])
@validate_investment_company_data
def create_company():
    """Create a new investment company using services"""
    try:
        dto = company_controller.create_company()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating company: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete company
###############################################

@company_bp.route('/api/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    """
    Delete a company
    """
    try:
        dto = company_controller.delete_company(company_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting company {company_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


################################################################################
# CONTACTS ENDPOINTS
################################################################################

###############################################
# Get contacts
###############################################

@company_bp.route('/api/contacts', methods=['GET'])
def get_contacts():
    """
    Get list of all contacts
    """
    try:
        dto = company_controller.get_contacts()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting contacts: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@company_bp.route('/api/contacts/<int:company_id>/<int:contact_id>', methods=['GET'])
def get_contact_by_id(contact_id):
    """
    Get a specific contact
    """
    try:
        dto = company_controller.get_contact_by_id(contact_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting contact {contact_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create contact
###############################################

@company_bp.route('/api/contacts/<int:company_id>', methods=['POST'])
def create_contact():
    """
    Create a new contact
    """
    try:
        dto = company_controller.create_contact()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating contact: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete contact
###############################################

@company_bp.route('/api/contacts/<int:company_id>/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """
    Delete a specific contact
    """
    try:
        dto = company_controller.delete_contact(contact_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting contact {contact_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()