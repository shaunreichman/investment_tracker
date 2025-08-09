import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import TemplateSelectionSection, { FundTemplate } from '../TemplateSelectionSection';

const theme = createTheme();
const renderWithTheme = (ui: React.ReactElement) => render(<ThemeProvider theme={theme}>{ui}</ThemeProvider>);

describe('TemplateSelectionSection', () => {
  const templates: FundTemplate[] = [
    {
      id: 'cost',
      name: 'Cost-Based Fund',
      description: 'Track with capital calls',
      icon: <span data-testid="icon" />,
      fund_type: '',
      tracking_type: 'cost_based',
      currency: 'AUD',
      description_template: ''
    },
    {
      id: 'nav',
      name: 'NAV-Based Fund',
      description: 'Track with NAV and units',
      icon: <span data-testid="icon" />,
      fund_type: '',
      tracking_type: 'nav_based',
      currency: 'AUD',
      description_template: ''
    }
  ];

  it('renders templates and calls onSelect when a template is clicked', () => {
    const onSelect = jest.fn();
    renderWithTheme(<TemplateSelectionSection templates={templates} onSelect={onSelect} />);

    // Both templates are visible
    expect(screen.getByText('Cost-Based Fund')).toBeInTheDocument();
    expect(screen.getByText('NAV-Based Fund')).toBeInTheDocument();

    // Click one template
    fireEvent.click(screen.getByText('Cost-Based Fund'));
    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ id: 'cost' }));
  });
});


