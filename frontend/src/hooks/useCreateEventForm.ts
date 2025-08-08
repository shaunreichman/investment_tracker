import { useState, useEffect, useCallback } from 'react';
import { validateField } from '../utils/validators';
import { calculateTaxPaymentDate } from '../utils/helpers';
import { EventType, ValidationErrors, FormData, UseEventFormReturn } from './useEventForm';

export interface UseCreateEventFormProps {
  open: boolean;
  fundTrackingType: 'nav_based' | 'cost_based';
}

/**
 * Create-only form state management hook
 */
export const useCreateEventForm = ({
  open,
  fundTrackingType
}: UseCreateEventFormProps): UseEventFormReturn => {
  // Form state
  const [eventType, setEventType] = useState<EventType | ''>('');
  const [distributionType, setDistributionType] = useState<string>('');
  const [subDistributionType, setSubDistributionType] = useState<string>('');
  const [formData, setFormData] = useState<FormData>({});
  const [success, setSuccess] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [isFormValid, setIsFormValid] = useState(false);

  // Hybrid field state
  const [hybridFieldOverrides, setHybridFieldOverrides] = useState<{[key: string]: boolean}>({});

  // Initialize form when modal opens
  useEffect(() => {
    if (open) {
      setEventType('');
      setDistributionType('');
      setSubDistributionType('');
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
      const amt = parseFloat(formData.amount || '');
      if (!formData.amount) {
        errors.amount = 'Amount is required';
      } else if (isNaN(amt) || amt <= 0) {
        errors.amount = 'Enter a valid positive amount';
      }
      
      if (eventType === 'DISTRIBUTION' && !distributionType) {
        errors.distribution_type = 'Distribution type is required';
      }
    }
    
    if ((distributionType === 'DIVIDEND_FRANKED' || distributionType === 'DIVIDEND_UNFRANKED') && !subDistributionType) {
      errors.sub_distribution_type = 'Sub-distribution type is required';
    }
    
    // Simple validation for withholding tax fields when checkbox is checked
    if (distributionType === 'INTEREST' && formData.has_withholding_tax === true) {
      if (formData.withholding_tax_amount && parseFloat(formData.withholding_tax_amount) < 0) {
        errors.withholding_tax_amount = 'Tax amount must be positive';
      }
      if (formData.withholding_tax_rate && (parseFloat(formData.withholding_tax_rate) < 0 || parseFloat(formData.withholding_tax_rate) > 100)) {
        errors.withholding_tax_rate = 'Tax rate must be between 0 and 100';
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
    
    // Create-specific validations
    if (!eventType) {
      errors.event_type = 'Please select an event type';
    }
    
    if (eventType === 'DISTRIBUTION' && !distributionType) {
      errors.distribution_type = 'Distribution type is required';
    }
    
    if (distributionType === 'INTEREST' && !subDistributionType) {
      errors.sub_distribution_type = 'Interest type is required';
    }
    
    setValidationErrors(errors);
    const isValid = Object.keys(errors).length === 0;
    setIsFormValid(isValid);
    return isValid;
  }, [eventType, distributionType, subDistributionType, formData]);

  // Update form validity when relevant state changes
  useEffect(() => {
    if (open) {
      validateForm();
    }
  }, [open, eventType, distributionType, subDistributionType, formData, validateForm]);

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