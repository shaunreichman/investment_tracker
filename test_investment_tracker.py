#!/usr/bin/env python3
"""
Comprehensive test file for the investment tracker.
This file consolidates all testing inputs into a single Python file.
"""

import sys
import os
from datetime import datetime, date

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    Base, InvestmentCompany, Entity, Fund, FundEvent, 
    TaxStatement, EventType, DistributionType, FundType
)


def create_event_without_tax(date, event_type, amount, description, distribution_type=None):
    """Helper function to create an event with no tax withholding (default scenario)."""
    return (date, event_type, amount, description, distribution_type, None)


def create_event_with_tax_rate(date, event_type, amount, description, distribution_type, tax_rate):
    """Helper function to create an event with tax withholding rate."""
    return (date, event_type, amount, description, distribution_type, ('rate', tax_rate))


def create_event_with_tax_amount(date, event_type, amount, description, distribution_type, tax_amount):
    """Helper function to create an event with tax withheld amount."""
    return (date, event_type, amount, description, distribution_type, ('amount', tax_amount))


def setup_database():
    """Create database and tables."""
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Base.metadata.create_all(engine)
    return engine


def create_or_get_entity(session, name, description=None, tax_jurisdiction="AU"):
    """Create or get an entity."""
    entity = session.query(Entity).filter(Entity.name == name).first()
    if not entity:
        entity = Entity(
            name=name,
            description=description or f"Entity: {name}",
            tax_jurisdiction=tax_jurisdiction
        )
        session.add(entity)
        session.commit()
        print(f"Created entity: {name}")
    else:
        print(f"Using existing entity: {name}")
    return entity


def create_or_get_investment_company(session, name, description=None, website=None, contact_email=None):
    """Create or get an investment company."""
    company = session.query(InvestmentCompany).filter(InvestmentCompany.name == name).first()
    if not company:
        company = InvestmentCompany(
            name=name,
            description=description or f"Investment company: {name}",
            website=website,
            contact_email=contact_email
        )
        session.add(company)
        session.commit()
        print(f"Created investment company: {name}")
    else:
        print(f"Using existing investment company: {name}")
    return company


def create_or_get_fund(session, company, entity, fund_data):
    """Create or get a fund."""
    fund = session.query(Fund).filter(
        Fund.name == fund_data['name'],
        Fund.investment_company_id == company.id,
        Fund.entity_id == entity.id
    ).first()
    
    if not fund:
        fund = Fund(
            investment_company_id=company.id,
            entity_id=entity.id,
            name=fund_data['name'],
            fund_type=fund_data.get('fund_type', 'Private Debt'),
            vintage_year=fund_data.get('vintage_year'),
            tracking_type=fund_data.get('tracking_type', FundType.COST_BASED),
            commitment_amount=fund_data['commitment_amount'],
            current_equity_balance=fund_data.get('current_equity_balance', 0.0),
            expected_irr=fund_data.get('expected_irr'),
            expected_duration_months=fund_data.get('expected_duration_months'),
            currency=fund_data.get('currency', 'AUD'),
            description=fund_data.get('description', f"Fund: {fund_data['name']}")
        )
        session.add(fund)
        session.commit()
        print(f"Created fund: {fund_data['name']}")
    else:
        print(f"Using existing fund: {fund_data['name']}")
    return fund


def add_fund_event(session, fund, event_data):
    """Add a fund event."""
    event = FundEvent(
        fund_id=fund.id,
        event_type=event_data['event_type'],
        event_date=event_data['event_date'],
        amount=event_data['amount'],
        description=event_data.get('description', ''),
        distribution_type=event_data.get('distribution_type'),
        tax_withheld=event_data.get('tax_withheld', 0.0),
        tax_withholding_rate=event_data.get('tax_withholding_rate', 0.0)
    )
    session.add(event)
    session.commit()
    print(f"Added {event_data['event_type']}: ${event_data['amount']:,.0f} on {event_data['event_date']}")


def add_fund_events_with_tax_handling(session, fund, events_data):
    """Add fund events with proper tax withholding handling."""
    all_events = []
    
    for event_tuple in events_data:
        if len(event_tuple) == 6:  # Has tax info
            event_date, event_type, amount, description, distribution_type, tax_info = event_tuple
            
            # Check if event already exists on the same date and type (replace if amount is different)
            existing_event = session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id,
                FundEvent.event_type == event_type,
                FundEvent.event_date == event_date,
                FundEvent.distribution_type == distribution_type
            ).first()
            
            if existing_event:
                if abs(existing_event.amount - amount) < 0.01:  # Amount is the same (within rounding)
                    print(f"Using existing {event_type}: ${amount:,.0f} on {event_date}")
                    continue
                else:
                    # Amount is different, replace the existing event
                    print(f"Replacing {event_type} on {event_date}: ${existing_event.amount:,.0f} → ${amount:,.0f}")
                    session.delete(existing_event)
                    session.commit()
            
            event = FundEvent(
                fund_id=fund.id,
                event_type=event_type,
                event_date=event_date,
                amount=amount,
                description=description,
                distribution_type=distribution_type
            )
            
            # Handle tax information
            if tax_info:
                tax_type, tax_value = tax_info
                if tax_type == 'rate':
                    event.tax_withholding_rate = tax_value
                    event.tax_withheld = event.calculate_tax_from_rate()
                elif tax_type == 'amount':
                    event.tax_withheld = tax_value
                    event.tax_withholding_rate = event.calculate_rate_from_tax()
            else:
                event.tax_withheld = 0.0
                event.tax_withholding_rate = 0.0
            
            all_events.append(event)
            print(f"Added {event_type}: ${amount:,.0f} on {event_date}")
            
        else:  # No tax info (capital events)
            event_date, event_type, amount, description = event_tuple
            
            # Check if event already exists on the same date and type (replace if amount is different)
            existing_event = session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id,
                FundEvent.event_type == event_type,
                FundEvent.event_date == event_date
            ).first()
            
            if existing_event:
                if abs(existing_event.amount - amount) < 0.01:  # Amount is the same (within rounding)
                    print(f"Using existing {event_type}: ${amount:,.0f} on {event_date}")
                    continue
                else:
                    # Amount is different, replace the existing event
                    print(f"Replacing {event_type} on {event_date}: ${existing_event.amount:,.0f} → ${amount:,.0f}")
                    session.delete(existing_event)
                    session.commit()
            
            event = FundEvent(
                fund_id=fund.id,
                event_type=event_type,
                event_date=event_date,
                amount=amount,
                description=description
            )
            all_events.append(event)
            print(f"Added {event_type}: ${amount:,.0f} on {event_date}")
    
    if all_events:
        session.add_all(all_events)
        session.commit()
        # Always update the stored average equity balance after event changes
        fund.update_average_equity_balance(session)


def add_tax_statement(session, fund, entity, tax_data):
    """Add a tax statement."""
    # Check if tax statement already exists
    existing_statement = session.query(TaxStatement).filter(
        TaxStatement.fund_id == fund.id,
        TaxStatement.entity_id == entity.id,
        TaxStatement.financial_year == tax_data['financial_year']
    ).first()
    
    if existing_statement:
        print(f"Using existing tax statement for {fund.name}, {entity.name}, FY {tax_data['financial_year']}")
        return existing_statement
    
    # Calculate net interest income
    net_interest_income = tax_data['gross_interest_income'] - tax_data['tax_withheld']
    
    statement = TaxStatement(
        fund_id=fund.id,
        entity_id=entity.id,
        financial_year=tax_data['financial_year'],
        gross_interest_income=tax_data['gross_interest_income'],
        net_interest_income=net_interest_income,
        tax_withheld=tax_data['tax_withheld'],
        foreign_income=tax_data.get('foreign_income', 0.0),
        capital_gains=tax_data.get('capital_gains', 0.0),
        other_income=tax_data.get('other_income', 0.0),
        foreign_tax_credits=tax_data.get('foreign_tax_credits', 0.0),
        non_resident=tax_data.get('non_resident', False),
        accountant=tax_data.get('accountant'),
        statement_date=tax_data.get('statement_date'),
        notes=tax_data.get('notes', '')
    )
    
    # Calculate total income
    statement.calculate_total_income()
    
    session.add(statement)
    session.commit()
    print(f"Added tax statement for {fund.name}, {entity.name}, FY {tax_data['financial_year']}")
    return statement


def run_comprehensive_test():
    """Run the comprehensive test with all fund data."""
    
    print("COMPREHENSIVE INVESTMENT TRACKER TEST")
    print("=" * 50)
    
    # Setup database
    engine = setup_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # ============================================================================
        # ENTITIES
        # ============================================================================
        print("\n1. SETTING UP ENTITIES")
        print("-" * 30)
        
        shaun = create_or_get_entity(
            session, 
            "Shaun Reichman", 
            "Individual investor",
            "AU"
        )
        
        # ============================================================================
        # INVESTMENT COMPANIES
        # ============================================================================
        print("\n2. SETTING UP INVESTMENT COMPANIES")
        print("-" * 30)
        
        alceon = create_or_get_investment_company(
            session,
            "Alceon",
            "Australian private debt investment manager",
            "https://www.alceon.com.au",
            "investor.relations@alceon.com.au"
        )
        
        # ============================================================================
        # FUNDS
        # ============================================================================
        print("\n3. SETTING UP FUNDS")
        print("-" * 30)
        
        # Senior Debt Fund No.24
        senior_debt_fund_data = {
            'name': 'Senior Debt Fund No.24',
            'fund_type': 'Private Debt',
            'vintage_year': 2023,
            'tracking_type': FundType.COST_BASED,
            'commitment_amount': 100000.0,
            'currency': 'AUD',
            'description': 'Senior debt fund with quarterly distributions'
        }
        
        senior_debt_fund = create_or_get_fund(session, alceon, shaun, senior_debt_fund_data)
        
        # 3PG Finance
        three_pg_fund_data = {
            'name': '3PG Finance',
            'fund_type': 'Private Debt',
            'vintage_year': 2022,
            'tracking_type': FundType.COST_BASED,
            'commitment_amount': 100000.0,
            'currency': 'AUD',
            'description': '3PG Finance debt fund'
        }
        
        three_pg_fund = create_or_get_fund(session, alceon, shaun, three_pg_fund_data)
        
        # ============================================================================
        # FUND EVENTS - Senior Debt Fund No.24
        # ============================================================================
        print("\n4. ADDING FUND EVENTS - Senior Debt Fund No.24")
        print("-" * 30)
        
        # Capital events (no tax withholding)
        senior_debt_capital_events = [
            (date(2023, 6, 23), EventType.CAPITAL_CALL, 100000.0, "Initial capital call"),
            (date(2023, 12, 8), EventType.RETURN_OF_CAPITAL, 7000.0, "Return of capital"),
            (date(2024, 3, 26), EventType.RETURN_OF_CAPITAL, 45000.0, "Partial exit distribution"),
            (date(2024, 8, 2), EventType.RETURN_OF_CAPITAL, 48000.0, "Final return of capital"),
        ]
        
        # Distribution events (with tax withholding using helper functions)
        senior_debt_distribution_events = [
            # With tax withholding rate
            create_event_with_tax_rate(
                date(2023, 10, 20), EventType.DISTRIBUTION, 3030.62, 
                "Interest distribution", DistributionType.INTEREST, 10.0
            ),
            create_event_with_tax_rate(
                date(2024, 1, 16), EventType.DISTRIBUTION, 2836.98, 
                "Interest distribution", DistributionType.INTEREST, 10.0
            ),
            create_event_with_tax_rate(
                date(2024, 3, 26), EventType.DISTRIBUTION, 2630.16, 
                "Interest distribution", DistributionType.INTEREST, 10.0
            ),
            create_event_with_tax_rate(
                date(2024, 7, 9), EventType.DISTRIBUTION, 1392.19, 
                "Interest distribution", DistributionType.INTEREST, 10.0
            ),
            create_event_with_tax_rate(
                date(2024, 8, 2), EventType.DISTRIBUTION, 509.84, 
                "Interest distribution", DistributionType.INTEREST, 10.0
            ),
        ]
        
        # Combine all events
        senior_debt_all_events = senior_debt_capital_events + senior_debt_distribution_events
        add_fund_events_with_tax_handling(session, senior_debt_fund, senior_debt_all_events)
        
        # ============================================================================
        # FUND EVENTS - 3PG Finance
        # ============================================================================
        print("\n5. ADDING FUND EVENTS - 3PG Finance")
        print("-" * 30)
        
        # Capital events (no tax withholding)
        three_pg_capital_events = [
            (date(2022, 11, 24), EventType.CAPITAL_CALL, 100000.0, "Initial capital call"),
            (date(2023, 3, 24), EventType.RETURN_OF_CAPITAL, 7324.0, "Return of capital"),
            (date(2023, 7, 7), EventType.RETURN_OF_CAPITAL, 26327.0, "Partial exit distribution"),
            (date(2023, 8, 4), EventType.RETURN_OF_CAPITAL, 8528.0, "Return of capital"),
            (date(2023, 9, 22), EventType.RETURN_OF_CAPITAL, 8805.0, "Return of capital"),
            (date(2023, 10, 13), EventType.RETURN_OF_CAPITAL, 9815.0, "Return of capital"),
            (date(2023, 11, 21), EventType.RETURN_OF_CAPITAL, 6968.0, "Return of capital"),
            (date(2024, 4, 19), EventType.RETURN_OF_CAPITAL, 32233.0, "Final return of capital"),
        ]
        
        # Distribution events (with tax withholding using helper functions)
        three_pg_distribution_events = [
            # No tax withholding
            create_event_without_tax(
                date(2023, 3, 24), EventType.DISTRIBUTION, 3076.0, 
                "Interest distribution", DistributionType.INTEREST
            ),
            # With tax withholding rate
            create_event_with_tax_rate(
                date(2023, 7, 7), EventType.DISTRIBUTION, 4472.0, 
                "Interest distribution", DistributionType.INTEREST, 10.0
            ),
            create_event_with_tax_rate(
                date(2023, 8, 4), EventType.DISTRIBUTION, 872.0, 
                "Interest distribution", DistributionType.INTEREST, 10.0
            ),
            create_event_with_tax_rate(
                date(2023, 9, 22), EventType.DISTRIBUTION, 794.0, 
                "Interest distribution", DistributionType.INTEREST, 10.0
            ),
            create_event_with_tax_rate(
                date(2023, 10, 13), EventType.DISTRIBUTION, 685.0, 
                "Interest distribution", DistributionType.INTEREST, 10.0
            ),
            create_event_with_tax_rate(
                date(2023, 11, 21), EventType.DISTRIBUTION, 531.0, 
                "Interest distribution", DistributionType.INTEREST, 10.0
            ),
            create_event_with_tax_rate(
                date(2024, 4, 19), EventType.DISTRIBUTION, 4399.0, 
                "Interest distribution", DistributionType.INTEREST, 10.0
            ),
        ]
        
        # Combine all events
        three_pg_all_events = three_pg_capital_events + three_pg_distribution_events
        add_fund_events_with_tax_handling(session, three_pg_fund, three_pg_all_events)
        
        # ============================================================================
        # TAX STATEMENTS
        # ============================================================================
        print("\n6. ADDING TAX STATEMENTS")
        print("-" * 30)
        
        # Senior Debt Fund No.24 Tax Statements
        senior_debt_tax_statements = [
            {
                'financial_year': '2022-23',
                'gross_interest_income': 0.0,
                'tax_withheld': 0.0,
                'non_resident': True,
                'accountant': 'Findex',
                'statement_date': date(2023, 8, 24),
                'notes': 'FY23 tax statement from fund manager'
            },
            {
                'financial_year': '2023-24',
                'gross_interest_income': 8499.98,
                'tax_withheld': 852.0,
                'non_resident': True,
                'accountant': 'Findex',
                'statement_date': date(2024, 8, 12),
                'notes': 'FY24 tax statement from fund manager'
            }
        ]
        
        for tax_data in senior_debt_tax_statements:
            add_tax_statement(session, senior_debt_fund, shaun, tax_data)
        
        # 3PG Finance Tax Statements
        three_pg_tax_statements = [
            {
                'financial_year': '2022-23',
                'gross_interest_income': 3075.57,
                'tax_withheld': 0.0,
                'non_resident': True,
                'accountant': 'Findex',
                'statement_date': date(2023, 7, 26),
                'notes': 'FY23 tax statement from fund manager'
            },
            {
                'financial_year': '2023-24',
                'gross_interest_income': 11757.14,
                'tax_withheld': 1179.0,
                'non_resident': True,
                'accountant': 'Findex',
                'statement_date': date(2024, 7, 1),
                'notes': 'FY24 tax statement from fund manager'
            }
        ]
        
        for tax_data in three_pg_tax_statements:
            add_tax_statement(session, three_pg_fund, shaun, tax_data)
        
        # ============================================================================
        # ANALYSIS AND REPORTING
        # ============================================================================
        print("\n7. FUND ANALYSIS")
        print("=" * 50)
        
        funds_to_analyze = [senior_debt_fund, three_pg_fund]
        
        for fund in funds_to_analyze:
            print(f"\nFUND: {fund.name}")
            print("-" * 30)
            
            # Update fund status
            fund.update_active_status(session)
            
            # Basic info
            print(f"Investment Company: {fund.investment_company.name}")
            print(f"Entity: {fund.entity.name}")
            print(f"Commitment: ${fund.commitment_amount:,.0f}")
            print(f"Current Equity Balance: ${fund.current_equity_balance:,.0f}")
            print(f"Average Equity Balance: ${fund.average_equity_balance:,.0f}")
            print(f"Investment Duration: {fund.total_investment_duration_months} months")
            print(f"Fund Status: {'Active' if fund.is_active else 'Exited'}")
            print(f"Start Date: {fund.start_date}")
            print(f"Duration: {fund.total_investment_duration_months} months")
            print(f"IRR: {fund.get_irr_percentage(session)}")
            
            # Capital movements
            capital_movements = fund.get_capital_movements(session)
            print(f"\nCapital Movements:")
            print(f"  Total Capital Calls: ${capital_movements['calls']:,.0f}")
            print(f"  Total Capital Returns: ${capital_movements['returns']:,.0f}")
            print(f"  Net Capital Invested: ${capital_movements['calls'] - capital_movements['returns']:,.0f}")
            
            # Distributions
            distributions = fund.get_total_distributions(session)
            print(f"\nDistributions:")
            print(f"  Total Distributions: ${distributions:,.0f}")
            
            # Debt cost analysis
            debt_cost = fund.calculate_debt_cost(session)
            if debt_cost:
                print(f"\nDebt Cost Analysis:")
                print(f"  Average Risk-Free Rate: {debt_cost['average_risk_free_rate']:.2f}%")
                print(f"  Total Debt Cost: ${debt_cost['total_debt_cost']:,.0f}")
                print(f"  Debt Cost as % of Average Equity: {debt_cost['debt_cost_percentage']:.2f}%")
        
        print("\n" + "=" * 50)
        print("COMPREHENSIVE TEST COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error during test: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_comprehensive_test() 