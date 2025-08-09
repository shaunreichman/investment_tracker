import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import FundFormSection, { CreateFundFormData, ValidationErrors } from '../FundFormSection';

const theme = createTheme();
const renderWithTheme = (ui: React.ReactElement) => render(<ThemeProvider theme={theme}>{ui}</ThemeProvider>);

describe('FundFormSection', () => {
  const baseForm: CreateFundFormData = {
    entity_id: '',
    name: '',
    fund_type: '',
    tracking_type: '',
    currency: 'AUD',
    commitment_amount: '',
    expected_irr: '',
    expected_duration_months: '',
    description: ''
  };

  const baseErrors: ValidationErrors = {};

  it('renders fields and propagates input changes', () => {
    const onInputChange = jest.fn();
    const onCreateEntity = jest.fn();

    renderWithTheme(
      <FundFormSection
        formData={baseForm}
        validationErrors={baseErrors}
        entities={[{ id: 1, name: 'Entity A' } as any]}
        onInputChange={onInputChange}
        onCreateEntity={onCreateEntity}
      />
    );

    // Change fund name
    fireEvent.change(screen.getByLabelText(/Fund Name/i), { target: { value: 'My Fund' } });
    expect(onInputChange).toHaveBeenCalledWith('name', 'My Fund');

    // Open entity menu and click create new
    fireEvent.mouseDown(screen.getByLabelText(/Entity/i));
    fireEvent.click(screen.getByText(/Create New Entity/i));
    expect(onCreateEntity).toHaveBeenCalled();
  });
});


