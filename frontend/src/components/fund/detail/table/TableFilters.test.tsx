import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import TableFilters from './TableFilters';

describe('TableFilters', () => {
  const defaultProps = {
    showTaxEvents: false,
    showNavUpdates: false,
    isNavBasedFund: false,
    onShowTaxEventsChange: jest.fn(),
    onShowNavUpdatesChange: jest.fn(),
    onAddEventClick: jest.fn(),
  };

  it('renders Add Event button', () => {
    render(<TableFilters {...defaultProps} />);
    expect(screen.getByText('Add Event')).toBeInTheDocument();
  });

  it('renders Show Tax Events switch', () => {
    render(<TableFilters {...defaultProps} />);
    expect(screen.getByText('Show Tax Events')).toBeInTheDocument();
  });

  it('shows NAV Updates switch only for NAV-based funds', () => {
    const { rerender } = render(<TableFilters {...defaultProps} />);
    expect(screen.queryByText('Show NAV Updates')).not.toBeInTheDocument();

    rerender(<TableFilters {...defaultProps} isNavBasedFund={true} />);
    expect(screen.getByText('Show NAV Updates')).toBeInTheDocument();
  });

  it('calls onAddEventClick when Add Event button is clicked', () => {
    const onAddEventClick = jest.fn();
    render(<TableFilters {...defaultProps} onAddEventClick={onAddEventClick} />);
    
    fireEvent.click(screen.getByText('Add Event'));
    expect(onAddEventClick).toHaveBeenCalledTimes(1);
  });

  it('calls onShowTaxEventsChange when tax events switch is toggled', () => {
    const onShowTaxEventsChange = jest.fn();
    render(<TableFilters {...defaultProps} onShowTaxEventsChange={onShowTaxEventsChange} />);
    
    // Find the switch by looking for the checkbox input within the Switch component
    const switches = screen.getAllByRole('checkbox');
    const taxSwitch = switches[0]; // First switch should be tax events
    if (taxSwitch) {
      fireEvent.click(taxSwitch);
    }
    expect(onShowTaxEventsChange).toHaveBeenCalledWith(true);
  });

  it('calls onShowNavUpdatesChange when NAV updates switch is toggled', () => {
    const onShowNavUpdatesChange = jest.fn();
    render(
      <TableFilters 
        {...defaultProps} 
        isNavBasedFund={true}
        onShowNavUpdatesChange={onShowNavUpdatesChange} 
      />
    );
    
    // Find the switch by looking for the checkbox input within the Switch component
    const switches = screen.getAllByRole('checkbox');
    const navSwitch = switches[1]; // Second switch should be NAV updates
    if (navSwitch) {
      fireEvent.click(navSwitch);
    }
    expect(onShowNavUpdatesChange).toHaveBeenCalledWith(true);
  });

  it('reflects the correct checked state for switches', () => {
    render(
      <TableFilters 
        {...defaultProps} 
        showTaxEvents={true}
        showNavUpdates={true}
        isNavBasedFund={true}
      />
    );
    
    const switches = screen.getAllByRole('checkbox');
    const taxSwitch = switches[0];
    const navSwitch = switches[1];
    
    expect(taxSwitch).toBeChecked();
    expect(navSwitch).toBeChecked();
  });
}); 