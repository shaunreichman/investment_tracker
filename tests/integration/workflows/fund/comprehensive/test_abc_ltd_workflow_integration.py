"""
Integration tests for ABC Ltd comprehensive workflow.

This test recreates the complete ABC Ltd scenario from the old test,
validating that the refactored backend produces the same results as the original system.

Test Scenario:
- NAV-based Equity fund
- Unit purchases, unit sales, NAV updates, and distributions
- Tax statements for capital gains
- IRR calculations and fund status transitions
- Complete lifecycle from ACTIVE to COMPLETED

Expected Results (from old test):
- Current equity: $0.00
- Average equity: $3,746.21
- Status: COMPLETED
- IRR: 11.43% (gross), 8.63% (after-tax), 6.73% (real)
- Events: 2 unit purchases, 2 unit sales, 14 NAV updates, 1 distribution, 411 daily interest charges
- Capital gain for 2013-14: 397.50 (discount: 196.35, tax: 119.25)
"""

import pytest
from datetime import date
from decimal import Decimal

from src.fund.enums import FundTrackingType, FundStatus, EventType, DistributionType, FundInvestmentType
from src.fund.services.fund_service import FundService
from src.fund.services.fund_event_service import FundEventService
from src.fund.services.fund_tax_statement_service import FundTaxStatementService
from src.fund.services.fund_equity_service import FundEquityService
from src.fund.services.fund_status_service import FundStatusService
from src.fund.services.fund_irr_service import FundIrRService
from src.investment_company.services.company_service import CompanyService
from src.entity.services.entity_service import EntityService
from src.shared.enums.shared_enums import Country


class TestABCLtdWorkflowIntegration:
    """Test complete ABC Ltd workflow through all refactored layers"""

    def test_abc_ltd_complete_lifecycle(self, db_session, seeded_test_data):
        """Test complete ABC Ltd lifecycle with all events and validations"""
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
        
        # 1. Create investment company (Shares)
        company_data = {
            'name': 'Shares',
            'description': 'Share trading'
        }
        company = company_service.create_company(company_data, db_session)
        db_session.commit()
        
        # 2. Create entity (Shaun Reichman)
        entity_data = {
            'name': 'Shaun Reichman',
            'description': 'Personal entity',
            'entity_type': 'PERSON',
            'tax_jurisdiction': Country.AU
        }
        entity = entity_service.create_entity(entity_data, db_session)
        db_session.commit()
        
        # 3. Create ABC Ltd fund
        fund_data = {
            'investment_company_id': company.id,
            'entity_id': entity.id,
            'name': 'ABC Ltd',
            'fund_investment_type': FundInvestmentType.OTHER,  # Using OTHER since EQUITY is not in the enum
            'tracking_type': FundTrackingType.NAV_BASED,
            'currency': 'AUD',
            'description': 'ABC Ltd on the ASX',
            'tax_jurisdiction': Country.AU,
            'commitment_amount': 0.0  # NAV-based funds don't have commitment amounts
        }
        fund = fund_service.create_fund(fund_data, db_session)
        db_session.commit()
        
        # Verify initial fund state
        assert fund.name == 'ABC Ltd'
        assert fund.tracking_type == FundTrackingType.NAV_BASED
        assert fund.status == FundStatus.ACTIVE
        assert fund.current_equity_balance == 0.0
        assert fund.current_units == 0.0
        
        # 4. Add initial unit purchase
        unit_purchase_1_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2013, 3, 28),
            'units_purchased': 85.0,
            'unit_price': 58.00,
            'brokerage_fee': 19.95,
            'description': 'Initial unit purchase',
            'fund_id': fund.id
        }
        unit_purchase_1_event = fund_event_service.create_fund_event(fund.id, unit_purchase_1_data, db_session)
        db_session.commit()
        
        # Verify fund state after unit purchase (equity should be updated automatically)
        db_session.refresh(fund)
        assert fund.current_units == 85.0
        assert fund.current_unit_price == 58.00
        assert fund.current_equity_balance == 4930.0  # (85 * 58.00) - equity balance excludes brokerage fees
        assert fund.average_equity_balance > 0.0
        assert fund.status == FundStatus.ACTIVE
        
        # 5. Add NAV updates
        nav_updates_data = [
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2013, 3, 31),
                'nav_per_share': 57.20,
                'description': 'March 2013 NAV update',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2013, 4, 30),
                'nav_per_share': 55.80,
                'description': 'April 2013 NAV update',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2013, 5, 31),
                'nav_per_share': 55.18,
                'description': 'May 2013 NAV update',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2013, 6, 30),
                'nav_per_share': 52.37,
                'description': 'June 2013 NAV update',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2013, 7, 31),
                'nav_per_share': 57.51,
                'description': 'July 2013 NAV update',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2013, 8, 31),
                'nav_per_share': 58.30,
                'description': 'August 2013 NAV update',
                'fund_id': fund.id
            }
        ]
        
        for nav_data in nav_updates_data:
            fund_event_service.create_fund_event(fund.id, nav_data, db_session)
            db_session.commit()
            db_session.refresh(fund)
        
        # 6. Add partial unit sale
        unit_sale_1_data = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2013, 9, 4),
            'units_sold': 40.0,
            'unit_price': 61.20,
            'brokerage_fee': 24.95,
            'description': 'Partial unit sale',
            'fund_id': fund.id
        }
        unit_sale_1_event = fund_event_service.create_fund_event(fund.id, unit_sale_1_data, db_session)
        db_session.commit()
        db_session.refresh(fund)
        
        # Verify fund state after partial sale
        assert fund.current_units == 45.0  # 85 - 40
        assert fund.average_equity_balance > 0.0

        # 7. Add distribution
        distribution_data = {
            'event_type': EventType.DISTRIBUTION,
            'event_date': date(2013, 9, 12),
            'distribution_type': DistributionType.DIVIDEND_FRANKED,
            'amount': 79.05,
            'has_withholding_tax': False,
            'description': 'Fully Franked Dividend',
            'fund_id': fund.id
        }
        distribution_event = fund_event_service.create_fund_event(fund.id, distribution_data, db_session)
        db_session.commit()
        db_session.refresh(fund)
        
        # 8. Add more NAV updates
        more_nav_updates_data = [
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2013, 9, 30),
                'nav_per_share': 59.30,
                'description': 'September 2013 NAV update',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2013, 10, 31),
                'nav_per_share': 53.30,
                'description': 'October 2013 NAV update',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2013, 11, 30),
                'nav_per_share': 54.30,
                'description': 'November 2013 NAV update',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2013, 12, 31),
                'nav_per_share': 48.30,
                'description': 'December 2013 NAV update',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2014, 1, 31),
                'nav_per_share': 59.30,
                'description': 'January 2014 NAV update',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2014, 2, 28),
                'nav_per_share': 54.30,
                'description': 'February 2014 NAV update',
                'fund_id': fund.id
            },
            {
                'event_type': EventType.NAV_UPDATE,
                'event_date': date(2014, 3, 31),
                'nav_per_share': 56.30,
                'description': 'March 2014 NAV update',
                'fund_id': fund.id
            }
        ]
        
        for nav_data in more_nav_updates_data:
            fund_event_service.create_fund_event(fund.id, nav_data, db_session)
            db_session.commit()
            db_session.refresh(fund)
        
        # 9. Add additional unit purchase
        unit_purchase_2_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2014, 4, 30),
            'units_purchased': 120.0,
            'unit_price': 61.4,
            'brokerage_fee': 19.95,
            'description': 'Additional unit purchase',
            'fund_id': fund.id
        }
        unit_purchase_2_event = fund_event_service.create_fund_event(fund.id, unit_purchase_2_data, db_session)
        db_session.commit()
        db_session.refresh(fund)
        
        # Verify fund state after additional purchase
        assert fund.current_units == 165.0  # 45 + 120
        
        # 10. Add NAV update on same date as purchase
        nav_update_same_date_data = {
            'event_type': EventType.NAV_UPDATE,
            'event_date': date(2014, 4, 30),
            'nav_per_share': 61.25,
            'description': 'April 2014 NAV update',
            'fund_id': fund.id
        }
        nav_update_same_date_event = fund_event_service.create_fund_event(fund.id, nav_update_same_date_data, db_session)
        db_session.commit()
        db_session.refresh(fund)
        
        # 11. Add final unit sale
        unit_sale_2_data = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2014, 5, 13),
            'units_sold': 165.0,
            'unit_price': 62.62,
            'brokerage_fee': 19.95,
            'description': 'Full unit sale',
            'fund_id': fund.id
        }
        unit_sale_2_event = fund_event_service.create_fund_event(fund.id, unit_sale_2_data, db_session)
        db_session.commit()
        db_session.refresh(fund)
        
        # Verify fund state after final sale
        assert fund.current_units == 0.0
        assert fund.current_unit_price == 62.62
        assert fund.current_equity_balance == 0.0
        assert fund.status == FundStatus.REALIZED
        
        # 12. Add tax statements
        tax_statement_data_2012_13 = {
            'entity_id': entity.id,
            'financial_year': '2013',  # Financial year ending 2013 (2012-13)
            'notes': 'FY13 tax statement from fund manager',
            'accountant': 'Findex',
            'statement_date': date(2013, 8, 22),
            'eofy_debt_interest_deduction_rate': 32.5
        }
        
        tax_statement_2012_13 = fund_tax_statement_service.create_fund_tax_statement(
            fund.id, tax_statement_data_2012_13, db_session
        )
        db_session.commit()
        
        tax_statement_data_2013_14 = {
            'entity_id': entity.id,
            'financial_year': '2014',  # Financial year ending 2014 (2013-14)
            'notes': 'FY14 tax statement from fund manager',
            'accountant': 'Findex',
            'statement_date': date(2014, 8, 12),
            'capital_gain_income_tax_rate': 30,
            'eofy_debt_interest_deduction_rate': 32.5,
            'capital_gain_discount_applicable_flag': False # We can toggle this to see capital gains with or without discount works
        }
        
        tax_statement_2013_14 = fund_tax_statement_service.create_fund_tax_statement(
            fund.id, tax_statement_data_2013_14, db_session
        )
        db_session.commit()
        
        # 13. Final refresh to get updated state
        db_session.refresh(fund)
        
        # 14. Validate final fund state against expected results
        assert fund.current_equity_balance == 0.0
        assert fund.status == FundStatus.COMPLETED  # Should be completed after final tax statement
        assert fund.end_date == date(2014, 5, 13)  # Last unit sale date
        
        # Validate average equity (should be approximately $3,746.21)
        assert abs(fund.average_equity_balance - 3746.21) < 1.0  # Within $1 tolerance
        
        # 15. Validate event counts
        all_events = fund_event_service.get_fund_events(
            session=db_session,
            fund_ids=[fund.id]
        )
        
        unit_purchase_events = [e for e in all_events if e.event_type == EventType.UNIT_PURCHASE]
        unit_sale_events = [e for e in all_events if e.event_type == EventType.UNIT_SALE]
        nav_update_events = [e for e in all_events if e.event_type == EventType.NAV_UPDATE]
        distribution_events = [e for e in all_events if e.event_type == EventType.DISTRIBUTION]
        daily_interest_events = [e for e in all_events if e.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE]
        
        # DEBUG: Print detailed event analysis
        print(f"\n=== EVENT ANALYSIS ===")
        print(f"Total events: {len(all_events)}")
        print(f"Unit purchases: {len(unit_purchase_events)}")
        print(f"Unit sales: {len(unit_sale_events)}")
        print(f"NAV updates: {len(nav_update_events)}")
        print(f"Distributions: {len(distribution_events)}")
        print(f"Daily interest events: {len(daily_interest_events)}")
        
        # DEBUG: Print equity balances for all events
        print(f"\n=== EQUITY BALANCE ANALYSIS ===")
        for i, event in enumerate(all_events):
            print(f"Event {i+1}: {event.event_date} | {event.event_type} | Equity: {event.current_equity_balance} | Units: {event.units_owned}")
        
        # DEBUG: Print daily interest events details
        if daily_interest_events:
            print(f"\n=== DAILY INTEREST EVENTS DETAILS ===")
            sample_events = sorted(daily_interest_events, key=lambda x: x.event_date)[:10]
            for event in sample_events:
                print(f"  {event.event_date} | Amount: {event.amount:.6f} | Equity: {event.dc_current_equity_balance:.2f} | Rate: {event.dc_risk_free_rate:.2f}%")
            if len(daily_interest_events) > 10:
                print(f"  ... and {len(daily_interest_events) - 10} more events")
            
            min_date = min(e.event_date for e in daily_interest_events)
            max_date = max(e.event_date for e in daily_interest_events)
            print(f"Date range: {min_date} to {max_date}")
        
        assert len(unit_purchase_events) == 2
        assert len(unit_sale_events) == 2
        assert len(nav_update_events) == 14
        assert len(distribution_events) == 1
        assert len(daily_interest_events) == 411  # Daily interest charges created by tax statement (was 411, now 412 due to improved boundary handling)
        
        # 16. Validate IRR calculation (should be calculated automatically by the fund)
        # Note: IRR calculation happens automatically through the fund's calculated fields
        # We can validate the fund's IRR fields if they exist
        
        if tax_statement_2013_14.capital_gain_discount_applicable_flag:
            assert abs(fund.completed_irr_gross - 0.1143) < 0.0001  # Within 0.1% tolerance
            assert abs(fund.completed_irr_after_tax - 0.0931) < 0.0001  # Within 0.1% tolerance
            assert abs(fund.completed_irr_real - 0.0740) < 0.0001  # Within 0.1% tolerance
        else:
            assert abs(fund.completed_irr_gross - 0.1143) < 0.0001  # Within 0.1% tolerance
            assert abs(fund.completed_irr_after_tax - 0.0863) < 0.0001  # Within 0.1% tolerance
            assert abs(fund.completed_irr_real - 0.0673) < 0.0001  # Within 0.1% tolerance
        
        # 17. Validate tax statements
        tax_statements = fund_tax_statement_service.get_fund_tax_statements(
            session=db_session,
            fund_id=fund.id
        )
        assert len(tax_statements) == 2
        
        # Validate specific tax statement data
        fy_2012_13 = next((ts for ts in tax_statements if ts.financial_year == '2013'), None)
        fy_2013_14 = next((ts for ts in tax_statements if ts.financial_year == '2014'), None)
        
        assert fy_2012_13 is not None
        assert fy_2012_13.accountant == 'Findex'
        assert fy_2012_13.eofy_debt_interest_deduction_rate == 32.5
        
        assert fy_2013_14 is not None
        assert fy_2013_14.capital_gain_income_tax_rate == 30
        assert fy_2013_14.eofy_debt_interest_deduction_rate == 32.5
        
        # 18. Validate capital gains calculation (from old test)
        # Capital gain for 2013-14: 397.50 total, 191.90 discountable, 301.55 taxable, tax: 90.47
        # This would be calculated by the tax statement service
        assert abs(fy_2013_14.capital_gain_income_amount - 397.50) < 0.01  # Within 1 cent tolerance
        if fy_2013_14.capital_gain_discount_applicable_flag:
            assert abs(fy_2013_14.capital_gain_discount_amount - 191.90) < 0.01  # Within 1 cent tolerance
            assert abs(fy_2013_14.capital_gain_tax_amount - 90.47) < 0.01  # Within 1 cent tolerance (tax on taxable amount)
        else:
            assert abs(fy_2013_14.capital_gain_discount_amount - 0.00) < 0.01  # Within 1 cent tolerance
            assert abs(fy_2013_14.capital_gain_tax_amount - 119.25) < 0.01  # Within 1 cent tolerance (tax on taxable amount)
        
        print(f"\n=== ABC Ltd Validation Results ===")
        print(f"Current Equity: ${fund.current_equity_balance:,.2f}")
        print(f"Average Equity: ${fund.average_equity_balance:,.2f}")
        print(f"Status: {fund.status}")
        print(f"End Date: {fund.end_date}")
        print(f"Current Units: {fund.current_units}")
        print(f"Current Unit Price: ${fund.current_unit_price:.4f}")
        print(f"Gross IRR: {fund.completed_irr_gross:.2f}%")
        print(f"After-Tax IRR: {fund.completed_irr_after_tax:.2f}%")
        print(f"Real IRR: {fund.completed_irr_real:.2f}%")
        print(f"Events: {len(unit_purchase_events)} unit purchases, {len(unit_sale_events)} unit sales, {len(nav_update_events)} NAV updates, {len(distribution_events)} distributions, {len(daily_interest_events)} daily interest charges")
        print(f"Tax Statements: {len(tax_statements)}")
        print(f"Capital Gain 2013-14: ${fy_2013_14.capital_gain_income_amount:.2f} (discount: ${fy_2013_14.capital_gain_discount_amount:.2f}, tax: ${fy_2013_14.capital_gain_tax_amount:.2f})")
