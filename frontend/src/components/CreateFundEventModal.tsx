import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Box,
  CircularProgress,
  Typography,
  Divider,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import { ErrorDisplay } from './ErrorDisplay';
import { useErrorHandler } from '../hooks/useErrorHandler';
import { useFund } from '../hooks/useFunds';
import { useCreateFundEvent, useCreateTaxStatement } from '../hooks/useFunds';
import { validateField } from '../utils/validators';
import { formatNumber, parseNumber, calculateTaxPaymentDate } from '../utils/helpers';
import EventTypeSelector from './modals/EventTypeSelector';
import DistributionForm from './modals/DistributionForm';
import UnitTransactionForm from './modals/UnitTransactionForm';
import NavUpdateForm from './modals/NavUpdateForm';
import { useEventForm, type EventType, type ValidationErrors } from '../hooks/useEventForm';

interface CreateFundEventModalProps {
  open: boolean;
  onClose: () => void;
  onEventCreated: () => void;
  fundId: number;
  fundTrackingType: 'nav_based' | 'cost_based';
}

const CreateFundEventModal: React.FC<CreateFundEventModalProps> = ({ open, onClose, onEventCreated, fundId, fundTrackingType }) => {
  // Use the extracted form state management hook
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
    withholdingAmountType,
    setWithholdingAmountType,
    withholdingTaxType,
    setWithholdingTaxType,
    hybridFieldOverrides,
    setHybridFieldOverrides,
    handleInputChange,
    handleHybridFieldToggle,
    validateForm,
    resetForm,
    handleBack,
  } = useEventForm(open, fundTrackingType);

  // Centralized error handler
  const { error, setError, clearError } = useErrorHandler();
  const [fundEntity, setFundEntity] = useState<any>(null);
  const [financialYears, setFinancialYears] = useState<string[]>([]);

  // Centralized API hooks
  const { data: fundData } = useFund(fundId);
  const createFundEvent = useCreateFundEvent(fundId);
  const createTaxStatement = useCreateTaxStatement(fundId);

  // Handle errors and success from hooks
  useEffect(() => {
    if (createFundEvent.error) {
      setError(createFundEvent.error);
    }
  }, [createFundEvent.error]);

  useEffect(() => {
    if (createTaxStatement.error) {
      setError(createTaxStatement.error);
    }
  }, [createTaxStatement.error]);

  useEffect(() => {
    if (createFundEvent.data) {
      setSuccess(true);
      setTimeout(() => {
        resetForm();
        onEventCreated();
        onClose();
      }, 1000);
    }
  }, [createFundEvent.data, onEventCreated, onClose]);

  useEffect(() => {
    if (createTaxStatement.data) {
      setSuccess(true);
      setTimeout(() => {
        resetForm();
        onEventCreated();
        onClose();
      }, 1000);
    }
  }, [createTaxStatement.data, onEventCreated, onClose]);

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

    // Prepare payload based on event type
    const payload: any = {
      event_type: eventType,
      event_date: formData.event_date || '',
      description: formData.description || '',
      reference_number: formData.reference_number || '',
    };

    // Handle different event types
    if (eventType === 'CAPITAL_CALL' || eventType === 'RETURN_OF_CAPITAL') {
      payload.amount = parseFloat(formData.amount || '0');
    } else if (eventType === 'DISTRIBUTION') {
      payload.amount = parseFloat(formData.amount || '0');
      if (distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX') {
        payload.gross_amount = parseFloat(formData.gross_amount || '0');
        payload.net_amount = parseFloat(formData.net_amount || '0');
        payload.withholding_tax_amount = parseFloat(formData.withholding_tax_amount || '0');
        payload.withholding_tax_rate = parseFloat(formData.withholding_tax_rate || '0');
      } else {
        payload.distribution_type = distributionType;
      }
    } else if (eventType === 'UNIT_PURCHASE') {
      payload.units_purchased = parseFloat(formData.units_purchased || '0');
      payload.unit_price = parseFloat(formData.unit_price || '0');
      payload.brokerage_fee = formData.brokerage_fee ? parseFloat(formData.brokerage_fee) : 0.0;
    } else if (eventType === 'UNIT_SALE') {
      payload.units_sold = parseFloat(formData.units_sold || '0');
      payload.unit_price = parseFloat(formData.unit_price || '0');
      payload.brokerage_fee = formData.brokerage_fee ? parseFloat(formData.brokerage_fee) : 0.0;
    } else if (eventType === 'NAV_UPDATE') {
      payload.nav_per_share = parseFloat(formData.nav_per_share || '0');
    }
    
    // Handle Tax Statement submission
    if (eventType === 'TAX_STATEMENT') {
      const taxStatementPayload = {
        entity_id: fundEntity?.id,
        financial_year: formData.financial_year || '',
        statement_date: formData.statement_date || '',
        eofy_debt_interest_deduction_rate: parseFloat(formData.eofy_debt_interest_deduction_rate || '0'),
        interest_received_in_cash: parseFloat(formData.interest_received_in_cash || '0'),
        interest_receivable_this_fy: parseFloat(formData.interest_receivable_this_fy || '0'),
        interest_receivable_prev_fy: parseFloat(formData.interest_receivable_prev_fy || '0'),
        interest_non_resident_withholding_tax_from_statement: parseFloat(formData.interest_non_resident_withholding_tax_from_statement || '0'),
        interest_income_tax_rate: parseFloat(formData.interest_income_tax_rate || '0'),
        dividend_franked_income_amount: parseFloat(formData.dividend_franked_income_amount || '0'),
        dividend_unfranked_income_amount: parseFloat(formData.dividend_unfranked_income_amount || '0'),
        dividend_franked_income_tax_rate: parseFloat(formData.dividend_franked_income_tax_rate || '0'),
        dividend_unfranked_income_tax_rate: parseFloat(formData.dividend_unfranked_income_tax_rate || '0'),
        capital_gain_income_amount: parseFloat(formData.capital_gain_income_amount || '0'),
        capital_gain_income_tax_rate: parseFloat(formData.capital_gain_income_tax_rate || '0'),
        accountant: formData.accountant || '',
        notes: formData.notes || '',
        non_resident: formData.non_resident || false
      };
      
      console.log('DEBUG: Sending tax statement payload:', taxStatementPayload);
      
      await createTaxStatement.mutate(taxStatementPayload);
      return;
    }
    
    // Debug: Log the payload being sent
    console.log('DEBUG: Sending payload:', payload);
    
    await createFundEvent.mutate(payload);
  };

  // UI rendering
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Add Cash Flow Event</DialogTitle>
      <DialogContent>
        {success && (
          <Box sx={{ mb: 2, p: 2, bgcolor: 'success.light', borderRadius: 1, display: 'flex', alignItems: 'center' }}>
            <Typography variant="body1" fontWeight="medium" color="success.main">
              Event created successfully!
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
          onEventTypeSelect={setEventType}
          onDistributionTypeSelect={setDistributionType}
          onSubDistributionTypeSelect={setSubDistributionType}
          onBack={handleBack}
        />

        {/* Form appears below all cards (after event type or distribution type selected) */}
        {((eventType && eventType !== 'DISTRIBUTION' && eventType !== 'TAX_STATEMENT') || (eventType === 'DISTRIBUTION' && distributionType && (distributionType === 'OTHER' || (distributionType === 'DIVIDEND' && subDistributionType) || (distributionType === 'INTEREST' && subDistributionType))) || eventType === 'TAX_STATEMENT') && (
          <Box mt={2}>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Fields marked with <span style={{ color: '#d32f2f' }}>*</span> are required.
            </Typography>
            <Box component="form" noValidate autoComplete="off">
              <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
                <TextField
                  label={<span>Event Date <span style={{ color: '#d32f2f' }}>*</span></span>}
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
                    label={<span>{eventType === 'RETURN_OF_CAPITAL' ? 'Return Amount' : 'Amount'} <span style={{ color: '#d32f2f' }}>*</span></span>}
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
                  withholdingAmountType={withholdingAmountType}
                  withholdingTaxType={withholdingTaxType}
                  hybridFieldOverrides={hybridFieldOverrides}
                  onInputChange={handleInputChange}
                  onWithholdingAmountTypeChange={setWithholdingAmountType}
                  onWithholdingTaxTypeChange={setWithholdingTaxType}
                  onHybridFieldToggle={handleHybridFieldToggle}
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
                

                
                {/* Tax Statement Form Fields */}
                {eventType === 'TAX_STATEMENT' && (
                  <>
                    {/* Basic Information */}
                    <Typography variant="h6" color="primary" sx={{ mt: 2, mb: 1 }}>
                      Basic Information
                    </Typography>
                    <TextField
                      label="Entity"
                      value={fundEntity?.name || 'Loading...'}
                      disabled
                      fullWidth
                    />
                    <TextField
                      select
                      label={<span>Financial Year <span style={{ color: '#d32f2f' }}>*</span></span>}
                      value={formData.financial_year || ''}
                      onChange={e => handleInputChange('financial_year', e.target.value)}
                      fullWidth
                      error={!!validationErrors.financial_year}
                      helperText={validationErrors.financial_year}
                    >
                      {financialYears.map((year) => (
                        <MenuItem key={year} value={year}>
                          {year}
                        </MenuItem>
                      ))}
                    </TextField>
                    <TextField
                      label={<span>Statement Date <span style={{ color: '#d32f2f' }}>*</span></span>}
                      type="date"
                      value={formData.statement_date || ''}
                      onChange={e => handleInputChange('statement_date', e.target.value)}
                      fullWidth
                      error={!!validationErrors.statement_date}
                      helperText={validationErrors.statement_date}
                      InputLabelProps={{ shrink: true }}
                    />
                    <TextField
                      label="Tax Payment Date"
                      value={formData.tax_payment_date || ''}
                      disabled
                      fullWidth
                      helperText="Auto-calculated as last day of financial year"
                    />
                    <TextField
                      label={<span>End of Financial Year Debt Interest Deduction Rate (%) <span style={{ color: '#d32f2f' }}>*</span></span>}
                      type="number"
                      value={formData.eofy_debt_interest_deduction_rate || ''}
                      onChange={e => handleInputChange('eofy_debt_interest_deduction_rate', e.target.value)}
                      fullWidth
                      error={!!validationErrors.eofy_debt_interest_deduction_rate}
                      helperText={validationErrors.eofy_debt_interest_deduction_rate}
                    />
                    
                    <Divider sx={{ my: 2 }} />
                    
                    {/* Interest Income */}
                    <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
                      Interest Income
                    </Typography>
                    

                    <TextField
                      label="Interest Received in Cash"
                      type="number"
                      value={formData.interest_received_in_cash || ''}
                      onChange={e => handleInputChange('interest_received_in_cash', e.target.value)}
                      fullWidth
                      error={!!validationErrors.interest_received_in_cash}
                      helperText={validationErrors.interest_received_in_cash}
                    />
                    <TextField
                      label="Interest Receivable This FY"
                      type="number"
                      value={formData.interest_receivable_this_fy || ''}
                      onChange={e => handleInputChange('interest_receivable_this_fy', e.target.value)}
                      fullWidth
                      error={!!validationErrors.interest_receivable_this_fy}
                      helperText={validationErrors.interest_receivable_this_fy}
                    />
                    <TextField
                      label="Interest Receivable Previous FY"
                      type="number"
                      value={formData.interest_receivable_prev_fy || ''}
                      onChange={e => handleInputChange('interest_receivable_prev_fy', e.target.value)}
                      fullWidth
                      error={!!validationErrors.interest_receivable_prev_fy}
                      helperText={validationErrors.interest_receivable_prev_fy}
                    />
                    <TextField
                      label="Interest Non-Resident Withholding Tax from Statement"
                      type="number"
                      value={formData.interest_non_resident_withholding_tax_from_statement || ''}
                      onChange={e => handleInputChange('interest_non_resident_withholding_tax_from_statement', e.target.value)}
                      fullWidth
                      error={!!validationErrors.interest_non_resident_withholding_tax_from_statement}
                      helperText={validationErrors.interest_non_resident_withholding_tax_from_statement}
                    />
                    <TextField
                      label="Interest Income Tax Rate (%)"
                      type="number"
                      value={formData.interest_income_tax_rate || ''}
                      onChange={e => handleInputChange('interest_income_tax_rate', e.target.value)}
                      fullWidth
                      error={!!validationErrors.interest_income_tax_rate}
                      helperText={validationErrors.interest_income_tax_rate}
                    />
                    
                    <Divider sx={{ my: 2 }} />
                    
                    {/* Dividend Income */}
                    <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
                      Dividend Income
                    </Typography>
                    <TextField
                      label="Dividend Franked Income Amount"
                      type="number"
                      value={formData.dividend_franked_income_amount || ''}
                      onChange={e => handleInputChange('dividend_franked_income_amount', e.target.value)}
                      fullWidth
                      error={!!validationErrors.dividend_franked_income_amount}
                      helperText={validationErrors.dividend_franked_income_amount}
                      InputProps={{
                        endAdornment: (
                          <Button
                            size="small"
                            variant={hybridFieldOverrides.dividend_franked_income_amount ? 'contained' : 'outlined'}
                            onClick={() => handleHybridFieldToggle('dividend_franked_income_amount')}
                            sx={{ minWidth: 'auto', px: 1 }}
                          >
                            {hybridFieldOverrides.dividend_franked_income_amount ? 'Manual' : 'Auto'}
                          </Button>
                        )
                      }}
                    />
                    <TextField
                      label="Dividend Unfranked Income Amount"
                      type="number"
                      value={formData.dividend_unfranked_income_amount || ''}
                      onChange={e => handleInputChange('dividend_unfranked_income_amount', e.target.value)}
                      fullWidth
                      error={!!validationErrors.dividend_unfranked_income_amount}
                      helperText={validationErrors.dividend_unfranked_income_amount}
                      InputProps={{
                        endAdornment: (
                          <Button
                            size="small"
                            variant={hybridFieldOverrides.dividend_unfranked_income_amount ? 'contained' : 'outlined'}
                            onClick={() => handleHybridFieldToggle('dividend_unfranked_income_amount')}
                            sx={{ minWidth: 'auto', px: 1 }}
                          >
                            {hybridFieldOverrides.dividend_unfranked_income_amount ? 'Manual' : 'Auto'}
                          </Button>
                        )
                      }}
                    />
                    <TextField
                      label="Dividend Franked Income Tax Rate (%)"
                      type="number"
                      value={formData.dividend_franked_income_tax_rate || ''}
                      onChange={e => handleInputChange('dividend_franked_income_tax_rate', e.target.value)}
                      fullWidth
                      error={!!validationErrors.dividend_franked_income_tax_rate}
                      helperText={validationErrors.dividend_franked_income_tax_rate}
                    />
                    <TextField
                      label="Dividend Unfranked Income Tax Rate (%)"
                      type="number"
                      value={formData.dividend_unfranked_income_tax_rate || ''}
                      onChange={e => handleInputChange('dividend_unfranked_income_tax_rate', e.target.value)}
                      fullWidth
                      error={!!validationErrors.dividend_unfranked_income_tax_rate}
                      helperText={validationErrors.dividend_unfranked_income_tax_rate}
                    />
                    
                    <Divider sx={{ my: 2 }} />
                    
                    {/* Capital Gains */}
                    <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
                      Capital Gains
                    </Typography>
                    <TextField
                      label="Capital Gain Income Amount"
                      type="number"
                      value={formData.capital_gain_income_amount || ''}
                      onChange={e => handleInputChange('capital_gain_income_amount', e.target.value)}
                      fullWidth
                      error={!!validationErrors.capital_gain_income_amount}
                      helperText={validationErrors.capital_gain_income_amount}
                      InputProps={{
                        endAdornment: (
                          <Button
                            size="small"
                            variant={hybridFieldOverrides.capital_gain_income_amount ? 'contained' : 'outlined'}
                            onClick={() => handleHybridFieldToggle('capital_gain_income_amount')}
                            sx={{ minWidth: 'auto', px: 1 }}
                          >
                            {hybridFieldOverrides.capital_gain_income_amount ? 'Manual' : 'Auto'}
                          </Button>
                        )
                      }}
                    />
                    <TextField
                      label="Capital Gain Income Tax Rate (%)"
                      type="number"
                      value={formData.capital_gain_income_tax_rate || ''}
                      onChange={e => handleInputChange('capital_gain_income_tax_rate', e.target.value)}
                      fullWidth
                      error={!!validationErrors.capital_gain_income_tax_rate}
                      helperText={validationErrors.capital_gain_income_tax_rate}
                    />
                    
                    <Divider sx={{ my: 2 }} />
                    
                    {/* Additional Information */}
                    <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
                      Additional Information
                    </Typography>
                    <TextField
                      label="Accountant"
                      value={formData.accountant || ''}
                      onChange={e => handleInputChange('accountant', e.target.value)}
                      fullWidth
                      error={!!validationErrors.accountant}
                      helperText={validationErrors.accountant}
                    />
                    <TextField
                      label="Notes"
                      multiline
                      rows={3}
                      value={formData.notes || ''}
                      onChange={e => handleInputChange('notes', e.target.value)}
                      fullWidth
                      error={!!validationErrors.notes}
                      helperText={validationErrors.notes}
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={formData.non_resident || false}
                          onChange={e => handleInputChange('non_resident', e.target.checked.toString())}
                        />
                      }
                      label="Non-Resident"
                    />
                  </>
                )}
              </Box>
            </Box>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={createFundEvent.loading || createTaxStatement.loading}>
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={createFundEvent.loading || createTaxStatement.loading || !isFormValid}
          startIcon={(createFundEvent.loading || createTaxStatement.loading) ? <CircularProgress size={20} /> : null}
        >
          {(createFundEvent.loading || createTaxStatement.loading) ? 'Adding Event...' : 'Add Event'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateFundEventModal; 