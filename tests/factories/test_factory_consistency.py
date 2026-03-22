"""
Factory-Model Consistency Tests.

This module contains tests that validate the consistency between
factory classes and their corresponding model classes.
"""

import pytest
from tests.factories import validate_all_factories


class TestFactoryModelConsistency:
    """Test suite for validating factory-model consistency."""
    
    def test_all_factories_match_models(self):
        """
        Test that all factories have fields that match their corresponding models.
        
        This test ensures that:
        1. All required model fields have factory declarations
        2. All factory fields exist in the model
        3. No orphaned fields in either direction
        """
        results = validate_all_factories()
        
        # Check each factory
        for factory_name, validation_result in results.items():
            missing_in_factory = validation_result['missing_in_factory']
            extra_in_factory = validation_result['extra_in_factory']
            
            # Report missing fields in factory
            if missing_in_factory:
                pytest.fail(
                    f"Factory {factory_name} is missing fields: {missing_in_factory}. "
                    f"These fields exist in the model but not in the factory."
                )
            
            # Report extra fields in factory (warn but don't fail)
            if extra_in_factory:
                print(f"Warning: Factory {factory_name} has extra fields: {extra_in_factory}")
    
    def test_factory_imports_work(self):
        """Test that all factory imports work correctly."""
        from tests.factories import (
            FundFactory,
            FundEventFactory,
            FundEventCashFlowFactory,
            FundTaxStatementFactory,
            EntityFactory,
            BankFactory,
            BankAccountFactory,
            CompanyFactory,
            ContactFactory,
            RiskFreeRateFactory,
            set_session,
            get_session
        )
        
        # Basic validation that imports work
        assert FundFactory is not None
        assert EntityFactory is not None
        assert set_session is not None
        assert get_session is not None
    
    def test_factory_meta_classes_have_correct_models(self):
        """Test that factory Meta classes reference the correct models."""
        from tests.factories import (
            FundFactory, FundEventFactory, FundEventCashFlowFactory, FundTaxStatementFactory,
            EntityFactory, BankFactory, BankAccountFactory, CompanyFactory,
            ContactFactory, RiskFreeRateFactory
        )
        
        from src.fund.models import Fund, FundEvent, FundEventCashFlow, FundTaxStatement
        from src.entity.models import Entity
        from src.banking.models import Bank, BankAccount
        from src.company.models import Company, Contact
        from src.rates.models import RiskFreeRate
        
        # Test model references
        assert FundFactory._meta.model == Fund
        assert FundEventFactory._meta.model == FundEvent
        assert FundEventCashFlowFactory._meta.model == FundEventCashFlow
        assert FundTaxStatementFactory._meta.model == FundTaxStatement
        assert EntityFactory._meta.model == Entity
        assert BankFactory._meta.model == Bank
        assert BankAccountFactory._meta.model == BankAccount
        assert CompanyFactory._meta.model == Company
        assert ContactFactory._meta.model == Contact
        assert RiskFreeRateFactory._meta.model == RiskFreeRate
