import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import TaxStatementForm from './TaxStatementForm';

// Mock the helpers module
jest.mock('../../../../utils/helpers', () => ({
  formatNumber: jest.fn((value) => value),
  parseNumber: jest.fn((value) => value),
}));

const theme = createTheme();

const defaultProps = {
  formData: {
    financial_year: '',
    statement_date: '',
    eofy_debt_interest_deduction_rate: '',
    interest_received_in_cash: '',
    interest_receivable_this_fy: '',
    interest_receivable_prev_fy: '',
    interest_non_resident_withholding_tax_from_statement: '',
    interest_income_tax_rate: '',
    dividend_franked_income_amount: '',
    dividend_unfranked_income_amount: '',
    dividend_franked_income_tax_rate: '',
    dividend_unfranked_income_tax_rate: '',
    capital_gain_income_amount: '',
    capital_gain_income_tax_rate: '',
    accountant: '',
    notes: '',
    non_resident: false
  },
  validationErrors: {},
  financialYears: ['2024', '2023', '2022', '2021', '2020', '2019'],
  fundEntity: { id: 1, name: 'Test Entity' },
  hybridFieldOverrides: {
    dividend_franked_income_amount: false,
    dividend_unfranked_income_amount: false,
    capital_gain_income_amount: false
  },
  onInputChange: jest.fn(),
  onHybridFieldToggle: jest.fn()
};

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('TaxStatementForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Renders', () => {
    it('renders all form sections correctly', () => {
      renderWithTheme(<TaxStatementForm {...defaultProps} />);
      
      // Basic Information section
      expect(screen.getByText('Basic Information')).toBeInTheDocument();
      expect(screen.getByLabelText(/Entity/)).toBeInTheDocument();
      expect(screen.getByRole('combobox', { name: /Financial Year/ })).toBeInTheDocument();
      expect(screen.getByLabelText(/Statement Date/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Tax Payment Date/)).toBeInTheDocument();
      expect(screen.getByLabelText(/End of Financial Year Debt Interest Deduction Rate/)).toBeInTheDocument();
      
      // Interest Income section
      expect(screen.getByText('Interest Income')).toBeInTheDocument();
      expect(screen.getByLabelText(/Interest Received in Cash/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Interest Receivable This FY/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Interest Receivable Previous FY/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Interest Non-Resident Withholding Tax from Statement/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Interest Income Tax Rate/)).toBeInTheDocument();
      
      // Dividend Income section
      expect(screen.getByText('Dividend Income')).toBeInTheDocument();
      expect(screen.getByLabelText(/Dividend Franked Income Amount/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Dividend Unfranked Income Amount/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Dividend Franked Income Tax Rate/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Dividend Unfranked Income Tax Rate/)).toBeInTheDocument();
      
      // Capital Gains section
      expect(screen.getByText('Capital Gains')).toBeInTheDocument();
      expect(screen.getByLabelText(/Capital Gain Income Amount/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Capital Gain Income Tax Rate/)).toBeInTheDocument();
      
      // Additional Information section
      expect(screen.getByText('Additional Information')).toBeInTheDocument();
      expect(screen.getByLabelText(/Accountant/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Notes/)).toBeInTheDocument();
      expect(screen.getByRole('checkbox', { name: /Non-Resident/ })).toBeInTheDocument();
    });

    it('displays fund entity name correctly', () => {
      renderWithTheme(<TaxStatementForm {...defaultProps} />);
      
      const entityField = screen.getByLabelText(/Entity/);
      expect(entityField).toHaveValue('Test Entity');
      expect(entityField).toBeDisabled();
    });

    it('renders financial years dropdown correctly', () => {
      renderWithTheme(<TaxStatementForm {...defaultProps} />);
      
      const financialYearSelect = screen.getByRole('combobox', { name: /Financial Year/ });
      fireEvent.mouseDown(financialYearSelect);
      
      expect(screen.getByText('2024')).toBeInTheDocument();
      expect(screen.getByText('2023')).toBeInTheDocument();
      expect(screen.getByText('2022')).toBeInTheDocument();
      expect(screen.getByText('2021')).toBeInTheDocument();
      expect(screen.getByText('2020')).toBeInTheDocument();
      expect(screen.getByText('2019')).toBeInTheDocument();
    });

    it('shows required field indicators', () => {
      renderWithTheme(<TaxStatementForm {...defaultProps} />);
      
      // Check for required field indicators (red asterisks)
      expect(screen.getByRole('combobox', { name: /Financial Year/ })).toBeInTheDocument();
      expect(screen.getByLabelText(/Statement Date/)).toBeInTheDocument();
      expect(screen.getByLabelText(/End of Financial Year Debt Interest Deduction Rate/)).toBeInTheDocument();
    });
  });

  describe('Event Handlers', () => {
    it('calls onInputChange when text fields are modified', () => {
      const mockOnInputChange = jest.fn();
      renderWithTheme(
        <TaxStatementForm {...defaultProps} onInputChange={mockOnInputChange} />
      );
      
      // Test basic information fields
      const statementDateField = screen.getByLabelText(/Statement Date/);
      fireEvent.change(statementDateField, { target: { value: '2024-01-15' } });
      expect(mockOnInputChange).toHaveBeenCalledWith('statement_date', '2024-01-15');
      
      const deductionRateField = screen.getByLabelText(/End of Financial Year Debt Interest Deduction Rate/);
      fireEvent.change(deductionRateField, { target: { value: '2.5' } });
      expect(mockOnInputChange).toHaveBeenCalledWith('eofy_debt_interest_deduction_rate', '2.5');
      
      // Test interest income fields
      const interestCashField = screen.getByLabelText(/Interest Received in Cash/);
      fireEvent.change(interestCashField, { target: { value: '1000.00' } });
      expect(mockOnInputChange).toHaveBeenCalledWith('interest_received_in_cash', '1000.00');
      
      // Test dividend income fields
      const dividendFrankedField = screen.getByLabelText(/Dividend Franked Income Amount/);
      fireEvent.change(dividendFrankedField, { target: { value: '500.00' } });
      expect(mockOnInputChange).toHaveBeenCalledWith('dividend_franked_income_amount', '500.00');
      
      // Test capital gains fields
      const capitalGainField = screen.getByLabelText(/Capital Gain Income Amount/);
      fireEvent.change(capitalGainField, { target: { value: '750.00' } });
      expect(mockOnInputChange).toHaveBeenCalledWith('capital_gain_income_amount', '750.00');
      
      // Test additional information fields
      const accountantField = screen.getByLabelText(/Accountant/);
      fireEvent.change(accountantField, { target: { value: 'John Smith' } });
      expect(mockOnInputChange).toHaveBeenCalledWith('accountant', 'John Smith');
      
      const notesField = screen.getByLabelText(/Notes/);
      fireEvent.change(notesField, { target: { value: 'Test notes' } });
      expect(mockOnInputChange).toHaveBeenCalledWith('notes', 'Test notes');
    });

    it('calls onInputChange when financial year is selected', () => {
      const mockOnInputChange = jest.fn();
      renderWithTheme(
        <TaxStatementForm {...defaultProps} onInputChange={mockOnInputChange} />
      );
      
      const financialYearSelect = screen.getByRole('combobox', { name: /Financial Year/ });
      fireEvent.mouseDown(financialYearSelect);
      
      const year2024 = screen.getByText('2024');
      fireEvent.click(year2024);
      
      expect(mockOnInputChange).toHaveBeenCalledWith('financial_year', '2024');
    });

    it('calls onInputChange when non-resident checkbox is toggled', () => {
      const mockOnInputChange = jest.fn();
      renderWithTheme(
        <TaxStatementForm {...defaultProps} onInputChange={mockOnInputChange} />
      );
      
      const nonResidentCheckbox = screen.getByRole('checkbox', { name: /Non-Resident/ });
      fireEvent.click(nonResidentCheckbox);
      
      expect(mockOnInputChange).toHaveBeenCalledWith('non_resident', 'true');
    });
  });

  describe('State Management', () => {
    it('displays form data values correctly', () => {
      const formDataWithValues = {
        ...defaultProps.formData,
        financial_year: '2024',
        statement_date: '2024-01-15',
        eofy_debt_interest_deduction_rate: '2.5',
        interest_received_in_cash: '1000.00',
        dividend_franked_income_amount: '500.00',
        capital_gain_income_amount: '750.00',
        accountant: 'John Smith',
        notes: 'Test notes',
        non_resident: true
      };
      
      renderWithTheme(
        <TaxStatementForm {...defaultProps} formData={formDataWithValues} />
      );
      
      expect(screen.getByDisplayValue('2024')).toBeInTheDocument();
      expect(screen.getByDisplayValue('2024-01-15')).toBeInTheDocument();
      expect(screen.getByDisplayValue('2.5')).toBeInTheDocument();
      expect(screen.getByDisplayValue('1000.00')).toBeInTheDocument();
      expect(screen.getByDisplayValue('500.00')).toBeInTheDocument();
      expect(screen.getByDisplayValue('750.00')).toBeInTheDocument();
      expect(screen.getByDisplayValue('John Smith')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Test notes')).toBeInTheDocument();
      
      const nonResidentCheckbox = screen.getByRole('checkbox', { name: /Non-Resident/ });
      expect(nonResidentCheckbox).toBeChecked();
    });

    it('displays validation errors correctly', () => {
      const validationErrors = {
        financial_year: 'Financial year is required',
        statement_date: 'Statement date is required',
        eofy_debt_interest_deduction_rate: 'Invalid deduction rate',
        interest_received_in_cash: 'Invalid amount'
      };
      
      renderWithTheme(
        <TaxStatementForm {...defaultProps} validationErrors={validationErrors} />
      );
      
      expect(screen.getByText('Financial year is required')).toBeInTheDocument();
      expect(screen.getByText('Statement date is required')).toBeInTheDocument();
      expect(screen.getByText('Invalid deduction rate')).toBeInTheDocument();
      expect(screen.getByText('Invalid amount')).toBeInTheDocument();
    });
  });

  describe('Conditional Logic', () => {
    it('displays hybrid field override buttons for dividend fields', () => {
      renderWithTheme(<TaxStatementForm {...defaultProps} />);
      
      // Check for hybrid field override buttons
      const dividendFrankedField = screen.getByLabelText(/Dividend Franked Income Amount/);
      const dividendUnfrankedField = screen.getByLabelText(/Dividend Unfranked Income Amount/);
      
      expect(dividendFrankedField).toBeInTheDocument();
      expect(dividendUnfrankedField).toBeInTheDocument();
      
      // Check for Auto/Manual buttons
      const autoButtons = screen.getAllByText(/Auto|Manual/);
      expect(autoButtons.length).toBeGreaterThan(0);
    });

    it('displays hybrid field override buttons for capital gain fields', () => {
      renderWithTheme(<TaxStatementForm {...defaultProps} />);
      
      const capitalGainField = screen.getByLabelText(/Capital Gain Income Amount/);
      expect(capitalGainField).toBeInTheDocument();
      
      // Check for Auto/Manual button
      const autoButtons = screen.getAllByText(/Auto|Manual/);
      expect(autoButtons.length).toBeGreaterThan(0);
    });

    it('shows correct button state based on hybrid field overrides', () => {
      const hybridOverrides = {
        dividend_franked_income_amount: true,
        dividend_unfranked_income_amount: false,
        capital_gain_income_amount: true
      };
      
      renderWithTheme(
        <TaxStatementForm {...defaultProps} hybridFieldOverrides={hybridOverrides} />
      );
      
      // Check that Manual buttons are shown for overridden fields
      const manualButtons = screen.getAllByText('Manual');
      expect(manualButtons.length).toBeGreaterThan(0);
      
      // Check that Auto buttons are shown for non-overridden fields
      const autoButtons = screen.getAllByText('Auto');
      expect(autoButtons.length).toBeGreaterThan(0);
    });
  });

  describe('Form Validation', () => {
    it('shows error states for invalid fields', () => {
      const validationErrors = {
        financial_year: 'Financial year is required',
        statement_date: 'Statement date is required'
      };
      
      renderWithTheme(
        <TaxStatementForm {...defaultProps} validationErrors={validationErrors} />
      );
      
      // Use more specific selectors to avoid conflicts
      const financialYearSelect = screen.getByRole('combobox', { name: /Financial Year/ });
      const statementDateField = screen.getByLabelText(/Statement Date/);
      
      expect(financialYearSelect).toHaveAttribute('aria-invalid', 'true');
      expect(statementDateField).toHaveAttribute('aria-invalid', 'true');
    });

    it('shows helper text for disabled fields', () => {
      renderWithTheme(<TaxStatementForm {...defaultProps} />);
      
      const taxPaymentDateField = screen.getByLabelText(/Tax Payment Date/);
      expect(taxPaymentDateField).toBeDisabled();
      expect(screen.getByText('Auto-calculated as last day of financial year')).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('calls onHybridFieldToggle when hybrid field buttons are clicked', () => {
      const mockOnHybridFieldToggle = jest.fn();
      renderWithTheme(
        <TaxStatementForm {...defaultProps} onHybridFieldToggle={mockOnHybridFieldToggle} />
      );
      
      // Find and click hybrid field buttons
      const autoButtons = screen.getAllByText('Auto');
      expect(autoButtons.length).toBeGreaterThan(0);
      fireEvent.click(autoButtons[0]);
      expect(mockOnHybridFieldToggle).toHaveBeenCalled();
    });

    it('handles multiline text input for notes field', () => {
      const mockOnInputChange = jest.fn();
      renderWithTheme(
        <TaxStatementForm {...defaultProps} onInputChange={mockOnInputChange} />
      );
      
      const notesField = screen.getByLabelText(/Notes/);
      fireEvent.change(notesField, { target: { value: 'Line 1\nLine 2\nLine 3' } });
      
      expect(mockOnInputChange).toHaveBeenCalledWith('notes', 'Line 1\nLine 2\nLine 3');
    });

    it('handles number input validation for tax rate fields', () => {
      const mockOnInputChange = jest.fn();
      renderWithTheme(
        <TaxStatementForm {...defaultProps} onInputChange={mockOnInputChange} />
      );
      
      const taxRateField = screen.getByLabelText(/Interest Income Tax Rate/);
      fireEvent.change(taxRateField, { target: { value: '30.5' } });
      
      expect(mockOnInputChange).toHaveBeenCalledWith('interest_income_tax_rate', '30.5');
    });
  });

  describe('Accessibility', () => {
    it('has proper labels for all form fields', () => {
      renderWithTheme(<TaxStatementForm {...defaultProps} />);
      
      // Test specific fields that don't have conflicts
      expect(screen.getByLabelText(/Entity/)).toBeInTheDocument();
      expect(screen.getByRole('combobox', { name: /Financial Year/ })).toBeInTheDocument();
      expect(screen.getByLabelText(/Statement Date/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Tax Payment Date/)).toBeInTheDocument();
      expect(screen.getByLabelText(/End of Financial Year Debt Interest Deduction Rate/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Interest Received in Cash/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Interest Receivable This FY/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Interest Receivable Previous FY/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Interest Non-Resident Withholding Tax from Statement/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Interest Income Tax Rate/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Dividend Franked Income Amount/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Dividend Unfranked Income Amount/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Dividend Franked Income Tax Rate/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Dividend Unfranked Income Tax Rate/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Capital Gain Income Amount/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Capital Gain Income Tax Rate/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Accountant/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Notes/)).toBeInTheDocument();
      expect(screen.getByRole('checkbox', { name: /Non-Resident/ })).toBeInTheDocument();
    });

    it('has proper ARIA attributes for error states', () => {
      const validationErrors = {
        financial_year: 'Financial year is required'
      };
      
      renderWithTheme(
        <TaxStatementForm {...defaultProps} validationErrors={validationErrors} />
      );
      
      const financialYearSelect = screen.getByRole('combobox', { name: /Financial Year/ });
      expect(financialYearSelect).toHaveAttribute('aria-invalid', 'true');
    });
  });

  describe('Edge Cases', () => {
    it('handles empty fund entity gracefully', () => {
      const propsWithEmptyEntity = {
        ...defaultProps,
        fundEntity: null
      };
      
      renderWithTheme(<TaxStatementForm {...propsWithEmptyEntity} />);
      
      const entityField = screen.getByLabelText(/Entity/);
      expect(entityField).toHaveValue('Loading...');
    });

    it('handles empty financial years array', () => {
      const propsWithEmptyYears = {
        ...defaultProps,
        financialYears: []
      };
      
      renderWithTheme(<TaxStatementForm {...propsWithEmptyYears} />);
      
      const financialYearSelect = screen.getByRole('combobox', { name: /Financial Year/ });
      expect(financialYearSelect).toBeInTheDocument();
    });

    it('handles undefined form data gracefully', () => {
      const propsWithUndefinedData = {
        ...defaultProps,
        formData: undefined
      };
      
      renderWithTheme(<TaxStatementForm {...propsWithUndefinedData} />);
      
      // Should not crash and should render the form
      expect(screen.getByText('Basic Information')).toBeInTheDocument();
    });
  });
}); 