import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import CreateFundEventModal from './CreateFundEventModal';
import { FundTrackingType } from '../../../types/api';

// Mock the hooks
jest.mock('../../../hooks/useErrorHandler');
jest.mock('../../../hooks/useFunds');
jest.mock('../../../hooks/useEventSubmission');
jest.mock('../../../hooks/forms/useUnifiedForm');


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

const mockUseUnifiedForm = {
  values: { event_date: '2024-01-15' },
  errors: {},
  touched: {},
  isDirty: false,
  isValid: true,
  isSubmitting: false,
  setFieldValue: jest.fn(),
  setFieldError: jest.fn(),
  validateField: jest.fn(),
  validateAll: jest.fn().mockReturnValue(true),
  handleSubmit: jest.fn(),
  reset: jest.fn(),
  clearErrors: jest.fn(),
  markFieldTouched: jest.fn(),
  markAllTouched: jest.fn(),
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



describe('CreateFundEventModal', () => {
  // Add jest-axe matcher
  expect.extend(toHaveNoViolations);

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Setup default mock implementations
    (require('../../../hooks/forms/useUnifiedForm') as any).useUnifiedForm = jest.fn().mockReturnValue(mockUseUnifiedForm);
    (require('../../../hooks/useErrorHandler') as any).useErrorHandler = jest.fn().mockReturnValue(mockUseErrorHandler);
    (require('../../../hooks/useFunds') as any).useFund = jest.fn().mockReturnValue(mockUseFund);
    (require('../../../hooks/useFunds') as any).useCreateFundEvent = jest.fn().mockReturnValue(mockUseEventSubmission.createFundEvent);
    (require('../../../hooks/useFunds') as any).useCreateTaxStatement = jest.fn().mockReturnValue(mockUseEventSubmission.createTaxStatement);

    (require('../../../hooks/useEventSubmission') as any).useEventSubmission = jest.fn().mockReturnValue(mockUseEventSubmission);
  });

  const defaultProps = {
    open: true,
    onClose: jest.fn(),
    onSuccess: jest.fn(),
    fundId: 1,
    fundTrackingType: FundTrackingType.COST_BASED,
  };

  // Note: mockEvent retained only if needed in future tests

  const renderComponent = (props = {}) => {
    return render(<CreateFundEventModal {...defaultProps} {...props} />);
  };

  describe('Form Functionality', () => {
    it('should render with correct title', () => {
      renderComponent();

      expect(screen.getByText('Add Cash Flow Event')).toBeInTheDocument();
      expect(screen.getByText('Add Event')).toBeInTheDocument();
    });

    it('should show event type selector', () => {
      renderComponent();

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
      (require('../../../hooks/forms/useUnifiedForm') as any).useUnifiedForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedForm,
        eventType: 'CAPITAL_CALL',
        formData: { event_date: '2024-01-15', amount: '1000' },
        validateForm: jest.fn().mockReturnValue(true),
      });

      renderComponent();

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

      renderComponent();

      expect(screen.getByText('Adding Event...')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Cancel' })).toBeDisabled();
    });

    it('should show success message after successful creation', () => {
      // Mock the success state to be true
      (require('../../../hooks/forms/useUnifiedForm') as any).useUnifiedForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedForm,
        success: true,
      });

      renderComponent();

      expect(screen.getByText('Event created successfully!')).toBeInTheDocument();
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
      (require('../../../hooks/forms/useUnifiedForm') as any).useUnifiedForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedForm,
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
      (require('../../../hooks/forms/useUnifiedForm') as any).useUnifiedForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedForm,
        eventType: 'DISTRIBUTION',
        distributionType: 'INTEREST',
        subDistributionType: 'REGULAR',
      });

      renderComponent();

      expect(screen.getByTestId('distribution-form')).toBeInTheDocument();
    });

    it('should show unit transaction form for NAV-based events', () => {
      (require('../../../hooks/forms/useUnifiedForm') as any).useUnifiedForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedForm,
        eventType: 'UNIT_PURCHASE',
      });

      renderComponent({ fundTrackingType: 'nav_based' });

      expect(screen.getByTestId('unit-transaction-form')).toBeInTheDocument();
    });

    it('should show NAV update form for NAV updates', () => {
      (require('../../../hooks/forms/useUnifiedForm') as any).useUnifiedForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedForm,
        eventType: 'NAV_UPDATE',
      });

      renderComponent({ fundTrackingType: 'nav_based' });

      expect(screen.getByTestId('nav-update-form')).toBeInTheDocument();
    });

    it('should show tax statement form for tax statements', () => {
      (require('../../../hooks/forms/useUnifiedForm') as any).useUnifiedForm = jest.fn().mockReturnValue({
        ...mockUseUnifiedForm,
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

  describe('Accessibility', () => {
    it('has no obvious accessibility violations (axe smoke)', async () => {
      const { container } = renderComponent();
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });
}); 