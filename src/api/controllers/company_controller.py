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

from flask import request, current_app
from sqlalchemy.orm import Session

from src.investment_company.services import CompanyService
from src.investment_company.services.company_contact_service import CompanyContactService
from src.api.dto.response_codes import ApiResponseCode
from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.controllers.formatters.company_formatter import format_contact, format_company_comprehensive


class CompanyController:
    """
    Controller for company operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for company operations. It now uses services directly for
    all business logic, maintaining clean separation of concerns.
    
    Attributes:
        company_service (CompanyService): Service for company operations
        company_contact_service (CompanyContactService): Service for company contact operations
    """
    
    def __init__(self):
        """Initialize the company controller with required services."""
        self.company_service = CompanyService()
        self.company_contact_service = CompanyContactService()


    ################################################################################
    # COMPANY ENDPOINTS
    ################################################################################

    ###############################################
    # Get companies
    ###############################################

    def get_companies(self, include_contacts: bool = False) -> tuple:
        """
        Get list of all companies with summary data.
        
        Args:
            include_contacts: Whether to include contacts in the response
            
        Returns:
            ControllerResponseDTO
        """
        try:
            session = self._get_session()
            try:
                companies = self.company_service.get_companies(session)
                if not companies:
                    return ControllerResponseDTO(error="Investment companies not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                if include_contacts:
                    for company in companies:
                        company.contacts = self.company_contact_service.get_contacts(session, company.id)
                formatted_companies = [format_company_comprehensive(company, include_contacts) for company in companies]
                return ControllerResponseDTO(data=formatted_companies, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting companies: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting companies: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting companies: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def get_company_by_id(self, company_id: int, include_contacts: bool = False) -> ControllerResponseDTO:
        """
        Get a specific company by ID.
        
        Args:
            company_id: ID of the company to retrieve
            include_contacts: Whether to include contacts in the response
            
        Returns:
            ControllerResponseDTO
        """
        try:
            session = self._get_session()
            try:
                company = self.company_service.get_company_by_id(company_id, session)
                if not company:
                    return ControllerResponseDTO(error="Company not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                if include_contacts:
                    company.contacts = self.company_contact_service.get_contacts(session, company.id)
                
                formatted_company = format_company_comprehensive(company, include_contacts)
                return ControllerResponseDTO(data=formatted_company, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting company {company_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting company {company_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting company {company_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Create company
    ###############################################
    
    def create_company(self) -> ControllerResponseDTO:
        """
        Create a new company using services.
            
        Returns:
            ControllerResponseDTO: DTO containing company data and status
        """

        try:
            # Get pre-validated data from middleware
            company_data = getattr(request, 'validated_data', {})
            if not company_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)

            session = self._get_session()

            try:
                company = self.company_service.create_company(company_data, session)
                
                session.commit()

                formatted_company = format_company_comprehensive(company, include_contacts=False)
                return ControllerResponseDTO(data=formatted_company, response_code=ApiResponseCode.CREATED)
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating company: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error creating company: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error creating company: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Delete company
    ###############################################
    
    def delete_company(self, company_id: int) -> ControllerResponseDTO:
        """
        Delete a company.
        
        Args:
            company_id: ID of the company to delete
            
        Returns:
            ControllerResponseDTO: DTO containing status of the operation
        """
        try:
            session = self._get_session()
            try:
                success = self.company_service.delete_company(company_id, session)
                if not success:
                    return ControllerResponseDTO(error="Company not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()
                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
   
            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting company {company_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting company {company_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error deleting company {company_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ################################################################################
    # CONTACTS ENDPOINTS
    ################################################################################

    ###############################################
    # Get contacts
    ###############################################

    def get_contacts(self, company_id: int) -> ControllerResponseDTO:
        """
        Get list of all contacts for a specific company

        Args:
            company_id: ID of the company to get contacts for
            
        Returns:
            ControllerResponseDTO
        """
        try:
            session = self._get_session()
            try:
                contacts = self.company_contact_service.get_contacts(session, company_id)
                if not contacts:
                    return ControllerResponseDTO(error="Contacts not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_contacts = [format_contact(contact) for contact in contacts]
                return ControllerResponseDTO(data=formatted_contacts, response_code=ApiResponseCode.SUCCESS)
            
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting contacts for company {company_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting contacts for company {company_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting contacts for company {company_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def get_contact_by_id(self, contact_id: int) -> ControllerResponseDTO:
        """
        Get a specific contact by its ID

        Args:
            contact_id: ID of the contact to get
            
        Returns:
            ControllerResponseDTO: DTO containing contact data and status
        """
        try:
            session = self._get_session()
            try:
                contact = self.company_contact_service.get_contact_by_id(contact_id, session)
                if not contact:
                    return ControllerResponseDTO(error="Contact not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                    
                formatted_contact = format_contact(contact)
                return ControllerResponseDTO(data=formatted_contact, response_code=ApiResponseCode.SUCCESS)
            
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting contact {contact_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting contact {contact_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting contact {contact_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Create contact
    ###############################################
    
    def create_contact(self) -> ControllerResponseDTO:
        """
        Create a new contact
            
        Returns:
            ControllerResponseDTO: DTO containing contact data and status
        """
        try:
            # Get pre-validated data from middleware
            contact_data = getattr(request, 'validated_data', {})
            if not contact_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)

            session = self._get_session()

            try:
                contact = self.company_contact_service.create_contact(contact_data, session)
                
                session.commit()
                
                formatted_contact = format_contact(contact)
                return ControllerResponseDTO(data=formatted_contact, response_code=ApiResponseCode.CREATED)
            
            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating contact: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error creating contact: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error creating contact: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Delete contact
    ###############################################
    
    def delete_contact(self, contact_id: int) -> ControllerResponseDTO:
        """
        Delete a specific contact by its ID
        
        Args:
            contact_id: ID of the contact to delete
            
        Returns:
            ControllerResponseDTO: DTO containing status of the operation
        """
        try:
            session = self._get_session()

            try:
                success = self.company_contact_service.delete_contact(contact_id, session)
                if not success:
                    return ControllerResponseDTO(error="Contact not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                session.commit()

                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
            
            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting contact {contact_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting contact {contact_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error deleting contact {contact_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################################################
    # SESSION HANDLING
    ###############################################################################
    
    def _get_session(self) -> Session:
        """
        Get the current database session from middleware.
        
        Returns:
            Database session from Flask's g context
        """
        from src.api.middleware.database_session import get_current_session
        return get_current_session()