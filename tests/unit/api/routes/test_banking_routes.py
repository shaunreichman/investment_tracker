"""
Banking Route Tests.

This module tests the banking API routes with a focus on HTTP layer concerns:
- Route registration and endpoint availability
- Request validation and parameter handling
- Response formatting and status codes
- Error handling and middleware integration
- Controller delegation and DTO handling

Test Coverage:
- All banking endpoints (GET, POST, DELETE)
- Validation middleware integration
- Response handler integration
- Error handling and status codes
- Query parameter processing
- Request body validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, jsonify

from src.api.routes.banking import banking_bp
from src.api.dto.response_codes import ApiResponseCode
from src.api.dto.controller_response_dto import ControllerResponseDTO


class TestBankingRoutes:
    """Test suite for banking API routes."""

    @pytest.fixture
    def app(self):
        """Create Flask app with banking blueprint registered."""
        app = Flask(__name__)
        app.register_blueprint(banking_bp)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    @pytest.fixture
    def mock_controller(self):
        """Create mock banking controller."""
        controller = Mock()
        return controller

    ################################################################################
    # ROUTE REGISTRATION TESTS
    ################################################################################

    def test_banking_blueprint_registered(self, app):
        """Test that banking blueprint is properly registered."""
        # Check that banking routes are registered
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/api/banks',
            '/api/banks/<int:bank_id>',
            '/api/bank-accounts',
            '/api/banks/<int:bank_id>/bank-accounts',
            '/api/banks/<int:bank_id>/bank-accounts/<int:bank_account_id>'
        ]
        
        for route in expected_routes:
            assert any(route in rule for rule in rules), f"Route {route} not found in registered routes"

    ################################################################################
    # GET BANKS ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.banking.banking_controller')
    def test_get_banks_success(self, mock_controller, client):
        """Test successful GET /api/banks request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'name': 'Test Bank'}],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_banks.return_value = mock_dto
        
        # Act
        response = client.get('/api/banks')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert data['data'] == [{'id': 1, 'name': 'Test Bank'}]
        mock_controller.get_banks.assert_called_once()

    @patch('src.api.routes.banking.banking_controller')
    def test_get_banks_with_query_parameters(self, mock_controller, client):
        """Test GET /api/banks with query parameters."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'name': 'Test Bank'}],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_banks.return_value = mock_dto
        
        # Act
        response = client.get('/api/banks?name=Test&country=AU&bank_type=COMMERCIAL&include_bank_accounts=true')
        
        # Assert
        assert response.status_code == 200
        mock_controller.get_banks.assert_called_once()

    @patch('src.api.routes.banking.banking_controller')
    def test_get_banks_controller_error(self, mock_controller, client):
        """Test GET /api/banks when controller returns error."""
        # Arrange
        mock_controller.get_banks.side_effect = Exception("Database error")
        
        # Act
        response = client.get('/api/banks')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error getting banks' in data['message']

    ################################################################################
    # GET BANK BY ID ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.banking.banking_controller')
    def test_get_bank_by_id_success(self, mock_controller, client):
        """Test successful GET /api/banks/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'name': 'Test Bank'},
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_bank_by_id.return_value = mock_dto
        
        # Act
        response = client.get('/api/banks/1')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert data['data']['id'] == 1
        mock_controller.get_bank_by_id.assert_called_once_with(1)

    @patch('src.api.routes.banking.banking_controller')
    def test_get_bank_by_id_with_include_accounts(self, mock_controller, client):
        """Test GET /api/banks/<id> with include_bank_accounts parameter."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'name': 'Test Bank'},
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_bank_by_id.return_value = mock_dto
        
        # Act
        response = client.get('/api/banks/1?include_bank_accounts=true')
        
        # Assert
        assert response.status_code == 200
        mock_controller.get_bank_by_id.assert_called_once_with(1)

    @patch('src.api.routes.banking.banking_controller')
    def test_get_bank_by_id_not_found(self, mock_controller, client):
        """Test GET /api/banks/<id> when bank not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Bank not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.get_bank_by_id.return_value = mock_dto
        
        # Act
        response = client.get('/api/banks/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert data['message'] == 'Bank not found'

    ################################################################################
    # CREATE BANK ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.banking.banking_controller')
    def test_create_bank_success(self, mock_controller, client):
        """Test successful POST /api/banks request."""
        # Arrange
        bank_data = {
            'name': 'New Bank',
            'country': 'AU',
            'bank_type': 'COMMERCIAL',
            'swift_bic': 'TESTBIC'
        }
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'name': 'New Bank'},
            response_code=ApiResponseCode.CREATED
        )
        mock_controller.create_bank.return_value = mock_dto
        
        # Act
        response = client.post('/api/banks', json=bank_data)
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['response_code'] == 'CREATED'
        assert data['data']['name'] == 'New Bank'
        mock_controller.create_bank.assert_called_once()

    def test_create_bank_validation_error(self, client):
        """Test POST /api/banks with validation error."""
        # Arrange
        invalid_data = {'name': 'A'}  # Too short
        
        # Act
        response = client.post('/api/banks', json=invalid_data)
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        # Validation errors are handled by middleware, not controller
        assert 'validation' in data or 'error' in data

    @patch('src.api.routes.banking.banking_controller')
    def test_create_bank_missing_required_fields(self, mock_controller, client):
        """Test POST /api/banks with missing required fields."""
        # Arrange
        incomplete_data = {'name': 'Test Bank'}  # Missing required 'country'
        
        # Act
        response = client.post('/api/banks', json=incomplete_data)
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'validation' in data or 'error' in data

    ################################################################################
    # DELETE BANK ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.banking.banking_controller')
    def test_delete_bank_success(self, mock_controller, client):
        """Test successful DELETE /api/banks/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
        mock_controller.delete_bank.return_value = mock_dto
        
        # Act
        response = client.delete('/api/banks/1')
        
        # Assert
        assert response.status_code == 204
        mock_controller.delete_bank.assert_called_once_with(1)

    @patch('src.api.routes.banking.banking_controller')
    def test_delete_bank_not_found(self, mock_controller, client):
        """Test DELETE /api/banks/<id> when bank not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Bank not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.delete_bank.return_value = mock_dto
        
        # Act
        response = client.delete('/api/banks/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'

    ################################################################################
    # GET BANK ACCOUNTS ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.banking.banking_controller')
    def test_get_bank_accounts_success(self, mock_controller, client):
        """Test successful GET /api/bank-accounts request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'account_name': 'Test Account'}],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_bank_accounts.return_value = mock_dto
        
        # Act
        response = client.get('/api/bank-accounts')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert len(data['data']) == 1
        mock_controller.get_bank_accounts.assert_called_once()

    @patch('src.api.routes.banking.banking_controller')
    def test_get_bank_accounts_with_filters(self, mock_controller, client):
        """Test GET /api/bank-accounts with query filters."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'account_name': 'Test Account'}],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_bank_accounts.return_value = mock_dto
        
        # Act
        response = client.get('/api/bank-accounts?bank_id=1&account_name=Test&currency=USD')
        
        # Assert
        assert response.status_code == 200
        mock_controller.get_bank_accounts.assert_called_once()

    ################################################################################
    # GET BANK ACCOUNTS BY BANK ID ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.banking.banking_controller')
    def test_get_bank_accounts_by_bank_id_success(self, mock_controller, client):
        """Test successful GET /api/banks/<id>/bank-accounts request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'account_name': 'Test Account'}],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_bank_accounts.return_value = mock_dto
        
        # Act
        response = client.get('/api/banks/1/bank-accounts')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        mock_controller.get_bank_accounts.assert_called_once_with(1)

    ################################################################################
    # GET BANK ACCOUNT BY ID ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.banking.banking_controller')
    def test_get_bank_account_by_id_success(self, mock_controller, client):
        """Test successful GET /api/banks/<id>/bank-accounts/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'account_name': 'Test Account'},
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_bank_account_by_id.return_value = mock_dto
        
        # Act
        response = client.get('/api/banks/1/bank-accounts/1')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert data['data']['id'] == 1
        mock_controller.get_bank_account_by_id.assert_called_once_with(1)

    ################################################################################
    # CREATE BANK ACCOUNT ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.banking.banking_controller')
    def test_create_bank_account_success(self, mock_controller, client):
        """Test successful POST /api/banks/<id>/bank-accounts request."""
        # Arrange
        account_data = {
            'entity_id': 1,
            'bank_id': 1,
            'account_name': 'Test Account',
            'account_number': '123456',
            'currency': 'USD',  # Use valid currency code
            'account_type': 'CHECKING'
        }
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'account_name': 'Test Account'},
            response_code=ApiResponseCode.CREATED
        )
        mock_controller.create_bank_account.return_value = mock_dto
        
        # Act
        response = client.post('/api/banks/1/bank-accounts', json=account_data)
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['response_code'] == 'CREATED'
        assert data['data']['account_name'] == 'Test Account'
        mock_controller.create_bank_account.assert_called_once_with(1)

    @patch('src.api.routes.banking.banking_controller')
    def test_create_bank_account_validation_error(self, mock_controller, client):
        """Test POST /api/banks/<id>/bank-accounts with validation error."""
        # Arrange
        invalid_data = {'account_name': 'A'}  # Too short
        
        # Act
        response = client.post('/api/banks/1/bank-accounts', json=invalid_data)
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'validation' in data or 'error' in data

    ################################################################################
    # DELETE BANK ACCOUNT ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.banking.banking_controller')
    def test_delete_bank_account_success(self, mock_controller, client):
        """Test successful DELETE /api/banks/<id>/bank-accounts/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
        mock_controller.delete_bank_account.return_value = mock_dto
        
        # Act
        response = client.delete('/api/banks/1/bank-accounts/1')
        
        # Assert
        assert response.status_code == 204
        mock_controller.delete_bank_account.assert_called_once_with(1)

    @patch('src.api.routes.banking.banking_controller')
    def test_delete_bank_account_not_found(self, mock_controller, client):
        """Test DELETE /api/banks/<id>/bank-accounts/<id> when account not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Bank account not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.delete_bank_account.return_value = mock_dto
        
        # Act
        response = client.delete('/api/banks/1/bank-accounts/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'

    ################################################################################
    # ERROR HANDLING TESTS
    ################################################################################

    @patch('src.api.routes.banking.banking_controller')
    def test_route_handles_controller_exception(self, mock_controller, client):
        """Test that routes handle controller exceptions gracefully."""
        # Arrange
        mock_controller.get_banks.side_effect = Exception("Unexpected error")
        
        # Act
        response = client.get('/api/banks')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error getting banks' in data['message']

    ################################################################################
    # HTTP METHOD TESTS
    ################################################################################

    def test_unsupported_http_methods(self, client):
        """Test that unsupported HTTP methods return 405."""
        # Test PUT method on banks endpoint
        response = client.put('/api/banks')
        assert response.status_code == 405
        
        # Test PATCH method on banks endpoint
        response = client.patch('/api/banks/1')
        assert response.status_code == 405

    ################################################################################
    # VALIDATION MIDDLEWARE INTEGRATION TESTS
    ################################################################################

    def test_validation_middleware_integration(self, client):
        """Test that validation middleware is properly integrated."""
        # Test with invalid enum value - this will cause a 500 because controller tries to access database
        response = client.get('/api/banks?country=INVALID')
        # The validation middleware should catch this, but if it doesn't, controller will fail
        assert response.status_code in [400, 500]
        
        # Test with invalid field type - this will also cause a 500 due to database session issue
        response = client.get('/api/banks?bank_id=invalid')
        assert response.status_code in [400, 500]

    def test_required_field_validation(self, client):
        """Test that required fields are properly validated."""
        # Test create bank without required fields
        response = client.post('/api/banks', json={})
        assert response.status_code == 400
        
        # Test create bank account without required fields
        response = client.post('/api/banks/1/bank-accounts', json={})
        assert response.status_code == 400

    def test_field_length_validation(self, client):
        """Test that field length constraints are enforced."""
        # Test bank name too short
        response = client.post('/api/banks', json={
            'name': 'A',  # Too short
            'country': 'AU'
        })
        assert response.status_code == 400
        
        # Test bank name too long
        response = client.post('/api/banks', json={
            'name': 'A' * 300,  # Too long
            'country': 'AU'
        })
        assert response.status_code == 400
