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
  Paper,
  Typography,
  Divider,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import { ErrorDisplay } from './ErrorDisplay';
import { useErrorHandler } from '../hooks/useErrorHandler';
import { TrendingUp, AccountBalance, Add as AddIcon, MonetizationOn, Receipt } from '@mui/icons-material';
import { useFund } from '../hooks/useFunds';
import { useCreateFundEvent, useCreateTaxStatement } from '../hooks/useFunds';
import { validateField } from '../utils/validators';
import { formatNumber, parseNumber, calculateTaxPaymentDate, calculateWithholdingTax } from '../utils/helpers';

interface CreateFundEventModalProps {
  open: boolean;
  onClose: () => void;
  onEventCreated: () => void;
  fundId: number;
  fundTrackingType: 'nav_based' | 'cost_based';
}

type EventType = 'CAPITAL_CALL' | 'DISTRIBUTION' | 'UNIT_PURCHASE' | 'UNIT_SALE' | 'NAV_UPDATE' | 'TAX_STATEMENT';

const EVENT_TEMPLATES: { label: string; value: EventType | 'RETURN_OF_CAPITAL'; description: string; icon: React.ReactNode; trackingType: 'nav_based' | 'cost_based' | 'both' }[] = [
  { label: 'Capital Call', value: 'CAPITAL_CALL', description: 'Add a capital call (cost-based funds)', icon: <AccountBalance color="primary" />, trackingType: 'cost_based' },
  { label: 'Capital Return', value: 'RETURN_OF_CAPITAL', description: 'Return capital to investors (cost-based funds)', icon: <AccountBalance color="warning" />, trackingType: 'cost_based' },
  { label: 'Unit Purchase', value: 'UNIT_PURCHASE', description: 'Buy units (NAV-based funds)', icon: <AddIcon color="primary" />, trackingType: 'nav_based' },
  { label: 'Unit Sale', value: 'UNIT_SALE', description: 'Sell units (NAV-based funds)', icon: <TrendingUp color="warning" />, trackingType: 'nav_based' },
  { label: 'NAV Update', value: 'NAV_UPDATE', description: 'Update NAV per share (NAV-based funds)', icon: <TrendingUp color="info" />, trackingType: 'nav_based' },
  { label: 'Distribution', value: 'DISTRIBUTION', description: 'Add a distribution (all funds)', icon: <MonetizationOn color="success" />, trackingType: 'both' },
  { label: 'Tax Statement', value: 'TAX_STATEMENT', description: 'Add a tax statement (all funds)', icon: <Receipt color="secondary" />, trackingType: 'both' },
];

const DISTRIBUTION_TEMPLATES = [
  { label: 'Interest', value: 'INTEREST', description: 'Interest distribution', icon: <MonetizationOn color="primary" /> },
  { label: 'Dividend', value: 'DIVIDEND', description: 'Dividend distribution', icon: <MonetizationOn color="success" /> },
  { label: 'Other', value: 'OTHER', description: 'Other distribution', icon: <MonetizationOn color="warning" /> },
];

const DIVIDEND_SUB_TEMPLATES = [
  { label: 'Franked', value: 'DIVIDEND_FRANKED', description: 'Franked dividend', icon: <MonetizationOn color="success" /> },
  { label: 'Unfranked', value: 'DIVIDEND_UNFRANKED', description: 'Unfranked dividend', icon: <MonetizationOn color="warning" /> },
];

const INTEREST_SUB_TEMPLATES = [
  { label: 'Regular', value: 'REGULAR', description: 'Regular interest', icon: <MonetizationOn color="primary" /> },
  { label: 'Withholding Tax', value: 'WITHHOLDING_TAX', description: 'Interest with withholding tax', icon: <MonetizationOn color="warning" /> },
];

interface ValidationErrors {
  event_date?: string;
  amount?: string;
  distribution_type?: string;
  sub_distribution_type?: string;
  units_purchased?: string;
  units_sold?: string;
  unit_price?: string;
  brokerage_fee?: string;
  nav_per_share?: string;
  gross_amount?: string;
  net_amount?: string;
  withholding_tax_amount?: string;
  withholding_tax_rate?: string;
  // Tax Statement fields
  financial_year?: string;
  statement_date?: string;
  eofy_debt_interest_deduction_rate?: string;
  interest_received_in_cash?: string;
  interest_receivable_this_fy?: string;
  interest_receivable_prev_fy?: string;
  interest_non_resident_withholding_tax_from_statement?: string;
  interest_income_tax_rate?: string;
  dividend_franked_income_amount?: string;
  dividend_unfranked_income_amount?: string;
  dividend_franked_income_tax_rate?: string;
  dividend_unfranked_income_tax_rate?: string;
  capital_gain_income_amount?: string;
  capital_gain_income_tax_rate?: string;
  accountant?: string;
  notes?: string;
}

const CreateFundEventModal: React.FC<CreateFundEventModalProps> = ({ open, onClose, onEventCreated, fundId, fundTrackingType }) => {
  const [eventType, setEventType] = useState<EventType | 'RETURN_OF_CAPITAL' | ''>('');
  const [distributionType, setDistributionType] = useState<string>('');
  const [subDistributionType, setSubDistributionType] = useState<string>('');
  const [formData, setFormData] = useState<any>({});
  const [success, setSuccess] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [isFormValid, setIsFormValid] = useState(false);

  // Centralized error handler
  const { error, setError, clearError } = useErrorHandler();
  const [withholdingAmountType, setWithholdingAmountType] = useState<'gross' | 'net' | ''>('');
  const [withholdingTaxType, setWithholdingTaxType] = useState<'amount' | 'rate' | ''>('');
  const [fundEntity, setFundEntity] = useState<any>(null);
  const [financialYears, setFinancialYears] = useState<string[]>([]);
  const [hybridFieldOverrides, setHybridFieldOverrides] = useState<{[key: string]: boolean}>({});

  // Centralized API hooks
  const { data: fundData, loading: fundLoading, error: fundError } = useFund(fundId);
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

  useEffect(() => {
    if (open) {
      setEventType('');
      setDistributionType('');
      setSubDistributionType('');
      setWithholdingAmountType('');
      setWithholdingTaxType('');
      setFormData({ event_date: new Date().toISOString().slice(0, 10) });
      clearError();
      setSuccess(false);
      setValidationErrors({});
    }
  }, [open]);

  // Validate formData.event_date after it is set on modal open
  useEffect(() => {
    if (open && formData.event_date) {
      validateForm();
    }
  }, [open, formData.event_date]);

  // Process fund data when it loads
  useEffect(() => {
    if (fundData && open) {
      setFundEntity(fundData.entity);
      
      // Generate financial years from fund creation to current year
      const currentYear = new Date().getFullYear();
      const fundStartYear = fundData.created_at ? new Date(fundData.created_at).getFullYear() : currentYear - 5;
      const years = [];
      for (let year = fundStartYear; year <= currentYear; year++) {
        years.push(`${year}-${(year + 1).toString().slice(-2)}`);
      }
      setFinancialYears(years);
    }
  }, [fundData, open]);

  const resetForm = () => {
    setEventType('');
    setDistributionType('');
    setSubDistributionType('');
    setWithholdingAmountType('');
    setWithholdingTaxType('');
    setFormData({});
    setHybridFieldOverrides({});
    clearError();
    setSuccess(false);
  };

  const handleClose = () => {
    if (!createFundEvent.loading && !createTaxStatement.loading) {
      resetForm();
      onClose();
    }
  };

  const handleTemplateSelect = (value: EventType | 'RETURN_OF_CAPITAL') => {
    setEventType(value);
    setDistributionType('');
    setSubDistributionType('');
    clearError();
    // Validate all required fields after template selection
    setTimeout(() => validateForm(), 0);
  };

  const handleDistributionTypeSelect = (distType: string) => {
    setDistributionType(distType);
  };

  const handleSubDistributionTypeSelect = (subDistType: string) => {
    setSubDistributionType(subDistType);
  };

  const handleBack = () => {
    if (distributionType) {
      setDistributionType('');
      setSubDistributionType('');
      setFormData((prev: any) => ({ ...prev, distribution_type: '' }));
    } else {
      setEventType('');
    }
  };

  // Form-level validation
  const validateForm = (): boolean => {
    const errors: ValidationErrors = {};
    if (!formData.event_date) {
      errors.event_date = 'Event date is required';
    }
    if (eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION' || eventType === 'RETURN_OF_CAPITAL') {
      // Skip amount validation for withholding tax scenarios
      if (!(distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX')) {
        const amt = parseFloat(formData.amount);
        if (!formData.amount) {
          errors.amount = 'Amount is required';
        } else if (isNaN(amt) || amt <= 0) {
          errors.amount = 'Enter a valid positive amount';
        }
      }
      if (eventType === 'DISTRIBUTION' && !distributionType) {
        errors.distribution_type = 'Distribution type is required';
      }
    }
          if ((distributionType === 'DIVIDEND_FRANKED' || distributionType === 'DIVIDEND_UNFRANKED') && !subDistributionType) {
        errors.sub_distribution_type = 'Sub-distribution type is required';
      }
      if (distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX') {
        // For withholding tax, require both amount type and tax type to be selected
        if (!withholdingAmountType) {
          errors.gross_amount = 'Select amount type (Gross or Net)';
        }
        if (!withholdingTaxType) {
          errors.withholding_tax_rate = 'Select tax type (Amount or Rate)';
        }
        // Also require the actual values to be entered
        const amountValue = withholdingAmountType === 'gross' ? formData.gross_amount : formData.net_amount;
        const taxValue = withholdingTaxType === 'rate' ? formData.withholding_tax_rate : formData.withholding_tax_amount;
        
        if (!amountValue) {
          if (withholdingAmountType === 'gross') {
            errors.gross_amount = 'Enter the gross amount';
          } else if (withholdingAmountType === 'net') {
            errors.net_amount = 'Enter the net amount';
          }
        }
        if (!taxValue) {
          if (withholdingTaxType === 'amount') {
            errors.withholding_tax_amount = 'Enter the tax amount';
          } else if (withholdingTaxType === 'rate') {
            errors.withholding_tax_rate = 'Enter the tax rate';
          }
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
    if (eventType === 'NAV_UPDATE') {
      const nav = parseFloat(formData.nav_per_share);
      if (!formData.nav_per_share) {
        errors.nav_per_share = 'NAV per share is required';
      } else if (isNaN(nav) || nav <= 0) {
        errors.nav_per_share = 'Enter a valid positive number';
      }
    }
    setValidationErrors(errors);
    const isValid = Object.keys(errors).length === 0;
    setIsFormValid(isValid);
    return isValid;
  };

  // Update form validity when relevant state changes
  useEffect(() => {
    if (open) {
      validateForm();
    }
  }, [open, eventType, distributionType, subDistributionType, withholdingAmountType, withholdingTaxType, formData]);

  // Handle input change
  const handleInputChange = (field: string, value: string) => {
    setFormData((prev: typeof formData) => {
      const newFormData = { ...prev, [field]: value };
      
      // Auto-calculate tax payment date when financial year changes
      if (field === 'financial_year' && eventType === 'TAX_STATEMENT') {
        newFormData.tax_payment_date = calculateTaxPaymentDate(value);
      }
      
      return newFormData;
    });
    
    // Real-time validation for the field
    const error = validateField(field, value);
    setValidationErrors(prev => ({
      ...prev,
      [field]: error || undefined
    }));
  };

  // Handle hybrid field toggle changes
  const handleHybridFieldToggle = (field: string) => {
    setHybridFieldOverrides(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const handleSubmit = async () => {
    clearError();
    if (!validateForm()) {
      setError('Please fill in all required fields.');
      return;
    }
    
    const payload: any = {
        event_type: eventType,
        event_date: formData.event_date,
        description: formData.description,
        reference_number: formData.reference_number,
      };
      if (eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION' || eventType === 'RETURN_OF_CAPITAL') {
        // Handle withholding tax distributions differently
        if (distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX') {
          // For withholding tax, send only the relevant fields
          if (withholdingAmountType === 'gross') {
            payload.gross_interest = parseFloat(formData.gross_amount);
          } else if (withholdingAmountType === 'net') {
            payload.net_interest = parseFloat(formData.net_amount);
          }
          if (withholdingTaxType === 'amount') {
            payload.withholding_amount = parseFloat(formData.withholding_tax_amount);
          } else if (withholdingTaxType === 'rate') {
            payload.withholding_rate = parseFloat(formData.withholding_tax_rate);
          }
          payload.distribution_type = distributionType;
          payload.sub_distribution_type = subDistributionType;
        } else {
          // For regular distributions, send the amount field
          payload.amount = parseFloat(formData.amount);
          if (eventType === 'DISTRIBUTION' && distributionType) {
            payload.distribution_type = distributionType;
          }
        }
      }
      if (distributionType === 'DIVIDEND') {
        if (!subDistributionType) {
          validationErrors.sub_distribution_type = 'Please select Franked or Unfranked';
        } else {
          payload.distribution_type = subDistributionType;
        }
      } else {
        payload.distribution_type = distributionType;
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
      if (eventType === 'NAV_UPDATE') {
        payload.nav_per_share = parseFloat(formData.nav_per_share);
      }
      
      // Handle Tax Statement submission
      if (eventType === 'TAX_STATEMENT') {
        const taxStatementPayload = {
          entity_id: fundEntity?.id,
          financial_year: formData.financial_year,
          statement_date: formData.statement_date,
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
                    setSubDistributionType('');
                  } else {
                    setEventType(template.value as EventType | 'RETURN_OF_CAPITAL');
                    setDistributionType('');
                    setSubDistributionType('');
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
                        setSubDistributionType('');
                      } else {
                        setDistributionType(dt.value);
                        setSubDistributionType('');
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

                 {/* Sub-Distribution Type Options (inline, below Distribution Type, only visible when Dividend is selected) */}
         {distributionType === 'DIVIDEND' && (
          <Box mb={2}>
            <Typography variant="subtitle1" mb={1} color="primary">Select Dividend Type</Typography>
            <Box display="flex" gap={2}>
              {DIVIDEND_SUB_TEMPLATES.map(sub => (
                <Button
                  key={sub.value}
                  variant={subDistributionType === sub.value ? 'contained' : 'outlined'}
                  color={sub.value === 'DIVIDEND_FRANKED' ? 'success' : 'warning'}
                  onClick={() => setSubDistributionType(sub.value)}
                  startIcon={sub.icon}
                >
                  {sub.label}
                </Button>
              ))}
            </Box>
          </Box>
        )}

                 {/* Interest Sub-Distribution Type Options (inline, below Distribution Type, only visible when Interest is selected) */}
         {distributionType === 'INTEREST' && (
          <Box mb={2}>
            <Typography variant="subtitle1" mb={1} color="primary">Select Interest Sub-Distribution Type</Typography>
            <Box display="flex" gap={2}>
              {INTEREST_SUB_TEMPLATES.map(subDt => {
                const isSelected = subDistributionType === subDt.value;
                return (
                  <Paper
                    key={subDt.value}
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
                        setSubDistributionType('');
                      } else {
                        setSubDistributionType(subDt.value);
                      }
                    }}
                  >
                    <Box display="flex" flexDirection="column" alignItems="center">
                      {subDt.icon}
                      <Typography variant="subtitle2" fontWeight={isSelected ? 'bold' : 'normal'}>{subDt.label}</Typography>
                    </Box>
                  </Paper>
                );
              })}
            </Box>
          </Box>
        )}

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
                                 {distributionType === 'DIVIDEND' && (
                  <TextField
                    label={<span>Sub-Distribution Type <span style={{ color: '#d32f2f' }}>*</span></span>}
                    value={subDistributionType}
                    disabled
                    fullWidth
                    error={!!validationErrors.sub_distribution_type}
                    helperText={validationErrors.sub_distribution_type}
                  />
                )}
                                 {distributionType === 'INTEREST' && (
                  <TextField
                    label={<span>Sub-Distribution Type <span style={{ color: '#d32f2f' }}>*</span></span>}
                    value={subDistributionType}
                    disabled
                    fullWidth
                    error={!!validationErrors.sub_distribution_type}
                    helperText={validationErrors.sub_distribution_type}
                  />
                )}
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
                    <TextField
                      label="Brokerage Fee (Optional)"
                      type="number"
                      value={formData.brokerage_fee || ''}
                      onChange={e => handleInputChange('brokerage_fee', e.target.value)}
                      fullWidth
                      error={!!validationErrors.brokerage_fee}
                      helperText={validationErrors.brokerage_fee}
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
                    <TextField
                      label="Brokerage Fee (Optional)"
                      type="number"
                      value={formData.brokerage_fee || ''}
                      onChange={e => handleInputChange('brokerage_fee', e.target.value)}
                      fullWidth
                      error={!!validationErrors.brokerage_fee}
                      helperText={validationErrors.brokerage_fee}
                    />
                  </>
                )}
                {eventType === 'NAV_UPDATE' && (
                  <>
                    <TextField
                      label={<span>NAV Per Share <span style={{ color: '#d32f2f' }}>*</span></span>}
                      type="number"
                      value={formData.nav_per_share || ''}
                      onChange={e => handleInputChange('nav_per_share', e.target.value)}
                      fullWidth
                      error={!!validationErrors.nav_per_share}
                      helperText={validationErrors.nav_per_share}
                    />
                  </>
                )}
                
                {/* Withholding Tax Selection Buttons - Inline within form grid */}
                {distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX' && (
                  <>
                    {/* Amount Type Selection */}
                    <Box>
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
                    <Box>
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

                    {/* Withholding Tax Input Fields */}
                    {withholdingAmountType && (
                      <TextField
                        label={`${withholdingAmountType === 'gross' ? 'Gross' : 'Net'} Amount`}
                        type="text"
                        value={formatNumber(formData[withholdingAmountType === 'gross' ? 'gross_amount' : 'net_amount'] || '')}
                        onChange={e => handleInputChange(withholdingAmountType === 'gross' ? 'gross_amount' : 'net_amount', parseNumber(e.target.value))}
                        fullWidth
                        error={!!validationErrors[withholdingAmountType === 'gross' ? 'gross_amount' : 'net_amount']}
                        helperText={validationErrors[withholdingAmountType === 'gross' ? 'gross_amount' : 'net_amount']}
                      />
                    )}

                    {withholdingTaxType && (
                      <TextField
                        label={withholdingTaxType === 'amount' ? 'Tax Amount' : 'Tax Rate (%)'}
                        type="text"
                        value={formatNumber(formData[withholdingTaxType === 'amount' ? 'withholding_tax_amount' : 'withholding_tax_rate'] || '')}
                        onChange={e => handleInputChange(withholdingTaxType === 'amount' ? 'withholding_tax_amount' : 'withholding_tax_rate', parseNumber(e.target.value))}
                        fullWidth
                        error={!!validationErrors[withholdingTaxType === 'amount' ? 'withholding_tax_amount' : 'withholding_tax_rate']}
                        helperText={validationErrors[withholdingTaxType === 'amount' ? 'withholding_tax_amount' : 'withholding_tax_rate']}
                      />
                    )}
                  </>
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