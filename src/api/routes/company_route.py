"""
Company API Routes.

This module contains all company-related API endpoints including
investment company management and company-specific contact operations.

All endpoints use middleware validation for input data.
All endpoints use the company controller with DTO responses.
"""

from flask import Blueprint, jsonify, request
from src.api.middleware.validation import validate_request
from src.api.controllers.company_controller import CompanyController
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response
from src.investment_company.enums.company_enums import CompanyType, CompanyStatus, SortFieldCompany
from src.shared.enums.shared_enums import SortOrder

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
@validate_request(
    field_types={
        'company_type': 'string',
        'company_types': 'string_array',
        'status': 'string',
        'statuses': 'string_array',
        'name': 'string',
        'names': 'string_array',
        'sort_by': 'string',
        'sort_order': 'string',
        'include_contacts': 'bool',
    },
    enum_fields={
        'company_type': CompanyType,
        'status': CompanyStatus,
        'sort_by': SortFieldCompany,
        'sort_order': SortOrder
    },
    array_element_enum_fields={
        'company_types': CompanyType,
        'statuses': CompanyStatus
    },
    field_lengths={
        'name': {'max': 255}
    },
    array_element_lengths={
        'names': {'max': 255}
    },
    mutually_exclusive_groups=[
        ['company_type', 'company_types'],
        ['status', 'statuses'],
        ['name', 'names']
    ],
    sanitize=True
)
def get_companies():
    """
    Get list of all companies with summary data

    Request Body:
        company_type (str): Company type (optional)
        status (str): Company status (optional)
        name (str): Company name (optional)
        sort_by (str): Sort by (NAME, STATUS, START_DATE, CREATED_AT, UPDATED_AT)
        sort_order (str): Sort order (ASC, DESC)
        include_contacts (bool): Whether to include contacts (optional)

    Returns:
        Standardized response with companies data
    """
    try:
        dto = company_controller.get_companies()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting companies: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@company_bp.route('/api/companies/<int:company_id>', methods=['GET'])
@validate_request(
    field_types={
        'include_contacts': 'bool'
    },
    sanitize=True
)
def get_company_by_id(company_id):
    """
    Get a specific company by ID

    Request Body:
        include_contacts (bool): Whether to include contacts (optional)

    Returns:
        Standardized response with company data
    """
    try:
        dto = company_controller.get_company_by_id(company_id)
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
@validate_request(
    required_fields=['name'],
    field_types={
        'name': 'string',
        'description': 'string',
        'company_type': 'string',
        'website': 'string',
        'business_address': 'string'
    },
    field_lengths={
        'name': {'min': 2, 'max': 255},
        'description': {'max': 1000},
        'website': {'max': 255},
        'business_address': {'max': 1000}
    },
    enum_fields={
        'company_type': CompanyType
    },
    sanitize=True
)
def create_company():
    """
    Create a new investment company using services

    Request Body:
        name (str): Investment company name (required)
        description (str): Investment company description (optional)
        company_type (str): Investment company type (optional)
        website (str): Investment company website (optional)
        business_address (str): Investment company business address (optional)

    Returns:
        Standardized response with company data
    """
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

    Path Parameters:
        company_id (int): ID of the company to delete

    Returns:
        Standardized response confirming deletion
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
@validate_request(
    field_types={
        'company_id': 'int',
        'company_ids': 'int_array'
    },
    field_ranges={
        'company_id': {'min': 1}
    },
    array_element_ranges={
        'company_ids': {'min': 1}
    },
    mutually_exclusive_groups=[
        ['company_id', 'company_ids']
    ],

    sanitize=True
)
def get_contacts():
    """
    Get list of all contacts

    Query Parameters:
        company_id (int): ID of the company to get contacts for
        company_ids (int_array): IDs of the companies to get contacts for

    Returns:
        Standardized response with contacts data
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

@company_bp.route('/api/companies/<int:company_id>/contacts', methods=['GET'])
def get_contacts_by_company_id(company_id):
    """
    Get all contacts for a specific company (nested pattern)
    
    Path Parameters:
        company_id (int): ID of the company to get contacts for

    Returns:
        Standardized response with contacts data
    """
    try:
        dto = company_controller.get_contacts(company_id=company_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting contacts for company {company_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@company_bp.route('/api/companies/<int:company_id>/contacts/<int:contact_id>', methods=['GET'])
def get_contact_by_id(company_id, contact_id):
    """
    Get a specific contact for a specific company

    Path Parameters:
        company_id (int): ID of the company (not used)
        contact_id (int): ID of the contact

    Returns:
        Standardized response with contact data
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

@company_bp.route('/api/companies/<int:company_id>/contacts', methods=['POST'])
@validate_request(
    required_fields=['name'],
    field_types={
        'name': 'string',
        'email': 'string',
        'phone': 'string',
        'title': 'string'
    },
    field_lengths={
        'name': {'min': 2, 'max': 255},
        'email': {'max': 255},
        'phone': {'max': 50},
        'title': {'max': 100}
    },
    sanitize=True
)
def create_contact(company_id):
    """
    Create a new contact for the specified company

    Path Parameters:
        company_id (int): ID of the company to add contact to

    Request Body:
        name (str): Name of the contact (required)
        email (str): Email address (optional)
        phone (str): Phone number (optional)
        title (str): Job title (optional)

    Returns:
        Standardized response with contact data
    """
    try:
        dto = company_controller.create_contact(company_id)
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

@company_bp.route('/api/companies/<int:company_id>/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(company_id, contact_id):
    """
    Delete a specific contact for the specified company

    Path Parameters:
        company_id (int): ID of the company (not used)
        contact_id (int): ID of the contact

    Returns:
        Standardized response confirming deletion
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