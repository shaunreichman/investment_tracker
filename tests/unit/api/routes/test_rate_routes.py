"""
Rate Route Tests - New Concise Version.

This module tests the rate API routes focusing on HTTP layer concerns:
- Route registration and endpoint availability
- Request validation and parameter handling
- Response formatting and status codes
- Error handling and middleware integration
- Controller delegation and DTO handling

Test Coverage:
- All rate endpoints (GET, POST, DELETE) for both risk-free rates and FX rates
- Validation middleware integration
- Response handler integration
- Error handling and status codes
"""

import pytest
from unittest.mock import Mock, patch
from flask import Flask

from src.api.routes.rate_route import rate_bp
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

    ################################################################################
    # ROUTE REGISTRATION TESTS
    ################################################################################

    def test_rate_blueprint_registered(self, app):
        """Test that rate blueprint is properly registered."""
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
    # RISK FREE RATE ENDPOINTS TESTS
    ################################################################################

    @patch('src.api.routes.rate_route.rate_controller')
    def test_get_risk_free_rates_success(self, mock_controller, client):
        """Test successful GET /api/risk-free-rates request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'currency': 'USD', 'date': '2024-01-01', 'rate': 0.05}],
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
        mock_controller.get_risk_free_rates.assert_called_once()

    @patch('src.api.routes.rate_route.rate_controller')
    def test_get_risk_free_rates_with_query_params(self, mock_controller, client):
        """Test GET /api/risk-free-rates with query parameters."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'currency': 'USD', 'date': '2024-01-01', 'rate': 0.05}],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_risk_free_rates.return_value = mock_dto
        
        # Act
        response = client.get('/api/risk-free-rates?currencies=USD&rate_types=GOVERNMENT_BOND')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        mock_controller.get_risk_free_rates.assert_called_once()

    @patch('src.api.routes.rate_route.rate_controller')
    def test_get_risk_free_rate_by_id_success(self, mock_controller, client):
        """Test successful GET /api/risk-free-rates/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'currency': 'USD', 'date': '2024-01-01', 'rate': 0.05},
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

    @patch('src.api.routes.rate_route.rate_controller')
    def test_create_risk_free_rate_success(self, mock_controller, client):
        """Test successful POST /api/risk-free-rates request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'currency': 'USD', 'date': '2024-01-01', 'rate': 0.05},
            response_code=ApiResponseCode.CREATED
        )
        mock_controller.create_risk_free_rate.return_value = mock_dto
        
        request_data = {
            'currency': 'USD',
            'date': '2024-01-01',
            'rate': 0.05,
            'rate_type': 'GOVERNMENT_BOND'
        }
        
        # Act
        response = client.post('/api/risk-free-rates', json=request_data)
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['response_code'] == 'CREATED'
        assert data['data']['currency'] == 'USD'
        mock_controller.create_risk_free_rate.assert_called_once()

    @patch('src.api.routes.rate_route.rate_controller')
    def test_delete_risk_free_rate_success(self, mock_controller, client):
        """Test successful DELETE /api/risk-free-rates/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
        mock_controller.delete_risk_free_rate.return_value = mock_dto
        
        # Act
        response = client.delete('/api/risk-free-rates/1')
        
        # Assert
        assert response.status_code == 204
        mock_controller.delete_risk_free_rate.assert_called_once_with(1)

    ################################################################################
    # FX RATE ENDPOINTS TESTS
    ################################################################################

    @patch('src.api.routes.rate_route.rate_controller')
    def test_get_fx_rates_success(self, mock_controller, client):
        """Test successful GET /api/fx-rates request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'from_currency': 'AUD', 'to_currency': 'USD', 'date': '2024-01-01', 'fx_rate': 0.6523}],
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
        mock_controller.get_fx_rates.assert_called_once()

    @patch('src.api.routes.rate_route.rate_controller')
    def test_get_fx_rates_with_query_params(self, mock_controller, client):
        """Test GET /api/fx-rates with query parameters."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'from_currency': 'EUR', 'to_currency': 'GBP', 'date': '2024-01-01', 'fx_rate': 0.9234}],
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

    @patch('src.api.routes.rate_route.rate_controller')
    def test_get_fx_rate_by_id_success(self, mock_controller, client):
        """Test successful GET /api/fx-rates/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'from_currency': 'AUD', 'to_currency': 'USD', 'date': '2024-01-01', 'fx_rate': 0.6523},
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
        mock_controller.get_fx_rate_by_id.assert_called_once_with(1)

    @patch('src.api.routes.rate_route.rate_controller')
    def test_create_fx_rate_success(self, mock_controller, client):
        """Test successful POST /api/fx-rates request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={'id': 1, 'from_currency': 'AUD', 'to_currency': 'USD', 'date': '2024-01-01', 'fx_rate': 0.6523},
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
        mock_controller.create_fx_rate.assert_called_once()

    @patch('src.api.routes.rate_route.rate_controller')
    def test_delete_fx_rate_success(self, mock_controller, client):
        """Test successful DELETE /api/fx-rates/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
        mock_controller.delete_fx_rate.return_value = mock_dto
        
        # Act
        response = client.delete('/api/fx-rates/1')
        
        # Assert
        assert response.status_code == 204
        mock_controller.delete_fx_rate.assert_called_once_with(1)

    ################################################################################
    # VALIDATION MIDDLEWARE TESTS
    ################################################################################

    def test_create_risk_free_rate_validation_error_missing_required_fields(self, client):
        """Test POST /api/risk-free-rates with missing required fields."""
        # Act
        response = client.post('/api/risk-free-rates', json={})
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_create_risk_free_rate_validation_error_invalid_field_types(self, client):
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

    def test_create_fx_rate_validation_error_missing_required_fields(self, client):
        """Test POST /api/fx-rates with missing required fields."""
        # Act
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

    def test_create_fx_rate_validation_error_invalid_range(self, client):
        """Test POST /api/fx-rates with fx_rate outside valid range."""
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

    def test_get_risk_free_rates_invalid_enum_values(self, client):
        """Test GET /api/risk-free-rates with invalid enum values."""
        # Act
        response = client.get('/api/risk-free-rates?currencies=INVALID&rate_types=INVALID')
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_get_fx_rates_invalid_enum_values(self, client):
        """Test GET /api/fx-rates with invalid enum values."""
        # Act
        response = client.get('/api/fx-rates?from_currency=INVALID&to_currency=INVALID')
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_get_risk_free_rates_mutually_exclusive_currency_params(self, client):
        """Test GET /api/risk-free-rates with mutually exclusive currency parameters."""
        # Act - using both currency and currencies (mutually exclusive)
        response = client.get('/api/risk-free-rates?currency=USD&currencies=EUR')
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_get_risk_free_rates_mutually_exclusive_rate_type_params(self, client):
        """Test GET /api/risk-free-rates with mutually exclusive rate_type parameters."""
        # Act - using both rate_type and rate_types (mutually exclusive)
        response = client.get('/api/risk-free-rates?rate_type=GOVERNMENT_BOND&rate_types=TREASURY_BILL')
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    def test_create_risk_free_rate_validation_error_invalid_date_length(self, client):
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

    def test_create_risk_free_rate_validation_error_invalid_enum_values(self, client):
        """Test POST /api/risk-free-rates with invalid enum values."""
        # Act
        response = client.post('/api/risk-free-rates', json={
            'currency': 'INVALID',
            'date': '2024-01-01',
            'rate': 0.05,
            'rate_type': 'INVALID_TYPE'
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

    def test_create_fx_rate_validation_error_fx_rate_too_large(self, client):
        """Test POST /api/fx-rates with fx_rate exceeding maximum range."""
        # Act
        response = client.post('/api/fx-rates', json={
            'from_currency': 'AUD',
            'to_currency': 'USD',
            'date': '2024-01-01',
            'fx_rate': 99999999999  # Too large (max is 9999999999)
        })
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation_error' in data['type']

    ################################################################################
    # ERROR HANDLING TESTS
    ################################################################################

    @patch('src.api.routes.rate_route.rate_controller')
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

    @patch('src.api.routes.rate_route.rate_controller')
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

    @patch('src.api.routes.rate_route.rate_controller')
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
            'rate_type': 'GOVERNMENT_BOND'
        }
        
        # Act
        response = client.post('/api/risk-free-rates', json=request_data)
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['response_code'] == 'BUSINESS_LOGIC_ERROR'
        assert 'Invalid rate value' in data['message']

    @patch('src.api.routes.rate_route.rate_controller')
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

    @patch('src.api.routes.rate_route.rate_controller')
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

    @patch('src.api.routes.rate_route.rate_controller')
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
