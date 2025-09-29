"""
Health Check Route Tests.

This module tests the health check API route with a focus on HTTP layer concerns:
- Route registration and endpoint availability
- Response formatting and status codes
- Error handling and controller integration
- Basic functionality verification

Test Coverage:
- Health check endpoint (GET)
- Response format validation
- Error handling scenarios
- HTTP method validation
"""

import pytest
from unittest.mock import Mock, patch
from flask import Flask

from src.api.routes.health_check import health_check_bp


class TestHealthCheckRoutes:
    """Test suite for health check API routes."""

    @pytest.fixture
    def app(self):
        """Create Flask app with health check blueprint registered."""
        app = Flask(__name__)
        app.register_blueprint(health_check_bp)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    ################################################################################
    # ROUTE REGISTRATION TESTS
    ################################################################################

    def test_health_check_blueprint_registered(self, app):
        """Test that health check blueprint is properly registered."""
        # Check that health check routes are registered
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/api/health-check'
        ]
        
        for route in expected_routes:
            assert any(route in rule for rule in rules), f"Route {route} not found in registered routes"

    ################################################################################
    # HEALTH CHECK ENDPOINT TESTS
    ################################################################################

    def test_health_check_success(self, client):
        """Test successful GET /api/health-check request."""
        # Act
        response = client.get('/api/health-check')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['message'] == 'API is running'

    def test_health_check_response_format(self, client):
        """Test that health check returns proper JSON format."""
        # Act
        response = client.get('/api/health-check')
        
        # Assert
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'status' in data
        assert 'message' in data
        assert data['status'] == 'ok'
        assert data['message'] == 'API is running'

    @patch('src.api.routes.health_check.health_check_controller')
    def test_health_check_controller_error(self, mock_controller, client):
        """Test health check when controller raises an exception."""
        # Arrange
        mock_controller.health_check.side_effect = Exception("Test error")
        
        # Act
        response = client.get('/api/health-check')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error in health check' in data['message']

    @patch('src.api.routes.health_check.health_check_controller')
    def test_health_check_controller_returns_error_response(self, mock_controller, client):
        """Test health check when controller returns error response."""
        # Arrange
        mock_controller.health_check.return_value = ({'error': 'Service unavailable'}, 503)
        
        # Act
        response = client.get('/api/health-check')
        
        # Assert
        assert response.status_code == 503
        data = response.get_json()
        assert data['error'] == 'Service unavailable'

    ################################################################################
    # HTTP METHOD TESTS
    ################################################################################

    def test_unsupported_http_methods(self, client):
        """Test that unsupported HTTP methods return 405."""
        # Test POST method
        response = client.post('/api/health-check')
        assert response.status_code == 405
        
        # Test PUT method
        response = client.put('/api/health-check')
        assert response.status_code == 405
        
        # Test DELETE method
        response = client.delete('/api/health-check')
        assert response.status_code == 405
        
        # Test PATCH method
        response = client.patch('/api/health-check')
        assert response.status_code == 405

    ################################################################################
    # CONTROLLER INTEGRATION TESTS
    ################################################################################

    @patch('src.api.routes.health_check.health_check_controller')
    def test_controller_called_correctly(self, mock_controller, client):
        """Test that the controller is called correctly."""
        # Arrange
        mock_controller.health_check.return_value = ({'status': 'ok', 'message': 'API is running'}, 200)
        
        # Act
        response = client.get('/api/health-check')
        
        # Assert
        assert response.status_code == 200
        mock_controller.health_check.assert_called_once()

    @patch('src.api.routes.health_check.health_check_controller')
    def test_controller_response_passthrough(self, mock_controller, client):
        """Test that controller response is passed through correctly."""
        # Arrange
        custom_response = {'status': 'custom', 'message': 'Custom health check', 'version': '1.0.0'}
        mock_controller.health_check.return_value = (custom_response, 200)
        
        # Act
        response = client.get('/api/health-check')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data == custom_response

    ################################################################################
    # EDGE CASE TESTS
    ################################################################################

    def test_health_check_with_query_parameters(self, client):
        """Test health check with query parameters (should be ignored)."""
        # Act
        response = client.get('/api/health-check?debug=true&verbose=1')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['message'] == 'API is running'

    def test_health_check_with_headers(self, client):
        """Test health check with custom headers."""
        # Act
        response = client.get('/api/health-check', headers={
            'Accept': 'application/json',
            'User-Agent': 'TestClient/1.0'
        })
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['message'] == 'API is running'

    ################################################################################
    # PERFORMANCE AND RELIABILITY TESTS
    ################################################################################

    def test_health_check_multiple_requests(self, client):
        """Test that health check works consistently across multiple requests."""
        # Act & Assert
        for i in range(5):
            response = client.get('/api/health-check')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'ok'
            assert data['message'] == 'API is running'

    @patch('src.api.routes.health_check.health_check_controller')
    def test_health_check_concurrent_requests(self, mock_controller, client):
        """Test health check with concurrent requests."""
        # Arrange
        mock_controller.health_check.return_value = ({'status': 'ok', 'message': 'API is running'}, 200)
        
        # Act - simulate concurrent requests
        responses = []
        for _ in range(3):
            response = client.get('/api/health-check')
            responses.append(response)
        
        # Assert
        for response in responses:
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'ok'
            assert data['message'] == 'API is running'
        
        # Controller should be called for each request
        assert mock_controller.health_check.call_count == 3
