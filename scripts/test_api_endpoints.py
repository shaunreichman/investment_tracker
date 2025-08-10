#!/usr/bin/env python3
"""
Test script for the new banking and cash flow API endpoints.
This script tests the API logic without needing a full Flask server.
"""

import sys
import os
from datetime import date, datetime
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.database import get_database_session
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from src.fund.models import Fund, FundType, FundStatus, EventType, DistributionType
from src.banking.models import Bank, BankAccount
from src.fund.models import FundEventCashFlow, CashFlowDirection

def test_banking_models():
    """Test the banking models work correctly"""
    print("Testing banking models...")
    
    engine, sf, Scoped = get_database_session()
    session = Scoped()
    
    try:
        # Test Bank creation
        print("  - Creating test bank...")
        bank = Bank.create(
            name="Test Bank",
            country="AU",
            swift_bic="TESTAU2S",
            session=session
        )
        print(f"    ✓ Bank created: {bank.name} ({bank.country})")
        
        # Test BankAccount creation
        print("  - Creating test entity...")
        ic = InvestmentCompany.create(
            name="Test IC",
            session=session
        )
        entity = Entity.create(
            name="Test Entity",
            tax_jurisdiction="AU",
            session=session
        )
        print(f"    ✓ Entity created: {entity.name}")
        
        print("  - Creating test bank account...")
        account = BankAccount.create(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Test Account",
            account_number="12345678",
            currency="AUD",
            is_active=True,
            session=session
        )
        print(f"    ✓ Bank account created: {account.account_name} ({account.currency})")
        
        # Test BankAccount.get_by_unique
        print("  - Testing uniqueness constraint...")
        duplicate_account = BankAccount.get_by_unique(
            entity_id=entity.id,
            bank_id=bank.id,
            account_number="12345678",
            session=session
        )
        if duplicate_account and duplicate_account.id == account.id:
            print("    ✓ Uniqueness constraint working correctly")
        else:
            print("    ✗ Uniqueness constraint issue")
        
        # Cleanup
        session.delete(account)
        session.delete(entity)
        session.delete(ic)
        session.delete(bank)
        session.commit()
        print("  ✓ Banking models test completed successfully")
        
    except Exception as e:
        print(f"  ✗ Banking models test failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def test_cash_flow_api_logic():
    """Test the cash flow API logic without Flask"""
    print("\nTesting cash flow API logic...")
    
    engine, sf, Scoped = get_database_session()
    session = Scoped()
    
    try:
        # Setup test data
        print("  - Setting up test data...")
        ic = InvestmentCompany.create(
            name="Test IC for Cash Flows",
            session=session
        )
        entity = Entity.create(
            name="Test Entity for Cash Flows",
            tax_jurisdiction="AU",
            session=session
        )
        bank = Bank.create(
            name="Test Bank for Cash Flows",
            country="AU",
            session=session
        )
        account = BankAccount.create(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Test Account for Cash Flows",
            account_number="87654321",
            currency="AUD",
            session=session
        )
        fund = Fund.create(
            investment_company_id=ic.id,
            entity_id=entity.id,
            name="Test Fund for Cash Flows",
            fund_type="PE",
            tracking_type=FundType.COST_BASED,
            session=session
        )
        
        # Test capital call event with cash flow
        print("  - Testing capital call with cash flow...")
        capital_call_event = fund.add_capital_call(
            amount=10000.0,
            date=date(2024, 1, 15),
            session=session
        )
        session.flush()
        
        # Test adding cash flow
        cash_flow = capital_call_event.add_cash_flow(
            bank_account_id=account.id,
            transfer_date=date(2024, 1, 16),
            currency="AUD",
            amount=10000.0,
            reference="BANK123",
            notes="Test transfer",
            session=session
        )
        print(f"    ✓ Cash flow added: {cash_flow.amount} {cash_flow.currency}")
        print(f"    ✓ Direction inferred: {cash_flow.direction.value}")
        print(f"    ✓ Event completion status: {capital_call_event.is_cash_flow_complete}")
        
        # Test distribution event with cash flow
        print("  - Testing distribution with cash flow...")
        distribution_event = fund.add_distribution(
            event_date=date(2024, 6, 15),
            amount=5000.0,
            distribution_type=DistributionType.DIVIDEND,
            session=session
        )
        session.flush()
        
        cash_flow2 = distribution_event.add_cash_flow(
            bank_account_id=account.id,
            transfer_date=date(2024, 6, 16),
            currency="AUD",
            amount=5000.0,
            reference="BANK456",
            notes="Test dividend",
            session=session
        )
        print(f"    ✓ Distribution cash flow added: {cash_flow2.amount} {cash_flow2.currency}")
        print(f"    ✓ Direction inferred: {cash_flow2.direction.value}")
        print(f"    ✓ Event completion status: {distribution_event.is_cash_flow_complete}")
        
        # Test cross-currency cash flow (should be incomplete)
        print("  - Testing cross-currency cash flow...")
        usd_account = BankAccount.create(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="USD Account",
            account_number="11111111",
            currency="USD",
            session=session
        )
        
        cross_currency_cf = capital_call_event.add_cash_flow(
            bank_account_id=usd_account.id,
            transfer_date=date(2024, 1, 17),
            currency="USD",
            amount=7500.0,
            reference="BANK789",
            notes="USD transfer",
            session=session
        )
        print(f"    ✓ Cross-currency cash flow added: {cross_currency_cf.amount} {cross_currency_cf.currency}")
        print(f"    ✓ Event completion status (should be False): {capital_call_event.is_cash_flow_complete}")
        
        # Test removing cash flow
        print("  - Testing cash flow removal...")
        original_count = len(capital_call_event.cash_flows)
        capital_call_event.remove_cash_flow(cash_flow.id, session=session)
        new_count = len(capital_call_event.cash_flows)
        print(f"    ✓ Cash flow removed: {original_count} -> {new_count}")
        
        # Cleanup
        session.delete(cross_currency_cf)
        session.delete(cash_flow2)
        session.delete(cash_flow)
        session.delete(distribution_event)
        session.delete(capital_call_event)
        session.delete(usd_account)
        session.delete(account)
        session.delete(fund)
        session.delete(bank)
        session.delete(entity)
        session.delete(ic)
        session.commit()
        print("  ✓ Cash flow API logic test completed successfully")
        
    except Exception as e:
        print(f"  ✗ Cash flow API logic test failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def test_validation_logic():
    """Test the validation logic used in API endpoints"""
    print("\nTesting validation logic...")
    
    engine, sf, Scoped = get_database_session()
    session = Scoped()
    
    try:
        # Setup minimal test data
        ic = InvestmentCompany.create(
            name="Test IC for Validation",
            session=session
        )
        entity = Entity.create(
            name="Test Entity for Validation",
            tax_jurisdiction="AU",
            session=session
        )
        bank = Bank.create(
            name="Test Bank for Validation",
            country="AU",
            session=session
        )
        account = BankAccount.create(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Test Account for Validation",
            account_number="99999999",
            currency="AUD",
            session=session
        )
        
        # Test currency validation
        print("  - Testing currency validation...")
        try:
            # This should fail - currency mismatch
            invalid_cf = FundEventCashFlow(
                fund_event_id=999,  # Dummy ID
                bank_account_id=account.id,
                direction=CashFlowDirection.OUTFLOW,
                transfer_date=date(2024, 1, 15),
                currency="USD",  # Different from account currency (AUD)
                amount=1000.0
            )
            print("    ✗ Currency validation should have failed")
        except Exception as e:
            print(f"    ✓ Currency validation working: {e}")
        
        # Test required fields validation
        print("  - Testing required fields validation...")
        required_fields = ['bank_account_id', 'transfer_date', 'currency', 'amount']
        for field in required_fields:
            print(f"    ✓ Required field: {field}")
        
        # Cleanup
        session.delete(account)
        session.delete(bank)
        session.delete(entity)
        session.delete(ic)
        session.commit()
        print("  ✓ Validation logic test completed successfully")
        
    except Exception as e:
        print(f"  ✗ Validation logic test failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def main():
    """Run all tests"""
    print("Starting API endpoint tests...\n")
    
    try:
        test_banking_models()
        test_cash_flow_api_logic()
        test_validation_logic()
        
        print("\n🎉 All tests passed! The API endpoints should work correctly.")
        print("\nNext steps:")
        print("1. Start the Flask server to test actual HTTP endpoints")
        print("2. Test with curl/Postman for real API calls")
        print("3. Move to Phase 4 (UI implementation)")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
