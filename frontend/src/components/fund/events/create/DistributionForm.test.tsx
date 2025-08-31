import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import DistributionForm from './DistributionForm';

// Mock the helpers
jest.mock('../../../../utils/helpers', () => ({
  formatNumber: (value: string) => value,
  parseNumber: (value: string) => value,
}));

const theme = createTheme();

const defaultProps = {
  distributionType: '',
  subDistributionType: '',
  formData: {},
  validationErrors: {},
  onInputChange: jest.fn(),
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

    it('should not render for non-distribution events', () => {
      renderWithTheme({ eventType: 'CAPITAL_CALL' });
      expect(screen.queryByLabelText(/Amount/)).not.toBeInTheDocument();
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

    it('should render amount field for withholding tax distributions', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX'
      });

      expect(screen.getByLabelText(/Amount/)).toBeInTheDocument();
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
    it('should render withholding tax checkbox for interest withholding tax', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX'
      });

      expect(screen.getByLabelText('Has Withholding Tax')).toBeInTheDocument();
    });

    it('should render withholding tax checkbox for other interest distributions', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'CASH'
      });

      expect(screen.getByLabelText('Has Withholding Tax')).toBeInTheDocument();
    });

    it('should handle withholding tax checkbox changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        onInputChange
      });

      const checkbox = screen.getByLabelText('Has Withholding Tax');
      fireEvent.click(checkbox);

      expect(onInputChange).toHaveBeenCalledWith('has_withholding_tax', 'true');
    });

    it('should render amount field for withholding tax distributions', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        formData: { amount: '1000' }
      });

      expect(screen.getByLabelText(/Amount/)).toBeInTheDocument();
      expect(screen.getByDisplayValue('1000')).toBeInTheDocument();
    });

    it('should render withholding tax amount field when checkbox is checked', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        formData: { 
          has_withholding_tax: true,
          withholding_tax_amount: '200' 
        }
      });

      expect(screen.getByLabelText('Withholding Tax Amount')).toBeInTheDocument();
      expect(screen.getByDisplayValue('200')).toBeInTheDocument();
    });

    it('should render withholding tax rate field when checkbox is checked', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        formData: { 
          has_withholding_tax: true,
          withholding_tax_rate: '15' 
        }
      });

      expect(screen.getByLabelText('Withholding Tax Rate (%)')).toBeInTheDocument();
      expect(screen.getByDisplayValue('15')).toBeInTheDocument();
    });

    it('should handle amount input changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        onInputChange
      });

      const amountField = screen.getByLabelText(/Amount/);
      fireEvent.change(amountField, { target: { value: '1500' } });

      expect(onInputChange).toHaveBeenCalledWith('amount', '1500');
    });

    it('should handle withholding tax amount input changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        formData: { has_withholding_tax: true },
        onInputChange
      });

      const taxAmountField = screen.getByLabelText('Withholding Tax Amount');
      fireEvent.change(taxAmountField, { target: { value: '300' } });

      expect(onInputChange).toHaveBeenCalledWith('withholding_tax_amount', '300');
    });

    it('should handle withholding tax rate input changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        formData: { has_withholding_tax: true },
        onInputChange
      });

      const taxRateField = screen.getByLabelText('Withholding Tax Rate (%)');
      fireEvent.change(taxRateField, { target: { value: '20' } });

      expect(onInputChange).toHaveBeenCalledWith('withholding_tax_rate', '20');
    });

    it('should display validation errors for withholding tax fields', () => {
      renderWithTheme({ 
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        formData: { has_withholding_tax: true },
        validationErrors: { 
          amount: 'Amount is required',
          withholding_tax_amount: 'Withholding tax amount is required'
        }
      });

      expect(screen.getByText('Amount is required')).toBeInTheDocument();
      expect(screen.getByText('Withholding tax amount is required')).toBeInTheDocument();
    });
  });

  describe('Error Display', () => {
    it('should display distribution type validation error', () => {
      renderWithTheme({ 
        validationErrors: { distribution_type: 'Distribution type is required' }
      });

      expect(screen.getByText('Distribution type is required')).toBeInTheDocument();
    });
  });
}); 