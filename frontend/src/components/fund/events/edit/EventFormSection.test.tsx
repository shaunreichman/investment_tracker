import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import EventFormSection from './EventFormSection';
import { ExtendedFundEvent, EventType, DistributionType } from '../../../../types/api';

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

const mockEvent: ExtendedFundEvent = {
  id: 1,
  fund_id: 1,
  event_type: EventType.CAPITAL_CALL,
  event_date: '2024-01-01',
  amount: 10000,
  description: 'Test event',
  reference_number: 'REF001',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
};

const mockFormData = {
  event_date: '2024-01-01',
  amount: '10000',
  description: 'Test event',
  reference_number: 'REF001'
};

const mockValidationErrors = {};

const defaultProps = {
  event: mockEvent,
  formData: mockFormData,
  setFormData: jest.fn(),
  validationErrors: mockValidationErrors,
  setValidationErrors: jest.fn(),
  isFormValid: true,
  setIsFormValid: jest.fn(),
  handleInputChange: jest.fn()
};

describe('EventFormSection', () => {
  describe('Rendering', () => {
    it('should render event date field', () => {
      renderWithTheme(<EventFormSection {...defaultProps} />);
      expect(screen.getByLabelText('Event Date')).toBeInTheDocument();
    });

    it('should render description field', () => {
      renderWithTheme(<EventFormSection {...defaultProps} />);
      expect(screen.getByLabelText('Description (Optional)')).toBeInTheDocument();
    });

    it('should render reference number field', () => {
      renderWithTheme(<EventFormSection {...defaultProps} />);
      expect(screen.getByLabelText('Reference Number (Optional)')).toBeInTheDocument();
    });
  });

  describe('Capital Call Events', () => {
    const capitalCallEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.CAPITAL_CALL
    };

    it('should render amount field for capital call events', () => {
      renderWithTheme(<EventFormSection {...defaultProps} event={capitalCallEvent} />);
      expect(screen.getByLabelText('Amount')).toBeInTheDocument();
    });

    it('should handle amount input changes', () => {
      const handleInputChange = jest.fn();
      renderWithTheme(
        <EventFormSection {...defaultProps} event={capitalCallEvent} handleInputChange={handleInputChange} />
      );
      
      const amountField = screen.getByLabelText('Amount');
      fireEvent.change(amountField, { target: { value: '15000' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('amount', '15000');
    });

    it('should display validation errors for amount', () => {
      const validationErrors = { amount: 'Amount is required' };
      renderWithTheme(
        <EventFormSection {...defaultProps} event={capitalCallEvent} validationErrors={validationErrors} />
      );
      
      expect(screen.getByText('Amount is required')).toBeInTheDocument();
    });
  });

  describe('Unit Purchase Events', () => {
    const unitPurchaseEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.UNIT_PURCHASE,
      units_purchased: 100,
      unit_price: 10.5,
      brokerage_fee: 50
    };

    const unitPurchaseFormData = {
      ...mockFormData,
      units_purchased: '100',
      unit_price: '10.5',
      brokerage_fee: '50'
    };

    it('should render unit purchase fields', () => {
      renderWithTheme(
        <EventFormSection {...defaultProps} event={unitPurchaseEvent} formData={unitPurchaseFormData} />
      );
      
      expect(screen.getByLabelText('Units Purchased')).toBeInTheDocument();
      expect(screen.getByLabelText('Unit Price')).toBeInTheDocument();
      expect(screen.getByLabelText('Brokerage Fee (Optional)')).toBeInTheDocument();
    });

    it('should handle units purchased input changes', () => {
      const handleInputChange = jest.fn();
      renderWithTheme(
        <EventFormSection {...defaultProps} event={unitPurchaseEvent} handleInputChange={handleInputChange} />
      );
      
      const unitsField = screen.getByLabelText('Units Purchased');
      fireEvent.change(unitsField, { target: { value: '150' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('units_purchased', '150');
    });

    it('should handle unit price input changes', () => {
      const handleInputChange = jest.fn();
      renderWithTheme(
        <EventFormSection {...defaultProps} event={unitPurchaseEvent} handleInputChange={handleInputChange} />
      );
      
      const priceField = screen.getByLabelText('Unit Price');
      fireEvent.change(priceField, { target: { value: '12.5' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('unit_price', '12.5');
    });

    it('should display validation errors for unit purchase fields', () => {
      const validationErrors = {
        units_purchased: 'Units purchased is required',
        unit_price: 'Unit price is required'
      };
      renderWithTheme(
        <EventFormSection {...defaultProps} event={unitPurchaseEvent} validationErrors={validationErrors} />
      );
      
      expect(screen.getByText('Units purchased is required')).toBeInTheDocument();
      expect(screen.getByText('Unit price is required')).toBeInTheDocument();
    });
  });

  describe('Unit Sale Events', () => {
    const unitSaleEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.UNIT_SALE,
      units_sold: 50,
      unit_price: 12.0,
      brokerage_fee: 25
    };

    const unitSaleFormData = {
      ...mockFormData,
      units_sold: '50',
      unit_price: '12.0',
      brokerage_fee: '25'
    };

    it('should render unit sale fields', () => {
      renderWithTheme(
        <EventFormSection {...defaultProps} event={unitSaleEvent} formData={unitSaleFormData} />
      );
      
      expect(screen.getByLabelText('Units Sold')).toBeInTheDocument();
      expect(screen.getByLabelText('Unit Price')).toBeInTheDocument();
      expect(screen.getByLabelText('Brokerage Fee (Optional)')).toBeInTheDocument();
    });

    it('should handle units sold input changes', () => {
      const handleInputChange = jest.fn();
      renderWithTheme(
        <EventFormSection {...defaultProps} event={unitSaleEvent} handleInputChange={handleInputChange} />
      );
      
      const unitsField = screen.getByLabelText('Units Sold');
      fireEvent.change(unitsField, { target: { value: '75' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('units_sold', '75');
    });

    it('should display validation errors for unit sale fields', () => {
      const validationErrors = {
        units_sold: 'Units sold is required',
        unit_price: 'Unit price is required'
      };
      renderWithTheme(
        <EventFormSection {...defaultProps} event={unitSaleEvent} validationErrors={validationErrors} />
      );
      
      expect(screen.getByText('Units sold is required')).toBeInTheDocument();
      expect(screen.getByText('Unit price is required')).toBeInTheDocument();
    });
  });

  describe('NAV Update Events', () => {
    const navUpdateEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.NAV_UPDATE,
      nav_per_share: 15.25
    };

    const navUpdateFormData = {
      ...mockFormData,
      nav_per_share: '15.25'
    };

    it('should render NAV per share field', () => {
      renderWithTheme(
        <EventFormSection {...defaultProps} event={navUpdateEvent} formData={navUpdateFormData} />
      );
      
      expect(screen.getByLabelText('NAV Per Share')).toBeInTheDocument();
    });

    it('should handle NAV per share input changes', () => {
      const handleInputChange = jest.fn();
      renderWithTheme(
        <EventFormSection {...defaultProps} event={navUpdateEvent} handleInputChange={handleInputChange} />
      );
      
      const navField = screen.getByLabelText('NAV Per Share');
      fireEvent.change(navField, { target: { value: '16.50' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('nav_per_share', '16.50');
    });

    it('should display validation errors for NAV per share', () => {
      const validationErrors = { nav_per_share: 'NAV per share is required' };
      renderWithTheme(
        <EventFormSection {...defaultProps} event={navUpdateEvent} validationErrors={validationErrors} />
      );
      
      expect(screen.getByText('NAV per share is required')).toBeInTheDocument();
    });
  });

  describe('Distribution Events', () => {
    const distributionEvent: ExtendedFundEvent = {
      ...mockEvent,
      event_type: EventType.DISTRIBUTION,
      distribution_type: DistributionType.DIVIDEND
    };

    const distributionFormData = {
      ...mockFormData,
      distribution_type: 'dividend',
      amount: '5000'
    };

    it('should render distribution type field', () => {
      renderWithTheme(
        <EventFormSection {...defaultProps} event={distributionEvent} formData={distributionFormData} />
      );
      
      expect(screen.getByLabelText('Distribution Type')).toBeInTheDocument();
    });

    it('should render amount field for non-interest distributions', () => {
      renderWithTheme(
        <EventFormSection {...defaultProps} event={distributionEvent} formData={distributionFormData} />
      );
      
      expect(screen.getByLabelText('Amount')).toBeInTheDocument();
    });

    it('should render distribution type field correctly', () => {
      renderWithTheme(
        <EventFormSection {...defaultProps} event={distributionEvent} />
      );
      
      expect(screen.getByLabelText('Distribution Type')).toBeInTheDocument();
    });

    it('should display dividend type buttons for dividend distributions', () => {
      const dividendFormData = {
        ...distributionFormData,
        distribution_type: 'dividend_franked'
      };
      
      renderWithTheme(
        <EventFormSection {...defaultProps} event={distributionEvent} formData={dividendFormData} />
      );
      
      expect(screen.getByText('Dividend Type')).toBeInTheDocument();
      expect(screen.getByText('Franked')).toBeInTheDocument();
      expect(screen.getByText('Unfranked')).toBeInTheDocument();
    });

    it('should handle dividend type button clicks', () => {
      const handleInputChange = jest.fn();
      const dividendFormData = {
        ...distributionFormData,
        distribution_type: 'dividend_franked'
      };
      
      renderWithTheme(
        <EventFormSection {...defaultProps} event={distributionEvent} formData={dividendFormData} handleInputChange={handleInputChange} />
      );
      
      const unfrankedButton = screen.getByText('Unfranked');
      fireEvent.click(unfrankedButton);
      
      expect(handleInputChange).toHaveBeenCalledWith('distribution_type', 'dividend_unfranked');
    });

    it('should display validation errors for distribution fields', () => {
      const validationErrors = {
        distribution_type: 'Distribution type is required',
        amount: 'Amount is required'
      };
      renderWithTheme(
        <EventFormSection {...defaultProps} event={distributionEvent} validationErrors={validationErrors} />
      );
      
      expect(screen.getByText('Distribution type is required')).toBeInTheDocument();
      expect(screen.getByText('Amount is required')).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('should validate event date', () => {
      const validationErrors = { event_date: 'Event date is required' };
      renderWithTheme(
        <EventFormSection {...defaultProps} validationErrors={validationErrors} />
      );
      
      expect(screen.getByText('Event date is required')).toBeInTheDocument();
    });

    it('should handle description input changes', () => {
      const handleInputChange = jest.fn();
      renderWithTheme(
        <EventFormSection {...defaultProps} handleInputChange={handleInputChange} />
      );
      
      const descriptionField = screen.getByLabelText('Description (Optional)');
      fireEvent.change(descriptionField, { target: { value: 'Updated description' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('description', 'Updated description');
    });

    it('should handle reference number input changes', () => {
      const handleInputChange = jest.fn();
      renderWithTheme(
        <EventFormSection {...defaultProps} handleInputChange={handleInputChange} />
      );
      
      const referenceField = screen.getByLabelText('Reference Number (Optional)');
      fireEvent.change(referenceField, { target: { value: 'REF002' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('reference_number', 'REF002');
    });
  });

  describe('Input Handling', () => {
    it('should handle event date changes', () => {
      const handleInputChange = jest.fn();
      renderWithTheme(
        <EventFormSection {...defaultProps} handleInputChange={handleInputChange} />
      );
      
      const dateField = screen.getByLabelText('Event Date');
      fireEvent.change(dateField, { target: { value: '2024-02-01' } });
      
      expect(handleInputChange).toHaveBeenCalledWith('event_date', '2024-02-01');
    });

    it('should display current form data values', () => {
      const formDataWithValues = {
        event_date: '2024-01-15',
        amount: '15000',
        description: 'Test description',
        reference_number: 'REF123'
      };
      
      renderWithTheme(
        <EventFormSection {...defaultProps} formData={formDataWithValues} />
      );
      
      expect(screen.getByDisplayValue('2024-01-15')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Test description')).toBeInTheDocument();
      expect(screen.getByDisplayValue('REF123')).toBeInTheDocument();
    });
  });
}); 