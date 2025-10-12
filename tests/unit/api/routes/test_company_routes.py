"""
Company Route Tests.

This module tests the company API routes with a focus on HTTP layer concerns:
- Route registration and endpoint availability
- Request validation and parameter handling
- Response formatting and status codes
- Error handling and middleware integration
- Controller delegation and DTO handling

Test Coverage:
- All company endpoints (GET, POST, DELETE)
- Contact endpoints (GET, POST, DELETE)
- Validation middleware integration
- Response handler integration
- Error handling and status codes
- Query parameter processing
- Request body validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, jsonify

from src.api.routes.company import company_bp
from src.api.dto.response_codes import ApiResponseCode
from src.api.dto.controller_response_dto import ControllerResponseDTO


class TestCompanyRoutes:
    """Test suite for company API routes."""

    @pytest.fixture
    def app(self):
        """Create Flask app with company blueprint registered."""
        app = Flask(__name__)
        app.register_blueprint(company_bp)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    @pytest.fixture
    def mock_controller(self):
        """Create mock company controller."""
        controller = Mock()
        return controller

    ################################################################################
    # ROUTE REGISTRATION TESTS
    ################################################################################

    def test_company_blueprint_registered(self, app):
        """Test that company blueprint is properly registered."""
        # Check that company routes are registered
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/api/companies',
            '/api/companies/<int:company_id>',
            '/api/contacts',
            '/api/companies/<int:company_id>/contacts',
            '/api/companies/<int:company_id>/contacts/<int:contact_id>'
        ]
        
        for route in expected_routes:
            assert any(route in rule for rule in rules), f"Route {route} not found in registered routes"

    ################################################################################
    # GET COMPANIES ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.company.company_controller')
    def test_get_companies_success(self, mock_controller, client):
        """Test successful GET /api/companies request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'name': 'Test Company', 'company_type': 'Private Equity'}],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_companies.return_value = mock_dto
        
        # Act
        response = client.get('/api/companies')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert data['data'] == [{'id': 1, 'name': 'Test Company', 'company_type': 'Private Equity'}]
        mock_controller.get_companies.assert_called_once_with(include_contacts=True)

    @patch('src.api.routes.company.company_controller')
    def test_get_companies_with_query_parameters(self, mock_controller, client):
        """Test GET /api/companies with query parameters."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'name': 'Test Company'}],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_companies.return_value = mock_dto
        
        # Act
        response = client.get('/api/companies?company_type=Private Equity&status=ACTIVE&name=Test&include_contacts=true')
        
        # Assert
        assert response.status_code == 200
        mock_controller.get_companies.assert_called_once_with(include_contacts=True)

    @patch('src.api.routes.company.company_controller')
    def test_get_companies_controller_error(self, mock_controller, client):
        """Test GET /api/companies with controller error."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Companies not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.get_companies.return_value = mock_dto
        
        # Act
        response = client.get('/api/companies')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert data['message'] == 'Companies not found'

    @patch('src.api.routes.company.company_controller')
    def test_get_companies_unexpected_error(self, mock_controller, client):
        """Test GET /api/companies with unexpected error."""
        # Arrange
        mock_controller.get_companies.side_effect = Exception("Database error")
        
        # Act
        response = client.get('/api/companies')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error getting companies' in data['message']

    ################################################################################
    # GET COMPANY BY ID ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.company.company_controller')
    def test_get_company_by_id_success(self, mock_controller, client):
        """Test successful GET /api/companies/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'name': 'Test Company'},
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_company_by_id.return_value = mock_dto
        
        # Act
        response = client.get('/api/companies/1')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert data['data'] == {'id': 1, 'name': 'Test Company'}
        mock_controller.get_company_by_id.assert_called_once_with(1, include_contacts=True)

    @patch('src.api.routes.company.company_controller')
    def test_get_company_by_id_not_found(self, mock_controller, client):
        """Test GET /api/companies/<id> with company not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Company not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.get_company_by_id.return_value = mock_dto
        
        # Act
        response = client.get('/api/companies/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert data['message'] == 'Company not found'

    ################################################################################
    # CREATE COMPANY ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.company.company_controller')
    def test_create_company_success(self, mock_controller, client):
        """Test successful POST /api/companies request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'name': 'New Company'},
            response_code=ApiResponseCode.CREATED
        )
        mock_controller.create_company.return_value = mock_dto
        
        company_data = {
            'name': 'New Company',
            'description': 'A new company',
            'company_type': 'Private Equity',
            'website': 'https://example.com',
            'business_address': '123 Main St'
        }
        
        # Act
        response = client.post('/api/companies', json=company_data)
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['response_code'] == 'CREATED'
        assert data['data'] == {'id': 1, 'name': 'New Company'}
        mock_controller.create_company.assert_called_once()

    @patch('src.api.routes.company.company_controller')
    def test_create_company_validation_error(self, mock_controller, client):
        """Test POST /api/companies with validation error."""
        # Arrange - validation happens at middleware level, not controller
        company_data = {'description': 'Missing name'}  # Missing required 'name' field
        
        # Act
        response = client.post('/api/companies', json=company_data)
        
        # Assert - validation middleware returns 400 with specific format
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Missing required fields: name'
        assert data['type'] == 'validation_error'

    @patch('src.api.routes.company.company_controller')
    def test_create_company_business_logic_error(self, mock_controller, client):
        """Test POST /api/companies with business logic error."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Company name already exists",
            response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR
        )
        mock_controller.create_company.return_value = mock_dto
        
        company_data = {'name': 'Existing Company'}
        
        # Act
        response = client.post('/api/companies', json=company_data)
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['response_code'] == 'BUSINESS_LOGIC_ERROR'
        assert data['message'] == 'Company name already exists'

    ################################################################################
    # DELETE COMPANY ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.company.company_controller')
    def test_delete_company_success(self, mock_controller, client):
        """Test successful DELETE /api/companies/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=None,
            response_code=ApiResponseCode.NO_CONTENT
        )
        mock_controller.delete_company.return_value = mock_dto
        
        # Act
        response = client.delete('/api/companies/1')
        
        # Assert
        assert response.status_code == 204
        mock_controller.delete_company.assert_called_once_with(1)

    @patch('src.api.routes.company.company_controller')
    def test_delete_company_not_found(self, mock_controller, client):
        """Test DELETE /api/companies/<id> with company not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Company not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.delete_company.return_value = mock_dto
        
        # Act
        response = client.delete('/api/companies/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert data['message'] == 'Company not found'

    ################################################################################
    # GET CONTACTS ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.company.company_controller')
    def test_get_contacts_success(self, mock_controller, client):
        """Test successful GET /api/contacts request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_contacts.return_value = mock_dto
        
        # Act
        response = client.get('/api/contacts?company_id=1')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert data['data'] == [{'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}]
        mock_controller.get_contacts.assert_called_once()

    ################################################################################
    # GET CONTACTS BY COMPANY ID ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.company.company_controller')
    def test_get_contacts_by_company_id_success(self, mock_controller, client):
        """Test successful GET /api/companies/<id>/contacts request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_contacts.return_value = mock_dto
        
        # Act
        response = client.get('/api/companies/1/contacts')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert data['data'] == [{'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}]
        mock_controller.get_contacts.assert_called_once_with(company_id=1)

    ################################################################################
    # GET CONTACT BY ID ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.company.company_controller')
    def test_get_contact_by_id_success(self, mock_controller, client):
        """Test successful GET /api/companies/<id>/contacts/<contact_id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_contact_by_id.return_value = mock_dto
        
        # Act
        response = client.get('/api/companies/1/contacts/1')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert data['data'] == {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}
        mock_controller.get_contact_by_id.assert_called_once_with(1)

    ################################################################################
    # CREATE CONTACT ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.company.company_controller')
    def test_create_contact_success(self, mock_controller, client):
        """Test successful POST /api/companies/<id>/contacts request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
            response_code=ApiResponseCode.CREATED
        )
        mock_controller.create_contact.return_value = mock_dto
        
        contact_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'title': 'Manager'
        }
        
        # Act
        response = client.post('/api/companies/1/contacts', json=contact_data)
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['response_code'] == 'CREATED'
        assert data['data'] == {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}
        mock_controller.create_contact.assert_called_once_with(1)

    @patch('src.api.routes.company.company_controller')
    def test_create_contact_validation_error(self, mock_controller, client):
        """Test POST /api/companies/<id>/contacts with validation error."""
        # Arrange - validation happens at middleware level, not controller
        contact_data = {'email': 'john@example.com'}  # Missing required 'name' field
        
        # Act
        response = client.post('/api/companies/1/contacts', json=contact_data)
        
        # Assert - validation middleware returns 400 with specific format
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Missing required fields: name'
        assert data['type'] == 'validation_error'

    ################################################################################
    # DELETE CONTACT ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.company.company_controller')
    def test_delete_contact_success(self, mock_controller, client):
        """Test successful DELETE /api/companies/<id>/contacts/<contact_id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=None,
            response_code=ApiResponseCode.NO_CONTENT
        )
        mock_controller.delete_contact.return_value = mock_dto
        
        # Act
        response = client.delete('/api/companies/1/contacts/1')
        
        # Assert
        assert response.status_code == 204
        mock_controller.delete_contact.assert_called_once_with(1)

    @patch('src.api.routes.company.company_controller')
    def test_delete_contact_not_found(self, mock_controller, client):
        """Test DELETE /api/companies/<id>/contacts/<contact_id> with contact not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Contact not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.delete_contact.return_value = mock_dto
        
        # Act
        response = client.delete('/api/companies/1/contacts/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert data['message'] == 'Contact not found'

    ################################################################################
    # ERROR HANDLING TESTS
    ################################################################################

    @patch('src.api.routes.company.company_controller')
    def test_unexpected_error_handling(self, mock_controller, client):
        """Test that unexpected errors are properly handled."""
        # Arrange
        mock_controller.get_companies.side_effect = Exception("Unexpected error")
        
        # Act
        response = client.get('/api/companies')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error getting companies' in data['message']

    ################################################################################
    # HTTP METHOD VALIDATION TESTS
    ################################################################################

    def test_invalid_http_methods(self, client):
        """Test that invalid HTTP methods return 405 Method Not Allowed."""
        # Test PUT method on companies endpoint
        response = client.put('/api/companies')
        assert response.status_code == 405
        
        # Test PATCH method on company by ID endpoint
        response = client.patch('/api/companies/1')
        assert response.status_code == 405

    ################################################################################
    # PATH PARAMETER VALIDATION TESTS
    ################################################################################

    def test_invalid_company_id_format(self, client):
        """Test that invalid company ID format returns 404."""
        # Test non-numeric company ID
        response = client.get('/api/companies/invalid')
        assert response.status_code == 404
        
        response = client.get('/api/companies/invalid/contacts')
        assert response.status_code == 404

    def test_invalid_contact_id_format(self, client):
        """Test that invalid contact ID format returns 404."""
        # Test non-numeric contact ID
        response = client.get('/api/companies/1/contacts/invalid')
        assert response.status_code == 404
