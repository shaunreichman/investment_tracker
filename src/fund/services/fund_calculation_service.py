"""
Fund Calculation Service.

This service extracts complex calculation logic from the Fund model to provide
clean separation of concerns and improved testability.

Extracted functionality:
- FIFO calculations for NAV-based funds
- Capital event field calculations
- Financial aggregation methods

Note: 
- Equity balance calculations have been moved to FundEquityCalculator
- IRR calculations have been moved to FundIrRCalculator and FundIrRService
for better separation of concerns and improved performance.
"""

from typing import List, Tuple, Optional, Dict, Any
from datetime import date, datetime
import numpy as np
import numpy_financial as npf
from sqlalchemy.orm import Session
from sqlalchemy import func

# Use string references to avoid circular imports
# from src.fund.models import Fund, FundEvent, EventType, FundType
# Migrated calculation functions are now internal utility methods

from src.shared.utils import with_session
from src.fund.enums import FundStatus, EventType
from src.fund.models import FundEvent
from src.fund.repositories import FundEventRepository
from src.fund.calculators.debt_cost_calculator import DebtCostCalculator
from src.fund.calculators.fifo_capital_gains_calculator import FifoCapitalGainsCalculator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.fund.models import Fund


class FundCalculationService:
    """
    Service for handling complex fund calculations extracted from the Fund model.
    
    This service provides clean separation of concerns for:
    - FIFO calculations for NAV-based funds
    - Capital event field calculations
    - Financial aggregation methods
    
    Note: 
    - Equity balance calculations have been moved to FundEquityCalculator
    - IRR calculations have been moved to FundIrRCalculator and FundIrRService
    for better separation of concerns and improved performance.
    """
    
    def __init__(self):
        """Initialize the FundCalculationService."""
        self.fund_event_repository = FundEventRepository()
    
    # ============================================================================
    # IRR CALCULATIONS
    # ============================================================================
    # NOTE: IRR calculations have been moved to FundIrRCalculator and FundIrRService
    # for better separation of concerns and improved performance.
    # Use FundIrRService for all IRR calculations.
    
    # ============================================================================
    # EQUITY BALANCE CALCULATIONS
    # ============================================================================
    
    def calculate_actual_duration_months(self, fund: 'Fund', session: Optional[Session] = None) -> Optional[float]:
        """
        [EXTRACTED] Calculate the actual duration of the fund in months.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float or None: Duration in months, or None if not computable
        """
        if not fund.start_date:
            return None
        
        if fund.end_date:
            end_date = fund.end_date
        elif fund.status == FundStatus.ACTIVE:
            end_date = date.today()
        else:
            return None
        
        delta = end_date - fund.start_date
        return delta.days / 30.44  # Average days per month
    
    # ============================================================================
    # IRR CALCULATIONS
    # ============================================================================
    
    
    
    
    # ============================================================================
    # FINANCIAL AGGREGATION METHODS (MIGRATED FROM LEGACY)
    # ============================================================================
    
    def get_total_capital_calls(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total capital calls for the fund.
        
        This method was migrated from the legacy Fund model to provide
        capital call aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total capital calls amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        return self.fund_event_repository.get_total_by_type(fund.id, EventType.CAPITAL_CALL, session)
    
    def get_total_capital_returns(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total capital returns for the fund.
        
        This method was migrated from the legacy Fund model to provide
        capital return aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total capital returns amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        return self.fund_event_repository.get_total_by_type(fund.id, EventType.RETURN_OF_CAPITAL, session)
    
    def get_total_distributions(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total distributions for the fund.
        
        This method was migrated from the legacy Fund model to provide
        distribution aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total distributions amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        return self.fund_event_repository.get_total_by_type(fund.id, EventType.DISTRIBUTION, session)
    
    def get_total_tax_withheld(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total tax withheld for the fund.
        
        This method was migrated from the legacy Fund model to provide
        tax withholding aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total tax withheld amount
        """
        if not session:
            return 0.0
        
        return self.fund_event_repository.get_total_tax_withheld(fund.id, session)
    
    def get_total_tax_payments(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total tax payments for the fund.
        
        This method was migrated from the legacy Fund model to provide
        tax payment aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total tax payments amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        return self.fund_event_repository.get_total_by_type(fund.id, EventType.TAX_PAYMENT, session)
    
    def get_total_daily_interest_charges(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total daily interest charges for the fund.
        
        This method was migrated from the legacy Fund model to provide
        interest charge aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total daily interest charges amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        return self.fund_event_repository.get_total_by_type(fund.id, EventType.DAILY_RISK_FREE_INTEREST_CHARGE, session)
    
    def get_total_unit_purchases(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total unit purchases for the fund.
        
        This method was migrated from the legacy Fund model to provide
        unit purchase aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total unit purchases amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        return self.fund_event_repository.get_total_by_type(fund.id, EventType.UNIT_PURCHASE, session)
    
    def get_total_unit_sales(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total unit sales for the fund.
        
        This method was migrated from the legacy Fund model to provide
        unit sale aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total unit sales amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        return self.fund_event_repository.get_total_by_type(fund.id, EventType.UNIT_SALE, session)
    
    def get_distributions_by_type(self, fund: 'Fund', session: Optional[Session] = None) -> Dict[str, float]:
        """
        [MIGRATED] Get distributions broken down by type.
        
        This method was migrated from the legacy Fund model to provide
        distribution type analysis capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            dict: Distribution amounts by type
        """
        if not session:
            return {}
        
        return self.fund_event_repository.get_distributions_by_type(fund.id, session)
    
    def get_taxable_distributions(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total taxable distributions for the fund.
        
        This method was migrated from the legacy Fund model to provide
        taxable distribution calculation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total taxable distributions amount
        """
        if not session:
            return 0.0
        
        return self.fund_event_repository.get_taxable_distributions(fund.id, session)
    
    def get_gross_distributions(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get gross distributions (before tax withholding) for the fund.
        
        This method was migrated from the legacy Fund model to provide
        gross distribution calculation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Gross distributions amount
        """
        # Gross distributions are the same as total distributions
        return self.get_total_distributions(fund, session)
    
    def get_net_distributions(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get net distributions (after tax withholding) for the fund.
        
        This method was migrated from the legacy Fund model to provide
        net distribution calculation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Net distributions amount
        """
        total_distributions = self.get_total_distributions(fund, session)
        total_tax_withheld = self.get_total_tax_withheld(fund, session)
        
        return total_distributions - total_tax_withheld

    # ============================================================================
    # MIGRATED CALCULATION FUNCTIONS FROM fund/calculations.py
    # ============================================================================
    

    def _calculate_debt_cost_utility(self, events, risk_free_rates, start_date, end_date, currency):
        """
        [REFACTORED] Calculate debt cost using pure calculator.
        
        This method now delegates to DebtCostCalculator for pure mathematical
        calculations, following the calculator layer rules.
        
        Args:
            events (list): List of FundEvent objects (capital movements).
            risk_free_rates (list): List of RiskFreeRate objects, sorted by date.
            start_date (date): Start date for the calculation period.
            end_date (date): End date for the calculation period.
            currency (str): Currency code for the calculation.
        
        Returns:
            dict: {
                'total_debt_cost': float,  # Total opportunity cost over the period
                'average_risk_free_rate': float,  # Weighted average risk-free rate
                'debt_cost_percentage': float,  # Debt cost as a percentage of average equity
                'investment_duration_years': float,  # Duration in years
                'average_equity': float,  # Average equity over the period
                'total_days': int  # Number of days in the period
            }
        
        Business context:
            Used for real IRR calculations in Fund models, to account for the opportunity cost of capital.
        """
        # CALCULATED: Delegate to pure calculator for mathematical operations
        result = DebtCostCalculator.calculate_debt_cost(
            events, risk_free_rates, start_date, end_date, currency
        )
        
        # Convert DebtCostResult to dictionary for backward compatibility
        return {
            'total_debt_cost': result.total_debt_cost,
            'average_risk_free_rate': result.average_risk_free_rate,
            'debt_cost_percentage': result.debt_cost_percentage,
            'investment_duration_years': result.investment_duration_years,
            'average_equity': result.average_equity,
            'total_days': result.total_days
        }

    def calculate_nav_based_capital_gains(self, events: List[FundEvent]) -> float:
        """
        [REFACTORED] Calculate capital gains for NAV-based funds using pure calculator.
        
        This method now delegates to FifoCapitalGainsCalculator for pure mathematical
        calculations, following the calculator layer rules.
        
        Args:
            events: List of FundEvent objects (unit purchases/sales)
            
        Returns:
            float: Total capital gains
            
        Business context:
            Used for tax calculations and performance reporting in NAV-based funds.
        """
        # CALCULATED: Delegate to pure calculator for mathematical operations
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events)
        return result.total_capital_gains

    def calculate_cost_based_capital_gains(self, events: List[FundEvent]) -> float:
        """
        [REFACTORED] Calculate capital gains for cost-based funds.
        
        For cost-based funds, capital gains are typically distributions of type CAPITAL_GAIN.
        This method extracts the calculation logic for better separation of concerns.
        
        Args:
            events: List of FundEvent objects (capital calls/returns/distributions)
            
        Returns:
            float: Total capital gains
            
        Business context:
            Used for tax calculations and performance reporting in cost-based funds.
        """
        from src.fund.enums import EventType, DistributionType
        
        # For cost-based funds, capital gains are typically distributions
        total_capital_gains = 0.0
        for event in events:
            if (event.event_type == EventType.DISTRIBUTION and 
                event.distribution_type and 
                event.distribution_type == DistributionType.CAPITAL_GAIN):
                total_capital_gains += event.amount or 0.0
        
        return total_capital_gains
