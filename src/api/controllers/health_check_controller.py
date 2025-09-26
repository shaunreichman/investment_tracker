"""
Health Check API Controller.

This controller handles HTTP requests for health check operations,
providing RESTful endpoints for portfolio summary, funds list, and performance data.

Key responsibilities:
- Health check endpoints
"""

from flask import jsonify, current_app


class HealthCheckController:
    """
    Controller for health check operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for health check operations. It delegates business logic to the domain
    models and handles request/response formatting.
    """
    
    def __init__(self):
        """Initialize the health check controller."""
    
    def health_check(self) -> tuple:
        """
        Health check endpoint.
        
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            return jsonify({"status": "ok", "message": "API is running"}), 200
        except Exception as e:
            current_app.logger.error(f"Error in health check: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    