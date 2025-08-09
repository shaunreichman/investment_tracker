import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CreateFundModal from '../CreateFundModal';

jest.mock('../../../../hooks/useEntities', () => {
  const actual = jest.requireActual('../../../../hooks/useEntities');
  return {
    ...actual,
    useEntities: () => ({ data: [{ id: 1, name: 'Entity A' }], loading: false, error: null }),
    useCreateEntity: () => ({ mutate: jest.fn(), loading: false, error: null })
  };
});

const mockMutate = jest.fn();
jest.mock('../../../../hooks/useFunds', () => ({
  useCreateFund: () => ({ mutate: mockMutate, loading: false, error: null })
}));

const theme = createTheme();
const renderWithTheme = (ui: React.ReactElement) => render(<ThemeProvider theme={theme}>{ui}</ThemeProvider>);

describe('CreateFundModal (orchestrator)', () => {
  const baseProps = {
    open: true,
    onClose: jest.fn(),
    onFundCreated: jest.fn(),
    companyId: 99,
    companyName: 'Company Z'
  };

  beforeEach(() => {
    mockMutate.mockReset();
  });

  it('enables submit after required fields and calls createFund', () => {
    renderWithTheme(<CreateFundModal {...baseProps} />);

    // Choose a template to reveal the form
    fireEvent.click(screen.getByText('NAV-Based Fund'));

    // Initially, submit should be disabled
    expect(screen.getByRole('button', { name: /Create Fund/i })).toBeDisabled();

    // Select entity
    const entityCombobox = screen.getByRole('combobox', { name: /Entity/i });
    fireEvent.mouseDown(entityCombobox);
    const listbox = screen.getByRole('listbox');
    fireEvent.click(within(listbox).getByText('Entity A'));

    // Fill name
    fireEvent.change(screen.getByLabelText(/Fund Name/i), { target: { value: 'My Fund' } });

    // Select Fund Type
    const fundTypeCombobox = screen.getByRole('combobox', { name: /Fund Type/i });
    fireEvent.mouseDown(fundTypeCombobox);
    const typeListbox = screen.getByRole('listbox');
    fireEvent.click(within(typeListbox).getByText('Private Equity'));

    // Button should now be enabled
    const submitBtn = screen.getByRole('button', { name: /Create Fund/i });
    expect(submitBtn).toBeEnabled();

    fireEvent.click(submitBtn);
    expect(mockMutate).toHaveBeenCalledTimes(1);
  });
});


