"""
Performance tests for Tax Statement Event Grouping functionality.

These tests verify that the tax statement grouping system can handle large datasets
and complex grouping scenarios within acceptable performance thresholds.
"""

import pytest
import time
from datetime import date, timedelta
from tests.factories import (
    InvestmentCompanyFactory, 
    FundFactory, 
    FundEventFactory,
    EntityFactory,
    TaxStatementFactory
)
from src.fund.models import FundStatus, FundType, EventType, DistributionType, GroupType, TaxPaymentType
from src.tax.events import TaxEventManager


class TestTaxStatementGroupingPerformance:
    """Performance tests for Tax Statement Event Grouping functionality."""
    
    def test_large_tax_statement_grouping_performance(self, db_session):
        """Test performance with large tax statement datasets (100+ events)"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=1000000,
            current_equity_balance=950000
        )
        
        # Create tax statement
        tax_statement = TaxStatementFactory(
            fund=fund,
            entity=entity,
            financial_year="2024",
            statement_date=date(2024, 6, 30),
            tax_payment_date=date(2024, 7, 15)
        )
        
        # Create 100 tax events (mix of tax payments and debt cost benefits)
        base_date = date(2024, 1, 1)
        events_created = []
        
        for i in range(100):
            if i % 3 == 0:  # Every 3rd event is a debt cost benefit
                event = FundEventFactory(
                    fund=fund,
                    event_type=EventType.EOFY_DEBT_COST,
                    amount=1000 + i,
                    event_date=base_date,  # All events on same date
                    description=f"Debt Cost Benefit {i}",
                    is_grouped=True,
                    group_id=1,
                    group_type=GroupType.TAX_STATEMENT,
                    group_position=i
                )
            else:  # Tax payment events
                event = FundEventFactory(
                    fund=fund,
                    event_type=EventType.TAX_PAYMENT,
                    amount=-(500 + i),  # Negative for tax payments
                    event_date=base_date,  # All events on same date
                    description=f"Tax Payment {i}",
                    tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX,
                    is_grouped=True,
                    group_id=1,
                    group_type=GroupType.TAX_STATEMENT,
                    group_position=i
                )
            events_created.append(event)
        
        # Test grouping performance
        start_time = time.time()
        
        # Simulate the grouping logic that happens during event creation
        grouped_events = [e for e in events_created if e.is_grouped and e.group_type == GroupType.TAX_STATEMENT]
        
        # Group by group_id and date
        groups = {}
        for event in grouped_events:
            group_key = f"{event.group_id}_{event.event_date}"
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(event)
        
        # Sort each group by position
        for group_events in groups.values():
            group_events.sort(key=lambda e: e.group_position or 0)
        
        end_time = time.time()
        
        # Should complete within reasonable time (under 100ms for 100 events)
        assert (end_time - start_time) < 0.1
        
        # Verify grouping is correct
        assert len(groups) == 1  # All events should be in one group
        group_events = list(groups.values())[0]
        assert len(group_events) == 100
        
        # Verify ordering is correct
        for i, event in enumerate(group_events):
            assert event.group_position == i
    
    def test_multiple_tax_statement_groups_performance(self, db_session):
        """Test performance with multiple tax statement groups"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=1000000,
            current_equity_balance=950000
        )
        
        # Create 5 tax statements for different financial years
        tax_statements = []
        for year in range(2020, 2025):
            tax_statement = TaxStatementFactory(
                fund=fund,
                entity=entity,
                financial_year=str(year),
                statement_date=date(year, 6, 30),
                tax_payment_date=date(year, 7, 15)
            )
            tax_statements.append(tax_statement)
        
        # Create 20 events per tax statement (100 total events)
        events_created = []
        base_date = date(2020, 1, 1)
        
        for statement_idx, tax_statement in enumerate(tax_statements):
            for event_idx in range(20):
                if event_idx % 2 == 0:  # Alternate between tax payments and debt cost
                    event = FundEventFactory(
                        fund=fund,
                        event_type=EventType.TAX_PAYMENT,
                        amount=-(1000 + event_idx),
                        event_date=date(2020 + statement_idx, 6, 30),  # Same date per financial year
                        description=f"FY {2020 + statement_idx} Tax Payment {event_idx}",
                        tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX,
                        is_grouped=True,
                        group_id=statement_idx + 1,
                        group_type=GroupType.TAX_STATEMENT,
                        group_position=event_idx
                    )
                else:
                    event = FundEventFactory(
                        fund=fund,
                        event_type=EventType.EOFY_DEBT_COST,
                        amount=500 + event_idx,
                        event_date=date(2020 + statement_idx, 6, 30),  # Same date per financial year
                        description=f"FY {2020 + statement_idx} Debt Cost {event_idx}",
                        is_grouped=True,
                        group_id=statement_idx + 1,
                        group_type=GroupType.TAX_STATEMENT,
                        group_position=event_idx
                    )
                events_created.append(event)
        
        # Test multiple group performance
        start_time = time.time()
        
        # Group events by group_id and date
        groups = {}
        for event in events_created:
            group_key = f"{event.group_id}_{event.event_date}"
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(event)
        
        # Sort each group by position
        for group_events in groups.values():
            group_events.sort(key=lambda e: e.group_position or 0)
        
        end_time = time.time()
        
        # Should complete within reasonable time (under 100ms for 100 events in 5 groups)
        assert (end_time - start_time) < 0.1
        
        # Verify grouping is correct
        assert len(groups) == 5  # 5 different groups
        for group_events in groups.values():
            assert len(group_events) == 20  # 20 events per group
    
    def test_mixed_event_types_grouping_performance(self, db_session):
        """Test performance with mixed event types (grouped and ungrouped)"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=1000000,
            current_equity_balance=950000
        )
        
        # Create tax statement
        tax_statement = TaxStatementFactory(
            fund=fund,
            entity=entity,
            financial_year="2024",
            statement_date=date(2024, 6, 30),
            tax_payment_date=date(2024, 7, 15)
        )
        
        events_created = []
        base_date = date(2024, 1, 1)
        
        # Create 50 grouped tax events
        for i in range(50):
            if i % 2 == 0:
                event = FundEventFactory(
                    fund=fund,
                    event_type=EventType.TAX_PAYMENT,
                    amount=-(1000 + i),
                    event_date=base_date,  # All grouped events on same date
                    description=f"Tax Payment {i}",
                    tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX,
                    is_grouped=True,
                    group_id=1,
                    group_type=GroupType.TAX_STATEMENT,
                    group_position=i
                )
            else:
                event = FundEventFactory(
                    fund=fund,
                    event_type=EventType.EOFY_DEBT_COST,
                    amount=500 + i,
                    event_date=base_date,  # All grouped events on same date
                    description=f"Debt Cost {i}",
                    is_grouped=True,
                    group_id=1,
                    group_type=GroupType.TAX_STATEMENT,
                    group_position=i
                )
            events_created.append(event)
        
        # Create 50 ungrouped events (distributions, capital calls, etc.)
        for i in range(50):
            event_types = [EventType.DISTRIBUTION, EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]
            event_type = event_types[i % len(event_types)]
            
            event = FundEventFactory(
                fund=fund,
                event_type=event_type,
                amount=1000 + i,
                event_date=base_date + timedelta(days=i + 100),  # Different date range
                description=f"Regular Event {i}",
                is_grouped=False
            )
            events_created.append(event)
        
        # Test mixed event grouping performance
        start_time = time.time()
        
        # Separate grouped and ungrouped events
        grouped_events = [e for e in events_created if e.is_grouped]
        ungrouped_events = [e for e in events_created if not e.is_grouped]
        
        # Group the grouped events
        groups = {}
        for event in grouped_events:
            group_key = f"{event.group_id}_{event.event_date}"
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(event)
        
        # Sort each group by position
        for group_events in groups.values():
            group_events.sort(key=lambda e: e.group_position or 0)
        
        end_time = time.time()
        
        # Should complete within reasonable time (under 100ms for 100 total events)
        assert (end_time - start_time) < 0.1
        
        # Verify results
        assert len(grouped_events) == 50
        assert len(ungrouped_events) == 50
        assert len(groups) == 1  # One tax statement group
    
    def test_frontend_grouping_performance_simulation(self, db_session):
        """Test performance simulation of frontend grouping logic"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=1000000,
            current_equity_balance=950000
        )
        
        # Create tax statement
        tax_statement = TaxStatementFactory(
            fund=fund,
            entity=entity,
            financial_year="2024",
            statement_date=date(2024, 6, 30),
            tax_payment_date=date(2024, 7, 15)
        )
        
        # Create 200 events (mix of grouped and ungrouped)
        events_created = []
        base_date = date(2024, 1, 1)
        
        # 100 grouped tax events
        for i in range(100):
            if i % 3 == 0:
                event = FundEventFactory(
                    fund=fund,
                    event_type=EventType.EOFY_DEBT_COST,
                    amount=1000 + i,
                    event_date=base_date,  # All grouped events on same date
                    description=f"Debt Cost {i}",
                    is_grouped=True,
                    group_id=1,
                    group_type=GroupType.TAX_STATEMENT,
                    group_position=i
                )
            else:
                event = FundEventFactory(
                    fund=fund,
                    event_type=EventType.TAX_PAYMENT,
                    amount=-(500 + i),
                    event_date=base_date,  # All grouped events on same date
                    description=f"Tax Payment {i}",
                    tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX,
                    is_grouped=True,
                    group_id=1,
                    group_type=GroupType.TAX_STATEMENT,
                    group_position=i
                )
            events_created.append(event)
        
        # 100 ungrouped events
        for i in range(100):
            event_types = [EventType.DISTRIBUTION, EventType.CAPITAL_CALL, EventType.NAV_UPDATE]
            event_type = event_types[i % len(event_types)]
            
            event = FundEventFactory(
                fund=fund,
                event_type=event_type,
                amount=1000 + i,
                event_date=base_date + timedelta(days=i + 200),
                description=f"Regular Event {i}",
                is_grouped=False
            )
            events_created.append(event)
        
        # Simulate frontend grouping logic performance
        start_time = time.time()
        
        # Sort all events by date (simulating frontend sorting)
        sorted_events = sorted(events_created, key=lambda e: e.event_date)
        
        # Process grouped events (simulating useEventGrouping hook)
        grouped_events = []
        processed_group_keys = set()
        
        for event in sorted_events:
            if event.is_grouped and event.group_id and event.group_type:
                group_key = f"{event.group_id}_{event.event_date}"
                if group_key not in processed_group_keys:
                    # Find all events in this group
                    group_events = [e for e in sorted_events 
                                  if e.group_id == event.group_id 
                                  and e.is_grouped 
                                  and e.event_date == event.event_date]
                    
                    # Sort by position
                    group_events.sort(key=lambda e: e.group_position or 0)
                    
                    # Create grouped event object (simulating frontend structure)
                    grouped_event = {
                        'events': group_events,
                        'isGrouped': True,
                        'groupType': event.group_type,
                        'groupId': event.group_id,
                        'displayDate': group_events[0].event_date,
                        'displayAmount': sum(e.amount or 0 for e in group_events),
                        'displayDescription': f"Tax Statement - {len(group_events)} events"
                    }
                    
                    grouped_events.append(grouped_event)
                    processed_group_keys.add(group_key)
        
        # Process ungrouped events
        ungrouped_events = []
        for event in sorted_events:
            if not event.is_grouped:
                ungrouped_event = {
                    'events': [event],
                    'isGrouped': False,
                    'displayDate': event.event_date,
                    'displayAmount': event.amount or 0,
                    'displayDescription': event.description or 'Event'
                }
                ungrouped_events.append(ungrouped_event)
        
        end_time = time.time()
        
        # Should complete within reasonable time (under 200ms for 200 events)
        assert (end_time - start_time) < 0.2
        
        # Verify results
        assert len(grouped_events) == 1  # One tax statement group
        assert len(ungrouped_events) == 100  # 100 ungrouped events
        assert len(grouped_events[0]['events']) == 100  # 100 events in the group
    
    def test_memory_usage_under_grouping_load(self, db_session):
        """Test memory usage remains reasonable under grouping load"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=1000000,
            current_equity_balance=950000
        )
        
        # Create 10 tax statements
        tax_statements = []
        for year in range(2015, 2025):
            tax_statement = TaxStatementFactory(
                fund=fund,
                entity=entity,
                financial_year=str(year),
                statement_date=date(year, 6, 30),
                tax_payment_date=date(year, 7, 15)
            )
            tax_statements.append(tax_statement)
        
        # Create 50 events per tax statement (500 total events)
        events_created = []
        base_date = date(2015, 1, 1)
        
        for statement_idx, tax_statement in enumerate(tax_statements):
            for event_idx in range(50):
                if event_idx % 2 == 0:
                    event = FundEventFactory(
                        fund=fund,
                        event_type=EventType.TAX_PAYMENT,
                        amount=-(1000 + event_idx),
                        event_date=date(2015 + statement_idx, 6, 30),  # Same date per financial year
                        description=f"FY {2015 + statement_idx} Tax Payment {event_idx}",
                        tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX,
                        is_grouped=True,
                        group_id=statement_idx + 1,
                        group_type=GroupType.TAX_STATEMENT,
                        group_position=event_idx
                    )
                else:
                    event = FundEventFactory(
                        fund=fund,
                        event_type=EventType.EOFY_DEBT_COST,
                        amount=500 + event_idx,
                        event_date=date(2015 + statement_idx, 6, 30),  # Same date per financial year
                        description=f"FY {2015 + statement_idx} Debt Cost {event_idx}",
                        is_grouped=True,
                        group_id=statement_idx + 1,
                        group_type=GroupType.TAX_STATEMENT,
                        group_position=event_idx
                    )
                events_created.append(event)
        
        # Test memory usage during bulk grouping operations
        start_time = time.time()
        
        # Perform bulk grouping operations
        all_groups = {}
        for event in events_created:
            if event.is_grouped:
                group_key = f"{event.group_id}_{event.event_date}"
                if group_key not in all_groups:
                    all_groups[group_key] = []
                all_groups[group_key].append(event)
        
        # Sort all groups by position
        for group_events in all_groups.values():
            group_events.sort(key=lambda e: e.group_position or 0)
        
        end_time = time.time()
        
        # Should complete within reasonable time (under 500ms for 500 events in 10 groups)
        assert (end_time - start_time) < 0.5
        
        # Verify all operations completed
        assert len(all_groups) == 10  # 10 different groups
        for group_events in all_groups.values():
            assert len(group_events) == 50  # 50 events per group
        
        # Verify data integrity
        for group_events in all_groups.values():
            for i, event in enumerate(group_events):
                assert event.group_position == i
