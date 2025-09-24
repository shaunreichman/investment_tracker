"""
Rate API Controller.

This controller handles HTTP requests for rate operations,
providing RESTful endpoints for rate management.
"""

from flask import request, current_app
from sqlalchemy.orm import Session

from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.dto.response_codes import ApiResponseCode
from src.api.controllers.formatters.rate_formatter import format_risk_free_rate

from src.rates.services.risk_free_rate_service import RiskFreeRateService

class RateController:
    """Rate Controller."""

    def __init__(self):
        """Initialize the rate controller."""
        self.risk_free_rate_service = RiskFreeRateService()


    ################################################################################
    # RATE ENDPOINTS
    ################################################################################

    ###############################################
    # Get Risk Free Rates
    ###############################################

    def get_risk_free_rates(self) -> ControllerResponseDTO:
        """
        Get risk free rates.
        """
        try:
            session = self._get_session()
            try:
                risk_free_rates = self.risk_free_rate_service.get_risk_free_rates(session)
                if risk_free_rates is None:
                    return ControllerResponseDTO(error="Risk free rates not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_risk_free_rates = [format_risk_free_rate(risk_free_rate) for risk_free_rate in risk_free_rates]
                return ControllerResponseDTO(data=formatted_risk_free_rates, response_code=ApiResponseCode.SUCCESS)
            
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting risk free rates: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting risk free rates: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting risk free rates: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def get_risk_free_rate_by_id(self, risk_free_rate_id: int) -> ControllerResponseDTO:
        """
        Get a risk free rate by its ID.
        """
        try:
            session = self._get_session()
            try:
                risk_free_rate = self.risk_free_rate_service.get_risk_free_rate_by_id(risk_free_rate_id, session)
                if risk_free_rate is None:
                    return ControllerResponseDTO(error="Risk free rate not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_risk_free_rate = format_risk_free_rate(risk_free_rate)
                return ControllerResponseDTO(data=formatted_risk_free_rate, response_code=ApiResponseCode.SUCCESS)
            
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting risk free rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting risk free rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting risk free rate: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Create Risk Free Rate
    ###############################################

    def create_risk_free_rate(self) -> ControllerResponseDTO:
        """
        Create a risk free rate.
        """
        try:
            risk_free_rate_data = getattr(request, 'validated_data', {})
            if not risk_free_rate_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)

            session = self._get_session()
            try:
                risk_free_rate = self.risk_free_rate_service.create_risk_free_rate(risk_free_rate_data, session)

                session.commit()

                formatted_risk_free_rate = format_risk_free_rate(risk_free_rate)
                return ControllerResponseDTO(data=formatted_risk_free_rate, response_code=ApiResponseCode.CREATED)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating risk free rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error creating risk free rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close() 

        except Exception as e:
            current_app.logger.error(f"Error creating risk free rate: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Delete Risk Free Rate
    ###############################################

    def delete_risk_free_rate(self, risk_free_rate_id: int) -> ControllerResponseDTO:
        """
        Delete a risk free rate.

        Args:
            risk_free_rate_id: ID of the risk free rate

        Returns:
            ControllerResponseDTO: DTO containing risk free rate data or error
        """
        try:
            session = self._get_session()
            try:
                success = self.risk_free_rate_service.delete_risk_free_rate(risk_free_rate_id, session)
                if not success:
                    return ControllerResponseDTO(error="Risk free rate not deleted", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                session.commit()

                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting risk free rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting risk free rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error deleting risk free rate: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ################################################################################
    # SESSION HANDLING
    ################################################################################

    def _get_session(self) -> Session:
        """
        Get a session from the database using the database session middleware.

        Returns:
            Session: A session from the database
        """
        from src.api.middleware.database_session import get_current_session
        return get_current_session()