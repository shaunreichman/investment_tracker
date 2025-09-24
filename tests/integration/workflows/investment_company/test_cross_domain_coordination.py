"""
Cross-Domain Coordination Integration Tests.

This module tests the coordination between investment company, fund, and entity domains,
ensuring proper cross-domain communication and event handling while maintaining
domain boundaries and single source of truth principles.

Key testing areas:
- Fund creation coordination between company and fund domains
- Cross-domain event publishing and handling
- Business rule validation across multiple domains
- Portfolio updates triggered by fund operations
- Data consistency across domain boundaries
- Error handling and rollback scenarios
"""

import pytest
from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from typing import Dict, Any
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.services import CompanyService
from src.investment_company.services.fund_coordination_service import FundCoordinationService
from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.enums import CompanyType, CompanyStatus
from src.fund.models import Fund, FundEvent
from src.fund.enums import FundStatus, FundTrackingType, EventType
from src.entity.models import Entity
from tests.factories import InvestmentCompanyFactory, ContactFactory, FundFactory, EntityFactory, FundEventFactory


class TestCrossDomainCoordination:
    """Test cross-domain coordination between company, fund, and entity domains."""
    
    def test_fund_creation_coordination_workflow(self, db_session: Session):
        """Test complete fund creation coordination workflow across domains."""
        # Arrange: Prepare company, entity, and fund data
        company_data = {
            'name': 'Coordination Test Company',
            'description': 'Company for cross-domain coordination testing',
            'company_type': CompanyType.PRIVATE_EQUITY,
            'status': CompanyStatus.ACTIVE
        }
        
        entity_data = {
            'name': 'Coordination Test Entity',
            'description': 'Entity for coordination testing',
            'tax_jurisdiction': 'AU'
        }
        
        fund_data = {
            'name': 'Coordination Test Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value,
            'currency': 'AUD',
            'description': 'Fund for coordination testing',
            'commitment_amount': 5000000.0,
            'expected_irr': 18.0,
            'expected_duration_months': 96
        }
        
        # Act: Create company and entity
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
            status=company_data['status'],
            session=db_session
        )
        
        entity = Entity.create(
            name=entity_data['name'],
            description=entity_data['description'],
            tax_jurisdiction=entity_data['tax_jurisdiction'],
            session=db_session
        )
        
        # Create fund through coordination service
        coordination_service = FundCoordinationService()
        fund = coordination_service.coordinate_fund_creation(
            company=company,
            entity=entity,
            fund_data=fund_data,
            session=db_session
        )
        
        # Assert: Verify cross-domain coordination worked correctly
        assert fund is not None
        assert fund.id is not None
        assert fund.name == fund_data['name']
        assert fund.entity_id == entity.id
        assert fund.investment_company_id == company.id
        
        # Verify fund was created in fund domain (single source of truth)
        db_session.refresh(fund)
        assert fund.fund_type == fund_data['fund_type']
        # Handle both enum and string values for tracking_type
        if hasattr(fund.tracking_type, 'value'):
            assert fund.tracking_type.value == fund_data['tracking_type']
        else:
            assert fund.tracking_type == fund_data['tracking_type']
        
        # Verify company portfolio was updated
        db_session.refresh(company)
        assert len(company.funds) == 1
        assert company.funds[0].id == fund.id
        
        # Verify entity relationship
        db_session.refresh(entity)
        assert len(entity.funds) == 1
        assert entity.funds[0].id == fund.id
        
        # Cleanup
        db_session.rollback()
    
    def test_cross_domain_business_rule_validation(self, db_session: Session):
        """Test business rule validation across multiple domains."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company and entity
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        fund_data = {
            'name': 'Validation Test Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value
        }
        
        # Act: Validate business rules through coordination service
        coordination_service = FundCoordinationService()
        validation_results = coordination_service.validate_fund_creation_business_rules(
            company=company,
            entity=entity,
            fund_data=fund_data
        )
        
        # Assert: Verify validation results
        assert validation_results is not None
        assert 'is_valid' in validation_results
        assert 'errors' in validation_results
        assert 'warnings' in validation_results
        assert isinstance(validation_results['errors'], list)
        assert isinstance(validation_results['warnings'], list)
        
        # Cleanup
        db_session.rollback()
    
    def test_cross_domain_event_publishing(self, db_session: Session):
        """Test cross-domain event publishing during fund creation."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company and entity
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        fund_data = {
            'name': 'Event Test Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value
        }
        
        # Act: Create fund and capture events
        with patch('src.investment_company.events.registry.CompanyEventHandlerRegistry.handle_event') as mock_handler:
            coordination_service = FundCoordinationService()
            fund = coordination_service.coordinate_fund_creation(
                company=company,
                entity=entity,
                fund_data=fund_data,
                session=db_session
            )
            
            # Assert: Verify event was published
            mock_handler.assert_called_once()
            call_args = mock_handler.call_args
            event_data = call_args[0][0]  # First argument, first element
            
            assert event_data['event_type'] == 'PORTFOLIO_UPDATED'
            assert event_data['company_id'] == company.id
            assert event_data['fund_id'] == fund.id
            assert event_data['operation'] == 'added'
        
        # Cleanup
        db_session.rollback()
    
    def test_portfolio_update_coordination(self, db_session: Session):
        """Test portfolio updates are triggered after fund creation."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company and entity
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        fund_data = {
            'name': 'Portfolio Test Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value
        }
        
        # Act: Create fund and verify portfolio updates
        with patch('src.investment_company.services.company_portfolio_service.CompanyPortfolioService._trigger_portfolio_summary_recalculation') as mock_portfolio_update:
            coordination_service = FundCoordinationService()
            fund = coordination_service.coordinate_fund_creation(
                company=company,
                entity=entity,
                fund_data=fund_data,
                session=db_session
            )
            
            # Assert: Verify portfolio update was triggered
            mock_portfolio_update.assert_called_once_with(company, db_session)
        
        # Cleanup
        db_session.rollback()
    
    def test_error_handling_in_coordination(self, db_session: Session):
        """Test error handling when coordination fails."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company and entity
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        # Invalid fund data (missing required fields)
        invalid_fund_data = {
            'name': 'Invalid Fund'
            # Missing fund_type and tracking_type
        }
        
        # Act & Assert: Verify coordination fails with proper error
        coordination_service = FundCoordinationService()
        
        with pytest.raises(ValueError, match="Fund type is required"):
            coordination_service.coordinate_fund_creation(
                company=company,
                entity=entity,
                fund_data=invalid_fund_data,
                session=db_session
            )
        
        # Cleanup
        db_session.rollback()
    
    def test_coordination_with_inactive_company(self, db_session: Session):
        """Test coordination behavior with inactive company."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create inactive company and entity
        company = InvestmentCompanyFactory(status=CompanyStatus.INACTIVE)
        entity = EntityFactory()
        
        fund_data = {
            'name': 'Inactive Company Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value
        }
        
        # Act: Validate business rules
        coordination_service = FundCoordinationService()
        validation_results = coordination_service.validate_fund_creation_business_rules(
            company=company,
            entity=entity,
            fund_data=fund_data
        )
        
        # Assert: Verify warning about inactive company
        assert validation_results['is_valid'] is True  # Should still be valid
        assert any('inactive' in warning.lower() for warning in validation_results['warnings'])
        
        # Cleanup
        db_session.rollback()
    
    def test_coordination_with_invalid_entity(self, db_session: Session):
        """Test coordination behavior with invalid entity data."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company and entity
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        # Mock entity with invalid ABN (if the model supports it)
        if hasattr(entity, 'abn'):
            entity.abn = "123"  # Too short for valid ABN
        
        fund_data = {
            'name': 'Invalid Entity Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value
        }
        
        # Act: Validate business rules
        coordination_service = FundCoordinationService()
        validation_results = coordination_service.validate_fund_creation_business_rules(
            company=company,
            entity=entity,
            fund_data=fund_data
        )
        
        # Assert: Verify validation results (may or may not have ABN warnings)
        assert validation_results is not None
        assert 'is_valid' in validation_results
        assert 'warnings' in validation_results
        
        # Cleanup
        db_session.rollback()
    
    def test_fund_creation_delegation_to_fund_domain(self, db_session: Session):
        """Test that fund creation is properly delegated to fund domain."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company and entity
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        fund_data = {
            'name': 'Delegation Test Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value
        }
        
        # Act: Create fund through coordination service
        with patch('src.fund.services.fund_service.FundService.create_fund') as mock_fund_service:
            # Mock the fund service to return a proper fund object
            mock_fund = MagicMock()
            mock_fund.id = 999
            mock_fund.name = 'Mock Fund'
            mock_fund.fund_type = fund_data['fund_type']
            mock_fund.tracking_type = fund_data['tracking_type']
            mock_fund.entity_id = entity.id
            mock_fund.investment_company_id = company.id
            
            mock_fund_service.return_value = {'id': 999, 'name': 'Mock Fund'}
            
            # Also mock the fund repository to return the mock fund
            with patch('src.fund.repositories.fund_repository.FundRepository.get_by_id') as mock_repo:
                mock_repo.return_value = mock_fund
                
                coordination_service = FundCoordinationService()
                fund = coordination_service.coordinate_fund_creation(
                    company=company,
                    entity=entity,
                    fund_data=fund_data,
                    session=db_session
                )
                
                # Assert: Verify fund service was called with correct data
                mock_fund_service.assert_called_once()
                call_args = mock_fund_service.call_args[0][0]  # First argument
                
                assert call_args['name'] == fund_data['name']
                assert call_args['entity_id'] == entity.id
                assert call_args['investment_company_id'] == company.id
                assert call_args['fund_type'] == fund_data['fund_type']
                assert call_args['tracking_type'] == fund_data['tracking_type']
        
        # Cleanup
        db_session.rollback()
    
    def test_coordination_with_max_funds_limit(self, db_session: Session):
        """Test coordination behavior when company reaches fund limit."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company with max funds limit
        company = InvestmentCompanyFactory()
        # Add max_funds attribute if it doesn't exist
        if not hasattr(company, 'max_funds'):
            company.max_funds = 2
        else:
            company.max_funds = 2
        
        entity = EntityFactory()
        
        # Create first fund
        fund_data_1 = {
            'name': 'First Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value
        }
        
        coordination_service = FundCoordinationService()
        fund1 = coordination_service.coordinate_fund_creation(
            company=company,
            entity=entity,
            fund_data=fund_data_1,
            session=db_session
        )
        
        # Create second fund
        fund_data_2 = {
            'name': 'Second Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value
        }
        
        fund2 = coordination_service.coordinate_fund_creation(
            company=company,
            entity=entity,
            fund_data=fund_data_2,
            session=db_session
        )
        
        # Act: Try to create third fund (should fail validation)
        fund_data_3 = {
            'name': 'Third Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value
        }
        
        validation_results = coordination_service.validate_fund_creation_business_rules(
            company=company,
            entity=entity,
            fund_data=fund_data_3
        )
        
        # Assert: Verify validation fails due to fund limit
        assert validation_results['is_valid'] is False
        assert any('maximum fund limit' in error.lower() for error in validation_results['errors'])
        
        # Cleanup
        db_session.rollback()
    
    def test_cross_domain_data_consistency(self, db_session: Session):
        """Test data consistency across domain boundaries."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company and entity
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        fund_data = {
            'name': 'Consistency Test Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value
        }
        
        # Act: Create fund through coordination
        coordination_service = FundCoordinationService()
        fund = coordination_service.coordinate_fund_creation(
            company=company,
            entity=entity,
            fund_data=fund_data,
            session=db_session
        )
        
        # Assert: Verify data consistency across domains
        # Company domain
        db_session.refresh(company)
        company_funds = [f for f in company.funds if f.id == fund.id]
        assert len(company_funds) == 1
        assert company_funds[0].name == fund_data['name']
        
        # Entity domain
        db_session.refresh(entity)
        entity_funds = [f for f in entity.funds if f.id == fund.id]
        assert len(entity_funds) == 1
        assert entity_funds[0].name == fund_data['name']
        
        # Fund domain
        db_session.refresh(fund)
        assert fund.name == fund_data['name']
        assert fund.entity_id == entity.id
        assert fund.investment_company_id == company.id
        
        # Cleanup
        db_session.rollback()
    
    def test_coordination_service_stateless_behavior(self, db_session: Session):
        """Test that coordination service maintains stateless behavior."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company and entity
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        fund_data = {
            'name': 'Stateless Test Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value
        }
        
        # Act: Create multiple coordination service instances
        coordination_service_1 = FundCoordinationService()
        coordination_service_2 = FundCoordinationService()
        
        # Verify they are different instances
        assert coordination_service_1 is not coordination_service_2
        
        # Both should work identically
        fund1 = coordination_service_1.coordinate_fund_creation(
            company=company,
            entity=entity,
            fund_data=fund_data,
            session=db_session
        )
        
        # Store fund1 attributes before deletion
        fund1_name = fund1.name
        fund1_fund_type = fund1.fund_type
        fund1_tracking_type = fund1.tracking_type
        
        # Cleanup first fund
        db_session.delete(fund1)
        db_session.flush()
        
        fund2 = coordination_service_2.coordinate_fund_creation(
            company=company,
            entity=entity,
            fund_data=fund_data,
            session=db_session
        )
        
        # Assert: Both should work identically
        assert fund1_name == fund2.name
        assert fund1_fund_type == fund2.fund_type
        # Handle both enum and string values for tracking_type
        if hasattr(fund1_tracking_type, 'value') and hasattr(fund2.tracking_type, 'value'):
            assert fund1_tracking_type.value == fund2.tracking_type.value
        else:
            assert fund1_tracking_type == fund2.tracking_type
        
        # Cleanup
        db_session.rollback()
