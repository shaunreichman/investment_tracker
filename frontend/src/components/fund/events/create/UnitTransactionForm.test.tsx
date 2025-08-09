import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import UnitTransactionForm from './UnitTransactionForm';

const theme = createTheme();

// Mock the helpers module
jest.mock('../../../../utils/helpers', () => ({
  formatNumber: jest.fn((value) => value ? `$${parseFloat(value).toFixed(2)}` : ''),
  parseNumber: jest.fn((value) => value),
}));

const defaultProps = {
  formData: {
    units_purchased: '',
    units_sold: '',
    unit_price: '',
    brokerage_fee: '',
    amount: '',
  },
  validationErrors: {
    units_purchased: '',
    units_sold: '',
    unit_price: '',
    brokerage_fee: '',
    amount: '',
  },
  onInputChange: jest.fn(),
};

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('UnitTransactionForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('renders without errors for unit purchase', () => {
      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
        />
      );

      // Test that component renders without throwing errors
      expect(screen.getByLabelText(/Units Purchased/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Unit Price/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Brokerage Fee/)).toBeInTheDocument();
    });

    it('renders without errors for unit sale', () => {
      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_SALE"
        />
      );

      // Test that component renders without throwing errors
      expect(screen.getByLabelText(/Units Sold/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Unit Price/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Brokerage Fee/)).toBeInTheDocument();
    });
  });

  describe('Event Handlers', () => {
    it('calls onInputChange when units purchased field changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
          onInputChange={onInputChange}
        />
      );

      const unitsField = screen.getByLabelText(/Units Purchased/);
      fireEvent.change(unitsField, { target: { value: '100' } });

      expect(onInputChange).toHaveBeenCalledWith('units_purchased', '100');
    });

    it('calls onInputChange when unit price field changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
          onInputChange={onInputChange}
        />
      );

      const priceField = screen.getByLabelText(/Unit Price/);
      fireEvent.change(priceField, { target: { value: '25.50' } });

      expect(onInputChange).toHaveBeenCalledWith('unit_price', '25.50');
    });

    it('calls onInputChange when brokerage fee field changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
          onInputChange={onInputChange}
        />
      );

      const brokerageField = screen.getByLabelText(/Brokerage Fee/);
      fireEvent.change(brokerageField, { target: { value: '15.00' } });

      expect(onInputChange).toHaveBeenCalledWith('brokerage_fee', '15.00');
    });

    it('calls onInputChange when units sold field changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_SALE"
          onInputChange={onInputChange}
        />
      );

      const unitsField = screen.getByLabelText(/Units Sold/);
      fireEvent.change(unitsField, { target: { value: '50' } });

      expect(onInputChange).toHaveBeenCalledWith('units_sold', '50');
    });
  });

  describe('State Management', () => {
    it('calculates amount correctly for unit purchase', async () => {
      const onInputChange = jest.fn();
      const formData = {
        units_purchased: '100',
        unit_price: '25.50',
        brokerage_fee: '15.00',
      };

      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
          formData={formData}
          onInputChange={onInputChange}
        />
      );

      // Wait for useEffect to trigger amount calculation
      await waitFor(() => {
        expect(onInputChange).toHaveBeenCalledWith('amount', '2565');
      });
    });

    it('calculates amount correctly for unit sale', async () => {
      const onInputChange = jest.fn();
      const formData = {
        units_sold: '50',
        unit_price: '30.00',
        brokerage_fee: '10.00',
      };

      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_SALE"
          formData={formData}
          onInputChange={onInputChange}
        />
      );

      // Wait for useEffect to trigger amount calculation
      await waitFor(() => {
        expect(onInputChange).toHaveBeenCalledWith('amount', '1510');
      });
    });
  });

  describe('Conditional Logic', () => {
    it('shows correct fields for unit purchase', () => {
      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
        />
      );

      expect(screen.getByLabelText(/Units Purchased/)).toBeInTheDocument();
      expect(screen.queryByLabelText(/Units Sold/)).not.toBeInTheDocument();
    });

    it('shows correct fields for unit sale', () => {
      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_SALE"
        />
      );

      expect(screen.getByLabelText(/Units Sold/)).toBeInTheDocument();
      expect(screen.queryByLabelText(/Units Purchased/)).not.toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('displays validation errors for unit purchase fields', () => {
      const propsWithErrors = {
        ...defaultProps,
        validationErrors: {
          units_purchased: 'Units purchased is required',
          unit_price: 'Unit price must be greater than 0',
        },
      };

      renderWithTheme(
        <UnitTransactionForm
          {...propsWithErrors}
          eventType="UNIT_PURCHASE"
        />
      );

      expect(screen.getByText('Units purchased is required')).toBeInTheDocument();
      expect(screen.getByText('Unit price must be greater than 0')).toBeInTheDocument();
    });

    it('displays validation errors for unit sale fields', () => {
      const propsWithErrors = {
        ...defaultProps,
        validationErrors: {
          units_sold: 'Units sold is required',
          unit_price: 'Unit price must be greater than 0',
        },
      };

      renderWithTheme(
        <UnitTransactionForm
          {...propsWithErrors}
          eventType="UNIT_SALE"
        />
      );

      expect(screen.getByText('Units sold is required')).toBeInTheDocument();
      expect(screen.getByText('Unit price must be greater than 0')).toBeInTheDocument();
    });

    it('applies proper input constraints', () => {
      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
        />
      );

      const unitsField = screen.getByLabelText(/Units Purchased/);
      const priceField = screen.getByLabelText(/Unit Price/);
      const brokerageField = screen.getByLabelText(/Brokerage Fee/);

      // Test that number inputs have proper constraints
      expect(unitsField).toHaveAttribute('type', 'number');
      expect(priceField).toHaveAttribute('type', 'number');
      expect(brokerageField).toHaveAttribute('type', 'number');
    });
  });

  describe('Business Logic', () => {
    it('handles zero values correctly', async () => {
      const onInputChange = jest.fn();
      const formData = {
        units_purchased: '0',
        unit_price: '0',
        brokerage_fee: '0',
      };

      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
          formData={formData}
          onInputChange={onInputChange}
        />
      );

      // Should not call onInputChange for zero amount
      await waitFor(() => {
        expect(onInputChange).not.toHaveBeenCalledWith('amount', expect.any(String));
      });
    });

    it('handles empty values correctly', async () => {
      const onInputChange = jest.fn();
      const formData = {
        units_purchased: '',
        unit_price: '',
        brokerage_fee: '',
      };

      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
          formData={formData}
          onInputChange={onInputChange}
        />
      );

      // Should not call onInputChange for empty values
      await waitFor(() => {
        expect(onInputChange).not.toHaveBeenCalledWith('amount', expect.any(String));
      });
    });

    it('handles negative values in calculation', async () => {
      const onInputChange = jest.fn();
      const formData = {
        units_purchased: '100',
        unit_price: '25.50',
        brokerage_fee: '-5.00', // Negative brokerage
      };

      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
          formData={formData}
          onInputChange={onInputChange}
        />
      );

      await waitFor(() => {
        expect(onInputChange).toHaveBeenCalledWith('amount', '2545');
      });
    });

    it('handles decimal values correctly', async () => {
      const onInputChange = jest.fn();
      const formData = {
        units_purchased: '100.5',
        unit_price: '25.75',
        brokerage_fee: '15.25',
      };

      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
          formData={formData}
          onInputChange={onInputChange}
        />
      );

      await waitFor(() => {
        expect(onInputChange).toHaveBeenCalledWith('amount', '2603.125');
      });
    });
  });

  describe('Edge Cases', () => {
    it('handles very large numbers', async () => {
      const onInputChange = jest.fn();
      const formData = {
        units_purchased: '1000000',
        unit_price: '100.00',
        brokerage_fee: '1000.00',
      };

      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
          formData={formData}
          onInputChange={onInputChange}
        />
      );

      await waitFor(() => {
        expect(onInputChange).toHaveBeenCalledWith('amount', '100001000');
      });
    });

    it('handles very small decimal values', async () => {
      const onInputChange = jest.fn();
      const formData = {
        units_purchased: '0.001',
        unit_price: '0.01',
        brokerage_fee: '0.001',
      };

      renderWithTheme(
        <UnitTransactionForm
          {...defaultProps}
          eventType="UNIT_PURCHASE"
          formData={formData}
          onInputChange={onInputChange}
        />
      );

      await waitFor(() => {
        expect(onInputChange).toHaveBeenCalledWith('amount', '0.00101');
      });
    });
  });
}); 