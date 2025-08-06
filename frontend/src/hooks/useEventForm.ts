import { useState, useEffect, useCallback } from 'react';
import { validateField } from '../utils/validators';
import { calculateTaxPaymentDate } from '../utils/helpers';

export type EventType = 'CAPITAL_CALL' | 'DISTRIBUTION' | 'UNIT_PURCHASE' | 'UNIT_SALE' | 'NAV_UPDATE' | 'TAX_STATEMENT' | 'RETURN_OF_CAPITAL';

export interface ValidationErrors {
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

export interface FormData {
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
  description?: string;
  reference_number?: string;
  tax_payment_date?: string;
  non_resident?: boolean;
}

export interface UseEventFormReturn {
  // Form state
  eventType: EventType | '';
  setEventType: (type: EventType | '') => void;
  distributionType: string;
  setDistributionType: (type: string) => void;
  subDistributionType: string;
  setSubDistributionType: (type: string) => void;
  formData: FormData;
  setFormData: (data: FormData | ((prev: FormData) => FormData)) => void;
  
  // Validation state
  validationErrors: ValidationErrors;
  isFormValid: boolean;
  
  // Withholding tax state
  withholdingAmountType: 'gross' | 'net' | '';
  setWithholdingAmountType: (type: 'gross' | 'net' | '') => void;
  withholdingTaxType: 'amount' | 'rate' | '';
  setWithholdingTaxType: (type: 'amount' | 'rate' | '') => void;
  
  // Hybrid field state
  hybridFieldOverrides: { [key: string]: boolean };
  setHybridFieldOverrides: (overrides: { [key: string]: boolean } | ((prev: { [key: string]: boolean }) => { [key: string]: boolean })) => void;
  
  // Form actions
  handleInputChange: (field: string, value: string) => void;
  handleHybridFieldToggle: (field: string) => void;
  validateForm: () => boolean;
  resetForm: () => void;
  handleBack: () => void;
  
  // Success state
  success: boolean;
  setSuccess: (success: boolean) => void;
}

export const useEventForm = (open: boolean, fundTrackingType: 'nav_based' | 'cost_based'): UseEventFormReturn => {
  // Form state
  const [eventType, setEventType] = useState<EventType | ''>('');
  const [distributionType, setDistributionType] = useState<string>('');
  const [subDistributionType, setSubDistributionType] = useState<string>('');
  const [formData, setFormData] = useState<FormData>({});
  const [success, setSuccess] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [isFormValid, setIsFormValid] = useState(false);

  // Withholding tax state
  const [withholdingAmountType, setWithholdingAmountType] = useState<'gross' | 'net' | ''>('');
  const [withholdingTaxType, setWithholdingTaxType] = useState<'amount' | 'rate' | ''>('');
  
  // Hybrid field state
  const [hybridFieldOverrides, setHybridFieldOverrides] = useState<{[key: string]: boolean}>({});

  // Initialize form when modal opens
  useEffect(() => {
    if (open) {
      setEventType('');
      setDistributionType('');
      setSubDistributionType('');
      setWithholdingAmountType('');
      setWithholdingTaxType('');
      setFormData({ event_date: new Date().toISOString().slice(0, 10) });
      setSuccess(false);
      setValidationErrors({});
      setHybridFieldOverrides({});
    }
  }, [open]);

  // Validate formData.event_date after it is set on modal open
  useEffect(() => {
    if (open && formData.event_date) {
      validateForm();
    }
  }, [open, formData.event_date]);

  // Form-level validation
  const validateForm = useCallback((): boolean => {
    const errors: ValidationErrors = {};
    
    if (!formData.event_date) {
      errors.event_date = 'Event date is required';
    }
    
    if (eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION' || eventType === 'RETURN_OF_CAPITAL') {
      // Skip amount validation for withholding tax scenarios
      if (!(distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX')) {
        const amt = parseFloat(formData.amount || '');
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
      const units = parseFloat(formData.units_purchased || '');
      const price = parseFloat(formData.unit_price || '');
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
      const units = parseFloat(formData.units_sold || '');
      const price = parseFloat(formData.unit_price || '');
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
      const nav = parseFloat(formData.nav_per_share || '');
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
  }, [eventType, distributionType, subDistributionType, withholdingAmountType, withholdingTaxType, formData]);

  // Update form validity when relevant state changes
  useEffect(() => {
    if (open) {
      validateForm();
    }
  }, [open, eventType, distributionType, subDistributionType, withholdingAmountType, withholdingTaxType, formData, validateForm]);

  // Handle input change
  const handleInputChange = useCallback((field: string, value: string) => {
    setFormData((prev: FormData) => {
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
  }, [eventType]);

  // Handle hybrid field toggle changes
  const handleHybridFieldToggle = useCallback((field: string) => {
    setHybridFieldOverrides(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  }, []);

  // Reset form
  const resetForm = useCallback(() => {
    setEventType('');
    setDistributionType('');
    setSubDistributionType('');
    setWithholdingAmountType('');
    setWithholdingTaxType('');
    setFormData({});
    setHybridFieldOverrides({});
    setSuccess(false);
  }, []);

  // Handle back navigation
  const handleBack = useCallback(() => {
    if (distributionType) {
      setDistributionType('');
      setSubDistributionType('');
      setFormData((prev: FormData) => ({ ...prev, distribution_type: '' }));
    } else {
      setEventType('');
    }
  }, [distributionType]);

  return {
    // Form state
    eventType,
    setEventType,
    distributionType,
    setDistributionType,
    subDistributionType,
    setSubDistributionType,
    formData,
    setFormData,
    
    // Validation state
    validationErrors,
    isFormValid,
    
    // Withholding tax state
    withholdingAmountType,
    setWithholdingAmountType,
    withholdingTaxType,
    setWithholdingTaxType,
    
    // Hybrid field state
    hybridFieldOverrides,
    setHybridFieldOverrides,
    
    // Form actions
    handleInputChange,
    handleHybridFieldToggle,
    validateForm,
    resetForm,
    handleBack,
    
    // Success state
    success,
    setSuccess,
  };
}; 