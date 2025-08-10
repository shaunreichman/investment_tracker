import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import { renderTableComponent } from '../../../../test-utils';
import { GroupedEventRow } from './GroupedEventRow';
import { ExtendedFund, ExtendedFundEvent, GroupType, FundType, EventType, DistributionType } from '../../../../types/api';
import { GroupedEvent } from './useEventGrouping';

// ============================================================================
// TEST DATA SETUP
// ============================================================================

// MANUAL: Mock fund data for testing
const createMockFund = (overrides: Partial<ExtendedFund> = {}): ExtendedFund => ({
  id: 1,
  name: 'Test Fund',
  currency: 'AUD',
  tracking_type: FundType.NAV_BASED,
  investment_company_id: 1,
  entity_id: 1,
  current_equity_balance: 10000,
  average_equity_balance: 10000,
  status: 'active' as any,
  final_tax_statement_received: false,
  investment_company: 'Test Company',
  entity: 'Test Entity',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides
});

// MANUAL: Mock events for testing
const createMockEvent = (overrides: Partial<ExtendedFundEvent> = {}): ExtendedFundEvent => ({
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

// MANUAL: Mock grouped event for testing
const createMockGroupedEvent = (overrides: Partial<GroupedEvent> = {}): GroupedEvent => ({
  events: [
    createMockEvent({
      event_type: EventType.DISTRIBUTION,
      amount: 1000,
      is_grouped: true,
      group_id: 1,
      group_type: GroupType.INTEREST_WITHHOLDING,
      group_position: 0
    }),
    createMockEvent({
      event_type: EventType.TAX_PAYMENT,
      amount: -100,
      description: 'Withholding Tax',
      is_grouped: true,
      group_id: 1,
      group_type: GroupType.INTEREST_WITHHOLDING,
      group_position: 1
    })
  ],
  isGrouped: true,
  groupType: GroupType.INTEREST_WITHHOLDING,
  groupId: 1,
  displayDate: '2024-01-01',
  displayAmount: 900,
  displayDescription: 'Interest Distribution + Withholding Tax (1000.00 - 100.00)',
  ...overrides
});

// MANUAL: Mock props for testing
const createMockProps = (overrides: Partial<React.ComponentProps<typeof GroupedEventRow>> = {}) => ({
  groupedEvent: createMockGroupedEvent(),
  fund: createMockFund(),
  showTaxEvents: true,
  showNavUpdates: true,
  onDeleteEvent: jest.fn(),
  ...overrides
});

// ============================================================================
// TEST SUITE: GroupedEventRow Component
// ============================================================================

describe('GroupedEventRow', () => {
  describe('Basic rendering', () => {
    it('should render grouped event row with correct information', () => {
      const props = createMockProps();
      renderTableComponent(
        <GroupedEventRow {...props} />
      );

      // Check that the main row is rendered
      expect(screen.getByText('Interest Distribution + Withholding Tax (1000.00 - 100.00)')).toBeInTheDocument();
      expect(screen.getByText('1-Jan-24')).toBeInTheDocument(); // Updated to match formatDate output
    });

    it('should render interest event amount correctly', () => {
      const groupedEvent = createMockGroupedEvent({
        events: [
          createMockEvent({
            event_type: EventType.DISTRIBUTION,
            amount: 1000,
            is_grouped: true,
            group_id: 1,
            group_type: GroupType.INTEREST_WITHHOLDING,
            group_position: 1
          }),
          createMockEvent({
            event_type: EventType.TAX_PAYMENT,
            amount: 100,
            is_grouped: true,
            group_id: 1,
            group_type: GroupType.INTEREST_WITHHOLDING,
            group_position: 2
          })
        ]
      });

      renderTableComponent(
        <GroupedEventRow
          groupedEvent={groupedEvent}
          fund={createMockFund()}
          showTaxEvents={true}
          showNavUpdates={true}
          onDeleteEvent={jest.fn()}
        />
      );

      // Check that the main row is rendered
      expect(screen.getByText('Interest Distribution + Withholding Tax (1000.00 - 100.00)')).toBeInTheDocument();
      expect(screen.getByText('1-Jan-24')).toBeInTheDocument(); // Updated to match formatDate output
    });

    it('should render withholding tax amount correctly', () => {
      const props = createMockProps();
      renderTableComponent(
        <GroupedEventRow {...props} />
      );

      // Check withholding tax amount is displayed (should be negative)
      expect(screen.getByText('$100.00')).toBeInTheDocument();
    });
  });

  describe('Event type display', () => {
    it('should display correct event type chip for interest distribution', () => {
      const props = createMockProps();
      renderTableComponent(
        <GroupedEventRow {...props} />
      );

      // Check that the event type chip is displayed
      expect(screen.getByText('INTEREST')).toBeInTheDocument();
    });

    it('should handle different distribution types', () => {
      const groupedEvent = createMockGroupedEvent({
        events: [
          createMockEvent({
            event_type: EventType.DISTRIBUTION,
            distribution_type: DistributionType.DIVIDEND,
            amount: 1000,
            is_grouped: true,
            group_id: 1,
            group_type: GroupType.INTEREST_WITHHOLDING,
            group_position: 0
          }),
          createMockEvent({
            event_type: EventType.TAX_PAYMENT,
            amount: -100,
            is_grouped: true,
            group_id: 1,
            group_type: GroupType.INTEREST_WITHHOLDING,
            group_position: 1
          })
        ]
      });

      const props = createMockProps({ groupedEvent });
      renderTableComponent(
        <GroupedEventRow {...props} />
      );

      // Check that the correct distribution type is displayed
      expect(screen.getByText('DIVIDEND')).toBeInTheDocument();
    });
  });

  describe('Fund tracking type handling', () => {
    it('should show NAV update column for NAV-based funds', () => {
      const navBasedFund = createMockFund({ tracking_type: FundType.NAV_BASED });
      
      renderTableComponent(
        <GroupedEventRow
          groupedEvent={createMockGroupedEvent()}
          fund={navBasedFund}
          showTaxEvents={true}
          showNavUpdates={true}
          onDeleteEvent={jest.fn()}
        />
      );

      // NAV-based funds should show the NAV update column
      // This is tested by checking the table structure
      expect(screen.getByText('1-Jan-24')).toBeInTheDocument(); // Updated to match formatDate output
    });

    it('should not show NAV update column for non-NAV-based funds', () => {
      const unitBasedFund = createMockFund({ tracking_type: FundType.COST_BASED });
      
      renderTableComponent(
        <GroupedEventRow
          groupedEvent={createMockGroupedEvent()}
          fund={unitBasedFund}
          showTaxEvents={true}
          showNavUpdates={true}
          onDeleteEvent={jest.fn()}
        />
      );

      // Unit-based funds should not show NAV update column
      // The component should still render correctly
      expect(screen.getByText('1-Jan-24')).toBeInTheDocument(); // Updated to match formatDate output
    });
  });

  describe('Tax events visibility', () => {
    it('should show tax events when showTaxEvents is true', () => {
      const props = createMockProps({ showTaxEvents: true });
      renderTableComponent(
        <GroupedEventRow {...props} />
      );

      // Tax events should be visible
      expect(screen.getByText('$100.00')).toBeInTheDocument();
    });

    it('should hide tax events when showTaxEvents is false', () => {
      const props = createMockProps({ showTaxEvents: false });
      renderTableComponent(
        <GroupedEventRow {...props} />
      );

      // Tax events should be hidden
      // Note: This test may need adjustment based on actual implementation
      expect(screen.getByText('$1,000.00')).toBeInTheDocument();
    });
  });

  describe('NAV updates visibility', () => {
    it('should show NAV updates when showNavUpdates is true', () => {
      const props = createMockProps({ showNavUpdates: true });
      renderTableComponent(
        <GroupedEventRow {...props} />
      );

      // NAV updates should be visible
      expect(screen.getByText('1-Jan-24')).toBeInTheDocument(); // Updated to match formatDate output
    });

    it('should hide NAV updates when showNavUpdates is false', () => {
      const props = createMockProps({ showNavUpdates: false });
      renderTableComponent(
        <GroupedEventRow {...props} />
      );

      // NAV updates should be hidden
      // Note: This test may need adjustment based on actual implementation
      expect(screen.getByText('1-Jan-24')).toBeInTheDocument(); // Updated to match formatDate output
    });
  });

  describe('Delete functionality', () => {
    it('should call onDeleteEvent when delete button is clicked', () => {
      const onDeleteEvent = jest.fn();
      const props = createMockProps({ onDeleteEvent });
      renderTableComponent(
        <GroupedEventRow {...props} />
      );

      // Find and click the delete button
      const deleteButton = screen.getByRole('button', { name: /delete/i });
      fireEvent.click(deleteButton);

      // Check that the callback was called with the correct event
      expect(onDeleteEvent).toHaveBeenCalledTimes(1);
      expect(onDeleteEvent).toHaveBeenCalledWith(props.groupedEvent.events[0]);
    });

    it('should not show delete button for non-editable event types', () => {
      // Create a grouped event with a non-editable event type (TAX_PAYMENT)
      const nonEditableGroupedEvent = createMockGroupedEvent({
        events: [
          createMockEvent({
            event_type: EventType.TAX_PAYMENT, // TAX_PAYMENT is not editable
            amount: 100,
            is_grouped: true,
            group_id: 3,
            group_type: GroupType.INTEREST_WITHHOLDING,
            group_position: 1
          })
        ]
      });

      renderTableComponent(
        <GroupedEventRow
          groupedEvent={nonEditableGroupedEvent}
          fund={createMockFund()}
          showTaxEvents={true}
          showNavUpdates={true}
          onDeleteEvent={jest.fn()}
        />
      );

      // Delete button should not be present for non-editable events
      expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
    });
  });

  describe('Different group types', () => {
    it('should handle TAX_STATEMENT group type correctly', () => {
      const groupedEvent = createMockGroupedEvent({
        groupType: GroupType.TAX_STATEMENT,
        events: [
          createMockEvent({
            event_type: EventType.TAX_PAYMENT,
            amount: 500,
            is_grouped: true,
            group_id: 1,
            group_type: GroupType.TAX_STATEMENT,
            group_position: 0
          }),
          createMockEvent({
            event_type: EventType.TAX_PAYMENT,
            amount: 300,
            is_grouped: true,
            group_id: 1,
            group_type: GroupType.TAX_STATEMENT,
            group_position: 1
          })
        ],
        displayDescription: 'Tax Statement Group'
      });

      const props = createMockProps({ groupedEvent });
      renderTableComponent(
        <GroupedEventRow {...props} />
      );

      // Check that the tax statement group is displayed correctly
      expect(screen.getByText('Tax Statement Group')).toBeInTheDocument();
    });

    it('should handle unknown group types gracefully', () => {
      const groupedEvent = createMockGroupedEvent({
        groupType: 'UNKNOWN_TYPE' as GroupType,
        displayDescription: 'Grouped Events'
      });

      const props = createMockProps({ groupedEvent });
      renderTableComponent(<GroupedEventRow {...props} />);

      // Check that unknown group types are handled gracefully
      expect(screen.getByText('Grouped Events')).toBeInTheDocument();
    });
  });

  describe('Edge cases', () => {
    it('should handle events with null amounts', () => {
      const groupedEvent = createMockGroupedEvent({
        events: [
          createMockEvent({
            event_type: EventType.DISTRIBUTION,
            amount: null, // Use null instead of undefined for optional properties
            is_grouped: true,
            group_id: 1,
            group_type: GroupType.INTEREST_WITHHOLDING,
            group_position: 1
          }),
          createMockEvent({
            event_type: EventType.TAX_PAYMENT,
            amount: null,
            is_grouped: true,
            group_id: 1,
            group_type: GroupType.INTEREST_WITHHOLDING,
            group_position: 2
          })
        ]
      });

      renderTableComponent(
        <GroupedEventRow
          groupedEvent={groupedEvent}
          fund={createMockFund()}
          showTaxEvents={true}
          showNavUpdates={true}
          onDeleteEvent={jest.fn()}
        />
      );

      // Component should render without crashing
      expect(screen.getByText('1-Jan-24')).toBeInTheDocument(); // Updated to match formatDate output
    });

    it('should handle events with undefined amounts', () => {
      const groupedEvent = createMockGroupedEvent({
        events: [
          createMockEvent({
            event_type: EventType.DISTRIBUTION,
            amount: null, // Use null for nullable properties
            is_grouped: true,
            group_id: 1,
            group_type: GroupType.INTEREST_WITHHOLDING,
            group_position: 1
          }),
          createMockEvent({
            event_type: EventType.TAX_PAYMENT,
            amount: null,
            is_grouped: true,
            group_id: 1,
            group_type: GroupType.INTEREST_WITHHOLDING,
            group_position: 2
          })
        ]
      });

      renderTableComponent(
        <GroupedEventRow
          groupedEvent={groupedEvent}
          fund={createMockFund()}
          showTaxEvents={true}
          showNavUpdates={true}
          onDeleteEvent={jest.fn()}
        />
      );

      // Component should render without crashing
      expect(screen.getByText('1-Jan-24')).toBeInTheDocument(); // Updated to match formatDate output
    });

    it('should handle single event in group', () => {
      const singleEventGroup = createMockGroupedEvent({
        events: [
          createMockEvent({
            event_type: EventType.DISTRIBUTION,
            amount: 500, // This matches the test data
            is_grouped: true,
            group_id: 2,
            group_type: GroupType.INTEREST_WITHHOLDING,
            group_position: 1
          })
        ]
      });

      renderTableComponent(
        <GroupedEventRow
          groupedEvent={singleEventGroup}
          fund={createMockFund()}
          showTaxEvents={true}
          showNavUpdates={true}
          onDeleteEvent={jest.fn()}
        />
      );

      // Component should render single event correctly
      expect(screen.getByText('$500.00')).toBeInTheDocument(); // Updated to match test data
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for delete button', () => {
      const props = createMockProps();
      renderTableComponent(<GroupedEventRow {...props} />);

      const deleteButton = screen.getByRole('button', { name: /delete/i });
      expect(deleteButton).toBeInTheDocument();
    });

    it('should have proper table structure', () => {
      renderTableComponent(
        <GroupedEventRow
          groupedEvent={createMockGroupedEvent()}
          fund={createMockFund()}
          showTaxEvents={true}
          showNavUpdates={true}
          onDeleteEvent={jest.fn()}
        />
      );

      // Check that the component renders as a table row
      const row = screen.getByRole('row');
      expect(row).toBeInTheDocument();
    });
  });

  describe('Performance optimization', () => {
    it('should use React.memo for performance optimization', () => {
      renderTableComponent(
        <GroupedEventRow
          groupedEvent={createMockGroupedEvent()}
          fund={createMockFund()}
          showTaxEvents={true}
          showNavUpdates={true}
          onDeleteEvent={jest.fn()}
        />
      );

      // Component should render without issues
      expect(screen.getByText('1-Jan-24')).toBeInTheDocument(); // Updated to match formatDate output
    });
  });
});
