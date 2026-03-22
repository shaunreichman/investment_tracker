"""
Health Check API Controller.
"""

from flask import jsonify, current_app


class HealthCheckController:
    """
    Controller for health check operations.
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
    
    