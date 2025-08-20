"""
Company API Routes.

This module contains all company-related API endpoints including
investment company management and company-specific fund operations.
"""

from flask import Blueprint, jsonify, request
from src.investment_company.models import InvestmentCompany
from src.fund.enums import FundStatus
from sqlalchemy.orm import joinedload
from datetime import date

# Create blueprint for company routes
company_bp = Blueprint('company', __name__)


@company_bp.route('/api/investment-companies', methods=['GET'])
def investment_companies():
    """Get list of all investment companies with summary data"""
    try:
        from src.api import get_db_session
        session = get_db_session()
        try:
            # Eagerly load funds relationship
            companies = session.query(InvestmentCompany).options(
                joinedload(InvestmentCompany.funds)
            ).all()
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
                    "fund_count": total_funds,  # Match frontend expectation
                    "active_funds": active_funds,
                    "total_commitments": float(total_commitments) if total_commitments else 0.0,
                    "total_equity_balance": float(total_equity),
                    "created_at": company.created_at.isoformat() if company.created_at else None,
                    "updated_at": company.updated_at.isoformat() if company.updated_at else None
                })
            # Serialize all data before closing session
            return jsonify({"companies": companies_data}), 200
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/api/investment-companies', methods=['POST'])
def create_investment_company():
    """Create a new investment company using domain methods"""
    try:
        from src.api import get_db_session
        session = get_db_session()
        
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
            
            # Check for duplicate names
            existing_company = session.query(InvestmentCompany).filter(
                InvestmentCompany.name == data['name'].strip()
            ).first()
            if existing_company:
                return jsonify({"error": "Investment company with this name already exists"}), 400
            
            # Create company using domain method
            company = InvestmentCompany.create(
                name=data['name'].strip(),
                description=data.get('description', ''),
                website=data.get('website', ''),
                company_type=data.get('company_type'),
                business_address=data.get('business_address'),
                session=session
            )
            
            session.commit()
            
            # Return company data
            company_data = {
                "id": company.id,
                "name": company.name,
                "description": company.description,
                "website": company.website,
                "company_type": company.company_type,
                "business_address": company.business_address,
                "created_at": company.created_at.isoformat() if company.created_at else None,
                "updated_at": company.updated_at.isoformat() if company.updated_at else None
            }
            
            return jsonify(company_data), 201
            
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/api/companies/<int:company_id>/funds', methods=['GET'])
def company_funds(company_id):
    """Get list of funds for a specific investment company"""
    try:
        from src.api import get_db_session
        session = get_db_session()
        
        try:
            # Use domain methods to get company
            company = InvestmentCompany.get_by_id(company_id, session=session)
            
            if not company:
                return jsonify({"error": "Investment company not found"}), 404
            
            # Get funds with summary data using domain methods
            funds_data = company.get_funds_with_summary(session=session)
            
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
                "funds": funds_data
            }), 200
            
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/api/companies/<int:company_id>/overview', methods=['GET'])
def company_overview(company_id):
    """Get company overview with portfolio summary for the Overview tab"""
    try:
        from src.api import get_db_session
        session = get_db_session()
        
        try:
            # Use domain methods to get company
            company = InvestmentCompany.get_by_id(company_id, session=session)
            
            if not company:
                return jsonify({"error": "Investment company not found"}), 404
            
            # Get comprehensive company summary data using domain methods
            summary_data = company.get_company_summary_data(session=session)
            
            return jsonify(summary_data), 200
            
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/api/companies/<int:company_id>/details', methods=['GET'])
def company_details(company_id):
    """Get company details information for the Company Details tab"""
    try:
        from src.api import get_db_session
        session = get_db_session()
        
        try:
            # Use domain methods to get company
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
            
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/api/companies/<int:company_id>/funds/enhanced', methods=['GET'])
def company_enhanced_funds(company_id):
    """Get enhanced fund comparison data for the Funds tab with sorting, filtering, and pagination"""
    try:
        from src.api import get_db_session
        session = get_db_session()
        
        try:
            # Use domain methods to get company
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
            all_funds = company.funds
            
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
            
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
