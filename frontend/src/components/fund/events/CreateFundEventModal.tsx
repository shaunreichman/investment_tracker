import React, { useState, useEffect, useCallback } from 'react';
import {
  TextField,
  Box,
  Typography,
  useTheme
} from '@mui/material';
import { useErrorHandler } from '../../../hooks/useErrorHandler';
import { useFund } from '../../../hooks/useFunds';
import { formatNumber, parseNumber } from '../../../utils/helpers';
import { useEventSubmission } from '../../../hooks/useEventSubmission';
import EventTypeSelector from './create/EventTypeSelector';
import DistributionForm from './create/DistributionForm';
import UnitTransactionForm from './create/UnitTransactionForm';
import NavUpdateForm from './create/NavUpdateForm';
import TaxStatementForm from './create/TaxStatementForm';
import { FormContainer } from '../../ui/FormContainer';
import { useUnifiedForm } from '../../../hooks/forms/useUnifiedForm';
import { createValidator, validationRules } from '../../../utils/validators';
import { SuccessBanner } from '../../ui/SuccessBanner';
import { FundType } from '../../../types/api';

interface CreateFundEventModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  fundId: number;
  fundTrackingType: FundType;
}

// Basic form data interface for common fields
interface EventFormData {
  event_date: string;
  amount: string;
  units_purchased: string;
  units_sold: string;
  unit_price: string;
  nav_per_share: string;
  brokerage_fee: string;
  gross_amount: string;
  net_amount: string;
  withholding_tax_amount: string;
  withholding_tax_rate: string;
  financial_year: string;
  statement_date: string;
  eofy_debt_interest_deduction_rate: string;
  interest_received_in_cash: string;
  interest_receivable_this_fy: string;
  interest_receivable_prev_fy: string;
  interest_non_resident_withholding_tax_from_statement: string;
  interest_income_tax_rate: string;
  dividend_franked_income_amount: string;
  dividend_unfranked_income_amount: string;
  dividend_franked_income_tax_rate: string;
  dividend_unfranked_income_tax_rate: string;
  capital_gain_income_amount: string;
  capital_gain_income_tax_rate: string;
  accountant: string;
  notes: string;
}

// Initial form values
const initialFormValues: EventFormData = {
  event_date: new Date().toISOString().slice(0, 10),
  amount: '',
  units_purchased: '',
  units_sold: '',
  unit_price: '',
  nav_per_share: '',
  brokerage_fee: '',
  gross_amount: '',
  net_amount: '',
  withholding_tax_amount: '',
  withholding_tax_rate: '',
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
  notes: ''
};

// Basic validation rules for common fields
const validators = {
  event_date: createValidator(
    validationRules.required('Event date'),
    validationRules.validDate('Event date')
  ),
  amount: (value: string) => {
    if (!value) return undefined;
    return validationRules.positiveNumber('Amount')(value);
  },
  units_purchased: (value: string) => {
    if (!value) return undefined;
    return validationRules.positiveNumber('Units purchased')(value);
  },
  units_sold: (value: string) => {
    if (!value) return undefined;
    return validationRules.positiveNumber('Units sold')(value);
  },
  unit_price: (value: string) => {
    if (!value) return undefined;
    return validationRules.positiveNumber('Unit price')(value);
  },
  nav_per_share: (value: string) => {
    if (!value) return undefined;
    return validationRules.positiveNumber('NAV per share')(value);
  },
  brokerage_fee: (value: string) => {
    if (!value) return undefined;
    return validationRules.nonNegativeNumber('Brokerage fee')(value);
  }
};

const CreateFundEventModal: React.FC<CreateFundEventModalProps> = ({
  open,
  onClose,
  onSuccess,
  fundId,
  fundTrackingType
}) => {
  const theme = useTheme();
  
  // Event type state (keeping existing logic for now)
  const [eventType, setEventType] = useState<string>('');
  const [distributionType, setDistributionType] = useState<string>('');
  const [subDistributionType, setSubDistributionType] = useState<string>('');
  const [success, setSuccess] = useState(false);
  const [hybridFieldOverrides, setHybridFieldOverrides] = useState<{[key: string]: boolean}>({});

  // Centralized error handler
  const { error, setError, clearError } = useErrorHandler();
  // Centralized API hooks
  const { data: fundData } = useFund(fundId);
  const { handleSubmit: submitEvent, createFundEvent, createTaxStatement } = useEventSubmission({
    fundId,
    fundEntity: fundData?.entity || null,
    onSuccess: () => {
      setSuccess(true);
      setTimeout(() => {
        resetForm();
        onSuccess();
        onClose();
      }, 1000);
    },
    onError: setError,
  });

  // Unified form management for basic form fields
  const {
    values: formData,
    errors: validationErrors,
    isDirty,
    isValid: formIsValid,
    isSubmitting: formIsSubmitting,
    setFieldValue,
    reset: resetFormData,
    clearErrors
  } = useUnifiedForm<EventFormData>({
    initialValues: initialFormValues,
    validators,
    onSubmit: async (values) => {
      // This will be handled by the existing event submission logic
      // For now, just validate and let the existing flow continue
      return Promise.resolve();
    },
    onSuccess: () => {
      // Success handled by existing flow
    },
    onError: setError
  });

  // Reset form function (combines unified form reset with event type reset)
  const resetForm = useCallback(() => {
    resetFormData();
    setEventType('');
    setDistributionType('');
    setSubDistributionType('');
    setSuccess(false);
    setHybridFieldOverrides({});
  }, [resetFormData, setEventType, setDistributionType, setSubDistributionType, setHybridFieldOverrides]);

  // Handle errors and success from hooks
  useEffect(() => {
    if (createFundEvent.error) {
      setError(createFundEvent.error);
    }
  }, [createFundEvent.error, setError]);

  useEffect(() => {
    if (createTaxStatement.error) {
      setError(createTaxStatement.error);
    }
  }, [createTaxStatement.error, setError]);

  // Handle success flow
  useEffect(() => {
    if (createFundEvent.data) {
      setSuccess(true);
      setTimeout(() => {
        resetForm();
        onSuccess();
        onClose();
      }, 1000);
    }
  }, [createFundEvent.data, onSuccess, onClose, resetForm]);

  useEffect(() => {
    if (createTaxStatement.data) {
      setSuccess(true);
      setTimeout(() => {
        resetForm();
        onSuccess();
        onClose();
      }, 1000);
    }
  }, [createTaxStatement.data, onSuccess, onClose, resetForm]);

  // Reset form when modal opens
  useEffect(() => {
    if (open) {
      resetForm();
      clearErrors();
    }
  }, [open, clearErrors, resetForm]);

  // Handle input change (combines unified form with existing logic)
  const handleInputChange = (field: string, value: string) => {
    setFieldValue(field as keyof EventFormData, value);
    
    // Auto-calculate tax payment date when financial year changes
    if (field === 'financial_year' && eventType === 'TAX_STATEMENT') {
      // This logic would need to be implemented based on your business rules
      // setFieldValue('tax_payment_date', calculateTaxPaymentDate(value));
    }
  };

  // Handle hybrid field toggle
  const handleHybridFieldToggle = (field: string) => {
    setHybridFieldOverrides(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  // Handle back navigation
  const handleBack = () => {
    if (distributionType) {
      setDistributionType('');
      setSubDistributionType('');
      setFieldValue('amount', '');
    } else {
      setEventType('');
    }
  };

  // Form validation (combines unified form validation with event type validation)
  const isFormValid = () => {
    // Basic form validation from unified form
    const basicFormValid = formIsValid;
    
    // Event type specific validation
    if (!eventType) return false;
    
    if (eventType === 'DISTRIBUTION' && !distributionType) return false;
    
    if (eventType === 'DISTRIBUTION' && distributionType === 'DIVIDEND' && !subDistributionType) return false;
    
    if (eventType === 'DISTRIBUTION' && distributionType === 'INTEREST' && !subDistributionType) return false;
    
    return basicFormValid;
  };

  // Handle form submission
  const handleSubmit = () => {
    clearError();
    submitEvent({
      eventType,
      formData,
      distributionType,
      subDistributionType,
    });
  };

  // Handle modal close
  const handleClose = () => {
    if (!formIsSubmitting) {
      onClose();
      clearError();
      resetForm();
    }
  };



  return (
    <FormContainer
      open={open}
      title="Create Fund Event"
      subtitle="Select event type and enter details"
      onClose={handleClose}
      onSubmit={handleSubmit}
      isSubmitting={formIsSubmitting}
      isValid={isFormValid()}
      isDirty={isDirty}
      showCloseConfirmation={true}
      maxWidth="lg"
      fullWidth={true}
    >
      {/* Success Banner */}
      {success && (
        <SuccessBanner 
          title="Event created successfully!" 
          subtitle="Redirecting to fund details..." 
        />
      )}

      {/* Error Display */}
      {error && (
        <Box sx={{ mb: 2 }}>
          <Typography color="error" variant="body2">
            {error.userMessage || error.message || 'An error occurred'}
          </Typography>
        </Box>
      )}

             {/* Event Type Selection */}
       {!eventType && (
         <EventTypeSelector
           fundTrackingType={fundTrackingType}
           eventType={eventType as any}
           distributionType={distributionType}
           subDistributionType={subDistributionType}
           onEventTypeSelect={setEventType as any}
           onDistributionTypeSelect={setDistributionType}
           onSubDistributionTypeSelect={setSubDistributionType}
           onBack={handleBack}
         />
       )}

       {/* Distribution Type Selection */}
       {eventType === 'DISTRIBUTION' && !distributionType && (
         <DistributionForm
           distributionType={distributionType}
           subDistributionType={subDistributionType}
           formData={formData as any}
           validationErrors={validationErrors as any}
           onInputChange={handleInputChange}
           eventType={eventType}
         />
       )}

      {/* Form appears below all cards (after event type or distribution type selected) */}
      {((eventType && eventType !== 'DISTRIBUTION' && eventType !== 'TAX_STATEMENT') || 
        (eventType === 'DISTRIBUTION' && distributionType && 
         (distributionType === 'OTHER' || 
          (distributionType === 'DIVIDEND' && subDistributionType) || 
          (distributionType === 'INTEREST' && subDistributionType))) || 
        eventType === 'TAX_STATEMENT') && (
        <Box mt={2}>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Fields marked with <span style={{ color: theme.palette.error.main }}>*</span> are required.
          </Typography>
          <Box component="form" noValidate autoComplete="off">
            <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
              <TextField
                label={<span>Event Date <span style={{ color: theme.palette.error.main }}>*</span></span>}
                type="date"
                value={formData.event_date || ''}
                onChange={e => handleInputChange('event_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
                error={!!validationErrors.event_date}
                helperText={validationErrors.event_date}
              />
              {(eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION' || eventType === 'RETURN_OF_CAPITAL') && 
               !(distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX') && (
                <TextField
                  label={<span>{eventType === 'RETURN_OF_CAPITAL' ? 'Return Amount' : 'Amount'} <span style={{ color: theme.palette.error.main }}>*</span></span>}
                  type="text"
                  value={formatNumber(formData.amount || '')}
                  onChange={e => handleInputChange('amount', parseNumber(e.target.value))}
                  fullWidth
                  error={!!validationErrors.amount}
                  helperText={validationErrors.amount}
                />
              )}
              
                             {/* Render appropriate form based on event type */}
               {eventType === 'UNIT_PURCHASE' && (
                 <UnitTransactionForm
                   eventType={eventType}
                   formData={formData as any}
                   validationErrors={validationErrors as any}
                   onInputChange={handleInputChange}
                 />
               )}
               
               {eventType === 'UNIT_SALE' && (
                 <UnitTransactionForm
                   eventType={eventType}
                   formData={formData as any}
                   validationErrors={validationErrors as any}
                   onInputChange={handleInputChange}
                 />
               )}
               
               {eventType === 'NAV_UPDATE' && (
                 <NavUpdateForm
                   formData={formData as any}
                   validationErrors={validationErrors as any}
                   onInputChange={handleInputChange}
                 />
               )}
               
               {eventType === 'TAX_STATEMENT' && (
                 <TaxStatementForm
                   formData={formData as any}
                   validationErrors={validationErrors as any}
                   financialYears={[]}
                   fundEntity={fundData?.entity || null}
                   hybridFieldOverrides={hybridFieldOverrides}
                   onInputChange={handleInputChange}
                   onHybridFieldToggle={handleHybridFieldToggle}
                 />
               )}
            </Box>
          </Box>
        </Box>
      )}
    </FormContainer>
  );
};

export default CreateFundEventModal; 