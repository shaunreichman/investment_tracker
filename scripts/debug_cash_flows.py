"""
Ad-hoc debug script for FundEvent cash flow logic.

Usage:
  source venv/bin/activate
  python scripts/debug_cash_flows.py

Creates a minimal fund, events, bank, and account; then exercises cash flow
reconciliation for:
  - same-currency match
  - same-currency mismatch
  - interest distribution with same-date withholding tax adjustment
  - cross-currency flow (should mark incomplete)
"""

from datetime import date

from src.database import get_database_session
from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany
from src.fund.models import Fund, FundType, EventType, DistributionType, CashFlowDirection
from src.banking.models import Bank, BankAccount


def main():
    engine, sf, Scoped = get_database_session()
    session = Scoped()
    try:
        # Setup root objects
        entity = Entity.create(name="Debug Entity", tax_jurisdiction="AU", session=session)
        ic = InvestmentCompany.create(name="Debug IC", session=session)
        fund = Fund.create(
            investment_company_id=ic.id,
            entity_id=entity.id,
            name="Debug Fund",
            fund_type="PE",
            tracking_type=FundType.COST_BASED,
            currency="AUD",
            session=session,
        )

        bank = Bank.create(name="DBG Bank", country="AU", session=session)
        acct_aud = BankAccount.create(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Main AUD",
            account_number="123456",
            currency="AUD",
            session=session,
        )
        acct_usd = BankAccount.create(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="USD",
            account_number="789012",
            currency="USD",
            session=session,
        )

        # Capital call 1000 AUD
        cc = fund.add_capital_call(amount=1000.0, date=date(2025, 8, 9), description="Capital call", session=session)

        # Add two same-currency flows that total 1000 => complete
        cc.add_cash_flow(
            bank_account_id=acct_aud.id,
            transfer_date=date(2025, 8, 10),
            currency="AUD",
            amount=400.0,
            reference="T1",
            session=session,
        )
        cc.add_cash_flow(
            bank_account_id=acct_aud.id,
            transfer_date=date(2025, 8, 11),
            currency="AUD",
            amount=600.0,
            reference="T2",
            session=session,
        )
        print("CC same-currency complete:", cc.is_cash_flow_complete)

        # Make mismatch by adding 10 more
        cc.add_cash_flow(
            bank_account_id=acct_aud.id,
            transfer_date=date(2025, 8, 12),
            currency="AUD",
            amount=10.0,
            reference="T3",
            session=session,
        )
        print("CC mismatch complete (should be False):", cc.is_cash_flow_complete)

        # Interest distribution with withholding
        dist, tax = fund.add_distribution(
            event_date=date(2025, 8, 15),
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True,
            gross_interest_amount=100.0,
            withholding_tax_amount=10.0,
            description="Interest with 10 withheld",
            session=session,
        )
        # Net should be 90; add a single 90 AUD inflow
        dist.add_cash_flow(
            bank_account_id=acct_aud.id,
            transfer_date=date(2025, 8, 15),
            currency="AUD",
            amount=90.0,
            reference="NET",
            session=session,
        )
        print("Interest net complete:", dist.is_cash_flow_complete)

        # Cross-currency flow (should mark incomplete)
        cc2 = fund.add_capital_call(amount=500.0, date=date(2025, 8, 20), description="CC2", session=session)
        # USD account, USD currency
        cc2.add_cash_flow(
            bank_account_id=acct_usd.id,
            transfer_date=date(2025, 8, 21),
            currency="USD",
            amount=500.0,
            reference="USD-T",
            session=session,
        )
        print("Cross-currency complete (should be False):", cc2.is_cash_flow_complete)

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()


