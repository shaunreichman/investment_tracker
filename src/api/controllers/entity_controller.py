"""
Entity API Controller.

This controller handles HTTP requests for entity operations,
providing RESTful endpoints for entity management.

Key responsibilities:
- Entity CRUD endpoints
- Business logic delegation to service layer
- Response formatting and error handling

Note: All input validation is handled by middleware validation decorators.
"""

from flask import request, current_app
from sqlalchemy.orm import Session

from src.entity.services.entity_service import EntityService
from src.api.controllers.formatters.entity_formatter import format_entity
from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.dto.response_codes import ApiResponseCode


class EntityController:
    """
    Controller for entity operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for entity operations. It delegates business logic to the service
    layer and handles request/response formatting.
    
    All input validation is handled by middleware validation decorators.
    
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
        - name: Filter by entity name
        - entity_type: Filter by entity type
        - tax_jurisdiction: Filter by tax jurisdiction
                    
        Returns:
            ControllerResponseDTO
        """
        try:
            # Get search parameters from middleware (all optional)
            search_data = getattr(request, 'validated_data', {})
            
            # Extract search parameters (None if not provided)
            entity_type = search_data.get('entity_type')
            tax_jurisdiction = search_data.get('tax_jurisdiction')
            name = search_data.get('name')
            
            session = self._get_session()
            try:
                # Pass search parameters to service (all are optional)
                entities = self.entity_service.get_entities(
                    session=session, 
                    entity_type=entity_type, 
                    tax_jurisdiction=tax_jurisdiction, 
                    name=name
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

    def get_entity(self, entity_id: int) -> ControllerResponseDTO:
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
                    return ControllerResponseDTO(error="Entity not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
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
                    return ControllerResponseDTO(error="Entity not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()
                
                return ControllerResponseDTO(message="Entity deleted successfully", response_code=ApiResponseCode.DELETED)
                
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