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
  Typography,
  Divider,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import { ErrorDisplay } from '../../ErrorDisplay';
import { useErrorHandler } from '../../../hooks/useErrorHandler';
import { useFund } from '../../../hooks/useFunds';
import { useCreateFundEvent, useCreateTaxStatement, useUpdateFundEvent } from '../../../hooks/useFunds';
import { validateField } from '../../../utils/validators';
import { formatNumber, parseNumber, calculateTaxPaymentDate } from '../../../utils/helpers';
import { useEventSubmission } from '../../../hooks/useEventSubmission';
import EventTypeSelector from './create/EventTypeSelector';
import DistributionForm from './create/DistributionForm';
import UnitTransactionForm from './create/UnitTransactionForm';
import NavUpdateForm from './create/NavUpdateForm';
import TaxStatementForm from './create/TaxStatementForm';
import { useUnifiedEventForm } from '../../../hooks/useUnifiedEventForm';
import { ExtendedFundEvent } from '../../../types/api';

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

interface UnifiedFundEventFormProps {
  mode: 'create' | 'edit';
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  fundId: number;
  fundTrackingType: 'nav_based' | 'cost_based';
  event?: ExtendedFundEvent; // Only for edit mode
  allEvents?: ExtendedFundEvent[]; // All events for edit mode to detect withholding tax
}

const UnifiedFundEventForm: React.FC<UnifiedFundEventFormProps> = ({
  mode,
  open,
  onClose,
  onSuccess,
  fundId,
  fundTrackingType,
  event,
  allEvents
}) => {
  // Use the unified form state management hook
  const {
    eventType,
    setEventType,
    distributionType,
    setDistributionType,
    subDistributionType,
    setSubDistributionType,
    formData,
    setFormData,
    success,
    setSuccess,
    validationErrors,
    isFormValid,
    hybridFieldOverrides,
    setHybridFieldOverrides,
    handleInputChange,
    handleHybridFieldToggle,
    validateForm,
    resetForm,
    handleBack,
  } = useUnifiedEventForm({
    mode,
    open,
    fundTrackingType,
    event,
    allEvents
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

  // Update event hook for edit mode
  const updateFundEvent = useUpdateFundEvent(fundId, event?.id || 0);

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

  useEffect(() => {
    if (updateFundEvent.error) {
      setError(updateFundEvent.error);
    }
  }, [updateFundEvent.error, setError]);

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

  useEffect(() => {
    if (updateFundEvent.data) {
      setSuccess(true);
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1000);
    }
  }, [updateFundEvent.data, onSuccess, onClose]);

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

    if (mode === 'create') {
      // Create mode: Use existing event submission logic
      await submitEvent({
        eventType,
        formData,
        distributionType,
        subDistributionType,
      });
    } else {
      // Edit mode: Use update event logic
      if (!event) return;

      const payload: any = {};

      // Add fields based on event type
      if (event.event_type === 'CAPITAL_CALL' || event.event_type === 'RETURN_OF_CAPITAL') {
        if (formData.amount) payload.amount = parseFloat(parseNumber(formData.amount));
        if (formData.event_date) payload.event_date = formData.event_date;
        if (formData.description !== undefined) payload.description = formData.description;
        if (formData.reference_number !== undefined) payload.reference_number = formData.reference_number;
      }

      if (event.event_type === 'UNIT_PURCHASE') {
        if (formData.units_purchased) payload.units_purchased = parseFloat(formData.units_purchased);
        if (formData.unit_price) payload.unit_price = parseFloat(formData.unit_price);
        if (formData.brokerage_fee) payload.brokerage_fee = parseFloat(formData.brokerage_fee);
        if (formData.event_date) payload.event_date = formData.event_date;
        if (formData.description !== undefined) payload.description = formData.description;
        if (formData.reference_number !== undefined) payload.reference_number = formData.reference_number;
      }

      if (event.event_type === 'UNIT_SALE') {
        if (formData.units_sold) payload.units_sold = parseFloat(formData.units_sold);
        if (formData.unit_price) payload.unit_price = parseFloat(formData.unit_price);
        if (formData.brokerage_fee) payload.brokerage_fee = parseFloat(formData.brokerage_fee);
        if (formData.event_date) payload.event_date = formData.event_date;
        if (formData.description !== undefined) payload.description = formData.description;
        if (formData.reference_number !== undefined) payload.reference_number = formData.reference_number;
      }

      if (event.event_type === 'NAV_UPDATE') {
        if (formData.nav_per_share) payload.nav_per_share = parseFloat(formData.nav_per_share);
        if (formData.event_date) payload.event_date = formData.event_date;
        if (formData.description !== undefined) payload.description = formData.description;
        if (formData.reference_number !== undefined) payload.reference_number = formData.reference_number;
      }

      if (event.event_type === 'DISTRIBUTION') {
        if (formData.distribution_type) payload.distribution_type = formData.distribution_type;
        if (formData.event_date) payload.event_date = formData.event_date;
        if (formData.description !== undefined) payload.description = formData.description;
        if (formData.reference_number !== undefined) payload.reference_number = formData.reference_number;
        
        // Handle all distributions with unified approach
        if (formData.amount) payload.amount = parseFloat(formData.amount);
        
        // Add withholding tax fields if checkbox is checked
        if (formData.has_withholding_tax === true) {
          if (formData.withholding_tax_amount) {
            payload.withholding_tax_amount = parseFloat(formData.withholding_tax_amount);
          }
          if (formData.withholding_tax_rate) {
            payload.withholding_tax_rate = parseFloat(formData.withholding_tax_rate);
          }
        }
      }

      await updateFundEvent.mutate(payload);
    }
  };

  // Determine loading state and button text based on mode
  const isLoading = mode === 'create' 
    ? (createFundEvent.loading || createTaxStatement.loading)
    : updateFundEvent.loading;

  const buttonText = mode === 'create' 
    ? (isLoading ? 'Adding Event...' : 'Add Event')
    : (isLoading ? 'Updating Event...' : 'Update Event');

  const dialogTitle = mode === 'create' ? 'Add Cash Flow Event' : 'Edit Event';

  // UI rendering
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>{dialogTitle}</DialogTitle>
      <DialogContent>
        {success && (
          <Box sx={SUCCESS_BOX_STYLES}>
            <Typography variant="body1" fontWeight="medium" color="success.main">
              Event {mode === 'create' ? 'created' : 'updated'} successfully!
            </Typography>
          </Box>
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
          mode={mode}
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

export default UnifiedFundEventForm; 