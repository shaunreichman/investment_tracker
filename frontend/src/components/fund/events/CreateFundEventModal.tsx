import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  CircularProgress,
  Typography
} from '@mui/material';
import { ErrorDisplay } from '../../ErrorDisplay';
import { SuccessBanner } from '../../ui/SuccessBanner';
import { useErrorHandler } from '../../../hooks/useErrorHandler';
import { useFund } from '../../../hooks/useFunds';
import { formatNumber, parseNumber } from '../../../utils/helpers';
// imports retained for reference types in hooks, not directly used here
import { useEventSubmission } from '../../../hooks/useEventSubmission';
import EventTypeSelector from './create/EventTypeSelector';
import DistributionForm from './create/DistributionForm';
import UnitTransactionForm from './create/UnitTransactionForm';
import NavUpdateForm from './create/NavUpdateForm';
import TaxStatementForm from './create/TaxStatementForm';
import { useCreateEventForm } from '../../../hooks/useCreateEventForm';
// ExtendedFundEvent type not used directly in this component

// Constants for styling
const REQUIRED_FIELD_COLOR = '#d32f2f';
const SUCCESS_BOX_STYLES = {
  mb: 2,
  p: 2,
  bgcolor: 'success.light',
  borderRadius: 1,
  display: 'flex',
  alignItems: 'center'
};

interface CreateFundEventModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  fundId: number;
  fundTrackingType: 'nav_based' | 'cost_based';
}

const CreateFundEventModal: React.FC<CreateFundEventModalProps> = ({
  open,
  onClose,
  onSuccess,
  fundId,
  fundTrackingType
}) => {
  // Use the create-only form state management hook
  const {
    eventType,
    setEventType,
    distributionType,
    setDistributionType,
    subDistributionType,
    setSubDistributionType,
    formData,
    // setFormData,
    success,
    setSuccess,
    validationErrors,
    isFormValid,
    hybridFieldOverrides,
    // setHybridFieldOverrides,
    handleInputChange,
    handleHybridFieldToggle,
    validateForm,
    resetForm,
    handleBack,
  } = useCreateEventForm({
    open,
    fundTrackingType
  });

  // Centralized error handler
  const { error, setError, clearError } = useErrorHandler();
  const [fundEntity, setFundEntity] = useState<any>(null);
  const [financialYears, setFinancialYears] = useState<string[]>([]);

  // Centralized API hooks
  const { data: fundData } = useFund(fundId);
  const { handleSubmit: submitEvent, createFundEvent, createTaxStatement } = useEventSubmission({
    fundId,
    fundEntity,
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

  // Edit functionality removed - use delete + create pattern instead

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

  // Edit functionality removed - use delete + create pattern instead

  useEffect(() => {
    if (createFundEvent.data) {
      setSuccess(true);
      setTimeout(() => {
        resetForm();
        onSuccess();
        onClose();
      }, 1000);
    }
  }, [createFundEvent.data, onSuccess, onClose, resetForm, setSuccess]);

  useEffect(() => {
    if (createTaxStatement.data) {
      setSuccess(true);
      setTimeout(() => {
        resetForm();
        onSuccess();
        onClose();
      }, 1000);
    }
  }, [createTaxStatement.data, onSuccess, onClose, resetForm, setSuccess]);

  // Edit functionality removed - use delete + create pattern instead

  // Load fund entity and financial years
  useEffect(() => {
    if (fundData) {
      setFundEntity(fundData.entity);
      // Generate financial years (current year + 5 years back)
      const currentYear = new Date().getFullYear();
      const years = [];
      for (let i = 0; i < 6; i++) {
        years.push((currentYear - i).toString());
      }
      setFinancialYears(years);
    }
  }, [fundData]);

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    clearError();

    // Create mode: Use existing event submission logic
    await submitEvent({
      eventType,
      formData,
      distributionType,
      subDistributionType,
    });
  };

  // Determine loading state and button text (edit mode removed)
  const isLoading = createFundEvent.loading || createTaxStatement.loading;

  const buttonText = isLoading ? 'Adding Event...' : 'Add Event';

  const dialogTitle = 'Add Cash Flow Event';

  // UI rendering
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>{dialogTitle}</DialogTitle>
      <DialogContent>
        {success && (
          <SuccessBanner title="Event created successfully!" />
        )}
        {error && (
          <ErrorDisplay
            error={error}
            canRetry={error.retryable}
            onRetry={() => handleSubmit()}
            onDismiss={clearError}
            variant="inline"
          />
        )}
        {/* Event Type Selection */}
        <EventTypeSelector
          fundTrackingType={fundTrackingType}
          eventType={eventType}
          distributionType={distributionType}
          subDistributionType={subDistributionType}
          mode="create"
          onEventTypeSelect={setEventType}
          onDistributionTypeSelect={setDistributionType}
          onSubDistributionTypeSelect={setSubDistributionType}
          onBack={handleBack}
        />

        {/* Form appears below all cards (after event type or distribution type selected) */}
        {((eventType && eventType !== 'DISTRIBUTION' && eventType !== 'TAX_STATEMENT') || (eventType === 'DISTRIBUTION' && distributionType && (distributionType === 'OTHER' || (distributionType === 'DIVIDEND' && subDistributionType) || (distributionType === 'INTEREST' && subDistributionType))) || eventType === 'TAX_STATEMENT') && (
          <Box mt={2}>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Fields marked with <span style={{ color: REQUIRED_FIELD_COLOR }}>*</span> are required.
            </Typography>
            <Box component="form" noValidate autoComplete="off">
              <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
                <TextField
                  label={<span>Event Date <span style={{ color: REQUIRED_FIELD_COLOR }}>*</span></span>}
                  type="date"
                  value={formData.event_date || ''}
                  onChange={e => handleInputChange('event_date', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  fullWidth
                  error={!!validationErrors.event_date}
                  helperText={validationErrors.event_date}
                />
                {(eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION' || eventType === 'RETURN_OF_CAPITAL') && !(distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX') && (
                  <TextField
                    label={<span>{eventType === 'RETURN_OF_CAPITAL' ? 'Return Amount' : 'Amount'} <span style={{ color: REQUIRED_FIELD_COLOR }}>*</span></span>}
                    type="text"
                    value={formatNumber(formData.amount || '')}
                    onChange={e => handleInputChange('amount', parseNumber(e.target.value))}
                    fullWidth
                    error={!!validationErrors.amount}
                    helperText={validationErrors.amount}
                  />
                )}
                <DistributionForm
                  distributionType={distributionType}
                  subDistributionType={subDistributionType}
                  formData={formData}
                  validationErrors={validationErrors}
                  onInputChange={handleInputChange}
                  eventType={eventType}
                />
                <TextField
                  label="Description (Optional)"
                  value={formData.description || ''}
                  onChange={e => handleInputChange('description', e.target.value)}
                  fullWidth
                />
                <TextField
                  label="Reference Number (Optional)"
                  value={formData.reference_number || ''}
                  onChange={e => handleInputChange('reference_number', e.target.value)}
                  fullWidth
                />
                
                {/* Unit Transaction Form */}
                {(eventType === 'UNIT_PURCHASE' || eventType === 'UNIT_SALE') && (
                  <UnitTransactionForm
                    eventType={eventType as 'UNIT_PURCHASE' | 'UNIT_SALE'}
                    formData={formData}
                    validationErrors={validationErrors}
                    onInputChange={handleInputChange}
                  />
                )}
                
                {/* NAV Update Form */}
                {eventType === 'NAV_UPDATE' && (
                  <NavUpdateForm
                    formData={formData}
                    validationErrors={validationErrors}
                    onInputChange={handleInputChange}
                  />
                )}
                
                {/* Tax Statement Form */}
                {eventType === 'TAX_STATEMENT' && (
                  <TaxStatementForm
                    formData={formData}
                    validationErrors={validationErrors}
                    financialYears={financialYears}
                    fundEntity={fundEntity}
                    hybridFieldOverrides={hybridFieldOverrides}
                    onInputChange={handleInputChange}
                    onHybridFieldToggle={handleHybridFieldToggle}
                  />
                )}
              </Box>
            </Box>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={isLoading || !isFormValid}
          startIcon={isLoading ? <CircularProgress size={20} /> : null}
        >
          {buttonText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateFundEventModal; 