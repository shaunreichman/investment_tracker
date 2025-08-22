"""
Company API Controller.

This controller handles HTTP requests for investment company operations,
providing RESTful endpoints for company management.

Key responsibilities:
- Investment company CRUD endpoints
- Company overview and performance data
- Company fund management
- Input validation and error handling
"""

from typing import List, Optional, Dict, Any
from flask import request, jsonify, current_app
from sqlalchemy.orm import Session

from src.investment_company.models import InvestmentCompany
from src.fund.enums import FundStatus


class CompanyController:
    """
    Controller for investment company operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for investment company operations. It delegates business logic to the
    InvestmentCompany domain model and handles request/response formatting.
    
    Attributes:
        None - Direct domain model usage for simplicity
    """
    
    def __init__(self):
        """Initialize the company controller."""
        pass
    
    def get_investment_companies(self, session: Session) -> tuple:
        """
        Get list of all investment companies with summary data.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Use domain methods to get companies with funds
            companies = session.query(InvestmentCompany).all()
            
            companies_data = []
            for company in companies:
                # Get fund count and summary data using domain methods
                total_funds = company.get_total_funds_under_management(session)
                total_commitments = company.get_total_commitments(session)
                active_funds = 0
                for fund in company.funds:
                    if fund.status == FundStatus.ACTIVE:
                        active_funds += 1
                total_equity = sum(fund.current_equity_balance or 0.0 for fund in company.funds)
                
                companies_data.append({
                    "id": company.id,
                    "name": company.name,
                    "description": company.description,
                    "website": company.website,
                    "company_type": company.company_type,
                    "business_address": company.business_address,
                    "fund_count": total_funds,
                    "active_funds": active_funds,
                    "total_commitments": float(total_commitments) if total_commitments else 0.0,
                    "total_equity_balance": float(total_equity),
                    "created_at": company.created_at.isoformat() if company.created_at else None,
                    "updated_at": company.updated_at.isoformat() if company.updated_at else None
                })
            
            return jsonify({"companies": companies_data}), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting investment companies: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def create_investment_company(self, session: Session) -> tuple:
        """
        Create a new investment company using domain methods.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Check if request has valid JSON
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 400
            
            try:
                data = request.get_json()
            except Exception:
                return jsonify({"error": "Invalid JSON format"}), 400
            
            if data is None:
                return jsonify({"error": "Request body is required"}), 400
            
            # Validate required fields
            required_fields = ['name']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Validate name length
            if len(data['name'].strip()) < 2:
                return jsonify({"error": "Company name must be at least 2 characters"}), 400
            
            if len(data['name'].strip()) > 255:
                return jsonify({"error": "Company name must be less than 255 characters"}), 400
            
            # Use domain method to create company (handles duplicate checking)
            company = InvestmentCompany.create(
                name=data['name'].strip(),
                description=data.get('description'),
                website=data.get('website'),
                company_type=data.get('company_type'),
                business_address=data.get('business_address'),
                session=session
            )
            
            # Commit the transaction
            session.commit()
            
            return jsonify({
                "id": company.id,
                "name": company.name,
                "description": company.description,
                "website": company.website,
                "company_type": company.company_type,
                "business_address": company.business_address,
                "created_at": company.created_at.isoformat() if company.created_at else None
            }), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error creating investment company: {str(e)}")
            session.rollback()
            return jsonify({"error": "Internal server error"}), 500
    
    def create_investment_company_with_data(self, session: Session, data: dict) -> tuple:
        """
        Create a new investment company with pre-validated data.
        
        Args:
            session: Database session
            data: Pre-validated company data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Use domain method to create company (handles duplicate checking)
            company = InvestmentCompany.create(
                name=data['name'],
                description=data.get('description'),
                website=data.get('website'),
                company_type=data.get('company_type'),
                business_address=data.get('business_address'),
                session=session
            )
            
            # Commit the transaction
            session.commit()
            
            return jsonify({
                "id": company.id,
                "name": company.name,
                "description": company.description,
                "website": company.website,
                "company_type": company.company_type,
                "business_address": company.business_address,
                "created_at": company.created_at.isoformat() if company.created_at else None
            }), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error creating investment company: {str(e)}")
            session.rollback()
            return jsonify({"error": "Internal server error"}), 500
    
    def get_company_funds(self, company_id: int, session: Session) -> tuple:
        """
        Get funds for a specific investment company.
        
        Args:
            company_id: ID of the investment company
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get company using domain method
            company = InvestmentCompany.get_by_id(company_id, session=session)
            
            if not company:
                return jsonify({"error": "Investment company not found"}), 404
            
            # Get funds using domain method
            funds = company.get_funds_with_summary(session=session)
            
            # Include company information with updated structure
            company_data = {
                "id": company.id,
                "name": company.name,
                "description": company.description,
                "website": company.website,
                "company_type": company.company_type,
                "business_address": company.business_address,
                "contacts": [
                    {
                        "id": contact.id,
                        "name": contact.name,
                        "title": contact.title,
                        "direct_number": contact.direct_number,
                        "direct_email": contact.direct_email,
                        "notes": contact.notes
                    }
                    for contact in company.contacts
                ]
            }
            
            return jsonify({
                "company": company_data,
                "funds": funds
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting company funds for company {company_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_company_overview(self, company_id: int, session: Session) -> tuple:
        """
        Get company overview data using domain method.
        
        Args:
            company_id: ID of the investment company
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get company using domain method
            company = InvestmentCompany.get_by_id(company_id, session=session)
            
            if not company:
                return jsonify({"error": "Investment company not found"}), 404
            
            # Use domain method to get comprehensive overview data
            overview_data = company.get_company_summary_data(session=session)
            
            return jsonify(overview_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting company overview for company {company_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_company_details(self, company_id: int, session: Session) -> tuple:
        """
        Get detailed company information.
        
        Args:
            company_id: ID of the investment company
            session: Session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get company using domain method
            company = InvestmentCompany.get_by_id(company_id, session=session)
            
            if not company:
                return jsonify({"error": "Investment company not found"}), 404
            
            # Return company details with contacts
            company_data = {
                "company": {
                    "id": company.id,
                    "name": company.name,
                    "company_type": company.company_type,
                    "business_address": company.business_address,
                    "website": company.website,
                    "contacts": [
                        {
                            "id": contact.id,
                            "name": contact.name,
                            "title": contact.title,
                            "direct_number": contact.direct_number,
                            "direct_email": contact.direct_email,
                            "notes": contact.notes
                        }
                        for contact in company.contacts
                    ]
                }
            }
            
            return jsonify(company_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting company details for company {company_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_company_funds_enhanced(self, company_id: int, session: Session) -> tuple:
        """
        Get enhanced fund data for a specific investment company with sorting, filtering, and pagination.
        
        Args:
            company_id: ID of the investment company
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get company using domain method
            company = InvestmentCompany.get_by_id(company_id, session=session)
            
            if not company:
                return jsonify({"error": "Investment company not found"}), 404
            
            # Get query parameters with validation
            sort_by = request.args.get('sort_by', 'start_date')
            sort_order = request.args.get('sort_order', 'desc')
            status_filter = request.args.get('status_filter', 'all')
            search = request.args.get('search', '')
            
            # Validate and parse numeric parameters with fallbacks
            try:
                page = int(request.args.get('page', 1))
                # Don't validate page - accept any value and handle edge cases gracefully
            except (ValueError, TypeError):
                page = 1
            
            try:
                per_page = int(request.args.get('per_page', 25))
                if per_page < 1:
                    per_page = 25
                elif per_page > 100:
                    per_page = 100
            except (ValueError, TypeError):
                per_page = 25
            
            # Get all funds for this company
            all_funds = company.get_funds_with_summary(session=session)
            
            # Apply status filter
            if status_filter != 'all':
                from src.fund.enums import FundStatus
                status_map = {
                    'active': FundStatus.ACTIVE,
                    'completed': FundStatus.COMPLETED,
                    'suspended': FundStatus.SUSPENDED
                }
                # Only apply filter if status_filter is valid, otherwise ignore it
                if status_filter in status_map:
                    all_funds = [f for f in all_funds if f.status == status_map[status_filter]]
            
            # Apply search filter
            if search:
                search_lower = search.lower()
                all_funds = [f for f in all_funds if search_lower in f.name.lower()]
            
            # Sort funds
            reverse_sort = sort_order.lower() == 'desc'
            if sort_by == 'name':
                all_funds.sort(key=lambda x: x.name.lower(), reverse=reverse_sort)
            elif sort_by == 'start_date':
                from datetime import date
                all_funds.sort(key=lambda x: x.start_date or date.min, reverse=reverse_sort)
            elif sort_by == 'status':
                all_funds.sort(key=lambda x: x.status.value if x.status else '', reverse=reverse_sort)
            elif sort_by == 'current_equity_balance':
                all_funds.sort(key=lambda x: x.current_equity_balance or 0.0, reverse=reverse_sort)
            else:
                # Default to name sorting
                all_funds.sort(key=lambda x: x.name.lower(), reverse=reverse_sort)
            
            # Calculate pagination
            total_funds = len(all_funds)
            total_pages = (total_funds + per_page - 1) // per_page
            
            # Apply pagination
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            paginated_funds = all_funds[start_index:end_index]
            
            # Prepare response data
            funds_data = []
            for fund in paginated_funds:
                fund_data = {
                    "id": fund.id,
                    "name": fund.name,
                    "fund_type": fund.fund_type.value if fund.fund_type else None,
                    "tracking_type": fund.tracking_type.value if fund.tracking_type else None,
                    "currency": fund.currency,
                    "start_date": fund.start_date.isoformat() if fund.start_date else None,
                    "status": fund.status.value if fund.status else None,
                    "current_equity_balance": float(fund.current_equity_balance) if fund.current_equity_balance else 0.0,
                    "average_equity_balance": float(fund.average_equity_balance) if fund.average_equity_balance else 0.0,
                    "total_commitments": float(fund.total_commitments) if fund.total_commitments else 0.0,
                    "total_capital_called": float(fund.total_capital_called) if fund.total_capital_called else 0.0,
                    "total_distributions": float(fund.total_distributions) if fund.total_distributions else 0.0,
                    "entity": fund.entity.name if fund.entity else "Unknown",
                    "created_at": fund.created_at.isoformat() if fund.created_at else None
                }
                funds_data.append(fund_data)
            
            # Return paginated response
            response_data = {
                "funds": funds_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_funds": total_funds,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                },
                "filters": {
                    "status_filter": status_filter,
                    "search": search,
                    "sort_by": sort_by,
                    "sort_order": sort_order
                }
            }
            
            return jsonify(response_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting enhanced company funds for company {company_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
