import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import DistributionForm from './DistributionForm';

// Mock the helpers
jest.mock('../../utils/helpers', () => ({
  formatNumber: (value: string) => value,
  parseNumber: (value: string) => value,
}));

const theme = createTheme();

const defaultProps = {
  distributionType: '',
  subDistributionType: '',
  formData: {},
  validationErrors: {},
  withholdingAmountType: '' as 'gross' | 'net' | '',
  withholdingTaxType: '' as 'amount' | 'rate' | '',
  hybridFieldOverrides: {},
  onInputChange: jest.fn(),
  onWithholdingAmountTypeChange: jest.fn(),
  onWithholdingTaxTypeChange: jest.fn(),
  onHybridFieldToggle: jest.fn(),
  eventType: 'DISTRIBUTION',
};

const renderWithTheme = (props = {}) => {
  return render(
    <ThemeProvider theme={theme}>
      <DistributionForm {...defaultProps} {...props} />
    </ThemeProvider>
  );
};

describe('DistributionForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render distribution type field', () => {
      renderWithTheme({ distributionType: 'INTEREST' });

      expect(screen.getByDisplayValue('INTEREST')).toBeInTheDocument();
    });

    it('should render sub-distribution type field for DIVIDEND', () => {
      renderWithTheme({ 
        distributionType: 'DIVIDEND',
        subDistributionType: 'FRANKED'
      });

      expect(screen.getByLabelText(/Sub-Distribution Type/)).toBeInTheDocument();
      expect(screen.getByDisplayValue('FRANKED')).toBeInTheDocument();
    });

    it('should render sub-distribution type field for INTEREST', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX'
      });

      expect(screen.getByLabelText(/Sub-Distribution Type/)).toBeInTheDocument();
      expect(screen.getByDisplayValue('WITHHOLDING_TAX')).toBeInTheDocument();
    });

    it('should not render for non-distribution events', () => {
      const { container } = renderWithTheme({ eventType: 'CAPITAL_CALL' });

      expect(container.firstChild).toBeNull();
    });
  });

  describe('Regular Distribution Amount', () => {
    it('should render amount field for regular distributions', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'CASH',
        formData: { amount: '1000' }
      });

      expect(screen.getByLabelText(/Amount/)).toBeInTheDocument();
      expect(screen.getByDisplayValue('1000')).toBeInTheDocument();
    });

    it('should not render amount field for withholding tax distributions', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX'
      });

      expect(screen.queryByLabelText(/Amount/)).not.toBeInTheDocument();
    });

    it('should handle amount input changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'CASH',
        onInputChange
      });

      const amountField = screen.getByLabelText(/Amount/);
      fireEvent.change(amountField, { target: { value: '2000' } });

      expect(onInputChange).toHaveBeenCalledWith('amount', '2000');
    });

    it('should display validation errors for amount', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'CASH',
        validationErrors: { amount: 'Amount is required' }
      });

      expect(screen.getByText('Amount is required')).toBeInTheDocument();
    });
  });

  describe('Withholding Tax Form', () => {
    it('should render withholding tax form for interest withholding tax', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX'
      });

      expect(screen.getByText('Amount Type:')).toBeInTheDocument();
      expect(screen.getByText('Tax Type:')).toBeInTheDocument();
      expect(screen.getByText('Gross')).toBeInTheDocument();
      expect(screen.getByText('Net')).toBeInTheDocument();
      expect(screen.getByText('Tax Amount')).toBeInTheDocument();
      expect(screen.getByText('Tax Rate (%)')).toBeInTheDocument();
    });

    it('should not render withholding tax form for other distributions', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'CASH'
      });

      expect(screen.queryByText('Amount Type:')).not.toBeInTheDocument();
      expect(screen.queryByText('Tax Type:')).not.toBeInTheDocument();
    });

    it('should handle gross amount type selection', () => {
      const onWithholdingAmountTypeChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        onWithholdingAmountTypeChange
      });

      const grossButton = screen.getByText('Gross');
      fireEvent.click(grossButton);

      expect(onWithholdingAmountTypeChange).toHaveBeenCalledWith('gross');
    });

    it('should handle net amount type selection', () => {
      const onWithholdingAmountTypeChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        onWithholdingAmountTypeChange
      });

      const netButton = screen.getByText('Net');
      fireEvent.click(netButton);

      expect(onWithholdingAmountTypeChange).toHaveBeenCalledWith('net');
    });

    it('should handle tax amount type selection', () => {
      const onWithholdingTaxTypeChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        onWithholdingTaxTypeChange
      });

      const taxAmountButton = screen.getByText('Tax Amount');
      fireEvent.click(taxAmountButton);

      expect(onWithholdingTaxTypeChange).toHaveBeenCalledWith('amount');
    });

    it('should handle tax rate type selection', () => {
      const onWithholdingTaxTypeChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        onWithholdingTaxTypeChange
      });

      const taxRateButton = screen.getByText('Tax Rate (%)');
      fireEvent.click(taxRateButton);

      expect(onWithholdingTaxTypeChange).toHaveBeenCalledWith('rate');
    });

    it('should render gross amount field when gross is selected', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingAmountType: 'gross',
        formData: { gross_amount: '1000' }
      });

      expect(screen.getByLabelText('Gross Amount')).toBeInTheDocument();
      expect(screen.getByDisplayValue('1000')).toBeInTheDocument();
    });

    it('should render net amount field when net is selected', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingAmountType: 'net',
        formData: { net_amount: '800' }
      });

      expect(screen.getByLabelText('Net Amount')).toBeInTheDocument();
      expect(screen.getByDisplayValue('800')).toBeInTheDocument();
    });

    it('should render tax amount field when amount is selected', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingTaxType: 'amount',
        formData: { withholding_tax_amount: '200' }
      });

      expect(screen.getByLabelText('Tax Amount')).toBeInTheDocument();
      expect(screen.getByDisplayValue('200')).toBeInTheDocument();
    });

    it('should render tax rate field when rate is selected', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingTaxType: 'rate',
        formData: { withholding_tax_rate: '15' }
      });

      expect(screen.getByLabelText('Tax Rate (%)')).toBeInTheDocument();
      expect(screen.getByDisplayValue('15')).toBeInTheDocument();
    });

    it('should handle gross amount input changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingAmountType: 'gross',
        onInputChange
      });

      const grossAmountField = screen.getByLabelText('Gross Amount');
      fireEvent.change(grossAmountField, { target: { value: '1500' } });

      expect(onInputChange).toHaveBeenCalledWith('gross_amount', '1500');
    });

    it('should handle net amount input changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingAmountType: 'net',
        onInputChange
      });

      const netAmountField = screen.getByLabelText('Net Amount');
      fireEvent.change(netAmountField, { target: { value: '1200' } });

      expect(onInputChange).toHaveBeenCalledWith('net_amount', '1200');
    });

    it('should handle tax amount input changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingTaxType: 'amount',
        onInputChange
      });

      const taxAmountField = screen.getByLabelText('Tax Amount');
      fireEvent.change(taxAmountField, { target: { value: '300' } });

      expect(onInputChange).toHaveBeenCalledWith('withholding_tax_amount', '300');
    });

    it('should handle tax rate input changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingTaxType: 'rate',
        onInputChange
      });

      const taxRateField = screen.getByLabelText('Tax Rate (%)');
      fireEvent.change(taxRateField, { target: { value: '20' } });

      expect(onInputChange).toHaveBeenCalledWith('withholding_tax_rate', '20');
    });

    it('should display validation errors for withholding tax fields', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingAmountType: 'gross',
        withholdingTaxType: 'amount',
        validationErrors: { 
          gross_amount: 'Enter the gross amount',
          withholding_tax_amount: 'Enter the tax amount'
        }
      });

      expect(screen.getByText('Enter the gross amount')).toBeInTheDocument();
      expect(screen.getByText('Enter the tax amount')).toBeInTheDocument();
    });
  });

  describe('Button States', () => {
    it('should show gross button as contained when selected', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingAmountType: 'gross'
      });

      const grossButton = screen.getByText('Gross');
      expect(grossButton).toHaveClass('MuiButton-contained');
    });

    it('should show net button as contained when selected', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingAmountType: 'net'
      });

      const netButton = screen.getByText('Net');
      expect(netButton).toHaveClass('MuiButton-contained');
    });

    it('should show tax amount button as contained when selected', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingTaxType: 'amount'
      });

      const taxAmountButtons = screen.getAllByText('Tax Amount');
      const button = taxAmountButtons.find(el => el.tagName === 'BUTTON');
      expect(button).toHaveClass('MuiButton-contained');
    });

    it('should show tax rate button as contained when selected', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingTaxType: 'rate'
      });

      const taxRateButtons = screen.getAllByText('Tax Rate (%)');
      const button = taxRateButtons.find(el => el.tagName === 'BUTTON');
      expect(button).toHaveClass('MuiButton-contained');
    });
  });

  describe('Error Display', () => {
    it('should display distribution type validation error', () => {
      renderWithTheme({ 
        validationErrors: { distribution_type: 'Distribution type is required' }
      });

      expect(screen.getByText('Distribution type is required')).toBeInTheDocument();
    });

    it('should display sub-distribution type validation error', () => {
      renderWithTheme({ 
        distributionType: 'DIVIDEND',
        validationErrors: { sub_distribution_type: 'Sub-distribution type is required' }
      });

      expect(screen.getByText('Sub-distribution type is required')).toBeInTheDocument();
    });
  });
}); 