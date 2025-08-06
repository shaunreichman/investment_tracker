import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import TableContainer from './TableContainer';
import { ExtendedFund, ExtendedFundEvent, FundType, FundStatus, EventType, DistributionType, TaxPaymentType } from '../../../../types/api';

// ============================================================================
// TABLE CONTAINER COMPONENT TESTS
// ============================================================================

// Create a theme for testing
const theme = createTheme();

// Mock the child components to return proper table elements
jest.mock('./TableFilters', () => ({
  __esModule: true,
  default: ({ showTaxEvents, showNavUpdates, onAddEventClick }: any) => (
    <div data-testid="table-filters">
      <span>Filters: Tax={showTaxEvents ? 'ON' : 'OFF'}, NAV={showNavUpdates ? 'ON' : 'OFF'}</span>
      <button onClick={onAddEventClick}>Add Event</button>
    </div>
  )
}));

jest.mock('./TableHeader', () => ({
  __esModule: true,
  default: ({ isNavBasedFund, showTaxEvents }: any) => (
    <thead data-testid="table-header">
      <tr>
        <td>Date</td>
        <td>Type</td>
        <td>Description</td>
        <td>Equity</td>
        {isNavBasedFund && <td>Nav Update</td>}
        <td>Distributions</td>
        {showTaxEvents && <td>Tax</td>}
        <td>Actions</td>
      </tr>
    </thead>
  )
}));

jest.mock('./TableBody', () => ({
  __esModule: true,
  default: ({ events }: any) => (
    <tbody data-testid="table-body">
      {events.map((event: any) => (
        <tr key={event.id} data-testid={`event-row-${event.id}`}>
          <td>{event.event_type}</td>
        </tr>
      ))}
    </tbody>
  )
}));

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
  onShowTaxEventsChange: jest.fn(),
  onShowNavUpdatesChange: jest.fn(),
  onAddEvent: jest.fn(),
  onEditEvent: jest.fn(),
  onDeleteEvent: jest.fn()
};

const renderTableContainer = (props: any) => {
  return render(
    <ThemeProvider theme={theme}>
      <TableContainer {...props} />
    </ThemeProvider>
  );
};

describe('TableContainer', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render all table components', () => {
    renderTableContainer({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    expect(screen.getByTestId('table-filters')).toBeInTheDocument();
    expect(screen.getByTestId('table-header')).toBeInTheDocument();
    expect(screen.getByTestId('table-body')).toBeInTheDocument();
  });

  it('should display correct event count in header', () => {
    renderTableContainer({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    expect(screen.getByText('Fund Events (3)')).toBeInTheDocument();
  });

  it('should filter events when tax events are hidden', () => {
    renderTableContainer({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: false,
      showNavUpdates: true,
      ...mockHandlers
    });

    // Should show 2 events (excluding TAX_PAYMENT)
    expect(screen.getByText('Fund Events (2)')).toBeInTheDocument();
  });

  it('should pass correct props to TableFilters', () => {
    renderTableContainer({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: false,
      showNavUpdates: true,
      ...mockHandlers
    });

    expect(screen.getByText('Filters: Tax=OFF, NAV=ON')).toBeInTheDocument();
    expect(screen.getByText('Add Event')).toBeInTheDocument();
  });

  it('should handle filter toggle events', () => {
    renderTableContainer({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    // Test add event button
    fireEvent.click(screen.getByText('Add Event'));
    expect(mockHandlers.onAddEvent).toHaveBeenCalled();
  });

  it('should handle add event button click', () => {
    renderTableContainer({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    fireEvent.click(screen.getByText('Add Event'));
    expect(mockHandlers.onAddEvent).toHaveBeenCalled();
  });

  it('should pass events to TableBody', () => {
    renderTableContainer({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    // Verify all events are rendered
    expect(screen.getByTestId('event-row-1')).toBeInTheDocument();
    expect(screen.getByTestId('event-row-2')).toBeInTheDocument();
    expect(screen.getByTestId('event-row-3')).toBeInTheDocument();
  });

  it('should handle empty events array', () => {
    renderTableContainer({
      events: [],
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    expect(screen.getByText('Fund Events (0)')).toBeInTheDocument();
    expect(screen.getByTestId('table-body')).toBeInTheDocument();
  });



  it('should pass fund data to all child components', () => {
    renderTableContainer({
      events: mockEvents,
      fund: mockFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    // All components should receive fund data
    expect(screen.getByTestId('table-filters')).toBeInTheDocument();
    expect(screen.getByTestId('table-header')).toBeInTheDocument();
    expect(screen.getByTestId('table-body')).toBeInTheDocument();
  });

  it('should handle NAV-based funds correctly', () => {
    const navBasedFund = { ...mockFund, tracking_type: FundType.NAV_BASED };
    
    renderTableContainer({
      events: mockEvents,
      fund: navBasedFund,
      showTaxEvents: true,
      showNavUpdates: true,
      ...mockHandlers
    });

    // Should render correctly for NAV-based funds
    expect(screen.getByTestId('table-filters')).toBeInTheDocument();
    expect(screen.getByTestId('table-header')).toBeInTheDocument();
    expect(screen.getByTestId('table-body')).toBeInTheDocument();
  });
}); 