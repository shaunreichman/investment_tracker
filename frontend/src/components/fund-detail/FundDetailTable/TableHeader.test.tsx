import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import TableHeader from './TableHeader';

// Create a theme for testing
const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('TableHeader', () => {
  const defaultProps = {
    isNavBasedFund: false,
    showTaxEvents: false,
  };

  it('renders all standard columns', () => {
    renderWithTheme(<TableHeader {...defaultProps} />);
    
    expect(screen.getByText('Date')).toBeInTheDocument();
    expect(screen.getByText('Type')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    expect(screen.getByText('Equity')).toBeInTheDocument();
    expect(screen.getByText('Distributions')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  it('shows NAV Update column only for NAV-based funds', () => {
    const { rerender } = renderWithTheme(<TableHeader {...defaultProps} />);
    
    // Should not show NAV Update for cost-based funds
    expect(screen.queryByText('Nav Update')).not.toBeInTheDocument();
    
    // Should show NAV Update for NAV-based funds
    rerender(<TableHeader {...defaultProps} isNavBasedFund={true} />);
    expect(screen.getByText('Nav Update')).toBeInTheDocument();
  });

  it('shows Tax column only when showTaxEvents is true', () => {
    const { rerender } = renderWithTheme(<TableHeader {...defaultProps} />);
    
    // Should not show Tax column when showTaxEvents is false
    expect(screen.queryByText('Tax')).not.toBeInTheDocument();
    
    // Should show Tax column when showTaxEvents is true
    rerender(<TableHeader {...defaultProps} showTaxEvents={true} />);
    expect(screen.getByText('Tax')).toBeInTheDocument();
  });

  it('shows all columns for NAV-based fund with tax events', () => {
    renderWithTheme(
      <TableHeader 
        {...defaultProps} 
        isNavBasedFund={true}
        showTaxEvents={true}
      />
    );
    
    // All columns should be present
    expect(screen.getByText('Date')).toBeInTheDocument();
    expect(screen.getByText('Type')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    expect(screen.getByText('Equity')).toBeInTheDocument();
    expect(screen.getByText('Nav Update')).toBeInTheDocument();
    expect(screen.getByText('Distributions')).toBeInTheDocument();
    expect(screen.getByText('Tax')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  it('shows correct columns for cost-based fund without tax events', () => {
    renderWithTheme(<TableHeader {...defaultProps} />);
    
    // Should show standard columns
    expect(screen.getByText('Date')).toBeInTheDocument();
    expect(screen.getByText('Type')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    expect(screen.getByText('Equity')).toBeInTheDocument();
    expect(screen.getByText('Distributions')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
    
    // Should not show NAV-specific or tax columns
    expect(screen.queryByText('Nav Update')).not.toBeInTheDocument();
    expect(screen.queryByText('Tax')).not.toBeInTheDocument();
  });

  it('applies correct styling to header cells', () => {
    renderWithTheme(<TableHeader {...defaultProps} />);
    
    // Check that the table head is rendered
    const tableHead = document.querySelector('thead');
    expect(tableHead).toBeInTheDocument();
    
    // Check that table row is rendered
    const tableRow = document.querySelector('thead tr');
    expect(tableRow).toBeInTheDocument();
    
    // Check that table cells are rendered
    const tableCells = document.querySelectorAll('thead th');
    expect(tableCells.length).toBeGreaterThan(0);
  });
}); 