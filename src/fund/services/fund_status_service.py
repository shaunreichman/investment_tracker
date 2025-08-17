"""
Fund Status Service.

This service handles all fund status transitions and calculations,
extracting complex status logic from the Fund model.

Key responsibilities:
- Status transition validation
- End date calculations
- Status-based IRR calculations
- Tax statement status checks
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from src.fund.enums import FundStatus
from src.fund.enums import EventType


class FundStatusService:
    """
    Service for handling fund status management extracted from the Fund model.
    
    This service provides clean separation of concerns for:
    - Status transition logic and business rules
    - Status updates triggered by equity events
    - Status updates triggered by tax statements
    - Status determination logic
    - End date calculation logic
    """
    
    def __init__(self):
        """Initialize the FundStatusService."""
        pass
    
    # ============================================================================
    # STATUS TRANSITION LOGIC AND BUSINESS RULES
    # ============================================================================
    
    def update_status(self, fund: 'Fund', session: Optional[Session] = None) -> None:
        """
        [EXTRACTED] Update the fund status based on current equity balance and tax statement status.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
        """
        # Determine if fund should be active based on equity balance
        should_be_active = self._should_be_active(fund, session)
        
        if should_be_active and fund.status != FundStatus.ACTIVE:
            fund.status = FundStatus.ACTIVE
            print(f"Fund {fund.name} status updated to ACTIVE")
        elif not should_be_active and fund.status == FundStatus.ACTIVE:
            fund.status = FundStatus.REALIZED
            print(f"Fund {fund.name} status updated to REALIZED")
            
            # Calculate and store IRRs for realized status
            self._calculate_and_store_irrs_for_status(fund, FundStatus.REALIZED, session)
    
    def update_status_after_equity_event(self, fund: 'Fund', session: Optional[Session] = None) -> None:
        """
        [EXTRACTED] Update fund status after an equity event (capital call, return, unit purchase/sale).
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
        """
        # Check if fund should still be active
        should_be_active = self._should_be_active(fund, session)
        
        if not should_be_active and fund.status == FundStatus.ACTIVE:
            fund.status = FundStatus.REALIZED
            print(f"Fund {fund.name} status updated to REALIZED after equity event")
            
            # Calculate and store IRRs for realized status
            self._calculate_and_store_irrs_for_status(fund, FundStatus.REALIZED, session)
    
    def update_status_after_tax_statement(self, fund: 'Fund', session: Optional[Session] = None) -> None:
        """
        [EXTRACTED] Update fund status after a tax statement event.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
        """
        if fund.status != FundStatus.ACTIVE:
            # Check if this tax statement makes the fund completed
            if self._is_final_tax_statement_received(fund, session):
                if fund.status != FundStatus.COMPLETED:
                    fund.status = FundStatus.COMPLETED
                    print(f"Fund {fund.name} status updated to COMPLETED")
                    
                    # Calculate and store IRRs for completed status
                    self._calculate_and_store_irrs_for_status(fund, FundStatus.COMPLETED, session)
            else:
                # Tax statement removed, revert to realized if was completed
                if fund.status == FundStatus.COMPLETED:
                    fund.status = FundStatus.REALIZED
                    print(f"Fund {fund.name} status reverted to REALIZED")
    
    def _should_be_active(self, fund: 'Fund', session: Optional[Session] = None) -> bool:
        """
        [EXTRACTED] Determine if the fund should be active based on equity balance.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            bool: True if fund should be active, False otherwise
        """
        # Get the most recent event to check current equity balance
        events = fund.get_all_fund_events(session=session)
        if not events:
            return True  # No events, assume active
        
        # Find the most recent event with equity balance
        last_event = None
        for event in reversed(events):
            if event.current_equity_balance is not None:
                last_event = event
                break
        
        if last_event is None:
            return True  # No equity balance found, assume active
        
        # Fund is active if equity balance > 0
        return last_event.current_equity_balance > 0
    
    def _is_final_tax_statement_received(self, fund: 'Fund', session: Optional[Session] = None) -> bool:
        """
        [EXTRACTED] Check if the final tax statement has been received for a realized fund.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            bool: True if final tax statement received, False otherwise
        """
        if fund.status == FundStatus.ACTIVE:
            return False
        
        # Get the fund's end date
        end_date = self.calculate_end_date(fund, session)
        if not end_date:
            return False
        
        # Check if there's a tax statement after the end date
        tax_statements = fund.tax_statements
        for tax_statement in tax_statements:
            if tax_statement.financial_year > end_date.year:
                return True
        
        return False
    
    def _calculate_and_store_irrs_for_status(self, fund: 'Fund', status: FundStatus, session: Optional[Session] = None) -> None:
        """
        [EXTRACTED] Calculate and store IRRs for a specific fund status.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            status: The status to calculate IRRs for
            session: Database session (optional)
        """
        if status == FundStatus.ACTIVE:
            # ACTIVE: No IRRs meaningful (fund has capital at risk)
            fund.irr_gross = None
            fund.irr_after_tax = None
            fund.irr_real = None
            fund.completed_irr = None
            fund.completed_after_tax_irr = None
            fund.completed_real_irr = None
            
            print(f"IRRs reset to None for active fund {fund.name}")
            
        elif status == FundStatus.REALIZED:
            # Calculate IRRs for realized status
            try:
                fund.irr_gross = fund.calculate_irr(session=session)
                fund.irr_after_tax = fund.calculate_after_tax_irr(session=session)
                fund.irr_real = fund.calculate_real_irr(session=session)
                
                print(f"IRRs calculated and stored for realized fund {fund.name}")
            except Exception as e:
                print(f"Error calculating IRRs for realized fund {fund.name}: {e}")
                fund.irr_gross = None
                fund.irr_after_tax = None
                fund.irr_real = None
            
        elif status == FundStatus.COMPLETED:
            # Calculate completed IRRs
            try:
                fund.completed_irr = fund.calculate_completed_irr(session=session)
                fund.completed_after_tax_irr = fund.calculate_completed_after_tax_irr(session=session)
                fund.completed_real_irr = fund.calculate_completed_real_irr(session=session)
                
                print(f"Completed IRRs calculated and stored for fund {fund.name}")
            except Exception as e:
                print(f"Error calculating completed IRRs for fund {fund.name}: {e}")
                fund.completed_irr = None
                fund.completed_after_tax_irr = None
                fund.completed_real_irr = None
    
    # ============================================================================
    # END DATE CALCULATION LOGIC
    # ============================================================================
    
    def calculate_end_date(self, fund: 'Fund', session: Optional[Session] = None) -> Optional[date]:
        """
        [EXTRACTED] Calculate the end date of the fund based on business logic.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            date or None: The calculated end date, or None if not computable
        """
        if not fund.start_date:
            return None
        
        # Get all fund events
        events = fund.get_all_fund_events(session=session)
        if not events:
            return None
        
        # Find the last equity or distribution event since equity balance went to zero
        last_equity_event_date = None
        equity_balance_zero_date = None
        
        for event in events:
            # Track when equity balance goes to zero
            if event.current_equity_balance is not None and event.current_equity_balance == 0:
                if equity_balance_zero_date is None:
                    equity_balance_zero_date = event.event_date
            
            # Check if this is an equity or distribution event
            if self._is_equity_or_distribution_event(event):
                if equity_balance_zero_date is None or event.event_date >= equity_balance_zero_date:
                    last_equity_event_date = event.event_date
        
        # Return the last equity event date, or None if no equity events
        return last_equity_event_date
    
    def _is_equity_or_distribution_event(self, event: 'FundEvent') -> bool:
        """
        [EXTRACTED] Determine if an event is an equity or distribution event.

        This method was extracted from the Fund model to improve separation of concerns.

        Args:
            event: The fund event to check

        Returns:
            bool: True if equity or distribution event, False otherwise
        """
        equity_event_types = [
            EventType.CAPITAL_CALL,
            EventType.RETURN_OF_CAPITAL,
            EventType.UNIT_PURCHASE,
            EventType.UNIT_SALE
        ]

        distribution_event_types = [
            EventType.DISTRIBUTION
        ]

        # Handle both enum objects and strings
        event_type_value = event.event_type if hasattr(event.event_type, 'value') else event.event_type
        return (event_type_value in equity_event_types or
               event_type_value in distribution_event_types)
    
    def should_calculate_irr(self, status: FundStatus, fund: 'Fund') -> bool:
        """
        Determine if IRR should be calculated for the current fund status.
        
        Args:
            status: Current fund status
            fund: The fund object
            
        Returns:
            bool: True if IRR should be calculated, False otherwise
        """
        # Calculate IRR when fund transitions to REALIZED or COMPLETED
        if status in [FundStatus.REALIZED, FundStatus.COMPLETED]:
            return True
        
        # Calculate IRR for active funds if they have significant activity
        if status == FundStatus.ACTIVE:
            # Check if fund has substantial equity balance or many events
            if fund.current_equity_balance and fund.current_equity_balance > 10000:
                return True
        
        return False
    
    # ============================================================================
    # STATUS VALIDATION AND BUSINESS RULES
    # ============================================================================
    
    def validate_status_transition(self, fund: 'Fund', new_status: FundStatus, session: Optional[Session] = None) -> bool:
        """
        [EXTRACTED] Validate if a status transition is allowed based on business rules.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            new_status: The proposed new status
            session: Database session (optional)
            
        Returns:
            bool: True if transition is allowed, False otherwise
        """
        current_status = fund.status
        
        # Define allowed transitions
        allowed_transitions = {
            FundStatus.ACTIVE: [FundStatus.REALIZED],
            FundStatus.REALIZED: [FundStatus.COMPLETED, FundStatus.ACTIVE],  # Can revert to active if equity restored
            FundStatus.COMPLETED: [FundStatus.REALIZED]  # Can revert to realized if tax statement removed
        }
        
        if current_status not in allowed_transitions:
            return False
        
        return new_status in allowed_transitions[current_status]
    
    def get_status_summary(self, fund: 'Fund', session: Optional[Session] = None) -> Dict[str, Any]:
        """
        [EXTRACTED] Get a summary of the fund's current status and transition information.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            dict: Status summary information
        """
        return {
            'current_status': fund.status,
            'start_date': fund.start_date,
            'end_date': self.calculate_end_date(fund, session),
            'should_be_active': self._should_be_active(fund, session),
            'is_final_tax_statement_received': self._is_final_tax_statement_received(fund, session),
            'status_transition_allowed': {
                'to_realized': self.validate_status_transition(fund, FundStatus.REALIZED, session),
                'to_completed': self.validate_status_transition(fund, FundStatus.COMPLETED, session),
                'to_active': self.validate_status_transition(fund, FundStatus.ACTIVE, session)
            }
        }
    
    # ============================================================================
    # FUND SUMMARY AND ANALYTICS METHODS (MIGRATED FROM LEGACY)
    # ============================================================================
    
    def get_enhanced_fund_metrics(self, fund: 'Fund', session: Optional[Session] = None) -> Dict[str, Any]:
        """
        [MIGRATED] Get comprehensive fund performance metrics and analytics.
        
        This method was migrated from the legacy Fund model to provide
        comprehensive fund analytics and reporting capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            dict: Comprehensive fund metrics and analytics
        """
        if not session:
            return {}
        
        # Get basic fund information
        metrics = {
            'fund_id': fund.id,
            'fund_name': fund.name,
            'tracking_type': fund.tracking_type.value if hasattr(fund.tracking_type, 'value') else fund.tracking_type,
            'status': fund.status.value if hasattr(fund.status, 'value') else fund.status,
            'commitment_amount': fund.commitment_amount,
            'current_equity_balance': fund.current_equity_balance,
            'average_equity_balance': fund.average_equity_balance,
            'start_date': fund.start_date,
            'end_date': fund.end_date,
            'expected_irr': fund.expected_irr,
            'expected_duration_months': fund.expected_duration_months
        }
        
        # Get financial aggregations
        from src.fund.services.fund_calculation_service import FundCalculationService
        calc_service = FundCalculationService()
        
        metrics.update({
            'total_capital_calls': calc_service.get_total_capital_calls(fund, session),
            'total_capital_returns': calc_service.get_total_capital_returns(fund, session),
            'total_distributions': calc_service.get_total_distributions(fund, session),
            'total_tax_withheld': calc_service.get_total_tax_withheld(fund, session),
            'total_tax_payments': calc_service.get_total_tax_payments(fund, session),
            'total_unit_purchases': calc_service.get_total_unit_purchases(fund, session),
            'total_unit_sales': calc_service.get_total_unit_sales(fund, session),
            'total_daily_interest_charges': calc_service.get_total_daily_interest_charges(fund, session)
        })
        
        # Get NAV-specific metrics for NAV-based funds
        if fund.tracking_type == 'NAV_BASED':
            metrics.update({
                'current_units': fund.current_units,
                'current_unit_price': fund.current_unit_price,
                'current_nav_total': fund.current_nav_total
            })
        
        # Get cost-specific metrics for cost-based funds
        if fund.tracking_type == 'COST_BASED':
            metrics.update({
                'total_cost_basis': fund.total_cost_basis
            })
        
        # Get IRR metrics
        metrics.update({
            'irr_gross': fund.irr_gross,
            'irr_after_tax': fund.irr_after_tax,
            'irr_real': fund.irr_real
        })
        
        # Calculate derived metrics
        if fund.commitment_amount and fund.commitment_amount > 0:
            metrics['commitment_utilization'] = (fund.current_equity_balance / fund.commitment_amount) * 100
            metrics['remaining_commitment'] = max(0, fund.commitment_amount - fund.current_equity_balance)
        else:
            metrics['commitment_utilization'] = 0.0
            metrics['remaining_commitment'] = 0.0
        
        # Calculate fund duration
        if fund.start_date and fund.end_date:
            metrics['actual_duration_months'] = self._calculate_months_between(fund.start_date, fund.end_date)
        elif fund.start_date:
            from datetime import date
            today = date.today()
            metrics['fund_age_months'] = self._calculate_months_between(fund.start_date, today)
        
        return metrics
    
    def get_distribution_summary(self, fund: 'Fund', session: Optional[Session] = None) -> Dict[str, Any]:
        """
        [MIGRATED] Get comprehensive distribution analysis and summaries.
        
        This method was migrated from the legacy Fund model to provide
        detailed distribution analytics and reporting.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            dict: Distribution summary and analysis
        """
        if not session:
            return {}
        
        from src.fund.services.fund_calculation_service import FundCalculationService
        calc_service = FundCalculationService()
        
        # Get basic distribution totals
        total_distributions = calc_service.get_total_distributions(fund, session)
        total_tax_withheld = calc_service.get_total_tax_withheld(fund, session)
        
        # Calculate net distributions
        net_distributions = total_distributions - total_tax_withheld if total_distributions else 0
        
        # Get distribution breakdown by type
        distributions_by_type = calc_service.get_distributions_by_type(fund, session)
        
        # Get taxable vs non-taxable breakdown
        taxable_distributions = calc_service.get_taxable_distributions(fund, session)
        gross_distributions = calc_service.get_gross_distributions(fund, session)
        
        return {
            'fund_id': fund.id,
            'fund_name': fund.name,
            'total_distributions': total_distributions,
            'total_tax_withheld': total_tax_withheld,
            'net_distributions': net_distributions,
            'distributions_by_type': distributions_by_type,
            'taxable_distributions': taxable_distributions,
            'gross_distributions': gross_distributions,
            'tax_withholding_rate': (total_tax_withheld / total_distributions * 100) if total_distributions else 0,
            'net_distribution_rate': (net_distributions / total_distributions * 100) if total_distributions else 0
        }
    
    def _calculate_months_between(self, start_date: date, end_date: date) -> int:
        """
        Calculate the number of months between two dates.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            int: Number of months between dates
        """
        year_diff = end_date.year - start_date.year
        month_diff = end_date.month - start_date.month
        
        total_months = year_diff * 12 + month_diff
        
        # Adjust for day of month
        if end_date.day < start_date.day:
            total_months -= 1
        
        return max(0, total_months)
