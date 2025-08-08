import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { TableBody } from './TableBody';
import { ExtendedFundEvent, ExtendedFund, FundType, FundStatus, EventType, DistributionType, TaxPaymentType } from '../../../../types/api';

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
    <tr data-testid={`grouped-row-${groupedEvent.date}`}>
      <td>Grouped Row: {groupedEvent.date}</td>
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
  tracking_type: FundType.COST_BASED,
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
    mockUseEventGrouping.mockReturnValue({
      groupedEvents: [],
      individualEvents: mockEvents.slice(0, 2), // First two events
      sortedEvents: mockEvents.slice(0, 2),
      totalEvents: 2,
      totalGroups: 0,
      interestWithholdingPairs: 0
    });

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
    const groupedEvents = [{
      date: '2023-06-30',
      events: mockEvents.slice(1, 3), // Interest + withholding events
      hasInterestWithholdingPair: true,
      interestEvent: mockEvents[1],
      withholdingEvent: mockEvents[2],
      otherEvents: []
    }];

    mockUseEventGrouping.mockReturnValue({
      groupedEvents,
      individualEvents: mockEvents.slice(0, 1), // Only capital call
      sortedEvents: [groupedEvents[0], ...mockEvents.slice(0, 1)],
      totalEvents: 3,
      totalGroups: 1,
      interestWithholdingPairs: 1
    });

    renderTableBody({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    expect(screen.getByTestId('grouped-row-2023-06-30')).toBeInTheDocument();
    expect(screen.getByTestId('event-row-1')).toBeInTheDocument();
  });

  it('should pass correct props to EventRow components', () => {
    mockUseEventGrouping.mockReturnValue({
      groupedEvents: [],
      individualEvents: mockEvents.slice(0, 1),
      sortedEvents: mockEvents.slice(0, 1),
      totalEvents: 1,
      totalGroups: 0,
      interestWithholdingPairs: 0
    });

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
    const groupedEvents = [{
      date: '2023-06-30',
      events: mockEvents.slice(1, 3),
      hasInterestWithholdingPair: true,
      interestEvent: mockEvents[1],
      withholdingEvent: mockEvents[2],
      otherEvents: []
    }];

    mockUseEventGrouping.mockReturnValue({
      groupedEvents,
      individualEvents: [],
      sortedEvents: groupedEvents,
      totalEvents: 2,
      totalGroups: 1,
      interestWithholdingPairs: 1
    });

    renderTableBody({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    // Verify GroupedEventRow is rendered
    expect(screen.getByTestId('grouped-row-2023-06-30')).toBeInTheDocument();
  });

  it('should handle empty events array', () => {
    mockUseEventGrouping.mockReturnValue({
      groupedEvents: [],
      individualEvents: [],
      sortedEvents: [],
      totalEvents: 0,
      totalGroups: 0,
      interestWithholdingPairs: 0
    });

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
    mockUseEventGrouping.mockReturnValue({
      groupedEvents: [],
      individualEvents: [],
      sortedEvents: [],
      totalEvents: 0,
      totalGroups: 0,
      interestWithholdingPairs: 0
    });

    renderTableBody({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: false,
      showNavUpdates: true,
      ...mockHandlers
    });

    expect(mockUseEventGrouping).toHaveBeenCalledWith(
      mockEvents,
      mockFund,
      false,
      true
    );
  });


}); 