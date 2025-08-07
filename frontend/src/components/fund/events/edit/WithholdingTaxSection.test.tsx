import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import WithholdingTaxSection from './WithholdingTaxSection';

// Mock the utilities
jest.mock('../../../../utils/validators', () => ({
  validateField: jest.fn()
}));

jest.mock('../../../../utils/helpers', () => ({
  formatNumber: jest.fn((value) => value),
  parseNumber: jest.fn((value) => value)
}));

const theme = createTheme();

// Mock event data
const mockEvent = {
  event_type: 'DISTRIBUTION',
  distribution_type: 'INTEREST',
  id: 1
};

// Mock props
const createMockProps = (overrides = {}) => ({
  formData: {
    distribution_type: 'interest',
    gross_interest: '',
    net_interest: '',
    withholding_amount: '',
    withholding_rate: ''
  },
  setFormData: jest.fn(),
  interestType: 'regular' as const,
  setInterestType: jest.fn(),
  withholdingAmountType: '' as const,
  setWithholdingAmountType: jest.fn(),
  withholdingTaxType: '' as const,
  setWithholdingTaxType: jest.fn(),
  validationErrors: {},
  setValidationErrors: jest.fn(),
  event: mockEvent,
  handleInputChange: jest.fn(),
  ...overrides
});

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('WithholdingTaxSection', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render for interest distribution events', () => {
      const props = createMockProps();
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      expect(screen.getByText('Interest Type')).toBeInTheDocument();
      expect(screen.getByText('Regular Interest')).toBeInTheDocument();
      expect(screen.getByText('Withholding Tax Interest')).toBeInTheDocument();
    });

    it('should not render for non-interest distribution events', () => {
      const props = createMockProps({
        formData: { distribution_type: 'dividend' }
      });
      const { container } = renderWithTheme(<WithholdingTaxSection {...props} />);
      
      expect(container.firstChild).toBeNull();
    });

    it('should not render for non-distribution events', () => {
      const props = createMockProps({
        event: { event_type: 'CAPITAL_CALL' }
      });
      const { container } = renderWithTheme(<WithholdingTaxSection {...props} />);
      
      expect(container.firstChild).toBeNull();
    });
  });

  describe('Regular Interest Mode', () => {
    it('should show gross interest field when interest type is regular', () => {
      const props = createMockProps({
        interestType: 'regular'
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      expect(screen.getByLabelText('Gross Interest')).toBeInTheDocument();
    });

    it('should handle gross interest input changes', () => {
      const handleInputChange = jest.fn();
      const props = createMockProps({
        interestType: 'regular',
        handleInputChange
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const grossInterestField = screen.getByLabelText('Gross Interest');
      fireEvent.change(grossInterestField, { target: { value: '1000' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('gross_interest', '1000');
    });

    it('should display validation errors for gross interest', () => {
      const props = createMockProps({
        interestType: 'regular',
        validationErrors: { gross_interest: 'Invalid amount' }
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      expect(screen.getByText('Invalid amount')).toBeInTheDocument();
    });
  });

  describe('Withholding Tax Mode', () => {
    it('should show withholding tax fields when interest type is withholding', () => {
      const props = createMockProps({
        interestType: 'withholding'
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      expect(screen.getByText('Amount Type:')).toBeInTheDocument();
      expect(screen.getByText('Tax Type:')).toBeInTheDocument();
      expect(screen.getByText('Gross')).toBeInTheDocument();
      expect(screen.getByText('Net')).toBeInTheDocument();
      expect(screen.getByText('Tax Amount')).toBeInTheDocument();
      expect(screen.getByText('Tax Rate (%)')).toBeInTheDocument();
    });

    it('should handle interest type change', () => {
      const setInterestType = jest.fn();
      const props = createMockProps({
        setInterestType
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const withholdingRadio = screen.getByLabelText('Withholding Tax Interest');
      fireEvent.click(withholdingRadio);
      
      expect(setInterestType).toHaveBeenCalledWith('withholding');
    });

    it('should handle amount type selection', () => {
      const setWithholdingAmountType = jest.fn();
      const props = createMockProps({
        interestType: 'withholding',
        setWithholdingAmountType
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const netButton = screen.getByText('Net');
      fireEvent.click(netButton);
      
      expect(setWithholdingAmountType).toHaveBeenCalledWith('net');
    });

    it('should handle tax type selection', () => {
      const setWithholdingTaxType = jest.fn();
      const props = createMockProps({
        interestType: 'withholding',
        setWithholdingTaxType
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const taxAmountButton = screen.getByText('Tax Amount');
      fireEvent.click(taxAmountButton);
      
      expect(setWithholdingTaxType).toHaveBeenCalledWith('amount');
    });

    it('should show gross interest field when amount type is gross', () => {
      const props = createMockProps({
        interestType: 'withholding',
        withholdingAmountType: 'gross'
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      expect(screen.getByLabelText('Gross Interest')).toBeInTheDocument();
    });

    it('should show net interest field when amount type is net', () => {
      const props = createMockProps({
        interestType: 'withholding',
        withholdingAmountType: 'net'
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      expect(screen.getByLabelText('Net Interest')).toBeInTheDocument();
    });

    it('should show tax amount field when tax type is amount', () => {
      const props = createMockProps({
        interestType: 'withholding',
        withholdingTaxType: 'amount'
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      expect(screen.getByLabelText('Tax Amount')).toBeInTheDocument();
    });

    it('should show tax rate field when tax type is rate', () => {
      const props = createMockProps({
        interestType: 'withholding',
        withholdingTaxType: 'rate'
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      expect(screen.getByLabelText('Tax Rate (%)')).toBeInTheDocument();
    });

    it('should handle gross interest input changes in withholding mode', () => {
      const handleInputChange = jest.fn();
      const props = createMockProps({
        interestType: 'withholding',
        withholdingAmountType: 'gross',
        handleInputChange
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const grossInterestField = screen.getByLabelText('Gross Interest');
      fireEvent.change(grossInterestField, { target: { value: '1000' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('gross_interest', '1000');
    });

    it('should handle net interest input changes in withholding mode', () => {
      const handleInputChange = jest.fn();
      const props = createMockProps({
        interestType: 'withholding',
        withholdingAmountType: 'net',
        handleInputChange
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const netInterestField = screen.getByLabelText('Net Interest');
      fireEvent.change(netInterestField, { target: { value: '800' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('net_interest', '800');
    });

    it('should handle tax amount input changes', () => {
      const handleInputChange = jest.fn();
      const props = createMockProps({
        interestType: 'withholding',
        withholdingTaxType: 'amount',
        handleInputChange
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const taxAmountField = screen.getByLabelText('Tax Amount');
      fireEvent.change(taxAmountField, { target: { value: '200' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('withholding_amount', '200');
    });

    it('should handle tax rate input changes', () => {
      const handleInputChange = jest.fn();
      const props = createMockProps({
        interestType: 'withholding',
        withholdingTaxType: 'rate',
        handleInputChange
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const taxRateField = screen.getByLabelText('Tax Rate (%)');
      fireEvent.change(taxRateField, { target: { value: '20' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('withholding_rate', '20');
    });

    it('should display validation errors for withholding fields', () => {
      const props = createMockProps({
        interestType: 'withholding',
        withholdingAmountType: 'gross',
        withholdingTaxType: 'amount',
        validationErrors: {
          gross_interest: 'Invalid gross amount',
          withholding_amount: 'Invalid tax amount'
        }
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      expect(screen.getByText('Invalid gross amount')).toBeInTheDocument();
      expect(screen.getByText('Invalid tax amount')).toBeInTheDocument();
    });
  });

  describe('Button States', () => {
    it('should show gross button as contained when selected', () => {
      const props = createMockProps({
        interestType: 'withholding',
        withholdingAmountType: 'gross'
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const grossButton = screen.getByText('Gross');
      expect(grossButton).toHaveClass('MuiButton-contained');
    });

    it('should show net button as contained when selected', () => {
      const props = createMockProps({
        interestType: 'withholding',
        withholdingAmountType: 'net'
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const netButton = screen.getByText('Net');
      expect(netButton).toHaveClass('MuiButton-contained');
    });

    it('should show tax amount button as contained when selected', () => {
      const props = createMockProps({
        interestType: 'withholding',
        withholdingTaxType: 'amount'
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const taxAmountButton = screen.getAllByText('Tax Amount')[0]; // Get the button, not the label
      expect(taxAmountButton).toHaveClass('MuiButton-contained');
    });

    it('should show tax rate button as contained when selected', () => {
      const props = createMockProps({
        interestType: 'withholding',
        withholdingTaxType: 'rate'
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const taxRateButton = screen.getAllByText('Tax Rate (%)')[0]; // Get the button, not the label
      expect(taxRateButton).toHaveClass('MuiButton-contained');
    });
  });

  describe('Form Data Integration', () => {
    it('should display existing form data values', () => {
      const props = createMockProps({
        interestType: 'regular',
        formData: {
          distribution_type: 'interest',
          gross_interest: '1000'
        }
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const grossInterestField = screen.getByLabelText('Gross Interest');
      expect(grossInterestField).toHaveValue(1000); // Number value, not string
    });

    it('should display withholding form data values', () => {
      const props = createMockProps({
        interestType: 'withholding',
        withholdingAmountType: 'gross',
        withholdingTaxType: 'amount',
        formData: {
          distribution_type: 'interest',
          gross_interest: '1000',
          withholding_amount: '200'
        }
      });
      renderWithTheme(<WithholdingTaxSection {...props} />);
      
      const grossInterestField = screen.getByLabelText('Gross Interest');
      const taxAmountField = screen.getByLabelText('Tax Amount');
      expect(grossInterestField).toHaveValue(1000); // Number value, not string
      expect(taxAmountField).toHaveValue(200); // Number value, not string
    });
  });
}); 