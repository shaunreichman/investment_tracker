"""
Rate API Controller.
"""

from flask import request, current_app
from sqlalchemy.orm import Session

from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.dto.response_codes import ApiResponseCode
from src.api.controllers.formatters.rate_formatter import format_risk_free_rate, format_fx_rate
from src.shared.exceptions import ValidationException
from src.rates.services.risk_free_rate_service import RiskFreeRateService
from src.rates.services.fx_rate_service import FxRateService


class RateController:
    """
    Rate Controller.
    
    Attributes:
        risk_free_rate_service (RiskFreeRateService): Service layer for risk free rate operations
        fx_rate_service (FxRateService): Service layer for FX rate operations
    """

    def __init__(self):
        """Initialize the rate controller."""
        self.risk_free_rate_service = RiskFreeRateService()
        self.fx_rate_service = FxRateService()


    ################################################################################
    # RATE ENDPOINTS
    ################################################################################

    ###############################################
    # Get Risk Free Rates
    ###############################################

    def get_risk_free_rates(self) -> ControllerResponseDTO:
        """
        Get risk free rates.

        Search parameters (all optional):
            currency: Single currency of the risk free rates to retrieve
            currencies: Multiple currencies of the risk free rates to retrieve
            rate_type: Single rate type of the risk free rates to retrieve
            rate_types: Multiple rate types of the risk free rates to retrieve
            start_date: Start date of the risk free rates to retrieve
            end_date: End date of the risk free rates to retrieve
            sort_by: Field to sort by
            sort_order: Order to sort by

        Returns:
            ControllerResponseDTO containing risk free rate data or error
        """
        try:
            search_data = getattr(request, 'validated_data', {})
            
            # Normalize single values to arrays for service layer
            if 'currency' in search_data:
                search_data['currencies'] = [search_data['currency']]
            if 'rate_type' in search_data:
                search_data['rate_types'] = [search_data['rate_type']]
            
            currencies = search_data.get('currencies')
            rate_types = search_data.get('rate_types')

            start_date = search_data.get('start_date')
            end_date = search_data.get('end_date')
            sort_by = search_data.get('sort_by')
            sort_order = search_data.get('sort_order')
            
            session = self._get_session()
            try:
                risk_free_rates = self.risk_free_rate_service.get_risk_free_rates(
                    session=session,
                    currencies=currencies,
                    rate_types=rate_types,
                    start_date=start_date,
                    end_date=end_date,
                    sort_by=sort_by,
                    sort_order=sort_order
                )
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

        Args:
            risk_free_rate_id: ID of the risk free rate to retrieve

        Returns:
            ControllerResponseDTO containing risk free rate data or error
        """
        try:
            session = self._get_session()
            try:
                risk_free_rate = self.risk_free_rate_service.get_risk_free_rate_by_id(risk_free_rate_id, session)
                if risk_free_rate is None:
                    return ControllerResponseDTO(error=f"Risk free rate with ID {risk_free_rate_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

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

        Returns:
            ControllerResponseDTO containing risk free rate data or error
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

            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating risk free rate: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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
            ControllerResponseDTO containing risk free rate data or error
        """
        try:
            session = self._get_session()
            try:
                success = self.risk_free_rate_service.delete_risk_free_rate(risk_free_rate_id, session)
                if not success:
                    return ControllerResponseDTO(error=f"Risk free rate with ID {risk_free_rate_id} not deleted", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                session.commit()

                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)

            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting risk free rate {risk_free_rate_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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



    ###############################################################################
    # FX RATE ENDPOINTS
    ###############################################################################

    ###############################################
    # Get FX Rates
    ###############################################

    def get_fx_rates(self) -> ControllerResponseDTO:
        """
        Get FX rates with optional search filters.

        Search parameters (all optional):
            from_currency: Currency of the FX rates to retrieve
            to_currency: Currency of the FX rates to retrieve
            start_date: Start date of the FX rates to retrieve
            end_date: End date of the FX rates to retrieve

        Returns:
            ControllerResponseDTO containing FX rate data or error
        """
        try:
            # Get search parameters from middleware (all optional)
            search_data = getattr(request, 'validated_data', {})

            # Extract search parameters (None if not provided)
            from_currency = search_data.get('from_currency')
            to_currency = search_data.get('to_currency')
            start_date = search_data.get('start_date')
            end_date = search_data.get('end_date')
            sort_by = search_data.get('sort_by')
            sort_order = search_data.get('sort_order')

            session = self._get_session()
            try:
                # Pass search parameters to service (all are optional)
                fx_rates = self.fx_rate_service.get_fx_rates(
                    session=session,
                    from_currency=from_currency,
                    to_currency=to_currency,
                    start_date=start_date,
                    end_date=end_date,
                    sort_by=sort_by,
                    sort_order=sort_order
                )
                if fx_rates is None:
                    return ControllerResponseDTO(error="FX rates not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_fx_rates = [format_fx_rate(fx_rate) for fx_rate in fx_rates]
                return ControllerResponseDTO(data=formatted_fx_rates, response_code=ApiResponseCode.SUCCESS)
            
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting FX rates: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting FX rates: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()
        except Exception as e:
            current_app.logger.error(f"Error getting FX rates: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def get_fx_rate_by_id(self, fx_rate_id: int) -> ControllerResponseDTO:
        """
        Get an FX rate by its ID.

        Args:
            fx_rate_id: ID of the FX rate to retrieve

        Returns:
            ControllerResponseDTO containing FX rate data or error
        """
        try:
            session = self._get_session()
            try:
                fx_rate = self.fx_rate_service.get_fx_rate_by_id(fx_rate_id, session)
                if fx_rate is None:
                    return ControllerResponseDTO(error=f"FX rate with ID {fx_rate_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_fx_rate = format_fx_rate(fx_rate)
                return ControllerResponseDTO(data=formatted_fx_rate, response_code=ApiResponseCode.SUCCESS)
            
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting FX rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting FX rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()
        except Exception as e:
            current_app.logger.error(f"Error getting FX rate: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Create FX Rate
    ###############################################
    def create_fx_rate(self) -> ControllerResponseDTO:
        """
        Create an FX rate.

        Returns:
            ControllerResponseDTO: DTO containing FX rate data or error
        """
        try:
            fx_rate_data = getattr(request, 'validated_data', {})
            if not fx_rate_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)
            session = self._get_session()
            try:
                fx_rate = self.fx_rate_service.create_fx_rate(fx_rate_data, session)
                session.commit()
                formatted_fx_rate = format_fx_rate(fx_rate)
                return ControllerResponseDTO(data=formatted_fx_rate, response_code=ApiResponseCode.CREATED)

            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating FX rate: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating FX rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error creating FX rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()
                
        except Exception as e:
            current_app.logger.error(f"Error creating FX rate: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Delete FX Rate
    ###############################################
    def delete_fx_rate(self, fx_rate_id: int) -> ControllerResponseDTO:
        """
        Delete an FX rate.

        Args:
            fx_rate_id: ID of the FX rate

        Returns:
            ControllerResponseDTO: DTO containing FX rate data or error
        """
        try:
            session = self._get_session()
            try:
                success = self.fx_rate_service.delete_fx_rate(fx_rate_id, session)
                if not success:
                    return ControllerResponseDTO(error=f"FX rate with ID {fx_rate_id} not deleted", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                session.commit()

                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)

            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting FX rate {fx_rate_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting FX rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting FX rate: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error deleting FX rate: {str(e)}")
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