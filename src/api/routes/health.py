"""
Health Check API Routes.

This module provides health check endpoints for production monitoring,
including system health, banking health, and performance metrics.
"""

from flask import Blueprint, jsonify, request
from src.api.database import get_db_session
from src.banking.services.banking_health_service import get_banking_health_service
import logging

# Create blueprint for health check routes
health_bp = Blueprint('health', __name__)

# Initialize health services
banking_health_service = get_banking_health_service()

logger = logging.getLogger(__name__)


@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Simple health status for load balancers and basic monitoring
    """
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": "2025-01-16T00:00:00Z",
            "service": "investment_tracker",
            "version": "1.0.0"
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@health_bp.route('/api/health/banking', methods=['GET'])
def banking_health_check():
    """
    Comprehensive banking system health check.
    
    Query Parameters:
        detailed (bool): Include detailed health information (default: false)
        
    Returns:
        Detailed banking system health status
    """
    try:
        detailed = request.args.get('detailed', 'false').lower() == 'true'
        
        session = get_db_session()
        try:
            if detailed:
                # Full health check
                health_status = banking_health_service.get_system_health(session)
                status_code = 200 if health_status['overall_status'] in ['healthy', 'degraded'] else 503
            else:
                # Quick health summary
                health_status = banking_health_service.get_health_summary()
                status_code = 200 if health_status['status'] in ['healthy', 'degraded'] else 503
            
            return jsonify(health_status), status_code
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Banking health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-01-16T00:00:00Z"
        }), 500


@health_bp.route('/api/health/banking/trends', methods=['GET'])
def banking_health_trends():
    """
    Get banking health trends over time.
    
    Query Parameters:
        hours (int): Number of hours to analyze (default: 24, max: 168)
        
    Returns:
        Health trends and status distribution
    """
    try:
        hours = min(int(request.args.get('hours', 24)), 168)  # Cap at 1 week
        
        trends = banking_health_service.get_health_trends(hours)
        
        return jsonify({
            "trends": trends,
            "timestamp": "2025-01-16T00:00:00Z"
        }), 200
        
    except Exception as e:
        logger.error(f"Health trends failed: {e}")
        return jsonify({
            "error": str(e),
            "timestamp": "2025-01-16T00:00:00Z"
        }), 500


@health_bp.route('/api/health/banking/cache', methods=['GET'])
def banking_cache_health():
    """
    Get banking cache health status.
    
    Returns:
        Cache system health and statistics
    """
    try:
        session = get_db_session()
        try:
            # Get cache health from banking health service
            health_status = banking_health_service.get_system_health(session)
            cache_health = health_status.get('checks', {}).get('cache', {})
            
            return jsonify({
                "cache_health": cache_health,
                "timestamp": "2025-01-16T00:00:00Z"
            }), 200
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return jsonify({
            "error": str(e),
            "timestamp": "2025-01-16T00:00:00Z"
        }), 500


@health_bp.route('/api/health/banking/performance', methods=['GET'])
def banking_performance_health():
    """
    Get banking performance metrics.
    
    Returns:
        Performance metrics and thresholds
    """
    try:
        session = get_db_session()
        try:
            # Get performance metrics from banking health service
            health_status = banking_health_service.get_system_health(session)
            performance_health = health_status.get('checks', {}).get('performance', {})
            
            return jsonify({
                "performance_metrics": performance_health,
                "timestamp": "2025-01-16T00:00:00Z"
            }), 200
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Performance health check failed: {e}")
        return jsonify({
            "error": str(e),
            "timestamp": "2025-01-16T00:00:00Z"
        }), 500


@health_bp.route('/api/health/banking/business-logic', methods=['GET'])
def banking_business_logic_health():
    """
    Get banking business logic integrity check.
    
    Returns:
        Business logic validation results
    """
    try:
        session = get_db_session()
        try:
            # Get business logic health from banking health service
            health_status = banking_health_service.get_system_health(session)
            business_logic_health = health_status.get('checks', {}).get('business_logic', {})
            
            return jsonify({
                "business_logic_health": business_logic_health,
                "timestamp": "2025-01-16T00:00:00Z"
            }), 200
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Business logic health check failed: {e}")
        return jsonify({
            "error": str(e),
            "timestamp": "2025-01-16T00:00:00Z"
        }), 500


@health_bp.route('/api/health/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check for Kubernetes/container orchestration.
    
    This endpoint checks if the service is ready to receive traffic.
    
    Returns:
        Readiness status
    """
    try:
        session = get_db_session()
        try:
            # Quick database connectivity check
            result = session.execute("SELECT 1")
            result.fetchone()
            
            return jsonify({
                "status": "ready",
                "timestamp": "2025-01-16T00:00:00Z"
            }), 200
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            "status": "not_ready",
            "error": str(e),
            "timestamp": "2025-01-16T00:00:00Z"
        }), 503


@health_bp.route('/api/health/live', methods=['GET'])
def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration.
    
    This endpoint checks if the service is alive and responsive.
    
    Returns:
        Liveness status
    """
    try:
        return jsonify({
            "status": "alive",
            "timestamp": "2025-01-16T00:00:00Z"
        }), 200
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return jsonify({
            "status": "not_alive",
            "error": str(e),
            "timestamp": "2025-01-16T00:00:00Z"
        }), 503
