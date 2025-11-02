"""
Entity API Controller.
"""

from flask import request, current_app
from sqlalchemy.orm import Session

from src.entity.services.entity_service import EntityService
from src.api.controllers.formatters.entity_formatter import format_entity
from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.dto.response_codes import ApiResponseCode
from src.shared.exceptions import ValidationException


class EntityController:
    """
    Controller for entity operations.
    
    Attributes:
        entity_service (EntityService): Service for entity business logic
    """
    
    def __init__(self):
        """Initialize the entity controller."""
        self.entity_service = EntityService()
    
    ################################################################################
    # ENTITY ENDPOINTS
    ###############################################################################

    ###############################################
    # Get entities
    ###############################################
    
    def get_entities(self) -> ControllerResponseDTO:
        """
        Get all entities with optional search filters.
        
        Search parameters (all optional):
            name: Filter by entity name
            names: Filter by entity names
            entity_type: Filter by entity type
            entity_types: Filter by entity types
            tax_jurisdiction: Filter by tax jurisdiction
            tax_jurisdictions: Filter by tax jurisdictions
            sort_by: Sort by (NAME, TYPE, TAX_JURISDICTION, CREATED_AT, UPDATED_AT)
            sort_order: Sort order (ASC, DESC)
                    
        Returns:
            ControllerResponseDTO containing entities data or error
        """
        try:
            # Get search parameters from middleware (all optional)
            search_data = getattr(request, 'validated_data', {})

            # Normalize single values to arrays for service layer
            if 'name' in search_data:
                search_data['names'] = [search_data['name']]
            if 'entity_type' in search_data:
                search_data['entity_types'] = [search_data['entity_type']]
            if 'tax_jurisdiction' in search_data:
                search_data['tax_jurisdictions'] = [search_data['tax_jurisdiction']]
            
            # Extract search parameters (None if not provided)
            entity_types = search_data.get('entity_types')
            tax_jurisdictions = search_data.get('tax_jurisdictions')
            names = search_data.get('names')
            sort_by = search_data.get('sort_by')
            sort_order = search_data.get('sort_order')
            
            session = self._get_session()
            try:
                # Pass search parameters to service (all are optional)
                entities = self.entity_service.get_entities(
                    session=session, 
                    entity_types=entity_types, 
                    tax_jurisdictions=tax_jurisdictions, 
                    names=names,
                    sort_by=sort_by,
                    sort_order=sort_order
                )
                
                if entities is None:
                    return ControllerResponseDTO(error="Entities not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                formatted_entities = [format_entity(entity) for entity in entities]
                return ControllerResponseDTO(data=formatted_entities, response_code=ApiResponseCode.SUCCESS)
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting entities: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting entities: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting entities: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def get_entity_by_id(self, entity_id: int) -> ControllerResponseDTO:
        """
        Get an entity by ID.
        
        Args:
            entity_id: ID of the entity to retrieve
            
        Returns:
            ControllerResponseDTO
        """
        try:
            session = self._get_session()
            try:
                entity = self.entity_service.get_entity_by_id(entity_id, session)
                if not entity:
                    return ControllerResponseDTO(error=f"Entity with ID {entity_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                formatted_entity = format_entity(entity)
                return ControllerResponseDTO(data=formatted_entity, response_code=ApiResponseCode.SUCCESS)
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting entity {entity_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting entity {entity_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting entity {entity_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    
    ###############################################
    # Create entity
    ###############################################
    
    def create_entity(self) -> ControllerResponseDTO:
        """
        Create a new entity.
            
        Returns:
            ControllerResponseDTO
            
        Note: Input data is pre-validated by middleware validation decorator.
        """
        try:
            # Get pre-validated data from middleware
            entity_data = getattr(request, 'validated_data', {})
            if not entity_data:
                return ControllerResponseDTO(error="No validated data available", response_code=ApiResponseCode.VALIDATION_ERROR)
                
            session = self._get_session()

            try:
                entity = self.entity_service.create_entity(entity_data, session)
                
                session.commit()
                
                formatted_entity = format_entity(entity)
                return ControllerResponseDTO(data=formatted_entity, response_code=ApiResponseCode.CREATED)
                
            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating entity: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating entity: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error creating entity: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error creating entity: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    

    ###############################################
    # Delete entity
    ###############################################
    
    def delete_entity(self, entity_id: int) -> ControllerResponseDTO:
        """
        Delete an entity.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            ControllerResponseDTO
        """
        try:
            session = self._get_session()
            try:
                success = self.entity_service.delete_entity(entity_id, session)
                if not success:
                    return ControllerResponseDTO(error=f"Entity with ID {entity_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()
                
                return ControllerResponseDTO(message="Entity deleted successfully", response_code=ApiResponseCode.DELETED)
                
            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting entity {entity_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting entity {entity_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting entity {entity_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error deleting entity {entity_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################################
    # SESSION HANDLING
    ###############################################################
    
    def _get_session(self) -> Session:
        """
        Get the current database session from middleware.
        
        Returns:
            Database session from Flask's g context
        """
        from src.api.middleware.database_session import get_current_session
        return get_current_session()