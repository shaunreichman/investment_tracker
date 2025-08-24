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
            
            # Get the fund
            fund = self.fund_service.get_fund(fund_id, session)
            
            if not fund:
                return jsonify({'error': 'Fund not found'}), 404
            
            return jsonify(fund), 200
            
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
            
            # Create the fund with validated data
            fund = self.fund_service.create_fund(fund_data, session)
            
            # Commit the transaction
            session.commit()
            
            return jsonify(fund), 201
            
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
        Delete a fund.
        
        Args:
            fund_id: ID of the fund to delete
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get database session
            session = self._get_session()
            
            # Delete the fund
            success = self.fund_service.delete_fund(fund_id, session)
            
            if not success:
                return jsonify({'error': 'Fund not found'}), 404
            
            # Commit the transaction
            session.commit()
            
            return jsonify({'message': 'Fund deleted successfully'}), 200
            
        except Exception as e:
            current_app.logger.error(f"Error deleting fund {fund_id}: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
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
    
    def add_fund_event(self, fund_id: int) -> tuple:
        """
        Add a fund event.
        
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
            
            # Get database session
            session = self._get_session()
            
            # Add the event
            event = self.fund_service.add_fund_event(fund_id, event_data, session)
            
            # Commit the transaction
            session.commit()
            
            return jsonify(event), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except RuntimeError as e:
            # Check if this is a "not found" error
            if "not found" in str(e).lower():
                return jsonify({'error': str(e)}), 404
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error adding fund event: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def add_fund_event_with_data(self, fund_id: int, event_data: dict) -> tuple:
        """
        Add a fund event with pre-validated data.
        
        Args:
            fund_id: ID of the fund
            event_data: Pre-validated event data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get database session
            session = self._get_session()
            
            # Add the event using pre-validated data
            event = self.fund_service.add_fund_event(fund_id, event_data, session)
            
            # Commit the transaction
            session.commit()
            
            return jsonify(event), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except RuntimeError as e:
            # Check if this is a "not found" error
            if "not found" in str(e).lower():
                return jsonify({'error': str(e)}), 404
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error adding fund event: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def get_fund_events(self, fund_id: int) -> tuple:
        """
        Get events for a specific fund.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get query parameters
            skip = request.args.get('skip', 0, type=int)
            limit = request.args.get('limit', 100, type=int)
            event_types = request.args.getlist('event_types')
            
            # Parse event types if provided
            parsed_event_types = None
            if event_types:
                try:
                    parsed_event_types = [EventType(et) for et in event_types]
                except ValueError:
                    return jsonify({'error': 'Invalid event types provided'}), 400
            
            # Get database session
            session = self._get_session()
            
            # Get events
            events = self.fund_service.get_fund_events(
                fund_id, session, skip, limit, parsed_event_types
            )
            
            return jsonify(events), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting fund events: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def update_fund_event(self, fund_id: int, event_id: int) -> tuple:
        """
        Update a fund event.
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event to update
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get request data
            event_data = request.get_json()
            if not event_data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Get database session
            session = self._get_session()
            
            # Update the event
            event = self.fund_service.update_fund_event(fund_id, event_id, event_data, session)
            
            if not event:
                return jsonify({'error': 'Event not found'}), 404
            
            # Commit the transaction
            session.commit()
            
            return jsonify(event), 200
            
        except Exception as e:
            current_app.logger.error(f"Error updating fund event: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
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
