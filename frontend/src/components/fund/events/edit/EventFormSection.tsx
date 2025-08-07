import React, { useCallback, useEffect } from 'react';
import {
  TextField,
  Box,
  Typography,
  Button,
  MenuItem
} from '@mui/material';
import { MonetizationOn } from '@mui/icons-material';
import { ExtendedFundEvent } from '../../../../types/api';
import { validateField } from '../../../../utils/validators';
import { formatNumber, parseNumber } from '../../../../utils/helpers';

interface ValidationErrors {
  event_date?: string;
  amount?: string;
  distribution_type?: string;
  units_purchased?: string;
  units_sold?: string;
  unit_price?: string;
  brokerage_fee?: string;
  nav_per_share?: string;
  gross_interest?: string;
  net_interest?: string;
  withholding_amount?: string;
  withholding_rate?: string;
}

interface EventFormSectionProps {
  event: ExtendedFundEvent;
  formData: any;
  setFormData: (data: any) => void;
  validationErrors: ValidationErrors;
  setValidationErrors: (errors: ValidationErrors) => void;
  isFormValid: boolean;
  setIsFormValid: (valid: boolean) => void;
  handleInputChange: (field: string, value: string) => void;
}

const EventFormSection: React.FC<EventFormSectionProps> = ({
  event,
  formData,
  setFormData,
  validationErrors,
  setValidationErrors,
  isFormValid,
  setIsFormValid,
  handleInputChange
}) => {
  const validateForm = useCallback((): boolean => {
    const errors: ValidationErrors = {};
    let isValid = true;

    // Validate required fields based on event type
    if (event?.event_type === 'CAPITAL_CALL' || event?.event_type === 'RETURN_OF_CAPITAL') {
      const amountError = validateField('amount', formData.amount || '');
      if (amountError) {
        errors.amount = amountError;
        isValid = false;
      }
    }

    if (event?.event_type === 'UNIT_PURCHASE') {
      const unitsError = validateField('units_purchased', formData.units_purchased || '');
      const priceError = validateField('unit_price', formData.unit_price || '');
      if (unitsError) {
        errors.units_purchased = unitsError;
        isValid = false;
      }
      if (priceError) {
        errors.unit_price = priceError;
        isValid = false;
      }
    }

    if (event?.event_type === 'UNIT_SALE') {
      const unitsError = validateField('units_sold', formData.units_sold || '');
      const priceError = validateField('unit_price', formData.unit_price || '');
      if (unitsError) {
        errors.units_sold = unitsError;
        isValid = false;
      }
      if (priceError) {
        errors.unit_price = priceError;
        isValid = false;
      }
    }

    if (event?.event_type === 'NAV_UPDATE') {
      const navError = validateField('nav_per_share', formData.nav_per_share || '');
      if (navError) {
        errors.nav_per_share = navError;
        isValid = false;
      }
    }

    if (event?.event_type === 'DISTRIBUTION') {
      if (formData.distribution_type === 'interest') {
        // Validate gross interest for interest distributions
        const grossInterestError = validateField('gross_interest', formData.gross_interest || '');
        if (grossInterestError) {
          errors.gross_interest = grossInterestError;
          isValid = false;
        }
      } else {
        // Validate amount for non-interest distributions
        const amountError = validateField('amount', formData.amount || '');
        if (amountError) {
          errors.amount = amountError;
          isValid = false;
        }
      }
    }

    // Validate date
    const dateError = validateField('event_date', formData.event_date || '');
    if (dateError) {
      errors.event_date = dateError;
      isValid = false;
    }

    setValidationErrors(errors);
    setIsFormValid(isValid);
    return isValid;
  }, [event, formData, setValidationErrors, setIsFormValid]);

  useEffect(() => {
    validateForm();
  }, [validateForm]);

  const DIVIDEND_SUB_TEMPLATES = [
    { label: 'Franked', value: 'dividend_franked', icon: <MonetizationOn color="success" /> },
    { label: 'Unfranked', value: 'dividend_unfranked', icon: <MonetizationOn color="warning" /> },
  ];

  return (
    <Box sx={{ mt: 2 }}>
      {/* Event Date */}
      <TextField
        fullWidth
        label="Event Date"
        type="date"
        value={formData.event_date || ''}
        onChange={(e) => handleInputChange('event_date', e.target.value)}
        error={!!validationErrors.event_date}
        helperText={validationErrors.event_date}
        sx={{ mb: 2 }}
        InputLabelProps={{ shrink: true }}
      />

      {/* Amount (for Capital Call, Return of Capital, Distribution) */}
      {['CAPITAL_CALL', 'RETURN_OF_CAPITAL'].includes(event.event_type) && (
        <TextField
          fullWidth
          label="Amount"
          type="text"
          value={formatNumber(formData.amount || '')}
          onChange={e => handleInputChange('amount', parseNumber(e.target.value))}
          error={!!validationErrors.amount}
          helperText={validationErrors.amount}
          sx={{ mb: 2 }}
        />
      )}

      {/* Units Purchased (for Unit Purchase) */}
      {event.event_type === 'UNIT_PURCHASE' && (
        <TextField
          fullWidth
          label="Units Purchased"
          type="number"
          value={formData.units_purchased || ''}
          onChange={(e) => handleInputChange('units_purchased', e.target.value)}
          error={!!validationErrors.units_purchased}
          helperText={validationErrors.units_purchased}
          sx={{ mb: 2 }}
        />
      )}

      {/* Units Sold (for Unit Sale) */}
      {event.event_type === 'UNIT_SALE' && (
        <TextField
          fullWidth
          label="Units Sold"
          type="number"
          value={formData.units_sold || ''}
          onChange={(e) => handleInputChange('units_sold', e.target.value)}
          error={!!validationErrors.units_sold}
          helperText={validationErrors.units_sold}
          sx={{ mb: 2 }}
        />
      )}

      {/* Unit Price (for Unit Purchase/Sale) */}
      {['UNIT_PURCHASE', 'UNIT_SALE'].includes(event.event_type) && (
        <TextField
          fullWidth
          label="Unit Price"
          type="number"
          value={formData.unit_price || ''}
          onChange={(e) => handleInputChange('unit_price', e.target.value)}
          error={!!validationErrors.unit_price}
          helperText={validationErrors.unit_price}
          sx={{ mb: 2 }}
        />
      )}

      {/* Brokerage Fee (for Unit Purchase/Sale) */}
      {['UNIT_PURCHASE', 'UNIT_SALE'].includes(event.event_type) && (
        <TextField
          fullWidth
          label="Brokerage Fee (Optional)"
          type="number"
          value={formData.brokerage_fee || ''}
          onChange={(e) => handleInputChange('brokerage_fee', e.target.value)}
          error={!!validationErrors.brokerage_fee}
          helperText={validationErrors.brokerage_fee}
          sx={{ mb: 2 }}
        />
      )}

      {/* NAV Per Share (for NAV Update) */}
      {event.event_type === 'NAV_UPDATE' && (
        <TextField
          fullWidth
          label="NAV Per Share"
          type="number"
          value={formData.nav_per_share || ''}
          onChange={(e) => handleInputChange('nav_per_share', e.target.value)}
          error={!!validationErrors.nav_per_share}
          helperText={validationErrors.nav_per_share}
          sx={{ mb: 2 }}
        />
      )}

      {/* Distribution Type (for Distribution) */}
      {event?.event_type === 'DISTRIBUTION' && (formData.distribution_type === 'dividend_franked' || formData.distribution_type === 'dividend_unfranked') ? (
        <Box mb={2}>
          <Typography variant="subtitle1" mb={1} color="primary">Dividend Type</Typography>
          <Box display="flex" gap={2}>
            {DIVIDEND_SUB_TEMPLATES.map(sub => (
              <Button
                key={sub.value}
                variant={formData.distribution_type === sub.value ? 'contained' : 'outlined'}
                color={sub.value === 'dividend_franked' ? 'success' : 'warning'}
                onClick={() => handleInputChange('distribution_type', sub.value)}
                startIcon={sub.icon}
              >
                {sub.label}
              </Button>
            ))}
          </Box>
        </Box>
      ) : (
        <TextField
          fullWidth
          label="Distribution Type"
          select
          value={formData.distribution_type || ''}
          onChange={(e) => handleInputChange('distribution_type', e.target.value)}
          error={!!validationErrors.distribution_type}
          helperText={validationErrors.distribution_type}
          sx={{ mb: 2 }}
        >
          <option value="">Select type</option>
          <option value="interest">Interest</option>
          <option value="dividend">Dividend</option>
          <option value="other">Other</option>
        </TextField>
      )}

      {/* Amount for other distribution types (non-interest) */}
      {event.event_type === 'DISTRIBUTION' && formData.distribution_type !== 'interest' && (
        <TextField
          fullWidth
          label="Amount"
          type="number"
          value={formData.amount || ''}
          onChange={(e) => handleInputChange('amount', e.target.value)}
          error={!!validationErrors.amount}
          helperText={validationErrors.amount}
          sx={{ mb: 2 }}
        />
      )}

      {/* Description */}
      <TextField
        fullWidth
        label="Description (Optional)"
        value={formData.description || ''}
        onChange={(e) => handleInputChange('description', e.target.value)}
        sx={{ mb: 2 }}
      />

      {/* Reference Number */}
      <TextField
        fullWidth
        label="Reference Number (Optional)"
        value={formData.reference_number || ''}
        onChange={(e) => handleInputChange('reference_number', e.target.value)}
        sx={{ mb: 2 }}
      />
    </Box>
  );
};

export default EventFormSection; 