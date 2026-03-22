"""
Company API Controller.
"""

from flask import request, current_app
from sqlalchemy.orm import Session

from src.company.services import CompanyService
from src.company.services.company_contact_service import CompanyContactService
from src.api.dto.response_codes import ApiResponseCode
from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.controllers.formatters.company_formatter import format_contact, format_company, format_company_comprehensive
from src.shared.exceptions import ValidationException

class CompanyController:
    """
    Controller for company operations.

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

    def get_companies(self) -> ControllerResponseDTO:
        """
        Get list of all companies with summary data.
        
        Search parameters (all optional):
            company_type: Company type to filter by
            status: Company status to filter by
            name: Company name to filter by
            sort_by: Sort by (NAME, STATUS, START_DATE, CREATED_AT, UPDATED_AT)
            sort_order: Sort order (ASC, DESC)
            include_contacts: Whether to include contacts in the response

        Returns:
            ControllerResponseDTO: DTO containing companies data and status
        """
        try:
            search_data = getattr(request, 'validated_data', {})

            # Normalize single values to arrays for service layer
            if 'company_type' in search_data:
                search_data['company_types'] = [search_data['company_type']]
            if 'status' in search_data:
                search_data['statuses'] = [search_data['status']]
            if 'name' in search_data:
                search_data['names'] = [search_data['name']]

            company_types = search_data.get('company_types')
            statuses = search_data.get('statuses')
            names = search_data.get('names')
            sort_by = search_data.get('sort_by')  # Will be None if not provided, service layer has default
            sort_order = search_data.get('sort_order')  # Will be None if not provided, service layer has default

            include_contacts = search_data.get('include_contacts', False)

            session = self._get_session()
            try:
                companies = self.company_service.get_companies(
                    session=session,
                    company_types=company_types,
                    statuses=statuses,
                    names=names,
                    sort_by=sort_by,
                    sort_order=sort_order,
                    include_contacts=include_contacts
                )
                if companies is None:
                    return ControllerResponseDTO(error="Companies not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                formatted_companies = [format_company_comprehensive(company, include_contacts=include_contacts) for company in companies]
                response_data = {
                    'companies': formatted_companies,
                    'count': len(formatted_companies)
                }
                return ControllerResponseDTO(data=response_data, response_code=ApiResponseCode.SUCCESS)

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

    def get_company_by_id(self, company_id: int) -> ControllerResponseDTO:
        """
        Get a specific company by ID.
        
        Args:
            company_id: ID of the company to retrieve

        Search parameters (all optional):
            include_contacts: Whether to include contacts in the response
            
        Returns:
            ControllerResponseDTO containing company data or error
        """
        try:
            search_data = getattr(request, 'validated_data', {})
            
            include_contacts = search_data.get('include_contacts', False)

            session = self._get_session()
            try:
                company = self.company_service.get_company_by_id(company_id, session, include_contacts=include_contacts)
                if not company:
                    return ControllerResponseDTO(error=f"Company with ID {company_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                formatted_company = format_company_comprehensive(company, include_contacts=include_contacts)
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
            company_data = getattr(request, 'validated_data', {})
            if not company_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)

            session = self._get_session()

            try:
                company = self.company_service.create_company(company_data, session)
                
                session.commit()

                formatted_company = format_company(company)
                return ControllerResponseDTO(data=formatted_company, response_code=ApiResponseCode.CREATED)
                
            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating company: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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
                    return ControllerResponseDTO(error=f"Company with ID {company_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()
                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
   
            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting company {company_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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

    def get_contacts(self, company_id: int = None) -> ControllerResponseDTO:
        """
        Get list of contacts with optional company filter

        Args:
            company_id: ID of the company to get contacts for (optional)
            
        Returns:
            ControllerResponseDTO
        """
        try:
            search_data = getattr(request, 'validated_data', {})

            # Normalize single values to arrays for service layer
            if 'company_id' in search_data:
                search_data['company_ids'] = [search_data['company_id']]

            company_ids = search_data.get('company_ids')
            
            session = self._get_session()
            try:
                contacts = self.company_contact_service.get_contacts(session=session, company_ids=company_ids)
                if not contacts:
                    return ControllerResponseDTO(error="Contacts not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_contacts = [format_contact(contact) for contact in contacts]
                response_data = {
                    'contacts': formatted_contacts,
                    'count': len(formatted_contacts)
                }
                return ControllerResponseDTO(data=response_data, response_code=ApiResponseCode.SUCCESS)
            
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
                    return ControllerResponseDTO(error=f"Contact with ID {contact_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                    
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
    
    def create_contact(self, company_id: int) -> ControllerResponseDTO:
        """
        Create a new contact for the specified company
            
        Args:
            company_id: ID of the company to add contact to
            
        Returns:
            ControllerResponseDTO: DTO containing contact data and status
        """
        try:
            contact_data = getattr(request, 'validated_data', {})
            if not contact_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)

            session = self._get_session()

            try:
                contact = self.company_contact_service.create_contact(company_id, contact_data, session)
                
                session.commit()
                
                formatted_contact = format_contact(contact)
                return ControllerResponseDTO(data=formatted_contact, response_code=ApiResponseCode.CREATED)
            
            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating contact: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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
                    return ControllerResponseDTO(error=f"Contact with ID {contact_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                session.commit()

                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
            
            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting contact {contact_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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