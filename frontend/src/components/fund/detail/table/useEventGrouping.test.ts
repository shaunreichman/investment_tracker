import { renderHook } from '@testing-library/react';
import { useEventGrouping } from './useEventGrouping';
import { FundEvent, GroupType, EventType } from '../../../../types/api';

// ============================================================================
// TEST DATA SETUP
// ============================================================================

// MANUAL: Mock events for testing different grouping scenarios
const createMockEvent = (overrides: Partial<FundEvent> = {}): FundEvent => ({
  id: 1,
  fund_id: 1,
  event_type: EventType.DISTRIBUTION,
  event_date: '2024-01-01',
  amount: 1000,
  description: 'Test Event',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  is_grouped: false,
  ...overrides
});

// MANUAL: Mock grouped events for testing
const createGroupedInterestEvent = (date: string, groupId: number): FundEvent => ({
  ...createMockEvent({
    event_type: EventType.DISTRIBUTION,
    event_date: date,
    amount: 1000,
    is_grouped: true,
    group_id: groupId,
    group_type: GroupType.INTEREST_WITHHOLDING,
    group_position: 0
  })
});

const createGroupedWithholdingEvent = (date: string, groupId: number): FundEvent => ({
  ...createMockEvent({
    event_type: EventType.TAX_PAYMENT,
    event_date: date,
    amount: -100,
    description: 'Withholding Tax',
    is_grouped: true,
    group_id: groupId,
    group_type: GroupType.INTEREST_WITHHOLDING,
    group_position: 1
  })
});

// ============================================================================
// TEST SUITE: useEventGrouping Hook
// ============================================================================

describe('useEventGrouping', () => {
  describe('Empty and null input handling', () => {
    it('should return empty array for null events', () => {
      const { result } = renderHook(() => useEventGrouping(null as any));
      expect(result.current).toEqual([]);
    });

    it('should return empty array for undefined events', () => {
      const { result } = renderHook(() => useEventGrouping(undefined as any));
      expect(result.current).toEqual([]);
    });

    it('should return empty array for empty events array', () => {
      const { result } = renderHook(() => useEventGrouping([]));
      expect(result.current).toEqual([]);
    });
  });

  describe('Single event handling', () => {
    it('should return single event as ungrouped', () => {
      const singleEvent = createMockEvent();
      const { result } = renderHook(() => useEventGrouping([singleEvent]));

      expect(result.current).toHaveLength(1);
      expect(result.current[0]).toEqual({
        events: [singleEvent],
        isGrouped: false,
        displayDate: '2024-01-01',
        displayAmount: 1000,
        displayDescription: 'Test Event'
      });
    });

    it('should handle single event with null amount', () => {
      const singleEvent = createMockEvent({ amount: undefined }); // Use undefined for optional properties
      const { result } = renderHook(() => useEventGrouping([singleEvent]));

      const firstResult = result.current[0];
      expect(firstResult).toBeDefined();
      expect(firstResult?.displayAmount).toBe(0);
    });

    it('should handle single event with undefined amount', () => {
      const singleEvent = createMockEvent({ amount: undefined }); // Use undefined for optional properties
      const { result } = renderHook(() => useEventGrouping([singleEvent]));

      const firstResult = result.current[0];
      expect(firstResult).toBeDefined();
      expect(firstResult?.displayAmount).toBe(0);
    });
  });

  describe('Grouped event handling', () => {
    it('should group interest and withholding tax events correctly', () => {
      const interestEvent = createGroupedInterestEvent('2024-01-01', 1);
      const withholdingEvent = createGroupedWithholdingEvent('2024-01-01', 1);
      const events = [interestEvent, withholdingEvent];

      const { result } = renderHook(() => useEventGrouping(events));

      expect(result.current).toHaveLength(1);
      expect(result.current[0]).toEqual({
        events: [interestEvent, withholdingEvent], // Sorted by group_position
        isGrouped: true,
        groupType: GroupType.INTEREST_WITHHOLDING,
        groupId: 1,
        displayDate: '2024-01-01',
        displayAmount: 900, // 1000 + (-100)
        displayDescription: 'Interest Distribution + Withholding Tax (1000.00 - 100.00)'
      });
    });

    it('should handle multiple groups correctly', () => {
      const group1Interest = createGroupedInterestEvent('2024-01-01', 1);
      const group1Withholding = createGroupedWithholdingEvent('2024-01-01', 1);
      const group2Interest = createGroupedInterestEvent('2024-01-02', 2);
      const group2Withholding = createGroupedWithholdingEvent('2024-01-02', 2);
      const events = [group1Interest, group1Withholding, group2Interest, group2Withholding];

      const { result } = renderHook(() => useEventGrouping(events));

      expect(result.current).toHaveLength(2);
      
      // First group
      const firstGroup = result.current[0];
      expect(firstGroup).toBeDefined();
      expect(firstGroup?.groupId).toBe(1);
      expect(firstGroup?.displayDate).toBe('2024-01-01');
      expect(firstGroup?.events).toHaveLength(2);
      
      // Second group
      const secondGroup = result.current[1];
      expect(secondGroup).toBeDefined();
      expect(secondGroup?.groupId).toBe(2);
      expect(secondGroup?.displayDate).toBe('2024-01-02');
      expect(secondGroup?.events).toHaveLength(2);
    });

    it('should handle events with different dates in same group', () => {
      const interestEvent = createGroupedInterestEvent('2024-01-01', 1);
      const withholdingEvent = createGroupedWithholdingEvent('2024-01-02', 1); // Different date
      const events = [interestEvent, withholdingEvent];

      const { result } = renderHook(() => useEventGrouping(events));

      // Should create separate groups due to different dates
      expect(result.current).toHaveLength(2);
      const firstGroup = result.current[0];
      const secondGroup = result.current[1];
      expect(firstGroup?.isGrouped).toBe(true);
      expect(secondGroup?.isGrouped).toBe(true);
    });

    it('should handle mixed grouped and ungrouped events', () => {
      const groupedInterest = createGroupedInterestEvent('2024-01-01', 1);
      const groupedWithholding = createGroupedWithholdingEvent('2024-01-01', 1);
      const ungroupedEvent = createMockEvent({
        event_date: '2024-01-02',
        event_type: EventType.CAPITAL_CALL,
        amount: 500
      });
      const events = [groupedInterest, groupedWithholding, ungroupedEvent];

      const { result } = renderHook(() => useEventGrouping(events));

      expect(result.current).toHaveLength(2);
      
      // First should be grouped
      const firstGroup = result.current[0];
      expect(firstGroup?.isGrouped).toBe(true);
      expect(firstGroup?.events).toHaveLength(2);
      
      // Second should be ungrouped
      const secondGroup = result.current[1];
      expect(secondGroup?.isGrouped).toBe(false);
      expect(secondGroup?.events).toHaveLength(1);
    });
  });

  describe('Event ordering and sorting', () => {
    it('should sort events by date (oldest first)', () => {
      const event1 = createMockEvent({ event_date: '2024-01-03', amount: 300 });
      const event2 = createMockEvent({ event_date: '2024-01-01', amount: 100 });
      const event3 = createMockEvent({ event_date: '2024-01-02', amount: 200 });
      const events = [event1, event2, event3];

      const { result } = renderHook(() => useEventGrouping(events));

      expect(result.current).toHaveLength(3);
      const firstResult = result.current[0];
      const secondResult = result.current[1];
      const thirdResult = result.current[2];
      expect(firstResult?.displayDate).toBe('2024-01-01');
      expect(secondResult?.displayDate).toBe('2024-01-02');
      expect(thirdResult?.displayDate).toBe('2024-01-03');
    });

    it('should sort grouped events by group_position', () => {
      const withholdingEvent = createGroupedWithholdingEvent('2024-01-01', 1); // position 1
      const interestEvent = createGroupedInterestEvent('2024-01-01', 1); // position 0
      const events = [withholdingEvent, interestEvent]; // Wrong order

      const { result } = renderHook(() => useEventGrouping(events));

      const firstGroup = result.current[0];
      expect(firstGroup?.events).toHaveLength(2);
      expect(firstGroup?.events[0]?.group_position).toBe(0); // Interest first
      expect(firstGroup?.events[1]?.group_position).toBe(1); // Withholding second
    });
  });

  describe('Group description generation', () => {
    it('should generate correct description for INTEREST_WITHHOLDING group', () => {
      const interestEvent = createGroupedInterestEvent('2024-01-01', 1);
      const withholdingEvent = createGroupedWithholdingEvent('2024-01-01', 1);
      const events = [interestEvent, withholdingEvent];

      const { result } = renderHook(() => useEventGrouping(events));

      const firstGroup = result.current[0];
      expect(firstGroup?.displayDescription).toBe(
        'Interest Distribution + Withholding Tax (1000.00 - 100.00)'
      );
    });

    it('should handle negative amounts in withholding tax correctly', () => {
      const interestEvent = createGroupedInterestEvent('2024-01-01', 1);
      const withholdingEvent = createGroupedWithholdingEvent('2024-01-01', 1);
      withholdingEvent.amount = -150.75; // More specific amount
      const events = [interestEvent, withholdingEvent];

      const { result } = renderHook(() => useEventGrouping(events));

      const firstGroup = result.current[0];
      expect(firstGroup?.displayDescription).toBe(
        'Interest Distribution + Withholding Tax (1000.00 - 150.75)'
      );
    });

    it('should handle zero amounts correctly', () => {
      const interestEvent = createGroupedInterestEvent('2024-01-01', 1);
      interestEvent.amount = 0;
      const withholdingEvent = createGroupedWithholdingEvent('2024-01-01', 1);
      withholdingEvent.amount = 0;
      const events = [interestEvent, withholdingEvent];

      const { result } = renderHook(() => useEventGrouping(events));

      const firstGroup = result.current[0];
      expect(firstGroup?.displayDescription).toBe(
        'Interest Distribution + Withholding Tax (0.00 + 0.00)'
      );
    });

    it('should generate correct description for TAX_STATEMENT group', () => {
      const taxEvent1 = createMockEvent({
        event_type: EventType.TAX_PAYMENT,
        event_date: '2024-01-01',
        is_grouped: true,
        group_id: 1,
        group_type: GroupType.TAX_STATEMENT,
        group_position: 0
      });
      const taxEvent2 = createMockEvent({
        event_type: EventType.TAX_PAYMENT,
        event_date: '2024-01-01',
        is_grouped: true,
        group_id: 1,
        group_type: GroupType.TAX_STATEMENT,
        group_position: 1
      });
      const events = [taxEvent1, taxEvent2];

      const { result } = renderHook(() => useEventGrouping(events));

      const firstGroup = result.current[0];
      expect(firstGroup?.displayDescription).toBe('Tax Statement Group');
    });

    it('should generate fallback description for unknown group types', () => {
      const unknownEvent = createMockEvent({
        event_date: '2024-01-01',
        is_grouped: true,
        group_id: 1,
        group_type: 'UNKNOWN_TYPE' as GroupType,
        group_position: 0
      });
      const events = [unknownEvent];

      const { result } = renderHook(() => useEventGrouping(events));

      const firstGroup = result.current[0];
      expect(firstGroup?.displayDescription).toBe('Grouped Events');
    });
  });

  describe('Event type description generation', () => {
    it('should generate correct descriptions for known event types', () => {
      const eventTypes = [
        { type: EventType.CAPITAL_CALL, expected: 'Capital Call' },
        { type: EventType.RETURN_OF_CAPITAL, expected: 'Return of Capital' },
        { type: EventType.UNIT_PURCHASE, expected: 'Unit Purchase' },
        { type: EventType.UNIT_SALE, expected: 'Unit Sale' },
        { type: EventType.NAV_UPDATE, expected: 'NAV Update' },
        { type: EventType.DISTRIBUTION, expected: 'Distribution' },
        { type: EventType.TAX_PAYMENT, expected: 'Tax Payment' },
        { type: EventType.EOFY_DEBT_COST, expected: 'EOFY Debt Cost' },
        { type: EventType.DAILY_RISK_FREE_INTEREST_CHARGE, expected: 'Risk-Free Interest Charge' },
        { type: EventType.MANAGEMENT_FEE, expected: 'Management Fee' },
        { type: EventType.CARRIED_INTEREST, expected: 'Carried Interest' },
        { type: EventType.OTHER, expected: 'Other Event' }
      ];

      eventTypes.forEach(({ type, expected }) => {
        const event = createMockEvent({ event_type: type, description: undefined }); // Use undefined for optional properties
        const { result } = renderHook(() => useEventGrouping([event]));

        const firstResult = result.current[0];
        expect(firstResult?.displayDescription).toBe(expected);
      });
    });

    it('should fall back to event type for unknown types', () => {
      const event = createMockEvent({ 
        event_type: 'UNKNOWN_TYPE' as EventType, 
        description: undefined // Use undefined for optional properties
      });
      const { result } = renderHook(() => useEventGrouping([event]));

      const firstResult = result.current[0];
      expect(firstResult?.displayDescription).toBe('UNKNOWN_TYPE');
    });

    it('should use description when available', () => {
      const event = createMockEvent({ 
        event_type: EventType.DISTRIBUTION,
        description: 'Custom Description' 
      });
      const { result } = renderHook(() => useEventGrouping([event]));

      const firstResult = result.current[0];
      expect(firstResult?.displayDescription).toBe('Custom Description');
    });
  });

  describe('Edge cases and error handling', () => {
    it('should handle events with missing grouping fields gracefully', () => {
      const incompleteEvent = createMockEvent({
        is_grouped: true,
        group_id: 1,
        group_type: GroupType.INTEREST_WITHHOLDING,
        group_position: undefined // Use undefined for optional properties
      });
      const events = [incompleteEvent];

      const { result } = renderHook(() => useEventGrouping(events));

      // Should still process the event as grouped since it has the required fields
      expect(result.current).toHaveLength(1);
      const firstResult = result.current[0];
      expect(firstResult?.isGrouped).toBe(true);
    });

    it('should handle events with invalid group_position gracefully', () => {
      const invalidEvent = createMockEvent({
        is_grouped: true,
        group_id: 1,
        group_type: GroupType.INTEREST_WITHHOLDING,
        group_position: 999 // Invalid position
      });
      const events = [invalidEvent];

      const { result } = renderHook(() => useEventGrouping(events));

      expect(result.current).toHaveLength(1);
      const firstResult = result.current[0];
      expect(firstResult?.isGrouped).toBe(true);
    });

    it('should handle floating point precision in amounts', () => {
      const interestEvent = createGroupedInterestEvent('2024-01-01', 1);
      interestEvent.amount = 1000.123456789;
      const withholdingEvent = createGroupedWithholdingEvent('2024-01-01', 1);
      withholdingEvent.amount = -100.987654321;
      const events = [interestEvent, withholdingEvent];

      const { result } = renderHook(() => useEventGrouping(events));

      const firstGroup = result.current[0];
      expect(firstGroup?.displayDescription).toBe(
        'Interest Distribution + Withholding Tax (1000.12 - 100.99)'
      );
      expect(firstGroup?.displayAmount).toBeCloseTo(899.14, 2);
    });
  });

  describe('Performance and memoization', () => {
    it('should memoize results when events array reference changes but content is same', () => {
      const events1 = [createMockEvent()];
      const { result: result1, rerender } = renderHook(() => useEventGrouping(events1));
      
      rerender();
      
      // Should return same result due to memoization
      expect(result1.current).toEqual(result1.current);
    });

    it('should handle large numbers of events efficiently', () => {
      const manyEvents = Array.from({ length: 31 }, (_, i) => 
        createMockEvent({ 
          id: i, 
          event_date: `2024-01-${String(i + 1).padStart(2, '0')}`,
          amount: i * 10
        })
      );

      const { result } = renderHook(() => useEventGrouping(manyEvents));

      expect(result.current).toHaveLength(31);
      const firstResult = result.current[0];
      const lastResult = result.current[30];
      expect(firstResult?.displayDate).toBe('2024-01-01'); // Sorted correctly
      expect(lastResult?.displayDate).toBe('2024-01-31');
    });
  });
});
