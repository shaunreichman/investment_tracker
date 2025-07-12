"""
Tax event creation framework for standardized tax payment event generation.
"""

from typing import Optional, List
from src.fund.models import FundEvent, EventType, TaxPaymentType, DistributionType
from src.tax.models import TaxStatement
from sqlalchemy.orm import Session

class TaxEventCriteria:
    """
    Standardized criteria for identifying tax events.
    Used for deduplication and event lookup.
    """
    def __init__(self, fund_id, event_type, event_date, amount, tax_payment_type=None):
        self.fund_id = fund_id
        self.event_type = event_type
        self.event_date = event_date
        self.amount = amount
        self.tax_payment_type = tax_payment_type

    def __repr__(self):
        return (f"<TaxEventCriteria fund_id={self.fund_id} event_type={self.event_type} "
                f"event_date={self.event_date} amount={self.amount} tax_payment_type={self.tax_payment_type}>")

    def to_dict(self):
        return {
            'fund_id': self.fund_id,
            'event_type': self.event_type,
            'event_date': self.event_date,
            'amount': self.amount,
            'tax_payment_type': self.tax_payment_type
        }

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
        tax_statement.calculate_interest_tax_amount()
        if not tax_statement:
            raise ValueError("tax_statement is required")
        if tax_statement.interest_tax_amount is None or tax_statement.interest_tax_amount <= 0.01:
            return None
        event = FundEvent(
            fund_id=tax_statement.fund_id,
            event_type=EventType.TAX_PAYMENT,
            event_date=tax_statement.get_tax_payment_date(),
            amount=tax_statement.interest_tax_amount,
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

        # Ensure dividend totals are calculated from fund events if not set
        tax_statement.calculate_dividend_totals(session)

        if dividend_type == DistributionType.DIVIDEND_FRANKED:
            tax_statement.calculate_dividend_franked_tax_amount()
            tax_amount = tax_statement.dividend_franked_tax_amount
            payment_type = TaxPaymentType.DIVIDENDS_FRANKED_TAX
            desc = f"Franked dividend tax (rate: {tax_statement.dividend_franked_income_tax_rate}%)"
            ref = f"DIV_FRANKED_TAX_{tax_statement.financial_year}"
        elif dividend_type == DistributionType.DIVIDEND_UNFRANKED:
            tax_statement.calculate_dividend_unfranked_tax_amount()
            tax_amount = tax_statement.dividend_unfranked_tax_amount
            payment_type = TaxPaymentType.DIVIDENDS_UNFRANKED_TAX
            desc = f"Unfranked dividend tax (rate: {tax_statement.dividend_unfranked_income_tax_rate}%)"
            ref = f"DIV_UNFRANKED_TAX_{tax_statement.financial_year}"

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
        tax_benefit = tax_statement.calculate_fy_debt_interest_deduction_total_deduction() if hasattr(tax_statement, 'calculate_fy_debt_interest_deduction_total_deduction') else (tax_statement.fy_debt_interest_deduction_total_deduction or 0.0)
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

class TaxEventManager:
    """
    Manages tax event creation, validation, and database operations.
    Provides static methods for event management and deduplication.
    """

    @staticmethod
    def create_or_update_tax_events(tax_statement: TaxStatement, session: Session) -> list:
        """
        Create or update all tax events for a tax statement in the database.
        Returns a list of created or updated FundEvent objects.
        """
        created_or_updated_events = []
        events = TaxEventFactory.create_all_tax_events(tax_statement, session=session)
        for event in events:
            criteria = TaxEventCriteria(
                fund_id=event.fund_id,
                event_type=event.event_type,
                event_date=event.event_date,
                amount=event.amount,  # Used for deduplication, but see below
                tax_payment_type=getattr(event, 'tax_payment_type', None)
            )
            # Find existing event by all criteria except amount
            from src.fund.models import FundEvent
            query = session.query(FundEvent).filter(
                FundEvent.fund_id == event.fund_id,
                FundEvent.event_type == event.event_type,
                FundEvent.event_date == event.event_date,
                FundEvent.tax_payment_type == getattr(event, 'tax_payment_type', None)
            )
            existing = query.first()
            if not existing:
                session.add(event)
                created_or_updated_events.append(event)
            else:
                # If amount or description has changed, update
                updated = False
                if existing.amount != event.amount:
                    existing.amount = event.amount
                    updated = True
                if hasattr(existing, 'description') and existing.description != event.description:
                    existing.description = event.description
                    updated = True
                if updated:
                    created_or_updated_events.append(existing)
        if created_or_updated_events:
            session.commit()
        else:
            pass # No new or updated tax events to commit.
        return created_or_updated_events

    @staticmethod
    def find_existing_event(event_criteria: TaxEventCriteria, session: Session) -> FundEvent:
        """
        Find existing event based on standardized criteria.
        Returns the FundEvent if found, else None.
        """
        from src.fund.models import FundEvent
        query = session.query(FundEvent).filter(
            FundEvent.fund_id == event_criteria.fund_id,
            FundEvent.event_type == event_criteria.event_type,
            FundEvent.event_date == event_criteria.event_date,
            FundEvent.amount == event_criteria.amount
        )
        if event_criteria.tax_payment_type is not None:
            query = query.filter(FundEvent.tax_payment_type == event_criteria.tax_payment_type)
        else:
            query = query.filter(FundEvent.tax_payment_type.is_(None))
        return query.first()

    @staticmethod
    def validate_event_creation(tax_statement: TaxStatement, event_type, session: Session) -> bool:
        """
        Validate that event creation is appropriate for the given tax statement and event type.
        Returns True if valid, False otherwise.
        """
        # Simple validation logic for now
        if event_type == EventType.TAX_PAYMENT:
            return (tax_statement.interest_tax_amount is not None and tax_statement.interest_tax_amount > 0.01)
        elif event_type == TaxPaymentType.DIVIDENDS_FRANKED_TAX:
            return (
                (tax_statement.dividend_franked_income_amount or 0.0) > 0 and
                (tax_statement.dividend_franked_income_tax_rate or 0.0) > 0
            )
        elif event_type == TaxPaymentType.DIVIDENDS_UNFRANKED_TAX:
            return (
                (tax_statement.dividend_unfranked_income_amount or 0.0) > 0 and
                (tax_statement.dividend_unfranked_income_tax_rate or 0.0) > 0
            )
        elif event_type == EventType.FY_DEBT_COST:
            benefit = tax_statement.calculate_fy_debt_interest_deduction_total_deduction() if hasattr(tax_statement, 'calculate_fy_debt_interest_deduction_total_deduction') else (tax_statement.fy_debt_interest_deduction_total_deduction or 0.0)
            return benefit > 0
        return False 