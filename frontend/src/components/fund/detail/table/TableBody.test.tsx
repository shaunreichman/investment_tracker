import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { TableBody } from './TableBody';
import { ExtendedFundEvent, ExtendedFund, FundTrackingType, FundStatus, EventType, DistributionType, TaxPaymentType } from '../../../../types/api';

// ============================================================================
// TABLE BODY COMPONENT TESTS
// ============================================================================

const theme = createTheme();

// Mock the extracted components
jest.mock('./EventRow', () => ({
  EventRow: ({ event }: { event: ExtendedFundEvent }) => (
    <tr data-testid={`event-row-${event.id}`}>
      <td>Event Row: {event.event_type} - {event.description}</td>
    </tr>
  )
}));

jest.mock('./GroupedEventRow', () => ({
  GroupedEventRow: ({ groupedEvent }: { groupedEvent: any }) => (
    <tr data-testid={`grouped-row-${groupedEvent.groupId}`}>
      <td>Grouped Row: {groupedEvent.displayDate}</td>
    </tr>
  )
}));

// Mock the useEventGrouping hook
jest.mock('./useEventGrouping', () => ({
  useEventGrouping: jest.fn()
}));

const mockUseEventGrouping = require('./useEventGrouping').useEventGrouping;

// Test data
const mockFund: ExtendedFund = {
  id: 1,
  name: 'Test Fund',
  tracking_type: FundTrackingType.COST_BASED,
  currency: 'AUD',
  investment_company: 'Test Company',
  entity: 'Test Entity',
  fund_type: 'Private Equity',
  investment_company_id: 1,
  entity_id: 1,
  current_equity_balance: 100000,
  average_equity_balance: 95000,
  status: FundStatus.ACTIVE,
  final_tax_statement_received: false,
  created_at: '2023-01-01',
  updated_at: '2023-01-01'
};

const mockEvents: ExtendedFundEvent[] = [
  {
    id: 1,
    fund_id: 1,
    event_type: EventType.CAPITAL_CALL,
    event_date: '2023-01-01',
    amount: 100000,
    description: 'Initial capital call',
    created_at: '2023-01-01',
    updated_at: '2023-01-01'
  },
  {
    id: 2,
    fund_id: 1,
    event_type: EventType.DISTRIBUTION,
    event_date: '2023-06-30',
    amount: 5000,
    distribution_type: DistributionType.INTEREST,
    description: 'Interest distribution',
    created_at: '2023-06-30',
    updated_at: '2023-06-30'
  },
  {
    id: 3,
    fund_id: 1,
    event_type: EventType.TAX_PAYMENT,
    event_date: '2023-06-30',
    amount: 500,
    tax_payment_type: TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING,
    description: 'Withholding tax',
    created_at: '2023-06-30',
    updated_at: '2023-06-30'
  }
];

const mockHandlers = {
  
  onDeleteEvent: jest.fn()
};

const renderTableBody = (props: any) => {
  return render(
    <ThemeProvider theme={theme}>
      <table>
        <TableBody {...props} />
      </table>
    </ThemeProvider>
  );
};

describe('TableBody', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render individual events when no grouped events', () => {
    // Mock the new flag-based grouping interface
    const individualEvents = mockEvents.slice(0, 2).map(event => ({
      events: [event],
      isGrouped: false,
      displayDate: event.event_date,
      displayAmount: event.amount || 0,
      displayDescription: event.description || 'Test Event'
    }));

    mockUseEventGrouping.mockReturnValue(individualEvents);

    renderTableBody({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    expect(screen.getByTestId('event-row-1')).toBeInTheDocument();
    expect(screen.getByTestId('event-row-2')).toBeInTheDocument();
    expect(screen.queryByTestId(/grouped-row/)).not.toBeInTheDocument();
  });

  it('should render grouped events when interest + withholding pairs exist', () => {
    // Mock the new flag-based grouping interface
    const groupedEvent = {
      events: mockEvents.slice(1, 3), // Interest + withholding events
      isGrouped: true,
      groupType: 'interest_withholding',
      groupId: 1,
      displayDate: '2023-06-30',
      displayAmount: 5500, // 5000 + 500
      displayDescription: 'Interest Distribution + Withholding Tax (5000 + 500)'
    };

    const individualEvent = {
      events: [mockEvents[0]!], // Capital call - use non-null assertion
      isGrouped: false,
      displayDate: mockEvents[0]!.event_date,
      displayAmount: mockEvents[0]!.amount || 0,
      displayDescription: mockEvents[0]!.description || 'Test Event'
    };

    mockUseEventGrouping.mockReturnValue([groupedEvent, individualEvent]);

    renderTableBody({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    expect(screen.getByTestId('grouped-row-1')).toBeInTheDocument();
    expect(screen.getByTestId('event-row-1')).toBeInTheDocument();
  });

  it('should pass correct props to EventRow components', () => {
    // Mock the new flag-based grouping interface
    const individualEvent = {
      events: [mockEvents[0]!], // Use non-null assertion
      isGrouped: false,
      displayDate: mockEvents[0]!.event_date,
      displayAmount: mockEvents[0]!.amount || 0,
      displayDescription: mockEvents[0]!.description || 'Test Event'
    };

    mockUseEventGrouping.mockReturnValue([individualEvent]);

    renderTableBody({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    // Verify EventRow is rendered with correct props
    expect(screen.getByTestId('event-row-1')).toBeInTheDocument();
  });

  it('should pass correct props to GroupedEventRow components', () => {
    // Mock the new flag-based grouping interface
    const groupedEvent = {
      events: mockEvents.slice(1, 3),
      isGrouped: true,
      groupType: 'interest_withholding',
      groupId: 1,
      displayDate: '2023-06-30',
      displayAmount: 5500,
      displayDescription: 'Interest Distribution + Withholding Tax (5000 + 500)'
    };

    mockUseEventGrouping.mockReturnValue([groupedEvent]);

    renderTableBody({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    // Verify GroupedEventRow is rendered
    expect(screen.getByTestId('grouped-row-1')).toBeInTheDocument();
  });

  it('should handle empty events array', () => {
    mockUseEventGrouping.mockReturnValue([]);

    renderTableBody({
      events: [],
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    // Should render empty table body without errors
    expect(screen.getByRole('table')).toBeInTheDocument();
  });

  it('should call useEventGrouping with correct parameters', () => {
    mockUseEventGrouping.mockReturnValue([]);

    renderTableBody({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: false,
      showNavUpdates: true,
      ...mockHandlers
    });

    expect(mockUseEventGrouping).toHaveBeenCalledWith(mockEvents);
  });


}); 