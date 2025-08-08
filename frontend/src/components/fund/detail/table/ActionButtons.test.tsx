import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ActionButtons from './ActionButtons';
import { ExtendedFundEvent, EventType } from '../../../../types/api';

// Create a theme for testing
const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('ActionButtons', () => {
  const mockEvent: ExtendedFundEvent = {
    id: 1,
    fund_id: 1,
    event_type: EventType.CAPITAL_CALL,
    event_date: '2023-01-01',
    amount: 100000,
    description: 'Test event',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const defaultProps = {
    event: mockEvent,
    onDeleteEvent: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders delete button for editable events', () => {
    renderWithTheme(<ActionButtons {...defaultProps} />);
    
    expect(screen.getByTitle('Delete event')).toBeInTheDocument();
  });

  it('calls onDeleteEvent when delete button is clicked', () => {
    const onDeleteEvent = jest.fn();
    renderWithTheme(<ActionButtons {...defaultProps} onDeleteEvent={onDeleteEvent} />);
    
    fireEvent.click(screen.getByTitle('Delete event'));
    expect(onDeleteEvent).toHaveBeenCalledWith(mockEvent);
  });

  it('does not render buttons for non-editable events', () => {
    const nonEditableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.TAX_PAYMENT
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={nonEditableEvent} />);
    
    expect(screen.queryByTitle('Delete event')).not.toBeInTheDocument();
  });

  it('does not render buttons for DAILY_RISK_FREE_INTEREST_CHARGE events', () => {
    const nonEditableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.DAILY_RISK_FREE_INTEREST_CHARGE
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={nonEditableEvent} />);
    
    expect(screen.queryByTitle('Edit event')).not.toBeInTheDocument();
    expect(screen.queryByTitle('Delete event')).not.toBeInTheDocument();
  });

  it('does not render buttons for EOFY_DEBT_COST events', () => {
    const nonEditableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.EOFY_DEBT_COST
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={nonEditableEvent} />);
    
    expect(screen.queryByTitle('Edit event')).not.toBeInTheDocument();
    expect(screen.queryByTitle('Delete event')).not.toBeInTheDocument();
  });

  it('does not render buttons for MANAGEMENT_FEE events', () => {
    const nonEditableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.MANAGEMENT_FEE
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={nonEditableEvent} />);
    
    expect(screen.queryByTitle('Edit event')).not.toBeInTheDocument();
    expect(screen.queryByTitle('Delete event')).not.toBeInTheDocument();
  });

  it('does not render buttons for CARRIED_INTEREST events', () => {
    const nonEditableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.CARRIED_INTEREST
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={nonEditableEvent} />);
    
    expect(screen.queryByTitle('Edit event')).not.toBeInTheDocument();
    expect(screen.queryByTitle('Delete event')).not.toBeInTheDocument();
  });

  it('does not render buttons for OTHER events', () => {
    const nonEditableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.OTHER
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={nonEditableEvent} />);
    
    expect(screen.queryByTitle('Edit event')).not.toBeInTheDocument();
    expect(screen.queryByTitle('Delete event')).not.toBeInTheDocument();
  });

  it('renders delete button for CAPITAL_CALL events', () => {
    const editableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.CAPITAL_CALL
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={editableEvent} />);
    
    expect(screen.getByTitle('Delete event')).toBeInTheDocument();
  });

  it('renders delete button for DISTRIBUTION events', () => {
    const editableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.DISTRIBUTION
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={editableEvent} />);
    
    expect(screen.getByTitle('Delete event')).toBeInTheDocument();
  });

  it('renders delete button for UNIT_PURCHASE events', () => {
    const editableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.UNIT_PURCHASE
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={editableEvent} />);
    
    expect(screen.getByTitle('Delete event')).toBeInTheDocument();
  });

  it('renders delete button for UNIT_SALE events', () => {
    const editableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.UNIT_SALE
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={editableEvent} />);
    
    expect(screen.getByTitle('Delete event')).toBeInTheDocument();
  });

  it('renders delete button for RETURN_OF_CAPITAL events', () => {
    const editableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.RETURN_OF_CAPITAL
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={editableEvent} />);
    
    expect(screen.getByTitle('Delete event')).toBeInTheDocument();
  });

  it('renders delete button for NAV_UPDATE events', () => {
    const editableEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.NAV_UPDATE
    };

    renderWithTheme(<ActionButtons {...defaultProps} event={editableEvent} />);
    
    expect(screen.getByTitle('Delete event')).toBeInTheDocument();
  });
}); 