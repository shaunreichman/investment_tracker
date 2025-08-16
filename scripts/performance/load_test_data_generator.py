#!/usr/bin/env python3
"""
Load Test Data Generator for Phase 6.1 Performance Testing.

This script generates realistic test datasets for performance testing:
- 1000+ events across multiple funds
- 50+ funds with different characteristics
- 10+ companies with various fund portfolios
- Realistic event patterns and amounts
"""

import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database imports
from sqlalchemy.orm import Session
from src.database import get_database_session
from src.fund.models import Fund, FundEvent, FundStatus
from src.fund.enums import FundType, EventType
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from src.tax.models import TaxStatement

class LoadTestDataGenerator:
    """Generates load test data for performance testing."""
    
    def __init__(self):
        self.companies = []
        self.entities = []
        self.funds = []
        self.events = []
        self.tax_statements = []
        
        # Event type distribution for realistic patterns
        self.event_type_distribution = {
            EventType.CAPITAL_CALL: 0.25,      # 25% capital calls
            EventType.RETURN_OF_CAPITAL: 0.20, # 20% returns
            EventType.DISTRIBUTION: 0.30,      # 30% distributions
            EventType.UNIT_PURCHASE: 0.10,     # 10% unit purchases
            EventType.UNIT_SALE: 0.10,         # 10% unit sales
            EventType.NAV_UPDATE: 0.05         # 5% NAV updates
        }
        
        # Fund type distribution
        self.fund_type_distribution = {
            FundType.COST_BASED: 0.7,  # 70% cost-based funds
            FundType.NAV_BASED: 0.3    # 30% NAV-based funds
        }
        
        # Fund status distribution
        self.fund_status_distribution = {
            FundStatus.ACTIVE: 0.6,      # 60% active funds
            FundStatus.REALIZED: 0.3,    # 30% realized funds
            FundStatus.COMPLETED: 0.1    # 10% completed funds
        }
    
    def generate_companies(self, count: int = 15, session: Session = None) -> List[InvestmentCompany]:
        """Generate test investment companies."""
        logger.info(f"Generating {count} test investment companies...")
        
        company_names = [
            "Alpha Capital Partners", "Beta Investment Group", "Gamma Ventures",
            "Delta Asset Management", "Epsilon Capital", "Zeta Investments",
            "Eta Financial Services", "Theta Capital Partners", "Iota Ventures",
            "Kappa Asset Management", "Lambda Capital", "Mu Investments",
            "Nu Financial Group", "Xi Capital Partners", "Omicron Ventures"
        ]
        
        companies = []
        for i in range(count):
            company = InvestmentCompany.create(
                name=company_names[i],
                description=f"Test investment company {i+1} for performance testing",
                company_type=random.choice(["Private Equity", "Venture Capital", "Asset Management", "Investment Group"]),
                business_address=f"{random.randint(1, 999)} Test Street, Test City, NSW {random.randint(2000, 2999)}",
                website=f"https://www.{company_names[i].lower().replace(' ', '')}.com.au",
                session=session
            )
            companies.append(company)
        
        self.companies = companies
        logger.info(f"Generated {len(companies)} companies")
        return companies
    
    def generate_entities(self, count: int = 25, session: Session = None) -> List[Entity]:
        """Generate test entities."""
        logger.info(f"Generating {count} test entities...")
        
        entity_names = [
            "Test Entity A", "Test Entity B", "Test Entity C", "Test Entity D", "Test Entity E",
            "Test Entity F", "Test Entity G", "Test Entity H", "Test Entity I", "Test Entity J",
            "Test Entity K", "Test Entity L", "Test Entity M", "Test Entity N", "Test Entity O",
            "Test Entity P", "Test Entity Q", "Test Entity R", "Test Entity S", "Test Entity T",
            "Test Entity U", "Test Entity V", "Test Entity W", "Test Entity X", "Test Entity Y"
        ]
        
        entities = []
        for i in range(count):
            entity = Entity.create(
                name=entity_names[i],
                description=f"Test entity {i+1} for performance testing",
                tax_jurisdiction=random.choice(["AU", "US", "UK", "CA"]),
                session=session
            )
            entities.append(entity)
        
        self.entities = entities
        logger.info(f"Generated {len(entities)} entities")
        return entities
    
    def generate_funds(self, count: int = 75, session: Session = None) -> List[Fund]:
        """Generate test funds."""
        logger.info(f"Generating {count} test funds...")
        
        fund_names = [
            "Growth Fund", "Income Fund", "Balanced Fund", "Conservative Fund", "Aggressive Fund",
            "Property Fund", "Equity Fund", "Debt Fund", "Hedge Fund", "Venture Fund",
            "Private Equity Fund", "Real Estate Fund", "Infrastructure Fund", "Commodity Fund", "Currency Fund"
        ]
        
        funds = []
        for i in range(count):
            # Select random company and entity
            company = random.choice(self.companies)
            entity = random.choice(self.entities)
            
            # Select fund characteristics
            fund_type = random.choices(
                list(self.fund_type_distribution.keys()),
                weights=list(self.fund_type_distribution.values())
            )[0]
            
            fund_status = random.choices(
                list(self.fund_status_distribution.keys()),
                weights=list(self.fund_status_distribution.values())
            )[0]
            
            # Generate fund data
            fund = Fund.create(
                investment_company_id=company.id,
                entity_id=entity.id,
                name=f"{company.name} - {random.choice(fund_names)} {i+1:03d}",
                fund_type=random.choice(["Private Equity", "Venture Capital", "Real Estate", "Infrastructure"]),
                tracking_type=fund_type,
                currency="AUD",
                description=f"Test fund {i+1} for performance testing",
                commitment_amount=Decimal(str(random.randint(100000, 10000000))),
                expected_irr=Decimal(str(random.uniform(8.0, 25.0))),
                expected_duration_months=random.randint(36, 120),
                session=session
            )
            funds.append(fund)
        
        self.funds = funds
        logger.info(f"Generated {len(funds)} funds")
        return funds
    
    def generate_events(self, count: int = 1500) -> List[FundEvent]:
        """Generate test fund events."""
        logger.info(f"Generating {count} test fund events...")
        
        events = []
        for i in range(count):
            # Select random fund
            fund = random.choice(self.funds)
            
            # Select event type based on distribution
            event_type = random.choices(
                list(self.event_type_distribution.keys()),
                weights=list(self.event_type_distribution.values())
            )[0]
            
            # Generate event date within fund's lifetime
            fund_start = date(2020, 1, 1)  # Use a fixed start date for testing
            fund_end = fund.end_date or date.today()
            days_range = (fund_end - fund_start).days
            event_date = fund_start + timedelta(days=random.randint(0, days_range))
            
            # Generate appropriate amount based on event type
            if event_type in [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]:
                amount = Decimal(str(random.randint(10000, 500000)))
            elif event_type == EventType.DISTRIBUTION:
                amount = Decimal(str(random.randint(1000, 100000)))
            elif event_type in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]:
                amount = Decimal(str(random.randint(100, 10000)))
            else:  # NAV_UPDATE
                amount = Decimal(str(random.uniform(0.8, 1.2)))
            
            # Create event
            event = FundEvent(
                fund_id=fund.id,
                event_type=event_type,
                event_date=event_date,
                amount=amount,
                description=f"Test {event_type.value} event {i+1}",
                reference_number=f"TEST-{event_type.value[:3].upper()}-{i+1:06d}",
                has_withholding_tax=event_type == EventType.DISTRIBUTION and random.random() < 0.3
            )
            events.append(event)
        
        self.events = events
        logger.info(f"Generated {len(events)} events")
        return events
    
    def generate_tax_statements(self, count: int = 200) -> List[TaxStatement]:
        """Generate test tax statements."""
        logger.info(f"Generating {count} test tax statements...")
        
        tax_statements = []
        for i in range(count):
            # Select random fund
            fund = random.choice(self.funds)
            
            # Generate tax statement date
            fund_start = date(2020, 1, 1)  # Use a fixed start date for testing
            fund_end = fund.end_date or date.today()
            days_range = (fund_end - fund_start).days
            statement_date = fund_start + timedelta(days=random.randint(0, days_range))
            
            # Generate financial year
            financial_year = statement_date.year
            if statement_date.month < 7:
                financial_year -= 1
            
            tax_statement = TaxStatement(
                fund_id=fund.id,
                entity_id=fund.entity_id,  # Use the fund's entity
                financial_year=financial_year,
                statement_date=statement_date,
                interest_income_amount=Decimal(str(random.randint(10000, 1000000))),
                interest_income_tax_rate=Decimal(str(random.uniform(20.0, 45.0))),
                interest_received_in_cash=Decimal(str(random.randint(8000, 800000))),
                dividend_franked_income_amount=Decimal(str(random.randint(0, 500000))),
                dividend_unfranked_income_amount=Decimal(str(random.randint(0, 500000))),
                capital_gain_income_amount=Decimal(str(random.randint(0, 300000))),
                notes=f"Test tax statement {i+1} for FY{financial_year}"
            )
            tax_statements.append(tax_statement)
        
        self.tax_statements = tax_statements
        logger.info(f"Generated {len(tax_statements)} tax statements")
        return tax_statements
    
    def save_to_database(self, session: Session) -> None:
        """Save all generated test data to the database."""
        logger.info("Saving test data to database...")
        
        try:
            # Save companies
            for company in self.companies:
                session.add(company)
            session.flush()
            logger.info(f"Saved {len(self.companies)} companies")
            
            # Save entities
            for entity in self.entities:
                session.add(entity)
            session.flush()
            logger.info(f"Saved {len(self.entities)} entities")
            
            # Save funds
            for fund in self.funds:
                session.add(fund)
            session.flush()
            logger.info(f"Saved {len(self.funds)} funds")
            
            # Save events
            for event in self.events:
                session.add(event)
            session.flush()
            logger.info(f"Saved {len(self.events)} events")
            
            # Save tax statements
            for tax_statement in self.tax_statements:
                session.add(tax_statement)
            session.flush()
            logger.info(f"Saved {len(self.tax_statements)} tax statements")
            
            # Commit all changes
            session.commit()
            logger.info("All test data saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving test data: {e}")
            session.rollback()
            raise
    
    def generate_complete_dataset(self, session: Session) -> Dict[str, int]:
        """Generate complete load test dataset."""
        logger.info("Generating complete load test dataset...")
        
        # Generate all data
        self.generate_companies(15, session)
        self.generate_entities(25, session)
        self.generate_funds(75, session)
        self.generate_events(1500)
        self.generate_tax_statements(200)
        
        # Save to database
        self.save_to_database(session)
        
        # Return summary
        summary = {
            'companies': len(self.companies),
            'entities': len(self.entities),
            'funds': len(self.funds),
            'events': len(self.events),
            'tax_statements': len(self.tax_statements)
        }
        
        logger.info(f"Load test dataset generated: {summary}")
        return summary

def main():
    """Main function to generate load test data."""
    logger.info("Starting load test data generation for Phase 6.1")
    
    try:
        # Get database session
        engine, session_factory, scoped_session = get_database_session()
        session = scoped_session()
        
        try:
            # Create data generator
            generator = LoadTestDataGenerator()
            
            # Generate complete dataset
            summary = generator.generate_complete_dataset(session)
            
            # Print summary
            print("\n" + "="*60)
            print("LOAD TEST DATA GENERATION COMPLETED")
            print("="*60)
            print(f"Companies: {summary['companies']}")
            print(f"Entities: {summary['entities']}")
            print(f"Funds: {summary['funds']}")
            print(f"Events: {summary['events']}")
            print(f"Tax Statements: {summary['tax_statements']}")
            print("="*60)
            print("Data ready for Phase 6.1 performance testing!")
            print("="*60)
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error in load test data generation: {e}")
        raise

if __name__ == "__main__":
    main()
