import React from 'react';
import { render, screen, fireEvent, within, act } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { createErrorInfo, ErrorType } from '../../../../types/errors';
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
const mockErrorState: { error: any } = { error: null };
jest.mock('../../../../hooks/useFunds', () => ({
  useCreateFund: () => ({ mutate: mockMutate, loading: false, error: mockErrorState.error })
}));

const theme = createTheme();
const renderWithTheme = (ui: React.ReactElement) => render(<ThemeProvider theme={theme}>{ui}</ThemeProvider>);

expect.extend(toHaveNoViolations);

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

  it('enables submit after required fields and calls createFund', async () => {
    mockErrorState.error = null;
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

    await act(async () => {
      fireEvent.click(submitBtn);
    });
    expect(mockMutate).toHaveBeenCalledTimes(1);
  });

  it('shows error display on failed submit', async () => {
    const err = new Error('server failed');
    mockMutate.mockRejectedValueOnce(err);
    mockErrorState.error = createErrorInfo(err, ErrorType.SERVER);
    renderWithTheme(<CreateFundModal {...baseProps} />);

    fireEvent.click(screen.getByText('NAV-Based Fund'));

    const entityCombobox = screen.getByRole('combobox', { name: /Entity/i });
    fireEvent.mouseDown(entityCombobox);
    const listbox = screen.getByRole('listbox');
    fireEvent.click(within(listbox).getByText('Entity A'));

    fireEvent.change(screen.getByLabelText(/Fund Name/i), { target: { value: 'My Fund' } });

    const fundTypeCombobox = screen.getByRole('combobox', { name: /Fund Type/i });
    fireEvent.mouseDown(fundTypeCombobox);
    const typeListbox = screen.getByRole('listbox');
    fireEvent.click(within(typeListbox).getByText('Private Equity'));

    const submitBtn = screen.getByRole('button', { name: /Create Fund/i });
    await act(async () => {
      fireEvent.click(submitBtn);
    });

    // Expect an error alert to be present
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('has no obvious accessibility violations (axe smoke)', async () => {
    const { container } = renderWithTheme(<CreateFundModal {...baseProps} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});


