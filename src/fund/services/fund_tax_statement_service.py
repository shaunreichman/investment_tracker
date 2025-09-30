"""
Fund Tax Statement Service.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date

from src.fund.repositories import FundTaxStatementRepository, FundEventRepository, FundRepository
from src.rates.repositories import RiskFreeRateRepository
from src.fund.models import FundTaxStatement, FundEvent
from src.fund.enums.fund_tax_statement_enums import SortFieldFundTaxStatement
from src.shared.enums.shared_enums import SortOrder, EventOperation
from src.fund.enums.fund_enums import FundTrackingType
from src.fund.enums.fund_event_enums import EventType, DistributionType, TaxPaymentType, GroupType
from src.fund.services.fund_validation_service import FundValidationService

class FundTaxStatementService:
    """
    Fund Tax Statement Service.

    This module provides the FundTaxStatementService class, which handles fund tax statement operations and business logic.
    The service provides clean separation of concerns for:
    - Fund tax statement retrieval
    - Fund tax statement creation
        - Creation of daily debt cost events
        - Creation of tax payment events
        - Handling of secondary impact of events
    - Fund tax statement deletion

    The service uses the FundTaxStatementRepository to perform CRUD operations.
    The service is used by the FundTaxStatementController to handle fund tax statement operations.
    The service also uses the FundEventRepository to perform CRUD operations.
    The service also uses the FinancialYearCalculator to calculate the financial year start and end dates.
    The service also uses the FifoCapitalGainsCalculator to calculate the capital gains.
    The service also uses the DebtCostCalculator to calculate the debt cost.
    The service also uses the RiskFreeRateRepository to perform CRUD operations.
    The service also uses the FundValidationService to validate fund tax statements.
    """

    def __init__(self):
        """
        Initialize the FundTaxStatementService.

        Args:
            fund_tax_statement_repository: Fund tax statement repository to use. If None, creates a new one.
            fund_event_repository: Fund event repository to use. If None, creates a new one.
            fund_validation_service: Fund validation service to use. If None, creates a new one.
        """
        self.fund_tax_statement_repository = FundTaxStatementRepository()
        self.fund_event_repository = FundEventRepository()
        self.fund_validation_service = FundValidationService()
        self.fund_repository = FundRepository()
        self.risk_free_rate_repository = RiskFreeRateRepository()


    ################################################################################
    # Create Fund Tax Statement
    ################################################################################

    def get_fund_tax_statements(self, session: Session,
        fund_id: Optional[int] = None,
        entity_id: Optional[int] = None,
        financial_year: Optional[str] = None,
        start_tax_payment_date: Optional['date'] = None,
        end_tax_payment_date: Optional['date'] = None,
        sort_by: SortFieldFundTaxStatement = SortFieldFundTaxStatement.FINANCIAL_YEAR,
        sort_order: SortOrder = SortOrder.ASC
    )-> List[FundTaxStatement]:
        """
        Get all fund tax statements.

        Args:
            fund_id: ID of the fund to filter by
            entity_id: ID of the entity to filter by
            financial_year: Financial year to filter by
            start_tax_payment_date: Start tax payment date to filter by
            end_tax_payment_date: End tax payment date to filter by
            sort_by: Field to sort by
            sort_order: Order to sort by
            session: Database session

        Returns:
            List[FundTaxStatement]: List of fund tax statements
        """
        return self.fund_tax_statement_repository.get_fund_tax_statements(fund_id, entity_id, financial_year, start_tax_payment_date, end_tax_payment_date, sort_by, sort_order, session)
        
    
    def get_fund_tax_statement_by_id(self, fund_tax_statement_id: int, session: Session) -> Optional[FundTaxStatement]:
        """
        Get a fund tax statement by ID.

        Args:
            fund_tax_statement_id: ID of the fund tax statement to retrieve
            session: Database session

        Returns:
            FundTaxStatement: Fund tax statement object
        """
        return self.fund_tax_statement_repository.get_fund_tax_statement_by_id(fund_tax_statement_id, session)


    ################################################################################
    # Create Fund Tax Statement
    ################################################################################

    def create_fund_tax_statement(self, fund_id: int, fund_tax_statement_data: Dict[str, Any], session: Session) -> FundTaxStatement:
        """
        Create a new fund tax statement.

        Args:
            fund_id: ID of the fund
            fund_tax_statement_data: Dictionary containing fund tax statement data
            session: Database session

        Returns:
            FundTaxStatement: The created fund tax statement
        """

        processed_data = fund_tax_statement_data.copy()
        processed_data['fund_id'] = fund_id

        # Validate Entity exists
        from src.entity.repositories.entity_repository import EntityRepository
        entity_repository = EntityRepository()
        entity = entity_repository.get_entity_by_id(processed_data['entity_id'], session)
        if not entity:
            raise ValueError(f"Entity not found")
 
        # Calculate the financial year start and end dates
        from src.fund.calculators.financial_year_calculator import FinancialYearCalculator
        fy_start_date, fy_end_date = FinancialYearCalculator.calculate_financial_year_dates(processed_data['financial_year'])
        processed_data['financial_year_start_date'] = fy_start_date
        processed_data['financial_year_end_date'] = fy_end_date

        # Create the fund tax statement
        fund_tax_statement = self.fund_tax_statement_repository.create_fund_tax_statement(processed_data, session)
        if not fund_tax_statement:
            raise ValueError(f"Failed to create fund tax statement")

        # Create the daily debt cost events
        daily_debt_cost_events = self._create_daily_debt_cost_events(fund_tax_statement, session)
        if daily_debt_cost_events:
            for event_data in daily_debt_cost_events:
                self.fund_event_repository.create_fund_event(event_data=event_data, session=session)

        # Create the tax payment events
        tax_events = self._create_tax_payment_events(fund_tax_statement, session)
        if tax_events:
            # Generate Group IDs for the tax events
            group_id = self.fund_event_repository.generate_group_id(session)
            group_position = 0
            for event_data in tax_events:
                event_data['group_id'] = group_id
                event_data['group_type'] = GroupType.TAX_STATEMENT
                event_data['is_grouped'] = True
                event_data['group_position'] = group_position
                group_position += 1
                self.fund_event_repository.create_fund_event(event_data=event_data, session=session)

        session.flush()

        # Call the Fund Event Secondary Service to handle the secondary impact of the events
        from src.fund.services.fund_event_secondary_service import FundEventSecondaryService
        fund_event_secondary_service = FundEventSecondaryService()
        fund_event_secondary_service.handle_event_secondary_impact(fund_id=fund_tax_statement.fund_id, fund_event_type=EventType.TAX_PAYMENT, fund_event_operation=EventOperation.CREATE, session=session, event_id=fund_tax_statement.id)

        return fund_tax_statement        


    ################################################################################
    # Delete Fund Tax Statement
    ################################################################################

    def delete_fund_tax_statement(self, fund_tax_statement_id: int, session: Session) -> bool:
        """
        Delete a fund tax statement.

        Args:
            fund_tax_statement_id: ID of the fund tax statement to delete
            session: Database session

        Returns:
            True if fund tax statement was deleted, False if not found
        """
        fund_tax_statement = self.fund_tax_statement_repository.get_fund_tax_statement_by_id(fund_tax_statement_id, session)
        if not fund_tax_statement:
            raise ValueError(f"Fund tax statement not found")

        validation_errors = self.fund_validation_service.validate_fund_tax_statement_deletion(fund_tax_statement_id, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")
        
        success = self.fund_tax_statement_repository.delete_fund_tax_statement(fund_tax_statement_id, session)
        if not success:
            raise ValueError(f"Failed to delete fund tax statement")

        # Delete the fund_events associated with the fund tax statement
        # Need to build the logic to get this from the fund_event repository

        return success


    ################################################################################
    # Create Tax Payment Events
    ################################################################################

    def _create_tax_payment_events(self, fund_tax_statement: FundTaxStatement, session: Session) -> List[FundEvent]:
        """
        Create the tax payment events for the given fund tax statement.

        Args:
            fund_tax_statement: Fund tax statement to create events for
            session: Database session

        Returns:
            List[FundEvent]: List of created tax payment events
        """
        events = []
        # Interest tax payment
        interest_event = self._create_interest_tax_payment(fund_tax_statement, session=session)
        if interest_event:
            events.append(interest_event)
        # Franked dividend tax payment
        franked_event = self._create_franked_dividend_tax_payment(
            fund_tax_statement, session=session)
        if franked_event:
            events.append(franked_event)
        # Unfranked dividend tax payment
        unfranked_event = self._create_unfranked_dividend_tax_payment(
            fund_tax_statement, session=session)
        if unfranked_event:
            events.append(unfranked_event)
        # Capital gain tax payment
        capital_gain_event = self._create_capital_gain_tax_payment(fund_tax_statement, session=session)
        if capital_gain_event:
            events.append(capital_gain_event)
        # FY debt cost event
        eofy_debt_cost_event = self._create_eofy_debt_cost_event(fund_tax_statement, session=session)
        if eofy_debt_cost_event:
            events.append(eofy_debt_cost_event)
        return events

    def _create_interest_tax_payment(self, fund_tax_statement: FundTaxStatement) -> Dict[str, Any]:
        """
        Create an interest tax payment event for the given fund tax statement.

        Args:
            fund_tax_statement: Fund tax statement to create event for

        Returns:
            Dict[str, Any]: Interest tax payment event data
        """
        if fund_tax_statement.interest_income_tax_rate and fund_tax_statement.interest_income_amount and fund_tax_statement.interest_income_tax_rate != 0 and fund_tax_statement.interest_income_amount > 0:
            total_tax_liability = fund_tax_statement.interest_income_amount * (fund_tax_statement.interest_income_tax_rate / 100)
            fund_tax_statement.interest_tax_amount = max(0, total_tax_liability - (fund_tax_statement.interest_non_resident_withholding_tax_from_statement or 0.0))
            event_data = {
                'fund_id': fund_tax_statement.fund_id,
                'event_type': EventType.TAX_PAYMENT,
                'tax_payment_type': TaxPaymentType.EOFY_INTEREST_TAX,
                'event_date': fund_tax_statement.tax_payment_date,
                'amount': fund_tax_statement.interest_tax_amount,
                'description': f"Tax payment for FY {fund_tax_statement.financial_year}",
                'reference_number': f"TAX-{fund_tax_statement.financial_year}",
                'tax_statement_id': fund_tax_statement.id
            }
            return event_data
        else:
            fund_tax_statement.interest_tax_amount = 0.0
            return None
        
    def _create_franked_dividend_tax_payment(self, fund_tax_statement: FundTaxStatement, session: Session) -> Dict[str, Any]:
        """
        Create a franked dividend tax payment event for the given fund tax statement.            
        """
        # 1. Calculate Franked Dividend received this FY
        if fund_tax_statement.dividend_franked_income_amount is None or fund_tax_statement.dividend_franked_income_amount == 0.0:
            franked_div_events = self.fund_event_repository.get_fund_events(fund_ids=[fund_tax_statement.fund_id],
                distribution_types=[DistributionType.DIVIDEND_FRANKED],
                start_event_date=fund_tax_statement.financial_year_start_date,
                end_event_date=fund_tax_statement.financial_year_end_date,
                session=session)
            franked_total = 0.0
            for event in franked_div_events:
                franked_total += event.amount or 0.0
            fund_tax_statement.dividend_franked_income_amount = franked_total
            fund_tax_statement.dividend_franked_income_amount_from_tax_statement_flag = False
        else:
            fund_tax_statement.dividend_franked_income_amount_from_tax_statement_flag = True
        
        # 2. Calculate Franked Dividend Tax Amount
        if fund_tax_statement.dividend_franked_income_tax_rate and fund_tax_statement.dividend_franked_income_amount and fund_tax_statement.dividend_franked_income_tax_rate != 0 and fund_tax_statement.dividend_franked_income_amount > 0:
            fund_tax_statement.dividend_franked_tax_amount = fund_tax_statement.dividend_franked_income_amount * (fund_tax_statement.dividend_franked_income_tax_rate / 100)
            event_data = {
                'fund_id': fund_tax_statement.fund_id,
                'event_type': EventType.TAX_PAYMENT,
                'tax_payment_type': TaxPaymentType.DIVIDENDS_FRANKED_TAX,
                'event_date': fund_tax_statement.tax_payment_date,
                'amount': fund_tax_statement.dividend_franked_tax_amount,
                'description': f"Tax payment for FY {fund_tax_statement.financial_year}",
                'reference_number': f"TAX-{fund_tax_statement.financial_year}",
                'tax_statement_id': fund_tax_statement.id
            }
            return event_data
        else:
            fund_tax_statement.dividend_franked_tax_amount = 0.0
            return None

    def _create_unfranked_dividend_tax_payment(self, fund_tax_statement: FundTaxStatement, session: Session) -> Dict[str, Any]:
        """
        Create an unfranked dividend tax payment event for the given fund tax statement.
        """
        # 1. Calculate Unfranked Dividend received this FY
        if fund_tax_statement.dividend_unfranked_income_amount is None or fund_tax_statement.dividend_unfranked_income_amount == 0.0:
            unfranked_div_events = self.fund_event_repository.get_fund_events(fund_ids=[fund_tax_statement.fund_id],
                distribution_types=[DistributionType.DIVIDEND_UNFRANKED],
                start_event_date=fund_tax_statement.financial_year_start_date,
                end_event_date=fund_tax_statement.financial_year_end_date,
                session=session)
            unfranked_total = 0.0
            for event in unfranked_div_events:
                unfranked_total += event.amount or 0.0
            fund_tax_statement.dividend_unfranked_income_amount = unfranked_total
            fund_tax_statement.dividend_unfranked_income_amount_from_tax_statement_flag = False
        else:
            fund_tax_statement.dividend_unfranked_income_amount_from_tax_statement_flag = True

        # 2. Calculate Unfranked Dividend Tax Amount
        if fund_tax_statement.dividend_unfranked_income_tax_rate and fund_tax_statement.dividend_unfranked_income_amount and fund_tax_statement.dividend_unfranked_income_tax_rate != 0 and fund_tax_statement.dividend_unfranked_income_amount > 0:
            fund_tax_statement.dividend_unfranked_tax_amount = fund_tax_statement.dividend_unfranked_income_amount * (fund_tax_statement.dividend_unfranked_income_tax_rate / 100)
            event_data = {
                'fund_id': fund_tax_statement.fund_id,
                'event_type': EventType.TAX_PAYMENT,
                'tax_payment_type': TaxPaymentType.DIVIDENDS_UNFRANKED_TAX,
                'event_date': fund_tax_statement.tax_payment_date,
                'amount': fund_tax_statement.dividend_unfranked_tax_amount,
                'description': f"Tax payment for FY {fund_tax_statement.financial_year}",
                'reference_number': f"TAX-{fund_tax_statement.financial_year}",
                'tax_statement_id': fund_tax_statement.id
            }
            return event_data
        else:
            fund_tax_statement.dividend_unfranked_tax_amount = 0.0
            return None
        

    def _create_capital_gain_tax_payment(self, fund_tax_statement: FundTaxStatement, session: Session) -> FundEvent:
        """
        Create a capital gain tax payment event for the given fund tax statement.
        """
        # Initialize capital_gains to ensure it's always defined
        capital_gains = 0.0
        
        if fund_tax_statement.capital_gain_income_amount is None or fund_tax_statement.capital_gain_income_amount == 0.0:
            # Capital gain income amount has not been added on the Tax Statement
            fund = self.fund_repository.get_fund_by_id(fund_tax_statement.fund_id, session=session)
            if fund.tracking_type == FundTrackingType.NAV_BASED:
                fund_events = self.fund_event_repository.get_fund_events(fund_ids=[fund.id], sort_order=SortOrder.ASC, session=session)
                
                from src.fund.calculators.fifo_capital_gains_calculator import FifoCapitalGainsCalculator
                fifo_capital_gains_calculator = FifoCapitalGainsCalculator()
                capital_gains_dict = fifo_capital_gains_calculator.calculate_capital_gains(fund_events=fund_events,
                    cg_start_date=fund_tax_statement.financial_year_start_date,
                    cg_end_date=fund_tax_statement.financial_year_end_date,
)
                capital_gains = capital_gains_dict.total_capital_gains
                fund_tax_statement.capital_gain_income_amount = capital_gains
                fund_tax_statement.capital_gain_income_amount_from_tax_statement_flag = False
            elif fund.tracking_type == FundTrackingType.COST_BASED:
                # No Capital Gains for Cost Based funds for now
                capital_gains = 0.0
        else:
            # Capital gain income amount has been added on the Tax Statement
            capital_gains = fund_tax_statement.capital_gain_income_amount
            fund_tax_statement.capital_gain_income_amount_from_tax_statement_flag = True

        if capital_gains > 0:
            event_data = {
                'fund_id': fund_tax_statement.fund_id,
                'event_type': EventType.TAX_PAYMENT,
                'tax_payment_type': TaxPaymentType.CAPITAL_GAINS_TAX,
                'event_date': fund_tax_statement.tax_payment_date,
                'amount': capital_gains,
                'description': f"Tax payment for FY {fund_tax_statement.financial_year}",
                'reference_number': f"TAX-{fund_tax_statement.financial_year}",
                'tax_statement_id': fund_tax_statement.id
            }
            return event_data
        else:
            return None

    def _create_eofy_debt_cost_event(self, fund_tax_statement: FundTaxStatement, session: Session) -> Dict[str, Any]:
        """
        Create a FY debt cost event for the given fund tax statement.
        """
        # 1. Get all the daily debt cost events for the given fund tax statement
        daily_debt_cost_events = self.fund_event_repository.get_fund_events(fund_ids=[fund_tax_statement.fund_id],
            event_types=[EventType.DAILY_RISK_FREE_INTEREST_CHARGE],
            start_event_date=fund_tax_statement.financial_year_start_date,
            end_event_date=fund_tax_statement.financial_year_end_date,
            session=session)

        # 2. Calculate the total debt cost
        total_debt_cost = 0.0
        for event in daily_debt_cost_events:
            total_debt_cost += event.amount or 0.0
        fund_tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest = total_debt_cost

        # 3. Calculate the FY debt cost tax benefit
        tax_benefit = total_debt_cost * (fund_tax_statement.eofy_debt_interest_deduction_rate / 100)
        fund_tax_statement.eofy_debt_interest_deduction_total_deduction = tax_benefit

        # 4. Create the FY debt cost event
        if tax_benefit > 0:
            event_data = {
            'fund_id': fund_tax_statement.fund_id,
            'event_type': EventType.TAX_PAYMENT,
            'tax_payment_type': TaxPaymentType.EOFY_INTEREST_TAX,
            'event_date': fund_tax_statement.tax_payment_date,
            'amount': tax_benefit,
            'description': f"FY {fund_tax_statement.financial_year} Interest Tax Benefit (${tax_benefit:,.2f})",
            'reference_number': f"EOFY_INTEREST_TAX benefit-{fund_tax_statement.financial_year}",
            'tax_statement_id': fund_tax_statement.id
            }
            return event_data
        else:
            return None


    ################################################################################
    # Create Daily Debt Cost Events
    ################################################################################

    def _create_daily_debt_cost_events(self, fund_tax_statement: FundTaxStatement, session: Session) -> List[Dict[str, Any]]:   
        """
        Create a FY debt cost event for the given fund tax statement.
        """
        fund = self.fund_repository.get_fund_by_id(fund_tax_statement.fund_id, session=session)
        capital_events = self.fund_event_repository.get_fund_events(fund_ids=[fund_tax_statement.fund_id],
            event_types=[EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE],
            session=session)
        risk_free_rates = self.risk_free_rate_repository.get_risk_free_rates(currency=fund.currency, session=session)

        # 1. Generate Daily Debt Cost
        from src.fund.calculators.debt_cost_calculator import DailyDebtCostCalculator
        debt_cost_calculator = DailyDebtCostCalculator()
        daily_debt_cost_dict = debt_cost_calculator.calculate_debt_cost(capital_events, risk_free_rates, fund_tax_statement.financial_year_start_date, fund_tax_statement.financial_year_end_date)

        # 2. Check if these Debt Costs already exist and if they're incorrect, update them
        dates_checked = []
        existing_debt_cost_events = self.fund_event_repository.get_fund_events(fund_ids=[fund_tax_statement.fund_id],
            event_types=[EventType.DAILY_RISK_FREE_INTEREST_CHARGE],
            start_event_date=fund_tax_statement.financial_year_start_date,
            end_event_date=fund_tax_statement.financial_year_end_date,
            session=session)
        if existing_debt_cost_events:
            for event in existing_debt_cost_events:
                dates_checked.append(event.event_date)
                if event.amount != daily_debt_cost_dict[event.event_date]['debt_cost']:
                    # Debt Cost is incorrect, update it
                    event.amount = daily_debt_cost_dict[event.event_date]['debt_cost']
                    event.description = f"FY {fund_tax_statement.financial_year} Debt Cost (${event.amount:,.2f})"
                    event.reference_number = f"DAILY_RISK_FREE_INTEREST_CHARGE_{fund_tax_statement.financial_year}"
                    event.tax_statement_id = fund_tax_statement.id
                    event.dc_current_equity_balance = daily_debt_cost_dict[event.event_date]['equity']
                    event.dc_risk_free_rate = daily_debt_cost_dict[event.event_date]['rate']
                    return event

        # 3. Create the Debt Cost event_data for the dates that haven't been set
        events_to_create = []
        if daily_debt_cost_dict:
            for date in daily_debt_cost_dict:
                if date not in dates_checked:
                    event_data = {
                        'fund_id': fund_tax_statement.fund_id,
                        'event_type': EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
                        'event_date': date,
                        'amount': daily_debt_cost_dict[date]['debt_cost'],
                        'description': f"FY {fund_tax_statement.financial_year} Debt Cost (${daily_debt_cost_dict[date]['debt_cost']:,.2f})",
                        'reference_number': f"DAILY_RISK_FREE_INTEREST_CHARGE_{fund_tax_statement.financial_year}",
                        'tax_statement_id': fund_tax_statement.id,
                        'dc_current_equity_balance': daily_debt_cost_dict[date]['equity'],
                        'dc_risk_free_rate': daily_debt_cost_dict[date]['rate']
                    }
                    events_to_create.append(event_data)
        return events_to_create