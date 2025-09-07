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

from src.fund.models import Fund
from src.fund.enums import FundStatus
from src.tax.models import TaxStatement


class DashboardController:
    """
    Controller for dashboard operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for dashboard operations. It delegates business logic to the domain
    models and handles request/response formatting.
    
    Attributes:
        None - Direct domain model usage for simplicity
    """
    
    def __init__(self):
        """Initialize the dashboard controller."""
        pass
    
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
    
    def portfolio_summary(self, session: Session) -> tuple:
        """
        Get overall portfolio summary with key metrics.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Use domain methods to get all funds
            funds = Fund.get_all(session=session)
            
            # Calculate summary metrics using domain data
            total_funds = len(funds)
            active_funds = sum(1 for fund in funds if fund.status == FundStatus.ACTIVE)
            total_equity = sum(fund.current_equity_balance or 0.0 for fund in funds)
            total_avg_equity = sum(fund.average_equity_balance or 0.0 for fund in funds)
            
            # Get tax statements count using domain method
            total_tax_statements = session.query(TaxStatement).count()
            
            summary = {
                "total_funds": total_funds,
                "active_funds": active_funds,
                "total_equity_balance": float(total_equity),
                "total_average_equity_balance": float(total_avg_equity),
                "total_tax_statements": total_tax_statements,
                "last_updated": date.today().isoformat()
            }
            
            return jsonify(summary), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting portfolio summary: {str(e)}")
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
            # Use domain methods to get all funds
            funds = Fund.get_all(session=session)
            
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
    
    def dashboard_performance(self, session: Session) -> tuple:
        """
        Get performance data for all funds.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get all funds using domain methods
            funds = Fund.get_all(session=session)
            
            performance_data = []
            for fund in funds:
                performance_data.append({
                    "fund_id": fund.id,
                    "fund_name": fund.name,
                    "current_equity": float(fund.current_equity_balance) if fund.current_equity_balance else 0.0,
                    "average_equity": float(fund.average_equity_balance) if fund.average_equity_balance else 0.0
                })
            
            # Sort by fund name
            performance_data.sort(key=lambda x: x['fund_name'])
            
            return jsonify({"performance": performance_data}), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting dashboard performance: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
