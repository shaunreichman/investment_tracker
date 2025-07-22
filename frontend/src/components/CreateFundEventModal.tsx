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
  Alert,
  CircularProgress,
  Paper,
  Typography
} from '@mui/material';
import { TrendingUp, AccountBalance, Add as AddIcon, MonetizationOn } from '@mui/icons-material';

interface CreateFundEventModalProps {
  open: boolean;
  onClose: () => void;
  onEventCreated: () => void;
  fundId: number;
  fundTrackingType: 'nav_based' | 'cost_based';
}

type EventType = 'CAPITAL_CALL' | 'DISTRIBUTION' | 'UNIT_PURCHASE' | 'UNIT_SALE';

const EVENT_TEMPLATES: { label: string; value: EventType | 'RETURN_OF_CAPITAL'; description: string; icon: React.ReactNode; trackingType: 'nav_based' | 'cost_based' | 'both' }[] = [
  { label: 'Capital Call', value: 'CAPITAL_CALL', description: 'Add a capital call (cost-based funds)', icon: <AccountBalance color="primary" />, trackingType: 'cost_based' },
  { label: 'Capital Return', value: 'RETURN_OF_CAPITAL', description: 'Return capital to investors (cost-based funds)', icon: <AccountBalance color="warning" />, trackingType: 'cost_based' },
  { label: 'Distribution', value: 'DISTRIBUTION', description: 'Add a distribution (all funds)', icon: <MonetizationOn color="success" />, trackingType: 'both' },
  { label: 'Unit Purchase', value: 'UNIT_PURCHASE', description: 'Buy units (NAV-based funds)', icon: <AddIcon color="primary" />, trackingType: 'nav_based' },
  { label: 'Unit Sale', value: 'UNIT_SALE', description: 'Sell units (NAV-based funds)', icon: <TrendingUp color="warning" />, trackingType: 'nav_based' },
];

const DISTRIBUTION_TEMPLATES = [
  { label: 'Interest', value: 'INTEREST', description: 'Interest distribution', icon: <MonetizationOn color="primary" /> },
  { label: 'Dividend', value: 'DIVIDEND', description: 'Dividend distribution', icon: <MonetizationOn color="success" /> },
  { label: 'Other', value: 'OTHER', description: 'Other distribution', icon: <MonetizationOn color="warning" /> },
];

interface ValidationErrors {
  event_date?: string;
  amount?: string;
  distribution_type?: string;
  units_purchased?: string;
  units_sold?: string;
  unit_price?: string;
}

const CreateFundEventModal: React.FC<CreateFundEventModalProps> = ({ open, onClose, onEventCreated, fundId, fundTrackingType }) => {
  const [eventType, setEventType] = useState<EventType | 'RETURN_OF_CAPITAL' | ''>('');
  const [distributionType, setDistributionType] = useState<string>('');
  const [formData, setFormData] = useState<any>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

  useEffect(() => {
    if (open) {
      setEventType('');
      setDistributionType('');
      setFormData({ event_date: new Date().toISOString().slice(0, 10) });
      setError(null);
      setSuccess(false);
      setSubmitting(false);
      setValidationErrors({});
    }
  }, [open]);

  // Validate formData.event_date after it is set on modal open
  useEffect(() => {
    if (open && formData.event_date) {
      validateForm();
    }
  }, [open, formData.event_date]);

  // Number formatting helpers
  const formatNumber = (value: string): string => {
    if (!value) return '';
    const num = parseFloat(value.replace(/,/g, ''));
    if (isNaN(num)) return value;
    return num.toLocaleString('en-US');
  };
  const parseNumber = (value: string): string => {
    if (!value) return '';
    return value.replace(/,/g, '');
  };

  const resetForm = () => {
    setEventType('');
    setDistributionType('');
    setFormData({});
    setError(null);
    setSuccess(false);
  };

  const handleClose = () => {
    if (!submitting) {
      resetForm();
      onClose();
    }
  };

  const handleTemplateSelect = (value: EventType | 'RETURN_OF_CAPITAL') => {
    setEventType(value);
    setDistributionType('');
    setError(null);
    // Validate all required fields after template selection
    setTimeout(() => validateForm(), 0);
  };

  const handleDistributionTypeSelect = (distType: string) => {
    setDistributionType(distType);
  };

  const handleBack = () => {
    if (distributionType) {
      setDistributionType('');
      setFormData((prev: any) => ({ ...prev, distribution_type: '' }));
    } else {
      setEventType('');
    }
  };

  // Field-level validation
  const validateField = (field: string, value: string): string | undefined => {
    switch (field) {
      case 'event_date':
        if (!value) return 'Event date is required';
        break;
      case 'amount':
        if (eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION' || eventType === 'RETURN_OF_CAPITAL') {
          const amt = parseFloat(value);
          if (!value) return 'Amount is required';
          if (isNaN(amt) || amt <= 0) return 'Enter a valid positive amount';
        }
        break;
      case 'distribution_type':
        if (eventType === 'DISTRIBUTION' && !distributionType) return 'Distribution type is required';
        break;
      case 'units_purchased':
        if (eventType === 'UNIT_PURCHASE') {
          const units = parseFloat(value);
          if (!value) return 'Units purchased is required';
          if (isNaN(units) || units <= 0) return 'Enter a valid positive number';
        }
        break;
      case 'units_sold':
        if (eventType === 'UNIT_SALE') {
          const units = parseFloat(value);
          if (!value) return 'Units sold is required';
          if (isNaN(units) || units <= 0) return 'Enter a valid positive number';
        }
        break;
      case 'unit_price':
        if ((eventType === 'UNIT_PURCHASE' || eventType === 'UNIT_SALE')) {
          const price = parseFloat(value);
          if (!value) return 'Unit price is required';
          if (isNaN(price) || price <= 0) return 'Enter a valid positive price';
        }
        break;
      default:
        return undefined;
    }
    return undefined;
  };

  // Form-level validation
  const validateForm = (): boolean => {
    const errors: ValidationErrors = {};
    if (!formData.event_date) {
      errors.event_date = 'Event date is required';
    }
    if (eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION' || eventType === 'RETURN_OF_CAPITAL') {
      const amt = parseFloat(formData.amount);
      if (!formData.amount) {
        errors.amount = 'Amount is required';
      } else if (isNaN(amt) || amt <= 0) {
        errors.amount = 'Enter a valid positive amount';
      }
      if (eventType === 'DISTRIBUTION' && !distributionType) {
        errors.distribution_type = 'Distribution type is required';
      }
    }
    if (eventType === 'UNIT_PURCHASE') {
      const units = parseFloat(formData.units_purchased);
      const price = parseFloat(formData.unit_price);
      if (!formData.units_purchased) {
        errors.units_purchased = 'Units purchased is required';
      } else if (isNaN(units) || units <= 0) {
        errors.units_purchased = 'Enter a valid positive number';
      }
      if (!formData.unit_price) {
        errors.unit_price = 'Unit price is required';
      } else if (isNaN(price) || price <= 0) {
        errors.unit_price = 'Enter a valid positive price';
      }
    }
    if (eventType === 'UNIT_SALE') {
      const units = parseFloat(formData.units_sold);
      const price = parseFloat(formData.unit_price);
      if (!formData.units_sold) {
        errors.units_sold = 'Units sold is required';
      } else if (isNaN(units) || units <= 0) {
        errors.units_sold = 'Enter a valid positive number';
      }
      if (!formData.unit_price) {
        errors.unit_price = 'Unit price is required';
      } else if (isNaN(price) || price <= 0) {
        errors.unit_price = 'Enter a valid positive price';
      }
    }
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Only validate form on modal open
  useEffect(() => {
    if (open) {
      validateForm();
    }
  }, [open]);

  // Handle input change
  const handleInputChange = (field: string, value: string) => {
    setFormData((prev: typeof formData) => ({
      ...prev,
      [field]: value
    }));
    // Real-time validation for the field
    const error = validateField(field, value);
    setValidationErrors(prev => ({
      ...prev,
      [field]: error || undefined
    }));
  };

  const handleSubmit = async () => {
    setError(null);
    if (!validateForm()) {
      setError('Please fill in all required fields.');
      return;
    }
    setSubmitting(true);
    try {
      const payload: any = {
        event_type: eventType,
        event_date: formData.event_date,
        description: formData.description,
        reference_number: formData.reference_number,
      };
      if (eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION' || eventType === 'RETURN_OF_CAPITAL') {
        payload.amount = parseFloat(formData.amount);
        if (eventType === 'DISTRIBUTION' && distributionType) {
          payload.distribution_type = distributionType;
        }
      }
      if (eventType === 'UNIT_PURCHASE') {
        payload.units_purchased = parseFloat(formData.units_purchased);
        payload.unit_price = parseFloat(formData.unit_price);
        payload.brokerage_fee = formData.brokerage_fee ? parseFloat(formData.brokerage_fee) : 0.0;
      }
      if (eventType === 'UNIT_SALE') {
        payload.units_sold = parseFloat(formData.units_sold);
        payload.unit_price = parseFloat(formData.unit_price);
        payload.brokerage_fee = formData.brokerage_fee ? parseFloat(formData.brokerage_fee) : 0.0;
      }
      const response = await fetch(`${API_BASE_URL}/api/funds/${fundId}/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Failed to create event');
      }
      setSuccess(true);
      setTimeout(() => {
        resetForm();
        onEventCreated();
        onClose();
      }, 1000);
    } catch (err: any) {
      setError(err.message || 'Failed to create event');
    } finally {
      setSubmitting(false);
    }
  };

  // UI rendering
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add Cash Flow Event</DialogTitle>
      <DialogContent>
        {success && <Alert severity="success">Event created successfully!</Alert>}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {/* Event Type Cards */}
        <Box display="flex" gap={2} mb={2}>
          {EVENT_TEMPLATES.filter(t => t.trackingType === fundTrackingType || t.trackingType === 'both').map(template => {
            const isSelected = eventType === template.value;
            const isDisabled = eventType && eventType !== template.value && !(eventType === 'DISTRIBUTION' && template.value === 'DISTRIBUTION');
            return (
              <Paper
                key={template.value}
                elevation={isSelected ? 6 : 1}
                sx={{
                  p: 2,
                  minWidth: 120,
                  border: isSelected ? '2px solid #1976d2' : '1px solid #ccc',
                  background: isSelected ? '#e3f2fd' : '#fff',
                  opacity: isDisabled ? 0.5 : 1,
                  cursor: isDisabled ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s',
                  position: 'relative',
                }}
                onClick={() => {
                  if (isDisabled) return;
                  if (isSelected) {
                    setEventType('');
                    setDistributionType('');
                  } else {
                    setEventType(template.value as EventType | 'RETURN_OF_CAPITAL');
                    setDistributionType('');
                  }
                }}
              >
                <Box display="flex" flexDirection="column" alignItems="center">
                  {template.icon}
                  <Typography variant="subtitle1" fontWeight={isSelected ? 'bold' : 'normal'}>
                    {template.label}
                  </Typography>
                </Box>
                {/* Expand indicator for Distribution */}
                {template.value === 'DISTRIBUTION' && isSelected && (
                  <Box position="absolute" top={8} right={8}>
                    <AddIcon color="primary" />
                  </Box>
                )}
              </Paper>
            );
          })}
        </Box>

        {/* Distribution Type Options (inline, below cards, always visible when Distribution is selected) */}
        {eventType === 'DISTRIBUTION' && (
          <Box mb={2}>
            <Typography variant="subtitle1" mb={1} color="primary">Select Distribution Type</Typography>
            <Box display="flex" gap={2}>
              {DISTRIBUTION_TEMPLATES.map(dt => {
                const isSelected = distributionType === dt.value;
                return (
                  <Paper
                    key={dt.value}
                    elevation={isSelected ? 6 : 2}
                    sx={{
                      p: 2,
                      minWidth: 120,
                      border: isSelected ? '2px solid #1976d2' : '1px solid #ccc',
                      background: isSelected ? '#e3f2fd' : '#f3f6fa',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                    onClick={() => {
                      if (isSelected) {
                        setDistributionType('');
                      } else {
                        setDistributionType(dt.value);
                      }
                    }}
                  >
                    <Box display="flex" flexDirection="column" alignItems="center">
                      {dt.icon}
                      <Typography variant="subtitle2" fontWeight={isSelected ? 'bold' : 'normal'}>{dt.label}</Typography>
                    </Box>
                  </Paper>
                );
              })}
            </Box>
          </Box>
        )}

        {/* Form appears below all cards (after event type or distribution type selected) */}
        {((eventType && eventType !== 'DISTRIBUTION') || (eventType === 'DISTRIBUTION' && distributionType)) && (
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
                {(eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION' || eventType === 'RETURN_OF_CAPITAL') && (
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
                {eventType === 'DISTRIBUTION' && (
                  <TextField
                    label={<span>Distribution Type <span style={{ color: '#d32f2f' }}>*</span></span>}
                    value={distributionType}
                    disabled
                    fullWidth
                    error={!!validationErrors.distribution_type}
                    helperText={validationErrors.distribution_type}
                  />
                )}
                <TextField
                  label="Description"
                  value={formData.description || ''}
                  onChange={e => handleInputChange('description', e.target.value)}
                  fullWidth
                />
                <TextField
                  label="Reference Number"
                  value={formData.reference_number || ''}
                  onChange={e => handleInputChange('reference_number', e.target.value)}
                  fullWidth
                />
                {eventType === 'UNIT_PURCHASE' && (
                  <>
                    <TextField
                      label={<span>Units Purchased <span style={{ color: '#d32f2f' }}>*</span></span>}
                      type="number"
                      value={formData.units_purchased || ''}
                      onChange={e => handleInputChange('units_purchased', e.target.value)}
                      fullWidth
                      error={!!validationErrors.units_purchased}
                      helperText={validationErrors.units_purchased}
                    />
                    <TextField
                      label={<span>Unit Price <span style={{ color: '#d32f2f' }}>*</span></span>}
                      type="number"
                      value={formData.unit_price || ''}
                      onChange={e => handleInputChange('unit_price', e.target.value)}
                      fullWidth
                      error={!!validationErrors.unit_price}
                      helperText={validationErrors.unit_price}
                    />
                  </>
                )}
                {eventType === 'UNIT_SALE' && (
                  <>
                    <TextField
                      label={<span>Units Sold <span style={{ color: '#d32f2f' }}>*</span></span>}
                      type="number"
                      value={formData.units_sold || ''}
                      onChange={e => handleInputChange('units_sold', e.target.value)}
                      fullWidth
                      error={!!validationErrors.units_sold}
                      helperText={validationErrors.units_sold}
                    />
                    <TextField
                      label={<span>Unit Price <span style={{ color: '#d32f2f' }}>*</span></span>}
                      type="number"
                      value={formData.unit_price || ''}
                      onChange={e => handleInputChange('unit_price', e.target.value)}
                      fullWidth
                      error={!!validationErrors.unit_price}
                      helperText={validationErrors.unit_price}
                    />
                  </>
                )}
              </Box>
            </Box>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default CreateFundEventModal; 