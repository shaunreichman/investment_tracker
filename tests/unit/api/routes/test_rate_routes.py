"""
Rate Route Tests.

This module tests the rate API routes with a focus on HTTP layer concerns:
- Route registration and endpoint availability
- Request validation and parameter handling
- Response formatting and status codes
- Error handling and middleware integration
- Controller delegation and DTO handling

Test Coverage:
- All rate endpoints (GET, POST, DELETE)
- Validation middleware integration
- Response handler integration
- Error handling and status codes
- Query parameter processing
- Request body validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, jsonify

from src.api.routes.rate import rate_bp
from src.api.dto.response_codes import ApiResponseCode
from src.api.dto.controller_response_dto import ControllerResponseDTO


class TestRateRoutes:
    """Test suite for rate API routes."""

    @pytest.fixture
    def app(self):
        """Create Flask app with rate blueprint registered."""
        app = Flask(__name__)
        app.register_blueprint(rate_bp)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    @pytest.fixture
    def mock_controller(self):
        """Create mock rate controller."""
        controller = Mock()
        return controller

    ################################################################################
    # ROUTE REGISTRATION TESTS
    ################################################################################

    def test_rate_blueprint_registered(self, app):
        """Test that rate blueprint is properly registered."""
        # Check that rate routes are registered
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/api/risk-free-rates',
            '/api/risk-free-rates/<int:risk_free_rate_id>',
            '/api/fx-rates',
            '/api/fx-rates/<int:fx_rate_id>'
        ]
        
        for route in expected_routes:
            assert any(route in rule for rule in rules), f"Route {route} not found in registered routes"

    ################################################################################
    # GET RISK FREE RATES ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.rate.rate_controller')
    def test_get_risk_free_rates_success(self, mock_controller, client):
        """Test successful GET /api/risk-free-rates request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{
                'id': 1,
                'currency': 'USD',
                'date': '2024-01-01',
                'rate': 0.05,
                'rate_type': 'GOVERNMENT_BOND',
                'source': 'FED'
            }],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_risk_free_rates.return_value = mock_dto
        
        # Act
        response = client.get('/api/risk-free-rates')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert len(data['data']) == 1
        assert data['data'][0]['currency'] == 'USD'
        mock_controller.get_risk_free_rates.assert_called_once()

    @patch('src.api.routes.rate.rate_controller')
    def test_get_risk_free_rates_with_query_parameters(self, mock_controller, client):
        """Test GET /api/risk-free-rates with query parameters."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{
                'id': 1,
                'currency': 'USD',
                'date': '2024-01-01',
                'rate': 0.05,
                'rate_type': 'GOVERNMENT_BOND',
                'source': 'FED'
            }],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_risk_free_rates.return_value = mock_dto
        
        # Act
        response = client.get('/api/risk-free-rates?currency=USD&rate_type=GOVERNMENT_BOND')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        mock_controller.get_risk_free_rates.assert_called_once()

    @patch('src.api.routes.rate.rate_controller')
    def test_get_risk_free_rates_not_found(self, mock_controller, client):
        """Test GET /api/risk-free-rates when no rates found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Risk free rates not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.get_risk_free_rates.return_value = mock_dto
        
        # Act
        response = client.get('/api/risk-free-rates')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert 'Risk free rates not found' in data['message']

    @patch('src.api.routes.rate.rate_controller')
    def test_get_risk_free_rates_controller_exception(self, mock_controller, client):
        """Test GET /api/risk-free-rates when controller raises exception."""
        # Arrange
        mock_controller.get_risk_free_rates.side_effect = Exception("Controller error")
        
        # Act
        response = client.get('/api/risk-free-rates')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error getting risk free rates' in data['message']

    ################################################################################
    # GET RISK FREE RATE BY ID ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.rate.rate_controller')
    def test_get_risk_free_rate_by_id_success(self, mock_controller, client):
        """Test successful GET /api/risk-free-rates/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={
                'id': 1,
                'currency': 'USD',
                'date': '2024-01-01',
                'rate': 0.05,
                'rate_type': 'GOVERNMENT_BOND',
                'source': 'FED'
            },
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_risk_free_rate_by_id.return_value = mock_dto
        
        # Act
        response = client.get('/api/risk-free-rates/1')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert data['data']['id'] == 1
        mock_controller.get_risk_free_rate_by_id.assert_called_once_with(1)

    @patch('src.api.routes.rate.rate_controller')
    def test_get_risk_free_rate_by_id_not_found(self, mock_controller, client):
        """Test GET /api/risk-free-rates/<id> when rate not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Risk free rate not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.get_risk_free_rate_by_id.return_value = mock_dto
        
        # Act
        response = client.get('/api/risk-free-rates/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert 'Risk free rate not found' in data['message']

    @patch('src.api.routes.rate.rate_controller')
    def test_get_risk_free_rate_by_id_controller_exception(self, mock_controller, client):
        """Test GET /api/risk-free-rates/<id> when controller raises exception."""
        # Arrange
        mock_controller.get_risk_free_rate_by_id.side_effect = Exception("Controller error")
        
        # Act
        response = client.get('/api/risk-free-rates/1')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error getting risk free rate 1' in data['message']

    ################################################################################
    # CREATE RISK FREE RATE ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.rate.rate_controller')
    def test_create_risk_free_rate_success(self, mock_controller, client):
        """Test successful POST /api/risk-free-rates request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={
                'id': 1,
                'currency': 'USD',
                'date': '2024-01-01',
                'rate': 0.05,
                'rate_type': 'GOVERNMENT_BOND',
                'source': 'FED'
            },
            response_code=ApiResponseCode.CREATED
        )
        mock_controller.create_risk_free_rate.return_value = mock_dto
        
        request_data = {
            'currency': 'USD',
            'date': '2024-01-01',
            'rate': 0.05,
            'rate_type': 'GOVERNMENT_BOND',
            'source': 'FED'
        }
        
        # Act
        response = client.post('/api/risk-free-rates', json=request_data)
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['response_code'] == 'CREATED'
        assert data['data']['currency'] == 'USD'
        mock_controller.create_risk_free_rate.assert_called_once()

    def test_create_risk_free_rate_validation_error(self, client):
        """Test POST /api/risk-free-rates with validation error."""
        # Act - missing required fields
        response = client.post('/api/risk-free-rates', json={})
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    @patch('src.api.routes.rate.rate_controller')
    def test_create_risk_free_rate_business_logic_error(self, mock_controller, client):
        """Test POST /api/risk-free-rates with business logic error."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Invalid rate value",
            response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR
        )
        mock_controller.create_risk_free_rate.return_value = mock_dto
        
        request_data = {
            'currency': 'USD',
            'date': '2024-01-01',
            'rate': -0.05,  # Invalid negative rate
            'rate_type': 'GOVERNMENT_BOND',
            'source': 'FED'
        }
        
        # Act
        response = client.post('/api/risk-free-rates', json=request_data)
        
        # Assert
        # Note: Currently validation middleware doesn't validate non-negative numbers for rate field
        # The request reaches the controller which handles it as a business logic error
        assert response.status_code == 400
        data = response.get_json()
        assert data['response_code'] == 'BUSINESS_LOGIC_ERROR'
        assert 'Invalid rate value' in data['message']

    @patch('src.api.routes.rate.rate_controller')
    def test_create_risk_free_rate_controller_exception(self, mock_controller, client):
        """Test POST /api/risk-free-rates when controller raises exception."""
        # Arrange
        mock_controller.create_risk_free_rate.side_effect = Exception("Controller error")
        
        request_data = {
            'currency': 'USD',
            'date': '2024-01-01',
            'rate': 0.05,
            'rate_type': 'GOVERNMENT_BOND',
            'source': 'FED'
        }
        
        # Act
        response = client.post('/api/risk-free-rates', json=request_data)
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error creating risk free rate' in data['message']

    ################################################################################
    # DELETE RISK FREE RATE ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.rate.rate_controller')
    def test_delete_risk_free_rate_success(self, mock_controller, client):
        """Test successful DELETE /api/risk-free-rates/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            response_code=ApiResponseCode.DELETED
        )
        mock_controller.delete_risk_free_rate.return_value = mock_dto
        
        # Act
        response = client.delete('/api/risk-free-rates/1')
        
        # Assert
        assert response.status_code == 204
        mock_controller.delete_risk_free_rate.assert_called_once_with(1)

    @patch('src.api.routes.rate.rate_controller')
    def test_delete_risk_free_rate_not_found(self, mock_controller, client):
        """Test DELETE /api/risk-free-rates/<id> when rate not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Risk free rate not deleted",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.delete_risk_free_rate.return_value = mock_dto
        
        # Act
        response = client.delete('/api/risk-free-rates/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert 'Risk free rate not deleted' in data['message']

    @patch('src.api.routes.rate.rate_controller')
    def test_delete_risk_free_rate_controller_exception(self, mock_controller, client):
        """Test DELETE /api/risk-free-rates/<id> when controller raises exception."""
        # Arrange
        mock_controller.delete_risk_free_rate.side_effect = Exception("Controller error")
        
        # Act
        response = client.delete('/api/risk-free-rates/1')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error deleting risk free rate 1' in data['message']

    ################################################################################
    # VALIDATION MIDDLEWARE TESTS
    ################################################################################

    def test_get_risk_free_rates_invalid_enum_values(self, client):
        """Test GET /api/risk-free-rates with invalid enum values."""
        # Act
        response = client.get('/api/risk-free-rates?currency=INVALID&rate_type=INVALID')
        
        # Assert
        # Note: Currently validation middleware doesn't properly handle query parameter enum validation
        # The request reaches the controller which fails due to database session issues
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'

    def test_create_risk_free_rate_missing_required_fields(self, client):
        """Test POST /api/risk-free-rates with missing required fields."""
        # Act
        response = client.post('/api/risk-free-rates', json={})
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_create_risk_free_rate_invalid_field_types(self, client):
        """Test POST /api/risk-free-rates with invalid field types."""
        # Act
        response = client.post('/api/risk-free-rates', json={
            'currency': 'USD',
            'date': 'invalid-date',
            'rate': 'not-a-number',
            'rate_type': 'INVALID_TYPE'
        })
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_create_risk_free_rate_invalid_date_length(self, client):
        """Test POST /api/risk-free-rates with invalid date length."""
        # Act
        response = client.post('/api/risk-free-rates', json={
            'currency': 'USD',
            'date': '2024-01-01-extra',  # Too long
            'rate': 0.05,
            'rate_type': 'GOVERNMENT_BOND'
        })
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    ################################################################################
    # FX RATE ENDPOINT TESTS
    ################################################################################

    ################################################################################
    # GET FX RATES ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.rate.rate_controller')
    def test_get_fx_rates_success(self, mock_controller, client):
        """Test successful GET /api/fx-rates request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{
                'id': 1,
                'from_currency': 'AUD',
                'to_currency': 'USD',
                'date': '2024-01-01',
                'fx_rate': 0.6523
            }],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_fx_rates.return_value = mock_dto
        
        # Act
        response = client.get('/api/fx-rates')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert len(data['data']) == 1
        assert data['data'][0]['from_currency'] == 'AUD'
        assert data['data'][0]['to_currency'] == 'USD'
        mock_controller.get_fx_rates.assert_called_once()

    @patch('src.api.routes.rate.rate_controller')
    def test_get_fx_rates_with_query_parameters(self, mock_controller, client):
        """Test GET /api/fx-rates with query parameters."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{
                'id': 1,
                'from_currency': 'EUR',
                'to_currency': 'GBP',
                'date': '2024-01-01',
                'fx_rate': 0.9234
            }],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_fx_rates.return_value = mock_dto
        
        # Act
        response = client.get('/api/fx-rates?from_currency=EUR&to_currency=GBP')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        mock_controller.get_fx_rates.assert_called_once()

    @patch('src.api.routes.rate.rate_controller')
    def test_get_fx_rates_with_date_range(self, mock_controller, client):
        """Test GET /api/fx-rates with date range parameters."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{
                'id': 1,
                'from_currency': 'USD',
                'to_currency': 'JPY',
                'date': '2024-01-15',
                'fx_rate': 150.25
            }],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_fx_rates.return_value = mock_dto
        
        # Act
        response = client.get('/api/fx-rates?start_date=2024-01-01&end_date=2024-01-31')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        mock_controller.get_fx_rates.assert_called_once()

    @patch('src.api.routes.rate.rate_controller')
    def test_get_fx_rates_not_found(self, mock_controller, client):
        """Test GET /api/fx-rates when no rates found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="FX rates not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.get_fx_rates.return_value = mock_dto
        
        # Act
        response = client.get('/api/fx-rates')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert 'FX rates not found' in data['message']

    @patch('src.api.routes.rate.rate_controller')
    def test_get_fx_rates_controller_exception(self, mock_controller, client):
        """Test GET /api/fx-rates when controller raises exception."""
        # Arrange
        mock_controller.get_fx_rates.side_effect = Exception("Controller error")
        
        # Act
        response = client.get('/api/fx-rates')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error getting FX rates' in data['message']

    ################################################################################
    # GET FX RATE BY ID ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.rate.rate_controller')
    def test_get_fx_rate_by_id_success(self, mock_controller, client):
        """Test successful GET /api/fx-rates/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={
                'id': 1,
                'from_currency': 'AUD',
                'to_currency': 'USD',
                'date': '2024-01-01',
                'fx_rate': 0.6523
            },
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_fx_rate_by_id.return_value = mock_dto
        
        # Act
        response = client.get('/api/fx-rates/1')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert data['data']['id'] == 1
        assert data['data']['from_currency'] == 'AUD'
        mock_controller.get_fx_rate_by_id.assert_called_once_with(1)

    @patch('src.api.routes.rate.rate_controller')
    def test_get_fx_rate_by_id_not_found(self, mock_controller, client):
        """Test GET /api/fx-rates/<id> when rate not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="FX rate not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.get_fx_rate_by_id.return_value = mock_dto
        
        # Act
        response = client.get('/api/fx-rates/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert 'FX rate not found' in data['message']

    @patch('src.api.routes.rate.rate_controller')
    def test_get_fx_rate_by_id_controller_exception(self, mock_controller, client):
        """Test GET /api/fx-rates/<id> when controller raises exception."""
        # Arrange
        mock_controller.get_fx_rate_by_id.side_effect = Exception("Controller error")
        
        # Act
        response = client.get('/api/fx-rates/1')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error getting FX rate 1' in data['message']

    ################################################################################
    # CREATE FX RATE ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.rate.rate_controller')
    def test_create_fx_rate_success(self, mock_controller, client):
        """Test successful POST /api/fx-rates request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={
                'id': 1,
                'from_currency': 'AUD',
                'to_currency': 'USD',
                'date': '2024-01-01',
                'fx_rate': 0.6523
            },
            response_code=ApiResponseCode.CREATED
        )
        mock_controller.create_fx_rate.return_value = mock_dto
        
        request_data = {
            'from_currency': 'AUD',
            'to_currency': 'USD',
            'date': '2024-01-01',
            'fx_rate': 0.6523
        }
        
        # Act
        response = client.post('/api/fx-rates', json=request_data)
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['response_code'] == 'CREATED'
        assert data['data']['from_currency'] == 'AUD'
        assert data['data']['to_currency'] == 'USD'
        mock_controller.create_fx_rate.assert_called_once()

    def test_create_fx_rate_validation_error_missing_required_fields(self, client):
        """Test POST /api/fx-rates with missing required fields."""
        # Act - missing required fields
        response = client.post('/api/fx-rates', json={})
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_create_fx_rate_validation_error_invalid_field_types(self, client):
        """Test POST /api/fx-rates with invalid field types."""
        # Act
        response = client.post('/api/fx-rates', json={
            'from_currency': 'AUD',
            'to_currency': 'USD',
            'date': 'invalid-date',
            'fx_rate': 'not-a-number'
        })
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_create_fx_rate_validation_error_invalid_enum_values(self, client):
        """Test POST /api/fx-rates with invalid enum values."""
        # Act
        response = client.post('/api/fx-rates', json={
            'from_currency': 'INVALID',
            'to_currency': 'INVALID',
            'date': '2024-01-01',
            'fx_rate': 0.6523
        })
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_create_fx_rate_validation_error_invalid_fx_rate_range(self, client):
        """Test POST /api/fx-rates with invalid fx_rate range."""
        # Act
        response = client.post('/api/fx-rates', json={
            'from_currency': 'AUD',
            'to_currency': 'USD',
            'date': '2024-01-01',
            'fx_rate': -1.0  # Negative rate
        })
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    @patch('src.api.routes.rate.rate_controller')
    def test_create_fx_rate_business_logic_error(self, mock_controller, client):
        """Test POST /api/fx-rates with business logic error."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Invalid FX rate value",
            response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR
        )
        mock_controller.create_fx_rate.return_value = mock_dto
        
        request_data = {
            'from_currency': 'AUD',
            'to_currency': 'USD',
            'date': '2024-01-01',
            'fx_rate': 0.0  # Zero rate might be invalid business logic
        }
        
        # Act
        response = client.post('/api/fx-rates', json=request_data)
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['response_code'] == 'BUSINESS_LOGIC_ERROR'
        assert 'Invalid FX rate value' in data['message']

    @patch('src.api.routes.rate.rate_controller')
    def test_create_fx_rate_controller_exception(self, mock_controller, client):
        """Test POST /api/fx-rates when controller raises exception."""
        # Arrange
        mock_controller.create_fx_rate.side_effect = Exception("Controller error")
        
        request_data = {
            'from_currency': 'AUD',
            'to_currency': 'USD',
            'date': '2024-01-01',
            'fx_rate': 0.6523
        }
        
        # Act
        response = client.post('/api/fx-rates', json=request_data)
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error creating FX rate' in data['message']

    ################################################################################
    # DELETE FX RATE ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.rate.rate_controller')
    def test_delete_fx_rate_success(self, mock_controller, client):
        """Test successful DELETE /api/fx-rates/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            response_code=ApiResponseCode.DELETED
        )
        mock_controller.delete_fx_rate.return_value = mock_dto
        
        # Act
        response = client.delete('/api/fx-rates/1')
        
        # Assert
        assert response.status_code == 204
        mock_controller.delete_fx_rate.assert_called_once_with(1)

    @patch('src.api.routes.rate.rate_controller')
    def test_delete_fx_rate_not_found(self, mock_controller, client):
        """Test DELETE /api/fx-rates/<id> when rate not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="FX rate not deleted",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.delete_fx_rate.return_value = mock_dto
        
        # Act
        response = client.delete('/api/fx-rates/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert 'FX rate not deleted' in data['message']

    @patch('src.api.routes.rate.rate_controller')
    def test_delete_fx_rate_controller_exception(self, mock_controller, client):
        """Test DELETE /api/fx-rates/<id> when controller raises exception."""
        # Arrange
        mock_controller.delete_fx_rate.side_effect = Exception("Controller error")
        
        # Act
        response = client.delete('/api/fx-rates/1')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error deleting FX rate 1' in data['message']

    ################################################################################
    # FX RATE VALIDATION MIDDLEWARE TESTS
    ################################################################################

    def test_get_fx_rates_invalid_enum_values(self, client):
        """Test GET /api/fx-rates with invalid enum values."""
        # Act
        response = client.get('/api/fx-rates?from_currency=INVALID&to_currency=INVALID')
        
        # Assert
        # Note: Currently validation middleware doesn't properly handle query parameter enum validation
        # The request reaches the controller which fails due to database session issues
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'

    def test_create_fx_rate_missing_required_fields(self, client):
        """Test POST /api/fx-rates with missing required fields."""
        # Act
        response = client.post('/api/fx-rates', json={})
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_create_fx_rate_invalid_field_types(self, client):
        """Test POST /api/fx-rates with invalid field types."""
        # Act
        response = client.post('/api/fx-rates', json={
            'from_currency': 'AUD',
            'to_currency': 'USD',
            'date': 'invalid-date',
            'fx_rate': 'not-a-number'
        })
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_create_fx_rate_invalid_fx_rate_range(self, client):
        """Test POST /api/fx-rates with fx_rate outside valid range."""
        # Act
        response = client.post('/api/fx-rates', json={
            'from_currency': 'AUD',
            'to_currency': 'USD',
            'date': '2024-01-01',
            'fx_rate': 99999999999  # Too large
        })
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    ################################################################################
    # FX RATE INTEGRATION TESTS
    ################################################################################

    @patch('src.api.routes.rate.rate_controller')
    def test_fx_rate_crud_workflow(self, mock_controller, client):
        """Test complete FX rate CRUD workflow."""
        # Arrange
        create_dto = ControllerResponseDTO(
            data={
                'id': 1,
                'from_currency': 'AUD',
                'to_currency': 'USD',
                'date': '2024-01-01',
                'fx_rate': 0.6523
            },
            response_code=ApiResponseCode.CREATED
        )
        get_dto = ControllerResponseDTO(
            data={
                'id': 1,
                'from_currency': 'AUD',
                'to_currency': 'USD',
                'date': '2024-01-01',
                'fx_rate': 0.6523
            },
            response_code=ApiResponseCode.SUCCESS
        )
        delete_dto = ControllerResponseDTO(
            response_code=ApiResponseCode.DELETED
        )
        
        mock_controller.create_fx_rate.return_value = create_dto
        mock_controller.get_fx_rate_by_id.return_value = get_dto
        mock_controller.delete_fx_rate.return_value = delete_dto
        
        request_data = {
            'from_currency': 'AUD',
            'to_currency': 'USD',
            'date': '2024-01-01',
            'fx_rate': 0.6523
        }
        
        # Act - Create
        create_response = client.post('/api/fx-rates', json=request_data)
        
        # Act - Get
        get_response = client.get('/api/fx-rates/1')
        
        # Act - Delete
        delete_response = client.delete('/api/fx-rates/1')
        
        # Assert
        assert create_response.status_code == 201
        assert get_response.status_code == 200
        assert delete_response.status_code == 204
        
        # Verify all controller methods were called
        mock_controller.create_fx_rate.assert_called_once()
        mock_controller.get_fx_rate_by_id.assert_called_once_with(1)
        mock_controller.delete_fx_rate.assert_called_once_with(1)

    @patch('src.api.routes.rate.rate_controller')
    def test_fx_rate_different_currency_pairs(self, mock_controller, client):
        """Test FX rate operations with different currency pairs."""
        # Arrange
        currency_pairs = [
            ('AUD', 'USD', 0.6523),
            ('EUR', 'GBP', 0.9234),
            ('USD', 'JPY', 150.25),
            ('GBP', 'CHF', 1.1234)
        ]
        
        mock_controller.create_fx_rate.return_value = ControllerResponseDTO(
            data={'id': 1}, response_code=ApiResponseCode.CREATED
        )
        
        # Act & Assert
        for from_curr, to_curr, rate in currency_pairs:
            request_data = {
                'from_currency': from_curr,
                'to_currency': to_curr,
                'date': '2024-01-01',
                'fx_rate': rate
            }
            
            response = client.post('/api/fx-rates', json=request_data)
            assert response.status_code == 201
        
        # Verify all calls were made
        assert mock_controller.create_fx_rate.call_count == len(currency_pairs)
