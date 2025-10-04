"""
Integration tests for 3PG Finance comprehensive workflow.

This test recreates the complete 3PG Finance scenario from the old test,
validating that the refactored backend produces the same results as the original system.

Test Scenario:
- Cost-based Private Debt fund
- Capital calls, returns of capital, and interest distributions
- Tax statements with withholding tax
- IRR calculations and fund status transitions
- Complete lifecycle from ACTIVE to COMPLETED

Expected Results (from old test):
- Current equity: $0.00
- Average equity: $66,045.18
- Status: COMPLETED
- IRR: 16.54% (gross), 14.86% (after-tax), 12.05% (real)
- Events: 1 capital call, 7 returns, 7 distributions, 6 tax payments, 512 daily interest charges
"""

from datetime import date
from src.fund.enums import FundTrackingType, FundStatus, EventType, DistributionType
from src.fund.services.fund_service import FundService
from src.fund.services.fund_event_service import FundEventService
from src.fund.services.fund_tax_statement_service import FundTaxStatementService
from src.investment_company.services.company_service import CompanyService
from src.entity.services.entity_service import EntityService


class Test3PGFinanceWorkflowIntegration:
    """Test complete 3PG Finance workflow through all refactored layers"""

    def test_3pg_finance_complete_lifecycle(self, db_session, seeded_test_data):
        """Test complete 3PG Finance lifecycle with all events and validations"""
        # Setup factories with session
        from tests.factories import FundFactory, EntityFactory, InvestmentCompanyFactory
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Initialize services
        fund_service = FundService()
        fund_event_service = FundEventService()
        fund_tax_statement_service = FundTaxStatementService()
        company_service = CompanyService()
        entity_service = EntityService()
        
        # 1. Create investment company (Alceon)
        company_data = {
            'name': 'Alceon',
            'description': 'Alceon Pty Ltd'
        }
        company = company_service.create_company(company_data, db_session)
        db_session.commit()
        
        # 2. Create entity (Shaun Reichman)
        from src.shared.enums.shared_enums import Country
        entity_data = {
            'name': 'Shaun Reichman',
            'description': 'Personal entity',
            'entity_type': 'PERSON',
            'tax_jurisdiction': Country.AU
        }
        entity = entity_service.create_entity(entity_data, db_session)
        db_session.commit()
        
        # 3. Create 3PG Finance fund
        fund_data = {
            'investment_company_id': company.id,
            'entity_id': entity.id,
            'name': '3PG Finance',
            'fund_investment_type': 'PRIVATE_DEBT',
            'tracking_type': FundTrackingType.COST_BASED,
            'commitment_amount': 100000.0,
            'expected_irr': 10.0,
            'expected_duration_months': 48,
            'currency': 'AUD',
            'description': '3PG Finance debt fund',
            'tax_jurisdiction': Country.AU
        }
        fund = fund_service.create_fund(fund_data, db_session)
        db_session.commit()
        
        # Verify initial fund state
        assert fund.name == '3PG Finance'
        assert fund.tracking_type == FundTrackingType.COST_BASED
        assert fund.commitment_amount == 100000.0
        assert fund.status == FundStatus.ACTIVE
        assert fund.current_equity_balance == 0.0
        
        # 4. Add capital call event
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2022, 11, 24),
            'amount': 100000.0,
            'description': 'Initial capital call',
            'fund_id': fund.id
        }
        capital_call_event = fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Verify fund state after capital call (equity should be updated automatically)
        db_session.refresh(fund)
        assert fund.current_equity_balance == 100000.0
        assert fund.status == FundStatus.ACTIVE
        
        # 5. Add return of capital events
        return_events_data = [
            {
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': date(2023, 3, 24),
                'amount': 7324.42,
                'description': 'Return of capital',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': date(2023, 7, 7),
                'amount': 26326.88,
                'description': 'Partial exit distribution',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': date(2023, 8, 4),
                'amount': 8527.53,
                'description': 'Return of capital',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': date(2023, 9, 22),
                'amount': 8805.21,
                'description': 'Return of capital',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': date(2023, 10, 13),
                'amount': 9814.74,
                'description': 'Return of capital',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': date(2023, 11, 21),
                'amount': 6967.81,
                'description': 'Return of capital',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': date(2024, 4, 19),
                'amount': 32233.41,
                'description': 'Final return of capital',
                'fund_id': fund.id
            }
        ]
        
        for return_data in return_events_data:
            fund_event_service.create_fund_event(fund.id, return_data, db_session)
            db_session.commit()
            db_session.refresh(fund)
        
        # Verify fund state after all returns
        assert fund.current_equity_balance == 0.0  # All capital returned
        assert fund.status == FundStatus.REALIZED  # Should be realized after equity reaches zero
        
        # 6. Add distribution events with tax
        distribution_events_data = [
            {
                'event_type': EventType.DISTRIBUTION,
                'event_date': date(2023, 3, 24),
                'distribution_type': DistributionType.INTEREST,
                'amount': 3075.58,  # No tax for first distribution
                'has_withholding_tax': False,
                'description': 'Interest distribution',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.DISTRIBUTION,
                'event_date': date(2023, 7, 7),
                'distribution_type': DistributionType.INTEREST,
                'gross_interest_amount': 4472.36,
                'withholding_tax_rate': 10.0,
                'has_withholding_tax': True,
                'description': 'Interest distribution',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.DISTRIBUTION,
                'event_date': date(2023, 8, 4),
                'distribution_type': DistributionType.INTEREST,
                'gross_interest_amount': 871.63,
                'withholding_tax_rate': 10.0,
                'has_withholding_tax': True,
                'description': 'Interest distribution',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.DISTRIBUTION,
                'event_date': date(2023, 9, 22),
                'distribution_type': DistributionType.INTEREST,
                'gross_interest_amount': 794.21,
                'withholding_tax_amount': 79.42,
                'has_withholding_tax': True,
                'description': 'Interest distribution',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.DISTRIBUTION,
                'event_date': date(2023, 10, 13),
                'distribution_type': DistributionType.INTEREST,
                'gross_interest_amount': 684.73,
                'withholding_tax_rate': 10.0,
                'has_withholding_tax': True,
                'description': 'Interest distribution',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.DISTRIBUTION,
                'event_date': date(2023, 11, 21),
                'distribution_type': DistributionType.INTEREST,
                'gross_interest_amount': 531.32,
                'withholding_tax_amount': 53.13,
                'has_withholding_tax': True,
                'description': 'Interest distribution',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.DISTRIBUTION,
                'event_date': date(2024, 4, 19),
                'distribution_type': DistributionType.INTEREST,
                'gross_interest_amount': 4399.27,
                'withholding_tax_rate': 10.0,
                'has_withholding_tax': True,
                'description': 'Interest distribution',
                'fund_id': fund.id
            }
        ]
        
        for distribution_data in distribution_events_data:
            fund_event_service.create_fund_event(fund.id, distribution_data, db_session)
            db_session.commit()
            db_session.refresh(fund)
        
        # 7. Add tax statements
        tax_statement_data_2022_23 = {
            'entity_id': entity.id,
            'financial_year': '2023',
            'notes': 'FY23 tax statement from fund manager',
            'interest_received_in_cash': 3075.58,
            'accountant': 'Findex',
            'statement_date': date(2024, 8, 24),
            'interest_income_tax_rate': 10.0,
            'eofy_debt_interest_deduction_rate': 32.5
        }
        
        tax_statement_2022_23 = fund_tax_statement_service.create_fund_tax_statement(
            fund.id, tax_statement_data_2022_23, db_session
        )
        db_session.commit()

        tax_statement_data_2023_24 = {
            'entity_id': entity.id,
            'financial_year': '2024',
            'notes': 'FY24 tax statement from fund manager',
            'interest_non_resident_withholding_tax_from_statement': 1076.4,
            'accountant': 'Findex',
            'statement_date': date(2024, 8, 12),
            'interest_income_tax_rate': 10.0,
            'eofy_debt_interest_deduction_rate': 32.5
        }
        
        tax_statement_2023_24 = fund_tax_statement_service.create_fund_tax_statement(
            fund.id, tax_statement_data_2023_24, db_session
        )
        db_session.commit()
        
        # 8. Final refresh to get updated state
        db_session.refresh(fund)
        
        # 9. Validate final fund state against expected results
        assert fund.current_equity_balance == 0.0
        assert fund.status == FundStatus.COMPLETED  # Should be completed after final tax statement
        assert fund.end_date == date(2024, 4, 19)  # Last return of capital date
        
        # Validate average equity (should be approximately $66,045.18)
        assert abs(fund.average_equity_balance - 66045.18) < 1.0  # Within $1 tolerance
        
        # 10. Validate event counts
        all_events = fund_event_service.get_fund_events(
            session=db_session,
            fund_ids=[fund.id]
        )
        
        capital_call_events = [e for e in all_events if e.event_type == EventType.CAPITAL_CALL]
        return_events = [e for e in all_events if e.event_type == EventType.RETURN_OF_CAPITAL]
        distribution_events = [e for e in all_events if e.event_type == EventType.DISTRIBUTION]
        tax_payment_events = [e for e in all_events if e.event_type == EventType.TAX_PAYMENT]
        daily_interest_events = [e for e in all_events if e.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE]

        assert len(capital_call_events) == 1
        assert len(return_events) == 7
        assert len(distribution_events) == 7
        assert len(tax_payment_events) == 7  # Only withholding tax events should be created for private debt funds
        assert len(daily_interest_events) == 512  # Daily interest charges created by tax statement
        
        # 11. Validate IRR calculation (should be calculated automatically by the fund)
        # Note: IRR calculation happens automatically through the fund's calculated fields
        # We can validate the fund's IRR fields if they exist
        assert abs(fund.completed_irr_gross - 0.1654) < 0.001  # Within 0.1% tolerance
        assert abs(fund.completed_irr_after_tax - 0.1486) < 0.001  # Within 0.1% tolerance
        assert abs(fund.completed_irr_real - 0.1205) < 0.001  # Within 0.1% tolerance
        
        # 12. Validate tax statements
        tax_statements = fund_tax_statement_service.get_fund_tax_statements(
            session=db_session,
            fund_id=fund.id
        )
        assert len(tax_statements) == 2
        
        # Validate specific tax statement data
        fy_2022_23 = next((ts for ts in tax_statements if ts.financial_year == '2023'), None)
        fy_2023_24 = next((ts for ts in tax_statements if ts.financial_year == '2024'), None)
        
        assert fy_2022_23 is not None
        assert fy_2022_23.interest_received_in_cash == 3075.58
        assert fy_2022_23.accountant == 'Findex'
        assert fy_2022_23.interest_income_tax_rate == 10.0
        assert fy_2022_23.eofy_debt_interest_deduction_rate == 32.5
        
        assert fy_2023_24 is not None
        assert fy_2023_24.interest_non_resident_withholding_tax_from_statement == 1076.4
        
        print(f"\n=== 3PG Finance Validation Results ===")
        print(f"Current Equity: ${fund.current_equity_balance:,.2f}")
        print(f"Average Equity: ${fund.average_equity_balance:,.2f}")
        print(f"Status: {fund.status}")
        print(f"End Date: {fund.end_date}")
        print(f"Gross IRR: {fund.completed_irr_gross * 100:.2f}%")
        print(f"After-Tax IRR: {fund.completed_irr_after_tax * 100:.2f}%")
        print(f"Real IRR: {fund.completed_irr_real * 100:.2f}%" if fund.completed_irr_real else "Real IRR: Not calculated")
        print(f"Events: {len(capital_call_events)} capital calls, {len(return_events)} returns, {len(distribution_events)} distributions, {len(tax_payment_events)} tax payments, {len(daily_interest_events)} daily interest charges")
        print(f"Tax Statements: {len(tax_statements)}")
