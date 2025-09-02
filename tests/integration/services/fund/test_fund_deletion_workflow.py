"""
Integration tests for fund deletion workflow.
"""

import pytest
from src.fund.services.fund_service import FundService
from src.fund.models import Fund
from src.fund.enums import FundStatus, FundType, EventType
from src.fund.models import FundEvent
from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany
from src.investment_company.enums import CompanyType


class TestFundDeletionWorkflow:
    """Test complete fund deletion workflow."""
    
    def test_delete_fund_with_events_fails(self, db_session):
        """Test deletion fails when fund has events."""
        # Arrange
        fund_service = FundService()
        
        # Create test entities
        entity = Entity(
            name="Test Entity",
            description="Test entity for fund deletion",
            tax_jurisdiction="AU"
        )
        db_session.add(entity)
        db_session.flush()
        
        company = InvestmentCompany(
            name="Test Company",
            company_type=CompanyType.PRIVATE_EQUITY
        )
        db_session.add(company)
        db_session.flush()
        
        # Create fund
        fund = Fund(
            name="Test Fund",
            fund_type="Private Equity",
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            entity_id=entity.id,
            investment_company_id=company.id,
            commitment_amount=1000000,
            currency="AUD"
        )
        db_session.add(fund)
        db_session.flush()
        
        # Add a fund event
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.CAPITAL_CALL,
            event_date="2024-01-01",
            amount=100000,
            description="Test investment"
        )
        db_session.add(event)
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Deletion validation failed"):
            fund_service.delete_fund(fund.id, db_session)
    
    def test_delete_fund_without_events_succeeds(self, db_session):
        """Test deletion succeeds when fund has no events."""
        # Arrange
        fund_service = FundService()
        
        # Create test entities
        entity = Entity(
            name="Test Entity",
            description="Test entity for fund deletion",
            tax_jurisdiction="AU"
        )
        db_session.add(entity)
        db_session.flush()
        
        company = InvestmentCompany(
            name="Test Company",
            company_type=CompanyType.PRIVATE_EQUITY
        )
        db_session.add(company)
        db_session.flush()
        
        # Create fund
        fund = Fund(
            name="Test Fund",
            fund_type="Private Equity",
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            entity_id=entity.id,
            investment_company_id=company.id,
            commitment_amount=1000000,
            currency="AUD"
        )
        db_session.add(fund)
        db_session.commit()
        
        # Act
        result = fund_service.delete_fund(fund.id, db_session)
        db_session.commit()  # Commit the deletion
        
        # Assert
        assert result is True
        assert db_session.query(Fund).filter(Fund.id == fund.id).first() is None
    
    def test_delete_fund_not_found_returns_false(self, db_session):
        """Test deletion returns False when fund doesn't exist."""
        # Arrange
        fund_service = FundService()
        non_existent_fund_id = 99999
        
        # Act
        result = fund_service.delete_fund(non_existent_fund_id, db_session)
        
        # Assert
        assert result is False
    
    def test_delete_fund_with_tax_statements_fails(self, db_session):
        """Test deletion fails when fund has tax statements."""
        # Arrange
        fund_service = FundService()
        
        # Create test entities
        entity = Entity(
            name="Test Entity",
            description="Test entity for fund deletion",
            tax_jurisdiction="AU"
        )
        db_session.add(entity)
        db_session.flush()
        
        company = InvestmentCompany(
            name="Test Company",
            company_type=CompanyType.PRIVATE_EQUITY
        )
        db_session.add(company)
        db_session.flush()
        
        # Create fund
        fund = Fund(
            name="Test Fund",
            fund_type="Private Equity",
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            entity_id=entity.id,
            investment_company_id=company.id,
            commitment_amount=1000000,
            currency="AUD"
        )
        db_session.add(fund)
        db_session.flush()
        
        # Add a tax statement
        from src.tax.models import TaxStatement
        tax_statement = TaxStatement(
            fund_id=fund.id,
            entity_id=entity.id,
            financial_year=2024,
            statement_date="2024-06-30"
        )
        db_session.add(tax_statement)
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Deletion validation failed"):
            fund_service.delete_fund(fund.id, db_session)
    
    def test_delete_fund_with_domain_events_fails(self, db_session):
        """Test deletion fails when fund has domain events."""
        # Arrange
        fund_service = FundService()
        
        # Create test entities
        entity = Entity(
            name="Test Entity",
            description="Test entity for fund deletion",
            tax_jurisdiction="AU"
        )
        db_session.add(entity)
        db_session.flush()
        
        company = InvestmentCompany(
            name="Test Company",
            company_type=CompanyType.PRIVATE_EQUITY
        )
        db_session.add(company)
        db_session.flush()
        
        # Create fund
        fund = Fund(
            name="Test Fund",
            fund_type="Private Equity",
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            entity_id=entity.id,
            investment_company_id=company.id,
            commitment_amount=1000000,
            currency="AUD"
        )
        db_session.add(fund)
        db_session.flush()
        
        # Add a domain event
        from src.fund.models import DomainEvent
        domain_event = DomainEvent(
            fund_id=fund.id,
            event_type="fund_created",
            event_data={"test": "data"},
            source="test"
        )
        db_session.add(domain_event)
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Deletion validation failed"):
            fund_service.delete_fund(fund.id, db_session)
