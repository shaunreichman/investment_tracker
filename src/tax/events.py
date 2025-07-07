"""
Tax event creation framework for standardized tax payment event generation.
"""

from typing import Optional, List
from src.fund.models import FundEvent, EventType, TaxPaymentType, DistributionType
from src.tax.models import TaxStatement
from sqlalchemy.orm import Session

class TaxEventFactory:
    """
    Factory for creating standardized tax payment events for funds.
    Provides static methods for each event type.
    """

    @staticmethod
    def create_interest_tax_payment(tax_statement: TaxStatement, session: Optional[Session] = None) -> Optional[FundEvent]:
        """
        Create an interest tax payment event object for the given tax statement.
        Returns the event object or None if not applicable.
        Does not add to the database.
        """
        if not tax_statement:
            raise ValueError("tax_statement is required")
        if tax_statement.tax_payable is None or tax_statement.tax_payable <= 0.01:
            return None
        event = FundEvent(
            fund_id=tax_statement.fund_id,
            event_type=EventType.TAX_PAYMENT,
            event_date=tax_statement.get_tax_payment_date(),
            amount=tax_statement.tax_payable,
            description=f"Tax payment for FY {tax_statement.financial_year}",
            reference_number=f"TAX-{tax_statement.financial_year}",
            tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX
        )
        return event

    @staticmethod
    def create_dividend_tax_payment(tax_statement: TaxStatement, dividend_type: DistributionType, session: Optional[Session] = None) -> Optional[FundEvent]:
        """
        Create a dividend tax payment event object for the given tax statement and dividend type.
        Returns the event object or None if not applicable.
        Does not add to the database.
        """
        if not tax_statement:
            raise ValueError("tax_statement is required")
        if dividend_type not in (DistributionType.DIVIDEND_FRANKED, DistributionType.DIVIDEND_UNFRANKED):
            raise ValueError("dividend_type must be DIVIDEND_FRANKED or DIVIDEND_UNFRANKED")

        if dividend_type == DistributionType.DIVIDEND_FRANKED:
            total = tax_statement.total_dividends_franked or 0.0
            rate = tax_statement.dividends_franked_taxable_rate or 0.0
            payment_type = TaxPaymentType.DIVIDENDS_FRANKED_TAX
            desc = f"Franked dividend tax (rate: {rate}%)"
            ref = f"DIV_FRANKED_TAX_{tax_statement.financial_year}"
        else:
            total = tax_statement.total_dividends_unfranked or 0.0
            rate = tax_statement.dividends_unfranked_taxable_rate or 0.0
            payment_type = TaxPaymentType.DIVIDENDS_UNFRANKED_TAX
            desc = f"Unfranked dividend tax (rate: {rate}%)"
            ref = f"DIV_UNFRANKED_TAX_{tax_statement.financial_year}"

        if total <= 0 or rate <= 0:
            return None

        tax_amount = total * (rate / 100.0)
        if tax_amount <= 0:
            return None

        event = FundEvent(
            fund_id=tax_statement.fund_id,
            event_type=EventType.TAX_PAYMENT,
            event_date=tax_statement.get_tax_payment_date(),
            amount=tax_amount,
            description=desc,
            reference_number=ref,
            tax_payment_type=payment_type
        )
        return event

    @staticmethod
    def create_fy_debt_cost_event(tax_statement: TaxStatement, session: Optional[Session] = None) -> Optional[FundEvent]:
        """
        Create a financial year debt cost event object for the given tax statement.
        Returns the event object or None if not applicable.
        Does not add to the database.
        """
        if not tax_statement:
            raise ValueError("tax_statement is required")
        tax_benefit = tax_statement.calculate_interest_tax_benefit() if hasattr(tax_statement, 'calculate_interest_tax_benefit') else (tax_statement.interest_tax_benefit or 0.0)
        if tax_benefit is None or tax_benefit <= 0:
            return None
        fy_start, fy_end = tax_statement.get_financial_year_dates() if hasattr(tax_statement, 'get_financial_year_dates') else (None, None)
        if not fy_end:
            return None
        event = FundEvent(
            fund_id=tax_statement.fund_id,
            event_type=EventType.FY_DEBT_COST,
            event_date=fy_end,
            amount=tax_benefit,
            description=f"FY {tax_statement.financial_year} Interest Tax Benefit (${tax_benefit:,.2f})",
            reference_number=f"FY_DEBT_COST_{tax_statement.financial_year}"
        )
        return event

    @staticmethod
    def create_all_tax_events(tax_statement: TaxStatement, session: Optional[Session] = None) -> List[FundEvent]:
        """
        Create all applicable tax payment events for the given tax statement.
        Returns a list of event objects (not added to the database).
        """
        events = []
        # Interest tax payment
        interest_event = TaxEventFactory.create_interest_tax_payment(tax_statement, session=session)
        if interest_event:
            events.append(interest_event)
        # Franked dividend tax payment
        franked_event = TaxEventFactory.create_dividend_tax_payment(
            tax_statement, DistributionType.DIVIDEND_FRANKED, session=session)
        if franked_event:
            events.append(franked_event)
        # Unfranked dividend tax payment
        unfranked_event = TaxEventFactory.create_dividend_tax_payment(
            tax_statement, DistributionType.DIVIDEND_UNFRANKED, session=session)
        if unfranked_event:
            events.append(unfranked_event)
        # FY debt cost event
        fy_debt_cost_event = TaxEventFactory.create_fy_debt_cost_event(tax_statement, session=session)
        if fy_debt_cost_event:
            events.append(fy_debt_cost_event)
        return events 