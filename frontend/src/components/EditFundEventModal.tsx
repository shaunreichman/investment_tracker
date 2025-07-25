import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Alert,
  CircularProgress,
  Typography,
  IconButton,
  RadioGroup,
  FormControlLabel,
  Radio
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { MonetizationOn } from '@mui/icons-material';

interface FundEvent {
  id: number;
  event_type: string;
  event_date: string;
  amount: number | null;
  description: string | null;
  reference_number: string | null;
  distribution_type: string | null;
  tax_payment_type: string | null;
  units_purchased: number | null;
  units_sold: number | null;
  unit_price: number | null;
  nav_per_share: number | null;
  brokerage_fee: number | null;
  // Interest distribution fields
  net_interest?: number | null;
  withholding_amount?: number | null;
  withholding_rate?: number | null;
  // Withholding tax context (added by parent component)
  has_withholding_tax?: boolean;
}

interface EditFundEventModalProps {
  open: boolean;
  onClose: () => void;
  onEventUpdated: () => void;
  fundId: number;
  event: FundEvent | null;
}

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

const EditFundEventModal: React.FC<EditFundEventModalProps> = ({ 
  open, 
  onClose, 
  onEventUpdated, 
  fundId, 
  event 
}) => {
  const [formData, setFormData] = useState<any>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [isFormValid, setIsFormValid] = useState(false);
  const [interestType, setInterestType] = useState<'regular' | 'withholding'>('regular');
  const [withholdingAmountType, setWithholdingAmountType] = useState<'gross' | 'net' | ''>('');
  const [withholdingTaxType, setWithholdingTaxType] = useState<'amount' | 'rate' | ''>('');


  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

  useEffect(() => {
    if (open && event) {
      // For interest events, check if there's a related withholding tax event
      let withholdingData = {
        net_interest: event.net_interest?.toString() || '',
        withholding_amount: event.withholding_amount?.toString() || '',
        withholding_rate: event.withholding_rate?.toString() || '',
      };
      
      if (event.event_type === 'DISTRIBUTION' && (event.distribution_type === 'interest' || event.distribution_type === 'INTEREST')) {
        // Check if there's a NON_RESIDENT_INTEREST_WITHHOLDING tax event on the same date
        const hasWithholdingTax = event.has_withholding_tax || false;
        
        if (hasWithholdingTax) {
          // Use the actual withholding data passed from the parent component
          withholdingData = {
            net_interest: event.net_interest?.toString() || '',
            withholding_amount: event.withholding_amount?.toString() || '',
            withholding_rate: event.withholding_rate?.toString() || '',
          };
        }
      }
      
      // Initialize form data from event
      setFormData({
        event_date: event.event_date,
        amount: event.amount?.toString() || '',
        description: event.description || '',
        reference_number: event.reference_number || '',
        distribution_type: event.distribution_type?.toLowerCase() || '',
        units_purchased: event.units_purchased?.toString() || '',
        units_sold: event.units_sold?.toString() || '',
        unit_price: event.unit_price?.toString() || '',
        brokerage_fee: event.brokerage_fee?.toString() || '',
        nav_per_share: event.nav_per_share?.toString() || '',
        // Interest distribution fields
        gross_interest: event.amount?.toString() || '',
        net_interest: withholdingData.net_interest,
        withholding_amount: withholdingData.withholding_amount,
        withholding_rate: withholdingData.withholding_rate,
      });
      
              // Set interest type based on whether withholding fields are populated
        if (event.event_type === 'DISTRIBUTION' && (event.distribution_type === 'interest' || event.distribution_type === 'INTEREST')) {
          if (withholdingData.withholding_amount || withholdingData.withholding_rate || withholdingData.net_interest) {
            setInterestType('withholding');
            
            // Determine amount type based on what's populated, default to gross
            if (formData.gross_interest && formData.gross_interest.trim() !== '') {
              setWithholdingAmountType('gross');
            } else if (formData.net_interest && formData.net_interest.trim() !== '') {
              setWithholdingAmountType('net');
            } else {
              // Default to gross if neither is populated
              setWithholdingAmountType('gross');
            }
            
            // Determine tax type based on what's populated, default to rate
            if (withholdingData.withholding_amount && withholdingData.withholding_amount.trim() !== '') {
              setWithholdingTaxType('amount');
            } else if (withholdingData.withholding_rate && withholdingData.withholding_rate.trim() !== '') {
              setWithholdingTaxType('rate');
            } else {
              // Default to rate if neither is populated
              setWithholdingTaxType('rate');
            }
          } else {
            setInterestType('regular');
            setWithholdingAmountType('');
            setWithholdingTaxType('');
          }
        }
      
      setError(null);
      setSuccess(false);
      setSubmitting(false);
      setValidationErrors({});
    }
  }, [open, event]);

  const formatNumber = (value: string): string => {
    return value.replace(/[^0-9.-]/g, '');
  };



  const validateField = useCallback((field: string, value: string): string | undefined => {
    if (!value.trim()) {
      if (field === 'event_date') return 'Event date is required';
      if (field === 'amount' && ['CAPITAL_CALL', 'RETURN_OF_CAPITAL', 'DISTRIBUTION'].includes(event?.event_type || '')) {
        return 'Amount is required';
      }
      if (field === 'units_purchased' && event?.event_type === 'UNIT_PURCHASE') {
        return 'Units purchased is required';
      }
      if (field === 'units_sold' && event?.event_type === 'UNIT_SALE') {
        return 'Units sold is required';
      }
      if (field === 'unit_price' && ['UNIT_PURCHASE', 'UNIT_SALE'].includes(event?.event_type || '')) {
        return 'Unit price is required';
      }
      if (field === 'nav_per_share' && event?.event_type === 'NAV_UPDATE') {
        return 'NAV per share is required';
      }
      return undefined;
    }

    const numValue = parseFloat(value);
    if (isNaN(numValue)) {
      return 'Must be a valid number';
    }

    if (numValue < 0) {
      return 'Must be positive';
    }

    // Specific validations
    if (field === 'units_sold' && event?.event_type === 'UNIT_SALE') {
      // This will be validated on the backend
    }

    return undefined;
  }, [event]);

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
        
        // Additional validation for interest distribution with withholding
        if (interestType === 'withholding') {
          // Must have exactly one of gross_interest or net_interest
          const hasGrossInterest = formData.gross_interest && formData.gross_interest.trim() !== '';
          const hasNetInterest = formData.net_interest && formData.net_interest.trim() !== '';
          
          if (!hasGrossInterest && !hasNetInterest) {
            errors.gross_interest = 'Must provide either gross or net interest amount.';
            errors.net_interest = 'Must provide either gross or net interest amount.';
            isValid = false;
          } else {
            // Validate the field that is provided
            if (hasGrossInterest) {
              const grossInterestError = validateField('gross_interest', formData.gross_interest);
              if (grossInterestError) {
                errors.gross_interest = grossInterestError;
                isValid = false;
              }
            } else {
              const netInterestError = validateField('net_interest', formData.net_interest);
              if (netInterestError) {
                errors.net_interest = netInterestError;
                isValid = false;
              }
            }
          }
          
          // Must have exactly one of withholding_amount or withholding_rate
          const hasWithholdingAmount = formData.withholding_amount && formData.withholding_amount.trim() !== '';
          const hasWithholdingRate = formData.withholding_rate && formData.withholding_rate.trim() !== '';
          
          if (!hasWithholdingAmount && !hasWithholdingRate) {
            errors.withholding_amount = 'Must provide either tax amount or tax rate.';
            errors.withholding_rate = 'Must provide either tax amount or tax rate.';
            isValid = false;
          } else {
            // Validate the field that is provided
            if (hasWithholdingAmount) {
              const withholdingAmountError = validateField('withholding_amount', formData.withholding_amount);
              if (withholdingAmountError) {
                errors.withholding_amount = withholdingAmountError;
                isValid = false;
              }
            } else {
              const withholdingRateError = validateField('withholding_rate', formData.withholding_rate);
              if (withholdingRateError) {
                errors.withholding_rate = withholdingRateError;
                isValid = false;
              }
            }
          }
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
  }, [event, formData, interestType, validateField]);

  useEffect(() => {
    validateForm();
  }, [validateForm]);



  const handleInputChange = (field: string, value: string) => {
    let processedValue = value;
    
    // Format numbers
    if (['amount', 'units_purchased', 'units_sold', 'unit_price', 'brokerage_fee', 'nav_per_share', 'gross_interest', 'net_interest', 'withholding_amount', 'withholding_rate'].includes(field)) {
      processedValue = formatNumber(value);
    }

    setFormData((prev: any) => {
      const newData = { ...prev, [field]: processedValue };
      
      // For withholding interest events, clear calculated fields when user changes input fields
      if (event?.event_type === 'DISTRIBUTION' && (event?.distribution_type === 'interest' || event?.distribution_type === 'INTEREST') && interestType === 'withholding') {
        // If user changes gross_interest, clear net_interest
        if (field === 'gross_interest') {
          newData.net_interest = '';
        }
        // If user changes net_interest, clear gross_interest
        if (field === 'net_interest') {
          newData.gross_interest = '';
        }
        // If user changes withholding_amount, clear withholding_rate
        if (field === 'withholding_amount') {
          newData.withholding_rate = '';
        }
        // If user changes withholding_rate, clear withholding_amount
        if (field === 'withholding_rate') {
          newData.withholding_amount = '';
        }
      }
      
      return newData;
    });
  };

  const handleSubmit = async () => {
    if (!validateForm() || !event) return;

    setSubmitting(true);
    setError(null);

    try {
      const payload: any = {};

      // Add fields based on event type
      if (event.event_type === 'CAPITAL_CALL' || event.event_type === 'RETURN_OF_CAPITAL') {
        if (formData.amount) payload.amount = parseFloat(formData.amount);
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
        
        if (formData.distribution_type === 'interest') {
          // Handle interest distribution
          if (interestType === 'withholding') {
            // For withholding tax interest, only send fields based on current button selections
            if (withholdingAmountType === 'gross' && formData.gross_interest && formData.gross_interest.trim() !== '') {
              payload.gross_interest = parseFloat(formData.gross_interest);
            } else if (withholdingAmountType === 'net' && formData.net_interest && formData.net_interest.trim() !== '') {
              payload.net_interest = parseFloat(formData.net_interest);
            }
            
            if (withholdingTaxType === 'amount' && formData.withholding_amount && formData.withholding_amount.trim() !== '') {
              payload.withholding_amount = parseFloat(formData.withholding_amount);
            } else if (withholdingTaxType === 'rate' && formData.withholding_rate && formData.withholding_rate.trim() !== '') {
              payload.withholding_rate = parseFloat(formData.withholding_rate);
            }
          } else {
            // For regular interest, send gross_interest as amount
            if (formData.gross_interest) payload.amount = parseFloat(formData.gross_interest);
            // Clear withholding fields for regular interest
            payload.net_interest = null;
            payload.withholding_amount = null;
            payload.withholding_rate = null;
          }
        } else {
          // Handle non-interest distributions
          if (formData.amount) payload.amount = parseFloat(formData.amount);
        }
      }

      const response = await fetch(`${API_BASE_URL}/api/funds/${fundId}/events/${event.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      setSuccess(true);
      setTimeout(() => {
        onEventUpdated();
        onClose();
      }, 1000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  const getEventTypeLabel = (eventType: string): string => {
    switch (eventType) {
      case 'CAPITAL_CALL': return 'Capital Call';
      case 'RETURN_OF_CAPITAL': return 'Capital Return';
      case 'UNIT_PURCHASE': return 'Unit Purchase';
      case 'UNIT_SALE': return 'Unit Sale';
      case 'NAV_UPDATE': return 'NAV Update';
      case 'DISTRIBUTION': return 'Distribution';
      default: return eventType;
    }
  };

  if (!event) return null;

  const DIVIDEND_SUB_TEMPLATES = [
    { label: 'Franked', value: 'dividend_franked', icon: <MonetizationOn color="success" /> },
    { label: 'Unfranked', value: 'dividend_unfranked', icon: <MonetizationOn color="warning" /> },
  ];

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            Edit {getEventTypeLabel(event.event_type)}
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Event updated successfully!
          </Alert>
        )}

        <Box sx={{ mt: 2 }}>
          {/* Interest Type Selection (for Interest Distribution events) */}
          {event?.event_type === 'DISTRIBUTION' && (event?.distribution_type === 'interest' || event?.distribution_type === 'INTEREST') && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Interest Type
              </Typography>
              <RadioGroup
                row
                value={interestType}
                onChange={(e) => setInterestType(e.target.value as 'regular' | 'withholding')}
              >
                <FormControlLabel
                  value="regular"
                  control={<Radio />}
                  label="Regular Interest"
                />
                <FormControlLabel
                  value="withholding"
                  control={<Radio />}
                  label="Withholding Tax Interest"
                />
              </RadioGroup>
            </Box>
          )}

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
              type="number"
              value={formData.amount || ''}
              onChange={(e) => handleInputChange('amount', e.target.value)}
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

          {/* Interest Distribution Fields */}
          {event.event_type === 'DISTRIBUTION' && formData.distribution_type === 'interest' && (
            <>
              {interestType === 'regular' && (
                <TextField
                  fullWidth
                  label="Gross Interest"
                  type="number"
                  value={formData.gross_interest || ''}
                  onChange={(e) => handleInputChange('gross_interest', e.target.value)}
                  error={!!validationErrors.gross_interest}
                  helperText={validationErrors.gross_interest}
                  sx={{ mb: 2 }}
                />
              )}
              
              {interestType === 'withholding' && (
                <>
                  {/* Amount Type Selection */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" mb={1}>
                      Amount Type:
                    </Typography>
                    <Box display="flex" gap={1}>
                      <Button
                        size="small"
                        variant={withholdingAmountType === 'gross' ? 'contained' : 'outlined'}
                        onClick={() => setWithholdingAmountType('gross')}
                      >
                        Gross
                      </Button>
                      <Button
                        size="small"
                        variant={withholdingAmountType === 'net' ? 'contained' : 'outlined'}
                        onClick={() => setWithholdingAmountType('net')}
                      >
                        Net
                      </Button>
                    </Box>
                  </Box>

                  {/* Tax Type Selection */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" mb={1}>
                      Tax Type:
                    </Typography>
                    <Box display="flex" gap={1}>
                      <Button
                        size="small"
                        variant={withholdingTaxType === 'amount' ? 'contained' : 'outlined'}
                        onClick={() => setWithholdingTaxType('amount')}
                      >
                        Tax Amount
                      </Button>
                      <Button
                        size="small"
                        variant={withholdingTaxType === 'rate' ? 'contained' : 'outlined'}
                        onClick={() => setWithholdingTaxType('rate')}
                      >
                        Tax Rate (%)
                      </Button>
                    </Box>
                  </Box>

                  {/* Amount Input Field */}
                  {withholdingAmountType && (
                    <TextField
                      fullWidth
                      label={`${withholdingAmountType === 'gross' ? 'Gross' : 'Net'} Interest`}
                      type="number"
                      value={formData[withholdingAmountType === 'gross' ? 'gross_interest' : 'net_interest'] || ''}
                      onChange={(e) => handleInputChange(withholdingAmountType === 'gross' ? 'gross_interest' : 'net_interest', e.target.value)}
                      error={!!validationErrors[withholdingAmountType === 'gross' ? 'gross_interest' : 'net_interest']}
                      helperText={validationErrors[withholdingAmountType === 'gross' ? 'gross_interest' : 'net_interest']}
                      sx={{ mb: 2 }}
                    />
                  )}

                  {/* Tax Input Field */}
                  {withholdingTaxType && (
                    <TextField
                      fullWidth
                      label={withholdingTaxType === 'amount' ? 'Tax Amount' : 'Tax Rate (%)'}
                      type="number"
                      value={formData[withholdingTaxType === 'amount' ? 'withholding_amount' : 'withholding_rate'] || ''}
                      onChange={(e) => handleInputChange(withholdingTaxType === 'amount' ? 'withholding_amount' : 'withholding_rate', e.target.value)}
                      error={!!validationErrors[withholdingTaxType === 'amount' ? 'withholding_amount' : 'withholding_rate']}
                      helperText={validationErrors[withholdingTaxType === 'amount' ? 'withholding_amount' : 'withholding_rate']}
                      sx={{ mb: 2 }}
                    />
                  )}
                </>
              )}
            </>
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
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={submitting}>
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={!isFormValid || submitting}
        >
          {submitting ? <CircularProgress size={20} /> : 'Update Event'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditFundEventModal; 