"""
Dashboard API Controller.

This controller handles HTTP requests for dashboard operations,
providing RESTful endpoints for portfolio summary, funds list, and performance data.

Key responsibilities:
- Portfolio summary endpoints
- Funds list and metrics
- Recent events aggregation
- Performance data compilation
- Input validation and error handling
"""

from typing import List, Optional, Dict, Any
from flask import request, jsonify, current_app
from sqlalchemy.orm import Session
from datetime import date, timedelta

from src.fund.services.fund_service import FundService


class DashboardController:
    """
    Controller for dashboard operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for dashboard operations. It delegates business logic to the domain
    models and handles request/response formatting.
    
    Attributes:
        fund_service (FundService): Service for fund operations
    """
    
    def __init__(self):
        """Initialize the dashboard controller."""
        self.fund_service = FundService()
    
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
    
    
    def funds_list(self, session: Session) -> tuple:
        """
        Get list of all funds with key metrics.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Use service layer to get all funds (follows proper architecture)
            funds = self.fund_service.get_funds(session)
            
            fund_data = []
            for fund in funds:
                fund_data.append({
                    "id": fund.id,
                    "name": fund.name,
                    "fund_type": fund.fund_type,
                    "tracking_type": fund.tracking_type.value if fund.tracking_type else None,
                    "currency": fund.currency,
                    "current_equity_balance": float(fund.current_equity_balance) if fund.current_equity_balance else 0.0,
                    "average_equity_balance": float(fund.average_equity_balance) if fund.average_equity_balance else 0.0,
                    "status": fund.status.value if fund.status else None,
                    "investment_company": fund.investment_company.name if fund.investment_company else "Unknown",
                    "entity": fund.entity.name if fund.entity else "Unknown",
                    "created_at": fund.created_at.isoformat() if fund.created_at else None
                })
            
            return jsonify({"funds": fund_data}), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting funds list: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
