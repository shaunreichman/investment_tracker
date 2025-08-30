"""
Company API Controller.

This controller handles HTTP requests for investment company operations,
providing RESTful endpoints for company management.

Key responsibilities:
- Investment company CRUD endpoints
- Company overview and performance data
- Company fund management
- Input validation and error handling

This controller now uses services directly instead of model methods,
maintaining clean separation of concerns.
"""

from typing import List, Optional, Dict, Any
from flask import request, jsonify, current_app
from sqlalchemy.orm import Session

from src.investment_company.models import InvestmentCompany
from src.investment_company.services import (
    CompanyService,
    CompanyPortfolioService,
    CompanySummaryService,
    CompanyValidationService
)
from src.fund.enums import FundStatus
from src.investment_company.enums import CompanyStatus


class CompanyController:
    """
    Controller for investment company operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for investment company operations. It now uses services directly for
    all business logic, maintaining clean separation of concerns.
    
    Attributes:
        company_service (CompanyService): Service for company operations
        portfolio_service (CompanyPortfolioService): Service for portfolio operations
        summary_service (CompanySummaryService): Service for summary calculations
        validation_service (CompanyValidationService): Service for validation
    """
    
    def __init__(self):
        """Initialize the company controller with required services."""
        self.company_service = CompanyService()
        self.portfolio_service = CompanyPortfolioService()
        self.summary_service = CompanySummaryService()
        self.validation_service = CompanyValidationService()
    
    def _extract_company_data(self, company: InvestmentCompany) -> Dict[str, Any]:
        """
        Extract company data into a dictionary while session is still active.
        
        This method prevents lazy loading issues by extracting all needed data
        before the session closes.
        
        Args:
            company: InvestmentCompany instance
            
        Returns:
            Dictionary containing company data
        """
        return {
            "id": company.id,
            "name": company.name,
            "company_type": company.company_type,
            "business_address": company.business_address,
            "website": company.website,
            "description": company.description,
            "created_at": company.created_at.isoformat() if company.created_at else None,
            "updated_at": company.updated_at.isoformat() if company.updated_at else None,
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
    
    def get_investment_companies(self, session: Session) -> tuple:
        """
        Get list of all investment companies with summary data.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get all companies using repository through service
            companies = self.company_service.get_all_companies(session)
            
            companies_data = []
            for company in companies:
                # Get fund count and summary data using services directly
                total_funds = self.portfolio_service.get_total_funds_under_management(company, session)
                total_commitments = self.portfolio_service.get_total_commitments(company, session)
                
                # Extract fund data while session is still active
                # This prevents lazy loading issues after session closes
                active_funds = 0
                total_equity = 0.0
                if company.funds:
                    for fund in company.funds:
                        if fund.status == FundStatus.ACTIVE:
                            active_funds += 1
                        total_equity += fund.current_equity_balance or 0.0
                
                # Handle company_type safely - it might be a string from old data or an enum
                company_type_value = None
                if company.company_type:
                    if hasattr(company.company_type, 'value'):
                        company_type_value = company.company_type.value
                    else:
                        company_type_value = str(company.company_type)
                
                # Handle status safely
                status_value = None
                if company.status:
                    if hasattr(company.status, 'value'):
                        status_value = company.status.value
                    else:
                        status_value = str(company.status)
                
                company_data = {
                    "id": company.id,
                    "name": company.name,
                    "description": company.description,
                    "website": company.website,
                    "company_type": company_type_value,
                    "status": status_value,
                    "business_address": company.business_address,
                    "fund_count": total_funds,
                    "active_funds": active_funds,
                    "total_commitments": float(total_commitments) if total_commitments else 0.0,
                    "total_equity_balance": float(total_equity),
                    "created_at": company.created_at.isoformat() if company.created_at else None,
                    "updated_at": company.updated_at.isoformat() if company.updated_at else None
                }
                
                companies_data.append(company_data)
            
            return jsonify({"companies": companies_data}), 200
            
        except Exception as e:
            # Use proper Flask logging when available, fallback to print for debugging
            try:
                if current_app and current_app.logger:
                    current_app.logger.error(f"Error getting investment companies: {str(e)}")
                else:
                    print(f"Error getting investment companies: {str(e)}")
            except:
                print(f"Error getting investment companies: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def create_investment_company(self, session: Session) -> tuple:
        """
        Create a new investment company using services.
        
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
            
            # Use service to create company (handles validation and creation)
            company = self.company_service.create_company(
                name=data['name'].strip(),
                description=data.get('description'),
                website=data.get('website'),
                company_type=data.get('company_type'),
                business_address=data.get('business_address'),
                status=data.get('status'),
                session=session
            )
            
            # Commit the transaction
            session.commit()
            
            return jsonify({
                "id": company.id,
                "name": company.name,
                "description": company.description,
                "website": company.website,
                "company_type": company.company_type.value if company.company_type else None,
                "status": company.status.value if company.status else None,
                "business_address": company.business_address,
                "created_at": company.created_at.isoformat() if company.created_at else None
            }), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error creating investment company: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def create_investment_company_with_data(self, session: Session, validated_data: Dict[str, Any]) -> tuple:
        """
        Create a new investment company with pre-validated data.
        
        Args:
            session: Database session
            validated_data: Pre-validated company data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            print(f"🚀 CompanyController.create_investment_company_with_data: Starting company creation with validated data: {validated_data}")
            
            # Use service to create company with validated data
            print("📋 CompanyController.create_investment_company_with_data: Calling CompanyService.create_company")
            company = self.company_service.create_company(
                name=validated_data['name'],
                description=validated_data.get('description'),
                website=validated_data.get('website'),
                company_type=validated_data.get('company_type'),
                business_address=validated_data.get('business_address'),
                status=validated_data.get('status'),
                session=session
            )
            
            print(f"✅ CompanyController.create_investment_company_with_data: Company created successfully with ID: {company.id}, Name: {company.name}")
            
            # Commit the transaction
            print("💾 CompanyController.create_investment_company_with_data: Committing transaction to database")
            session.commit()
            print("✅ CompanyController.create_investment_company_with_data: Transaction committed successfully")
            
            # Prepare response data
            response_data = {
                "id": company.id,
                "name": company.name,
                "description": company.description,
                "website": company.website,
                "company_type": company.company_type.value if company.company_type else None,
                "status": company.status.value if company.status else None,
                "business_address": company.business_address,
                "created_at": company.created_at.isoformat() if company.created_at else None
            }
            
            print(f"📤 CompanyController.create_investment_company_with_data: Returning response: {response_data}")
            return jsonify(response_data), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error creating investment company: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_company_funds(self, company_id: int, session: Session) -> tuple:
        """
        Get funds for a specific investment company.
        
        Args:
            company_id: Company ID
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get company using service
            company = self.company_service.get_company_by_id(company_id, session)
            if not company:
                return jsonify({"error": "Investment company not found"}), 404
            
            # Get funds with summary using service
            funds = self.portfolio_service.get_funds_with_summary(company, session)
            
            # Extract all needed data while session is still active
            # This prevents lazy loading issues after session closes
            company_data = self._extract_company_data(company)
            company_data.update({
                "funds": funds
            })
            
            return jsonify(company_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting company funds: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_company_overview(self, company_id: int, session: Session) -> tuple:
        """
        Get company overview with portfolio summary for the Overview tab.
        
        Args:
            company_id: Company ID
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get company using service
            company = self.company_service.get_company_by_id(company_id, session)
            if not company:
                return jsonify({"error": "Investment company not found"}), 404
            
            # Get overview data using service
            overview_data = self.summary_service.get_company_summary_data(company, session)
            
            return jsonify(overview_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting company overview: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_company_details(self, company_id: int, session: Session) -> tuple:
        """
        Get company details information for the Company Details tab.
        
        Args:
            company_id: Company ID
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get company using service
            company = self.company_service.get_company_by_id(company_id, session)
            if not company:
                return jsonify({"error": "Investment company not found"}), 404
            
            # Extract all needed data while session is still active
            # This prevents lazy loading issues after session closes
            company_data = self._extract_company_data(company)
            
            return jsonify(company_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting company details: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_company_funds_enhanced(self, company_id: int, session: Session) -> tuple:
        """
        Get enhanced fund comparison data for the Funds tab with sorting, filtering, and pagination.
        
        Args:
            company_id: Company ID
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get company using service
            company = self.company_service.get_company_by_id(company_id, session)
            if not company:
                return jsonify({"error": "Investment company not found"}), 404
            
            # Get enhanced funds data using service
            all_funds = self.portfolio_service.get_funds_with_summary(company, session)
            
            # Apply sorting and filtering (basic implementation)
            # In a real implementation, these would be passed as query parameters
            sorted_funds = sorted(all_funds, key=lambda x: x.get('name', ''))
            
            return jsonify({
                "id": company.id,
                "name": company.name,
                "funds": sorted_funds,
                "total_funds": len(sorted_funds),
                "active_funds": len([f for f in sorted_funds if f.get('status') == 'ACTIVE']),
                "completed_funds": len([f for f in sorted_funds if f.get('status') == 'COMPLETED'])
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting enhanced company funds: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
