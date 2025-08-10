import React from 'react';
import { render, screen } from '@testing-library/react';
import { EventTypeChip } from './EventTypeChip';

describe('EventTypeChip', () => {
  it('renders event type label with aria label', () => {
    render(<EventTypeChip eventType="NAV_UPDATE" />);
    expect(screen.getByLabelText(/event type: nav update/i)).toBeInTheDocument();
  });

  it('renders distribution type INTEREST correctly', () => {
    render(<EventTypeChip eventType="INTEREST" />);
    expect(screen.getByText('INTEREST')).toBeInTheDocument();
    expect(screen.getByLabelText(/event type: INTEREST/i)).toBeInTheDocument();
  });

  it('renders distribution type DIVIDEND correctly', () => {
    render(<EventTypeChip eventType="DIVIDEND" />);
    expect(screen.getByText('DIVIDEND')).toBeInTheDocument();
    expect(screen.getByLabelText(/event type: DIVIDEND/i)).toBeInTheDocument();
  });

  it('renders event type DISTRIBUTION correctly', () => {
    render(<EventTypeChip eventType="DISTRIBUTION" />);
    expect(screen.getByText('Distribution')).toBeInTheDocument();
    expect(screen.getByLabelText(/event type: Distribution/i)).toBeInTheDocument();
  });

  it('renders event type CAPITAL_CALL correctly', () => {
    render(<EventTypeChip eventType="CAPITAL_CALL" />);
    expect(screen.getByText('Capital Call')).toBeInTheDocument();
    expect(screen.getByLabelText(/event type: Capital Call/i)).toBeInTheDocument();
  });
});


