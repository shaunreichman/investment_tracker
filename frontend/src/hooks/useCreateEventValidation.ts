import { useState, useEffect, useCallback } from 'react';
import { validateField } from '../utils/validators';
import { calculateTaxPaymentDate } from '../utils/helpers';
import { EventType, ValidationErrors, FormData } from './useEventForm';

export interface CreateEventValidationConfig {
  eventType: EventType | '';
  distributionType: string;
  subDistributionType: string;
  withholdingAmountType: 'gross' | 'net' | '';
  withholdingTaxType: 'amount' | 'rate' | '';
  formData: FormData;
}

export interface UseCreateEventValidationReturn {
  validationErrors: ValidationErrors;
  isFormValid: boolean;
  validateForm: () => boolean;
}

/**
 * Create-only validation hook
 */
export const useCreateEventValidation = (config: CreateEventValidationConfig): UseCreateEventValidationReturn => {
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [isFormValid, setIsFormValid] = useState(false);

  // Form-level validation
  const validateForm = useCallback((): boolean => {
    const errors: ValidationErrors = {};
    
    // Common validations
    if (!config.formData.event_date) {
      errors.event_date = 'Event date is required';
    }
    
    if (config.eventType === 'CAPITAL_CALL' || config.eventType === 'DISTRIBUTION' || config.eventType === 'RETURN_OF_CAPITAL') {
      // Skip amount validation for withholding tax scenarios
      if (!(config.distributionType === 'INTEREST' && config.subDistributionType === 'WITHHOLDING_TAX')) {
        const amt = parseFloat(config.formData.amount || '');
        if (!config.formData.amount) {
          errors.amount = 'Amount is required';
        } else if (isNaN(amt) || amt <= 0) {
          errors.amount = 'Enter a valid positive amount';
        }
      }
      
      if (config.eventType === 'DISTRIBUTION' && !config.distributionType) {
        errors.distribution_type = 'Distribution type is required';
      }
    }
    
    if ((config.distributionType === 'DIVIDEND_FRANKED' || config.distributionType === 'DIVIDEND_UNFRANKED') && !config.subDistributionType) {
      errors.sub_distribution_type = 'Sub-distribution type is required';
    }
    
    if (config.distributionType === 'INTEREST' && config.subDistributionType === 'WITHHOLDING_TAX') {
      // For withholding tax, require both amount type and tax type to be selected
      if (!config.withholdingAmountType) {
        errors.gross_amount = 'Select amount type (Gross or Net)';
      }
      if (!config.withholdingTaxType) {
        errors.withholding_tax_rate = 'Select tax type (Amount or Rate)';
      }
      // Also require the actual values to be entered
      const amountValue = config.withholdingAmountType === 'gross' ? config.formData.gross_amount : config.formData.net_amount;
      const taxValue = config.withholdingTaxType === 'rate' ? config.formData.withholding_tax_rate : config.formData.withholding_tax_amount;
      
      if (!amountValue) {
        if (config.withholdingAmountType === 'gross') {
          errors.gross_amount = 'Enter the gross amount';
        } else if (config.withholdingAmountType === 'net') {
          errors.net_amount = 'Enter the net amount';
        }
      }
      if (!taxValue) {
        if (config.withholdingTaxType === 'amount') {
          errors.withholding_tax_amount = 'Enter the tax amount';
        } else if (config.withholdingTaxType === 'rate') {
          errors.withholding_tax_rate = 'Enter the tax rate';
        }
      }
    }
    
    if (config.eventType === 'UNIT_PURCHASE') {
      const units = parseFloat(config.formData.units_purchased || '');
      const price = parseFloat(config.formData.unit_price || '');
      if (!config.formData.units_purchased) {
        errors.units_purchased = 'Units purchased is required';
      } else if (isNaN(units) || units <= 0) {
        errors.units_purchased = 'Enter a valid positive number';
      }
      if (!config.formData.unit_price) {
        errors.unit_price = 'Unit price is required';
      } else if (isNaN(price) || price <= 0) {
        errors.unit_price = 'Enter a valid positive price';
      }
    }
    
    if (config.eventType === 'UNIT_SALE') {
      const units = parseFloat(config.formData.units_sold || '');
      const price = parseFloat(config.formData.unit_price || '');
      if (!config.formData.units_sold) {
        errors.units_sold = 'Units sold is required';
      } else if (isNaN(units) || units <= 0) {
        errors.units_sold = 'Enter a valid positive number';
      }
      if (!config.formData.unit_price) {
        errors.unit_price = 'Unit price is required';
      } else if (isNaN(price) || price <= 0) {
        errors.unit_price = 'Enter a valid positive price';
      }
    }
    
    if (config.eventType === 'NAV_UPDATE') {
      const nav = parseFloat(config.formData.nav_per_share || '');
      if (!config.formData.nav_per_share) {
        errors.nav_per_share = 'NAV per share is required';
      } else if (isNaN(nav) || nav <= 0) {
        errors.nav_per_share = 'Enter a valid positive number';
      }
    }
    
    // Create-specific validations
    if (!config.eventType) {
      errors.event_type = 'Please select an event type';
    }
    
    if (config.eventType === 'DISTRIBUTION' && !config.distributionType) {
      errors.distribution_type = 'Distribution type is required';
    }
    
    if (config.distributionType === 'INTEREST' && !config.subDistributionType) {
      errors.sub_distribution_type = 'Interest type is required';
    }
    
    setValidationErrors(errors);
    const isValid = Object.keys(errors).length === 0;
    setIsFormValid(isValid);
    return isValid;
  }, [
    config.eventType,
    config.distributionType,
    config.subDistributionType,
    config.withholdingAmountType,
    config.withholdingTaxType,
    config.formData.event_date,
    config.formData.amount,
    config.formData.units_purchased,
    config.formData.units_sold,
    config.formData.unit_price,
    config.formData.nav_per_share,
    config.formData.gross_amount,
    config.formData.net_amount,
    config.formData.withholding_tax_amount,
    config.formData.withholding_tax_rate
  ]);

  // Update form validity when relevant state changes
  useEffect(() => {
    validateForm();
  }, [validateForm]);

  return {
    validationErrors,
    isFormValid,
    validateForm,
  };
}; 