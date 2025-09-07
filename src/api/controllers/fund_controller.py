"""
Fund API Controller.

This controller handles HTTP requests for fund operations,
providing RESTful endpoints for fund management.

Key responsibilities:
- Fund CRUD endpoints
- Fund event endpoints
- Fund calculation endpoints
- Input validation and error handling
"""

from typing import List, Optional, Dict, Any
from flask import request, jsonify, current_app
from sqlalchemy.orm import Session

from src.fund.enums import FundStatus, FundType, EventType
from src.fund.services.fund_service import FundService
from src.fund.formatters import format_fund_with_events, format_fund, format_funds_list, format_events_list, format_event_response, format_event


class FundController:
    """
    Controller for fund operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for fund operations. It delegates business logic to the FundService
    and handles request/response formatting.
    
    Attributes:
        fund_service (FundService): Service layer for fund operations
    """
    
    def __init__(self):
        """Initialize the fund controller."""
        self.fund_service = FundService()
    
    def get_fund(self, fund_id: int) -> tuple:
        """
        Get a fund by ID.
        
        Args:
            fund_id: ID of the fund to retrieve
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get database session (this would be injected in a real Flask app)
            session = self._get_session()
            
            # Get the fund (now returns domain object)
            fund = self.fund_service.get_fund(fund_id, session)
            
            if not fund:
                return jsonify({'error': 'Fund not found'}), 404
            
            # Format the response using formatter
            formatted_fund = format_fund_with_events(fund)
            return jsonify(formatted_fund), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting fund {fund_id}: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def create_fund(self) -> tuple:
        """
        Create a new fund.
        
        Returns:
            Tuple of (response_data, status_code)
            
        Note: Input data is pre-validated by middleware validation decorator.
        """
        try:
            # Get pre-validated data from middleware
            fund_data = getattr(request, 'validated_data', {})
            if not fund_data:
                return jsonify({'error': 'No validated data available'}), 400
            
            # Get database session
            session = self._get_session()
            
            # Create the fund with validated data (now returns domain object)
            fund = self.fund_service.create_fund(fund_data, session)
            
            # Commit the transaction
            session.commit()
            
            # Format the response using formatter
            formatted_fund = format_fund(fund)
            return jsonify(formatted_fund), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error creating fund: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def update_fund(self, fund_id: int) -> tuple:
        """
        Update an existing fund.
        
        Args:
            fund_id: ID of the fund to update
            
        Returns:
            Tuple of (response_data, status_code)
            
        Note: Input data is pre-validated by middleware validation decorator.
        """
        try:
            # Get pre-validated data from middleware
            fund_data = getattr(request, 'validated_data', {})
            if not fund_data:
                return jsonify({'error': 'No validated data available'}), 400
            
            # Get database session
            session = self._get_session()
            
            # Update the fund with validated data
            fund = self.fund_service.update_fund(fund_id, fund_data, session)
            
            if not fund:
                return jsonify({'error': 'Fund not found'}), 404
            
            # Commit the transaction
            session.commit()
            
            return jsonify(fund), 200
            
        except Exception as e:
            current_app.logger.error(f"Error updating fund {fund_id}: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def delete_fund(self, fund_id: int) -> tuple:
        """
        Delete a fund with enterprise validation.
        
        Args:
            fund_id: ID of the fund to delete
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get database session
            session = self._get_session()
            
            try:
                # Delete the fund (now includes validation)
                success = self.fund_service.delete_fund(fund_id, session)
                
                if not success:
                    return jsonify({'error': 'Fund not found'}), 404
                
                # Commit the transaction
                session.commit()
                
                return jsonify({'message': 'Fund deleted successfully'}), 200
                
            except ValueError as e:
                # ENTERPRISE ERROR HANDLING: Validation errors
                session.rollback()
                return jsonify({
                    'error': 'Fund deletion validation failed',
                    'details': str(e)
                }), 400
                
            except Exception as e:
                # ENTERPRISE ERROR HANDLING: Unexpected errors
                session.rollback()
                return jsonify({'error': 'Internal server error'}), 500
                
            finally:
                session.close()
            
        except Exception as e:
            current_app.logger.error(f"Error deleting fund {fund_id}: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def get_funds(self) -> tuple:
        """
        Get funds with filtering, pagination, and search.
        
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get query parameters
            skip = request.args.get('skip', 0, type=int)
            limit = request.args.get('limit', 100, type=int)
            status = request.args.get('status')
            fund_type = request.args.get('fund_type')
            search = request.args.get('search')
            
            # Parse enums if provided
            parsed_status = None
            if status:
                try:
                    parsed_status = FundStatus(status)
                except ValueError:
                    return jsonify({'error': f'Invalid status: {status}'}), 400
            
            parsed_fund_type = None
            if fund_type:
                try:
                    parsed_fund_type = FundType(fund_type)
                except ValueError:
                    return jsonify({'error': f'Invalid fund_type: {fund_type}'}), 400
            
            # Get database session
            session = self._get_session()
            
            # Get funds
            funds = self.fund_service.get_funds(
                session, skip, limit, parsed_status, parsed_fund_type, search
            )
            
            return jsonify(funds), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting funds: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def add_capital_call(self, fund_id: int) -> tuple:
        """
        Add a capital call event.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get pre-validated data from middleware
            event_data = request.validated_data
            
            # Get database session
            session = self._get_session()
            
            # Get the fund
            fund = self.fund_service.get_fund(fund_id, session)
            if not fund:
                return jsonify({'error': 'Fund not found'}), 404
            
            # Add the capital call event using FundEventService
            # (Business validation happens in the service layer)
            event = self.fund_service.fund_event_service.add_capital_call(
                fund=fund,
                amount=float(event_data['amount']),
                call_date=event_data['event_date'],  # Already parsed by middleware
                description=event_data.get('description'),
                reference_number=event_data.get('reference_number'),
                session=session
            )
            
            # Commit the transaction
            session.commit()
            
            # Format the event for JSON response
            from src.fund.formatters import format_event
            formatted_event = format_event(event)
            return jsonify(formatted_event), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error adding capital call: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def add_return_of_capital(self, fund_id: int) -> tuple:
        """
        Add a return of capital event.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get request data
            event_data = request.get_json()
            if not event_data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['amount', 'event_date']
            for field in required_fields:
                if field not in event_data:
                    return jsonify({'error': f'Required field "{field}" is missing'}), 400
            
            # Get database session
            session = self._get_session()
            
            # Get the fund
            fund = self.fund_service.get_fund(fund_id, session)
            if not fund:
                return jsonify({'error': 'Fund not found'}), 404
            
            # Parse event date
            event_date = event_data['event_date']
            if isinstance(event_date, str):
                from datetime import datetime
                event_date = datetime.fromisoformat(event_date).date()
            
            # Add the return of capital event using FundEventService
            event = self.fund_service.fund_event_service.add_return_of_capital(
                fund=fund,
                amount=float(event_data['amount']),
                return_date=event_date,
                description=event_data.get('description'),
                reference_number=event_data.get('reference_number'),
                session=session
            )
            
            # Commit the transaction
            session.commit()
            
            # Format the event for JSON response
            from src.fund.formatters import format_event
            formatted_event = format_event(event)
            return jsonify(formatted_event), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error adding return of capital: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def add_unit_purchase(self, fund_id: int) -> tuple:
        """
        Add a unit purchase event.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get request data
            event_data = request.get_json()
            if not event_data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['units_purchased', 'unit_price', 'event_date']
            for field in required_fields:
                if field not in event_data:
                    return jsonify({'error': f'Required field "{field}" is missing'}), 400
            
            # Get database session
            session = self._get_session()
            
            # Get the fund
            fund = self.fund_service.get_fund(fund_id, session)
            if not fund:
                return jsonify({'error': 'Fund not found'}), 404
            
            # Parse event date
            event_date = event_data['event_date']
            if isinstance(event_date, str):
                from datetime import datetime
                event_date = datetime.fromisoformat(event_date).date()
            
            # Add the unit purchase event using FundEventService
            event = self.fund_service.fund_event_service.add_unit_purchase(
                fund=fund,
                units=float(event_data['units_purchased']),
                price=float(event_data['unit_price']),
                date=event_date,
                brokerage_fee=float(event_data.get('brokerage_fee', 0.0)),
                description=event_data.get('description'),
                reference_number=event_data.get('reference_number'),
                session=session
            )
            
            # Commit the transaction
            session.commit()
            
            # Format the event for JSON response
            from src.fund.formatters import format_event
            formatted_event = format_event(event)
            return jsonify(formatted_event), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error adding unit purchase: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def add_unit_sale(self, fund_id: int) -> tuple:
        """
        Add a unit sale event.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get request data
            event_data = request.get_json()
            if not event_data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['units_sold', 'unit_price', 'event_date']
            for field in required_fields:
                if field not in event_data:
                    return jsonify({'error': f'Required field "{field}" is missing'}), 400
            
            # Get database session
            session = self._get_session()
            
            # Get the fund
            fund = self.fund_service.get_fund(fund_id, session)
            if not fund:
                return jsonify({'error': 'Fund not found'}), 404
            
            # Parse event date
            event_date = event_data['event_date']
            if isinstance(event_date, str):
                from datetime import datetime
                event_date = datetime.fromisoformat(event_date).date()
            
            # Add the unit sale event using FundEventService
            event = self.fund_service.fund_event_service.add_unit_sale(
                fund=fund,
                units=float(event_data['units_sold']),
                price=float(event_data['unit_price']),
                date=event_date,
                brokerage_fee=float(event_data.get('brokerage_fee', 0.0)),
                description=event_data.get('description'),
                reference_number=event_data.get('reference_number'),
                session=session
            )
            
            # Commit the transaction
            session.commit()
            
            # Format the event for JSON response
            from src.fund.formatters import format_event
            formatted_event = format_event(event)
            return jsonify(formatted_event), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error adding unit sale: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def add_nav_update(self, fund_id: int) -> tuple:
        """
        Add a NAV update event.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get request data
            event_data = request.get_json()
            if not event_data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['nav_per_share', 'event_date']
            for field in required_fields:
                if field not in event_data:
                    return jsonify({'error': f'Required field "{field}" is missing'}), 400
            
            # Get database session
            session = self._get_session()
            
            # Get the fund
            fund = self.fund_service.get_fund(fund_id, session)
            if not fund:
                return jsonify({'error': 'Fund not found'}), 404
            
            # Parse event date
            event_date = event_data['event_date']
            if isinstance(event_date, str):
                from datetime import datetime
                event_date = datetime.fromisoformat(event_date).date()
            
            # Add the NAV update event using FundEventService
            event = self.fund_service.fund_event_service.add_nav_update(
                fund=fund,
                nav_per_share=float(event_data['nav_per_share']),
                date=event_date,
                description=event_data.get('description'),
                reference_number=event_data.get('reference_number'),
                session=session
            )
            
            # Commit the transaction
            session.commit()
            
            # Format the event for JSON response
            from src.fund.formatters import format_event
            formatted_event = format_event(event)
            return jsonify(formatted_event), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error adding NAV update: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def add_distribution(self, fund_id: int) -> tuple:
        """
        Add a distribution event.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get request data
            event_data = request.get_json()
            if not event_data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['event_date', 'distribution_type']
            for field in required_fields:
                if field not in event_data:
                    return jsonify({'error': f'Required field "{field}" is missing'}), 400
            
            # Get database session
            session = self._get_session()
            
            # Get the fund
            fund = self.fund_service.get_fund(fund_id, session)
            if not fund:
                return jsonify({'error': 'Fund not found'}), 404
            
            # Parse event date
            event_date = event_data['event_date']
            if isinstance(event_date, str):
                from datetime import datetime
                event_date = datetime.fromisoformat(event_date).date()
            
            # Parse distribution type
            from src.fund.enums import DistributionType
            distribution_type = DistributionType(event_data['distribution_type'])
            
            # Handle withholding tax distributions
            if (event_data.get('distribution_type') == 'INTEREST' and
                any([
                    event_data.get('interest_gross_amount') is not None,
                    event_data.get('interest_net_amount') is not None,
                    event_data.get('interest_withholding_tax_amount') is not None,
                    event_data.get('interest_withholding_tax_rate') is not None
                ])):
                # Withholding tax distribution
                event = self.fund_service.fund_event_service.add_distribution(
                    fund=fund,
                    event_date=event_date,
                    distribution_type=distribution_type,
                    has_withholding_tax=True,
                    gross_interest_amount=float(event_data.get('interest_gross_amount', 0)) if event_data.get('interest_gross_amount') else None,
                    net_interest_amount=float(event_data.get('interest_net_amount', 0)) if event_data.get('interest_net_amount') else None,
                    withholding_tax_amount=float(event_data.get('interest_withholding_tax_amount', 0)) if event_data.get('interest_withholding_tax_amount') else None,
                    withholding_tax_rate=float(event_data.get('interest_withholding_tax_rate', 0)) if event_data.get('interest_withholding_tax_rate') else None,
                    description=event_data.get('description'),
                    reference_number=event_data.get('reference_number'),
                    session=session
                )
            else:
                # Simple distribution
                if 'amount' not in event_data:
                    return jsonify({'error': 'Required field "amount" is missing for simple distribution'}), 400
                
                event = self.fund_service.fund_event_service.add_distribution(
                    fund=fund,
                    event_date=event_date,
                    distribution_type=distribution_type,
                    distribution_amount=float(event_data['amount']),
                    has_withholding_tax=False,
                    description=event_data.get('description'),
                    reference_number=event_data.get('reference_number'),
                    session=session
                )
            
            # Commit the transaction
            session.commit()
            
            # Format the event for JSON response
            from src.fund.formatters import format_event
            formatted_event = format_event(event)
            return jsonify(formatted_event), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error adding distribution: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def get_fund_events(self, fund_id: int) -> tuple:
        """
        Get all events for a specific fund - optimized for fast table updates.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get database session
            session = self._get_session()
            
            # Get fund events - service returns a list directly
            events = self.fund_service.get_fund_events(fund_id, session)
            
            if events is None:
                return jsonify({'error': 'Fund not found'}), 404
            
            # Format events using the formatter (grouping fields are already in the database)
            formatted_events = [format_event(event) for event in events]
            
            return jsonify(formatted_events), 200
            
        except Exception as e:
            print(f"❌ FundController.get_fund_events error: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def delete_fund_event(self, fund_id: int, event_id: int) -> tuple:
        """
        Delete a fund event.
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event to delete
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get database session
            session = self._get_session()
            
            # Delete the event
            success = self.fund_service.delete_fund_event(fund_id, event_id, session)
            
            if not success:
                return jsonify({'error': 'Event not found'}), 404
            
            # Commit the transaction
            session.commit()
            
            return '', 204  # DELETE operations return 204 No Content
            
        except Exception as e:
            current_app.logger.error(f"Error deleting fund event: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def get_fund_summary(self, fund_id: int) -> tuple:
        """
        Get a comprehensive summary of a fund.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get database session
            session = self._get_session()
            
            # Get fund summary
            summary = self.fund_service.get_fund_summary(fund_id, session)
            
            if not summary:
                return jsonify({'error': 'Fund not found'}), 404
            
            return jsonify(summary), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting fund summary: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def get_fund_metrics(self, fund_id: int) -> tuple:
        """
        Get performance metrics for a fund.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get database session
            session = self._get_session()
            
            # Get fund metrics
            metrics = self.fund_service.get_fund_metrics(fund_id, session)
            
            if not metrics:
                return jsonify({'error': 'Fund not found'}), 404
            
            return jsonify(metrics), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting fund metrics: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def _get_session(self) -> Session:
        """
        Get a database session.
        
        In a real Flask application, this would be injected or retrieved
        from a session factory. For now, we'll use the existing Flask session management.
        
        Returns:
            Database session
        """
        from flask import current_app
        # Access the get_db_session function from the Flask app context
        # The function is defined in the Flask app, so we need to access it differently
        try:
            # Try to get the test session first
            if current_app.config.get('TEST_DB_SESSION'):
                return current_app.config['TEST_DB_SESSION']
        except:
            pass
        
        # For now, let's use a simple approach - create a session directly
        # This is not ideal but will work for testing
        from src.database import create_database_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_database_engine()
        Session = sessionmaker(bind=engine)
        return Session()
    
    def add_cash_flow_to_event(self, fund_id: int, event_id: int, cash_flow_data: dict) -> tuple:
        """
        Add a cash flow to a fund event with pre-validated data.
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event
            cash_flow_data: Pre-validated cash flow data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get database session
            session = self._get_session()
            
            # Validate fund exists
            fund = self.fund_service.get_fund(fund_id, session)
            if not fund:
                return jsonify({'error': 'Fund not found'}), 404
            
            # Validate event exists and belongs to fund
            event = self.fund_service.get_fund_event(fund_id, event_id, session)
            if not event:
                return jsonify({'error': 'Fund event not found'}), 404
            
            # Validate bank account exists
            from src.banking.models import BankAccount
            bank_account = session.query(BankAccount).filter(BankAccount.id == cash_flow_data['bank_account_id']).first()
            if not bank_account:
                return jsonify({'error': 'Bank account not found'}), 404
            
            # Validate currency matches bank account
            if cash_flow_data['currency'].upper() != bank_account.currency.upper():
                return jsonify({'error': 'Cash flow currency must match bank account currency'}), 400
            
            # Add cash flow using domain method
            cash_flow = event.add_cash_flow(
                bank_account_id=cash_flow_data['bank_account_id'],
                transfer_date=cash_flow_data['transfer_date'],
                currency=cash_flow_data['currency'],
                amount=cash_flow_data['amount'],
                reference=cash_flow_data.get('reference'),
                notes=cash_flow_data.get('notes'),
                session=session
            )
            
            session.commit()
            
            response_data = {
                "id": cash_flow.id,
                "fund_event_id": cash_flow.fund_event_id,
                "bank_account_id": cash_flow.bank_account_id,
                "bank_name": bank_account.bank.name,
                "account_name": bank_account.account_name,
                "direction": cash_flow.direction.value,
                "transfer_date": cash_flow.transfer_date.isoformat(),
                "currency": cash_flow.currency,
                "amount": float(cash_flow.amount),
                "reference": cash_flow.reference,
                "notes": cash_flow.notes,
                "message": "Cash flow added successfully"
            }
            
            return jsonify(response_data), 201
            
        except Exception as e:
            current_app.logger.error(f"Error adding cash flow to event: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
