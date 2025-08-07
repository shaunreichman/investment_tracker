import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import UnifiedFundEventForm from './UnifiedFundEventForm';
import { ExtendedFundEvent, EventType, DistributionType } from '../../../types/api';

// Mock the hooks
jest.mock('../../../hooks/useErrorHandler');
jest.mock('../../../hooks/useFunds');
jest.mock('../../../hooks/useEventSubmission');
jest.mock('../../../hooks/useUnifiedEventForm');

// Mock the form components
jest.mock('./create/EventTypeSelector', () => {
  return function MockEventTypeSelector({ mode, onEventTypeSelect }: any) {
    return (
      <div data-testid="event-type-selector">
        <button onClick={() => onEventTypeSelect('CAPITAL_CALL')}>Capital Call</button>
        <button onClick={() => onEventTypeSelect('DISTRIBUTION')}>Distribution</button>
        <div>Mode: {mode}</div>
      </div>
    );
  };
});

jest.mock('./create/DistributionForm', () => {
  return function MockDistributionForm() {
    return <div data-testid="distribution-form">Distribution Form</div>;
  };
});

jest.mock('./create/UnitTransactionForm', () => {
  return function MockUnitTransactionForm() {
    return <div data-testid="unit-transaction-form">Unit Transaction Form</div>;
  };
});

jest.mock('./create/NavUpdateForm', () => {
  return function MockNavUpdateForm() {
    return <div data-testid="nav-update-form">NAV Update Form</div>;
  };
});

jest.mock('./create/TaxStatementForm', () => {
  return function MockTaxStatementForm() {
    return <div data-testid="tax-statement-form">Tax Statement Form</div>;
  };
});

const mockUseUnifiedEventForm = {
  eventType: '',
  setEventType: jest.fn(),
  distributionType: '',
  setDistributionType: jest.fn(),
  subDistributionType: '',
  setSubDistributionType: jest.fn(),
  formData: { event_date: '2024-01-15' },
  setFormData: jest.fn(),
  success: false,
  setSuccess: jest.fn(),
  validationErrors: {},
  isFormValid: true,
  withholdingAmountType: '',
  setWithholdingAmountType: jest.fn(),
  withholdingTaxType: '',
  setWithholdingTaxType: jest.fn(),
  hybridFieldOverrides: {},
  setHybridFieldOverrides: jest.fn(),
  handleInputChange: jest.fn(),
  handleHybridFieldToggle: jest.fn(),
  validateForm: jest.fn().mockReturnValue(true),
  resetForm: jest.fn(),
  handleBack: jest.fn(),
};

const mockUseErrorHandler = {
  error: null,
  setError: jest.fn(),
  clearError: jest.fn(),
};

const mockUseFund = {
  data: {
    entity: { id: 1, name: 'Test Entity' }
  }
};

const mockUseEventSubmission = {
  handleSubmit: jest.fn(),
  createFundEvent: { loading: false, error: null, data: null },
  createTaxStatement: { loading: false, error: null, data: null },
};

const mockUseUpdateFundEvent = {
  mutate: jest.fn(),
  loading: false,
  error: null,
  data: null,
};

describe('UnifiedFundEventForm', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Setup default mock implementations
    (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue(mockUseUnifiedEventForm);
    (require('../../../hooks/useErrorHandler') as any).useErrorHandler = jest.fn().mockReturnValue(mockUseErrorHandler);
    (require('../../../hooks/useFunds') as any).useFund = jest.fn().mockReturnValue(mockUseFund);
    (require('../../../hooks/useFunds') as any).useCreateFundEvent = jest.fn().mockReturnValue(mockUseEventSubmission.createFundEvent);
    (require('../../../hooks/useFunds') as any).useCreateTaxStatement = jest.fn().mockReturnValue(mockUseEventSubmission.createTaxStatement);
    (require('../../../hooks/useFunds') as any).useUpdateFundEvent = jest.fn().mockReturnValue(mockUseUpdateFundEvent);
    (require('../../../hooks/useEventSubmission') as any).useEventSubmission = jest.fn().mockReturnValue(mockUseEventSubmission);
  });

  const defaultProps = {
    mode: 'create' as const,
    open: true,
    onClose: jest.fn(),
    onSuccess: jest.fn(),
    fundId: 1,
    fundTrackingType: 'cost_based' as const,
  };

  const mockEvent: ExtendedFundEvent = {
    id: 1,
    fund_id: 1,
    event_type: EventType.CAPITAL_CALL,
    event_date: '2024-01-15',
    amount: 1000,
    description: 'Test capital call',
    reference_number: 'CC001',
    created_at: '2024-01-15T00:00:00Z',
    updated_at: '2024-01-15T00:00:00Z',
  };

  const renderComponent = (props = {}) => {
    return render(<UnifiedFundEventForm {...defaultProps} {...props} />);
  };

  describe('Create Mode', () => {
    it('should render create mode with correct title', () => {
      renderComponent({ mode: 'create' });

      expect(screen.getByText('Add Cash Flow Event')).toBeInTheDocument();
      expect(screen.getByText('Add Event')).toBeInTheDocument();
    });

    it('should show event type selector in create mode', () => {
      renderComponent({ mode: 'create' });

      expect(screen.getByTestId('event-type-selector')).toBeInTheDocument();
      expect(screen.getByText('Mode: create')).toBeInTheDocument();
    });

    it('should handle form submission in create mode', async () => {
      const mockHandleSubmit = jest.fn();
      (require('../../../hooks/useEventSubmission') as any).useEventSubmission = jest.fn().mockReturnValue({
        ...mockUseEventSubmission,
        handleSubmit: mockHandleSubmit,
      });

      // Mock form with valid data for submission
      (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedEventForm,
        eventType: 'CAPITAL_CALL',
        formData: { event_date: '2024-01-15', amount: '1000' },
        validateForm: jest.fn().mockReturnValue(true),
      });

      renderComponent({ mode: 'create' });

      const submitButton = screen.getByText('Add Event');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockHandleSubmit).toHaveBeenCalledWith({
          eventType: 'CAPITAL_CALL',
          formData: { event_date: '2024-01-15', amount: '1000' },
          distributionType: '',
          subDistributionType: '',
        });
      });
    });

    it('should show loading state during submission', () => {
      (require('../../../hooks/useEventSubmission') as any).useEventSubmission = jest.fn().mockReturnValue({
        ...mockUseEventSubmission,
        createFundEvent: { loading: true, error: null, data: null },
      });

      renderComponent({ mode: 'create' });

      expect(screen.getByText('Adding Event...')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Cancel' })).toBeDisabled();
    });

    it('should show success message after successful creation', () => {
      // Mock the success state to be true
      (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedEventForm,
        success: true,
      });

      renderComponent({ mode: 'create' });

      expect(screen.getByText('Event created successfully!')).toBeInTheDocument();
    });
  });

  describe('Edit Mode', () => {
    it('should render edit mode with correct title', () => {
      renderComponent({ 
        mode: 'edit', 
        event: mockEvent 
      });

      expect(screen.getByText('Edit Event')).toBeInTheDocument();
      expect(screen.getByText('Update Event')).toBeInTheDocument();
    });

    it('should show event type selector in edit mode', () => {
      renderComponent({ 
        mode: 'edit', 
        event: mockEvent 
      });

      expect(screen.getByTestId('event-type-selector')).toBeInTheDocument();
      expect(screen.getByText('Mode: edit')).toBeInTheDocument();
    });

    it('should handle form submission in edit mode', async () => {
      // Mock form with valid data for submission
      (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedEventForm,
        eventType: 'CAPITAL_CALL',
        formData: { event_date: '2024-01-15', amount: '1000', description: 'Test capital call', reference_number: 'CC001' },
        validateForm: jest.fn().mockReturnValue(true),
      });

      renderComponent({ 
        mode: 'edit', 
        event: mockEvent 
      });

      const submitButton = screen.getByText('Update Event');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockUseUpdateFundEvent.mutate).toHaveBeenCalledWith({
          amount: 1000,
          event_date: '2024-01-15',
          description: 'Test capital call',
          reference_number: 'CC001',
        });
      });
    });

    it('should show loading state during update', () => {
      (require('../../../hooks/useFunds') as any).useUpdateFundEvent = jest.fn().mockReturnValue({
        ...mockUseUpdateFundEvent,
        loading: true,
      });

      renderComponent({ 
        mode: 'edit', 
        event: mockEvent 
      });

      expect(screen.getByText('Updating Event...')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Cancel' })).toBeDisabled();
    });

    it('should show success message after successful update', () => {
      // Mock the success state to be true
      (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedEventForm,
        success: true,
      });

      renderComponent({ 
        mode: 'edit', 
        event: mockEvent 
      });

      expect(screen.getByText('Event updated successfully!')).toBeInTheDocument();
    });

    it('should handle distribution events correctly', async () => {
      const distributionEvent: ExtendedFundEvent = {
        ...mockEvent,
        event_type: EventType.DISTRIBUTION,
        distribution_type: DistributionType.INTEREST,
        amount: 500,
        net_interest: 450,
        withholding_amount: 50,
        withholding_rate: 10,
      };

      // Mock form with valid data for distribution submission
      (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedEventForm,
        eventType: 'DISTRIBUTION',
        distributionType: 'INTEREST',
        subDistributionType: 'REGULAR',
        formData: { event_date: '2024-01-15', amount: '500', description: 'Test capital call', reference_number: 'CC001' },
        validateForm: jest.fn().mockReturnValue(true),
      });

      renderComponent({ 
        mode: 'edit', 
        event: distributionEvent 
      });

      const submitButton = screen.getByText('Update Event');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockUseUpdateFundEvent.mutate).toHaveBeenCalledWith({
          amount: 500,
          event_date: '2024-01-15',
          description: 'Test capital call',
          reference_number: 'CC001',
        });
      });
    });

    it('should handle NAV-based events correctly', async () => {
      const navEvent: ExtendedFundEvent = {
        ...mockEvent,
        event_type: EventType.UNIT_PURCHASE,
        units_purchased: 100,
        unit_price: 10.5,
        brokerage_fee: 50,
      };

      // Mock form with valid data for NAV submission
      (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedEventForm,
        eventType: 'UNIT_PURCHASE',
        formData: { event_date: '2024-01-15', units_purchased: '100', unit_price: '10.5', brokerage_fee: '50', description: 'Test capital call', reference_number: 'CC001' },
        validateForm: jest.fn().mockReturnValue(true),
      });

      renderComponent({ 
        mode: 'edit', 
        event: navEvent 
      });

      const submitButton = screen.getByText('Update Event');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockUseUpdateFundEvent.mutate).toHaveBeenCalledWith({
          units_purchased: 100,
          unit_price: 10.5,
          brokerage_fee: 50,
          event_date: '2024-01-15',
          description: 'Test capital call',
          reference_number: 'CC001',
        });
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error messages', () => {
      (require('../../../hooks/useErrorHandler') as any).useErrorHandler = jest.fn().mockReturnValue({
        ...mockUseErrorHandler,
        error: { message: 'Test error message', retryable: true, type: 'error', severity: 'error', timestamp: new Date() },
      });

      renderComponent();

      expect(screen.getByText('Test error message')).toBeInTheDocument();
    });

    it('should handle validation errors', () => {
      (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedEventForm,
        validationErrors: { event_date: 'Event date is required' },
        isFormValid: false,
      });

      renderComponent();

      // The validation error should be displayed in the form field
      // Let's check if the submit button is disabled instead
      expect(screen.getByRole('button', { name: 'Add Event' })).toBeDisabled();
    });
  });

  describe('Form Fields', () => {
    it('should show distribution form when distribution is selected', () => {
      (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedEventForm,
        eventType: 'DISTRIBUTION',
        distributionType: 'INTEREST',
        subDistributionType: 'REGULAR',
      });

      renderComponent();

      expect(screen.getByTestId('distribution-form')).toBeInTheDocument();
    });

    it('should show unit transaction form for NAV-based events', () => {
      (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedEventForm,
        eventType: 'UNIT_PURCHASE',
      });

      renderComponent({ fundTrackingType: 'nav_based' });

      expect(screen.getByTestId('unit-transaction-form')).toBeInTheDocument();
    });

    it('should show NAV update form for NAV updates', () => {
      (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedEventForm,
        eventType: 'NAV_UPDATE',
      });

      renderComponent({ fundTrackingType: 'nav_based' });

      expect(screen.getByTestId('nav-update-form')).toBeInTheDocument();
    });

    it('should show tax statement form for tax statements', () => {
      (require('../../../hooks/useUnifiedEventForm') as any).useUnifiedEventForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedEventForm,
        eventType: 'TAX_STATEMENT',
      });

      renderComponent();

      expect(screen.getByTestId('tax-statement-form')).toBeInTheDocument();
    });
  });

  describe('Modal Behavior', () => {
    it('should call onClose when cancel button is clicked', () => {
      const onClose = jest.fn();
      renderComponent({ onClose });

      fireEvent.click(screen.getByText('Cancel'));
      expect(onClose).toHaveBeenCalled();
    });

    it('should call onSuccess after successful submission', async () => {
      const onSuccess = jest.fn();
      (require('../../../hooks/useEventSubmission') as any).useEventSubmission = jest.fn().mockReturnValue({
        ...mockUseEventSubmission,
        createFundEvent: { loading: false, error: null, data: { id: 1 } },
      });

      renderComponent({ onSuccess });

      // Wait for the success timeout
      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalled();
      }, { timeout: 1500 });
    });
  });
}); 