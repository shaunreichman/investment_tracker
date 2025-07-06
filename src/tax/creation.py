"""
Tax creation module.

This module contains methods for creating and managing tax statements and related events.
"""

from src.tax.models import TaxStatement
from src.fund.models import FundEvent, EventType, TaxPaymentType
from src.shared.utils import with_session

def _create_or_update_tax_statement_object(fund, entity_id, financial_year, **kwargs):
    """Create or update a tax statement object.
    Returns the TaxStatement object. No database operations.
    """
    statement = fund.get_tax_statement_for_entity_financial_year(entity_id, financial_year)
    if statement is None:
        statement = TaxStatement(
            fund_id=fund.id,
            entity_id=entity_id,
            financial_year=financial_year,
            **kwargs
        )
    else:
        for key, value in kwargs.items():
            if hasattr(statement, key):
                setattr(statement, key, value)
    statement.calculate_interest_income_fields()
    statement.calculate_total_income()
    return statement

@with_session
def create_or_update_tax_statement(fund, entity_id, financial_year, session=None, **kwargs):
    """Create or update a tax statement for a specific entity and financial year.
    If a statement exists, updates its fields; otherwise, creates a new one.
    Commits the change to the database.
    Returns the TaxStatement instance.
    """
    statement = _create_or_update_tax_statement_object(fund, entity_id, financial_year, **kwargs)
    if statement.id is None:
        session.add(statement)
    session.commit()
    return statement

def _create_tax_payment_event_object(fund, tax_statement):
    """Create a tax payment event object for a tax statement.
    Returns the event object or None if not applicable. No database operations.
    """
    tax_statement.calculate_tax_payable()
    if tax_statement.tax_payable > 0.01:
        tax_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=tax_statement.get_tax_payment_date(),
            amount=tax_statement.tax_payable,
            description=f"Tax payment for FY {tax_statement.financial_year}",
            reference_number=f"TAX-{tax_statement.financial_year}",
            tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX
        )
        return tax_event
    return None

@with_session
def create_tax_payment_events(fund, session=None):
    """Create tax payment events for this fund based on tax statements.
    Used for after-tax IRR calculations. Commits new events to the database.
    Returns a list of created events.
    """
    tax_statements = session.query(TaxStatement).filter(
        TaxStatement.fund_id == fund.id
    ).all()
    created_events = []
    for tax_statement in tax_statements:
        existing_event = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.TAX_PAYMENT,
            FundEvent.event_date == tax_statement.get_tax_payment_date(),
            FundEvent.amount == tax_statement.tax_payable,
            FundEvent.tax_payment_type == TaxPaymentType.EOFY_INTEREST_TAX
        ).first()
        if not existing_event:
            tax_event = _create_tax_payment_event_object(fund, tax_statement)
            if tax_event:
                session.add(tax_event)
                created_events.append(tax_event)
    if created_events:
        session.commit()
    return created_events


__all__ = [
    'create_or_update_tax_statement',
    'create_tax_payment_events',
] 