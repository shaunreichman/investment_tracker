import React from 'react';
import { render, screen, fireEvent, within, waitFor } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { createErrorInfo, ErrorType } from '../../../../types/errors';
import CreateFundModal from '../CreateFundModal';
import userEvent from '@testing-library/user-event';

jest.mock('../../../../hooks/useEntities', () => {
  const actual = jest.requireActual('../../../../hooks/useEntities');
  return {
    ...actual,
    useEntities: () => ({ data: [{ id: 1, name: 'Entity A' }], loading: false, error: null }),
    useCreateEntity: () => ({ mutate: jest.fn(), loading: false, error: null })
  };
});

const mockMutate = jest.fn().mockImplementation(() => Promise.resolve());
const mockErrorState: { error: any } = { error: null };
jest.mock('../../../../hooks/useFunds', () => ({
  useCreateFund: () => ({ 
    mutate: mockMutate, 
    loading: false, 
    error: mockErrorState.error,
    isSuccess: false,
    isError: false
  })
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
    mockMutate.mockImplementation(() => Promise.resolve());
    mockErrorState.error = null;
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  it('enables submit after required fields and calls createFund', async () => {
    // Increase timeout for this complex test with multiple async operations
    jest.setTimeout(15000);
    
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

    // Click submit and wait for the async operation to complete
    await userEvent.click(submitBtn);
    
    // Wait for the mock to be called and handle async state updates
    await waitFor(() => expect(mockMutate).toHaveBeenCalledTimes(1));
  }, 15000);

  it('shows error display on failed submit', async () => {
    // Set up the error state to simulate the hook's error handling
    mockErrorState.error = {
      message: 'server failed',
      type: 'server',
      severity: 'high',
      retryable: true,
      userMessage: 'A server error occurred. Please try again later.',
      timestamp: new Date(),
      id: 'test-error-id'
    };
    
    renderWithTheme(<CreateFundModal {...baseProps} />);

    await userEvent.click(screen.getByText('NAV-Based Fund'));

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
    await userEvent.click(submitBtn);

    // Wait for the error to be displayed through the hook's error handling
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
  });

  it('has no obvious accessibility violations (axe smoke)', async () => {
    const { container } = renderWithTheme(<CreateFundModal {...baseProps} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});


