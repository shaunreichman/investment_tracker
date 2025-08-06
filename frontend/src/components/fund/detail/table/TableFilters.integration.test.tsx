import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import TableFilters from './TableFilters';

// Create a theme for testing
const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('TableFilters Integration', () => {
  const defaultProps = {
    showTaxEvents: false,
    showNavUpdates: false,
    isNavBasedFund: false,
    onShowTaxEventsChange: jest.fn(),
    onShowNavUpdatesChange: jest.fn(),
    onAddEventClick: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with Material-UI theme', () => {
    renderWithTheme(<TableFilters {...defaultProps} />);
    
    expect(screen.getByText('Add Event')).toBeInTheDocument();
    expect(screen.getByText('Show Tax Events')).toBeInTheDocument();
  });

  it('handles all user interactions correctly', () => {
    const onAddEventClick = jest.fn();
    const onShowTaxEventsChange = jest.fn();
    const onShowNavUpdatesChange = jest.fn();

    renderWithTheme(
      <TableFilters 
        {...defaultProps}
        isNavBasedFund={true}
        onAddEventClick={onAddEventClick}
        onShowTaxEventsChange={onShowTaxEventsChange}
        onShowNavUpdatesChange={onShowNavUpdatesChange}
      />
    );

    // Test Add Event button
    fireEvent.click(screen.getByText('Add Event'));
    expect(onAddEventClick).toHaveBeenCalledTimes(1);

    // Test Tax Events switch
    const switches = screen.getAllByRole('checkbox');
    fireEvent.click(switches[0]);
    expect(onShowTaxEventsChange).toHaveBeenCalledWith(true);

    // Test NAV Updates switch
    fireEvent.click(switches[1]);
    expect(onShowNavUpdatesChange).toHaveBeenCalledWith(true);
  });

  it('conditionally shows NAV Updates switch based on fund type', () => {
    const { rerender } = renderWithTheme(<TableFilters {...defaultProps} />);
    
    // Should not show NAV Updates for cost-based funds
    expect(screen.queryByText('Show NAV Updates')).not.toBeInTheDocument();
    
    // Should show NAV Updates for NAV-based funds
    rerender(<TableFilters {...defaultProps} isNavBasedFund={true} />);
    expect(screen.getByText('Show NAV Updates')).toBeInTheDocument();
  });

  it('reflects the correct state from props', () => {
    renderWithTheme(
      <TableFilters 
        {...defaultProps}
        showTaxEvents={true}
        showNavUpdates={true}
        isNavBasedFund={true}
      />
    );

    const switches = screen.getAllByRole('checkbox');
    expect(switches[0]).toBeChecked(); // Tax Events switch
    expect(switches[1]).toBeChecked(); // NAV Updates switch
  });
}); 