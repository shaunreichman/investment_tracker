/**
 * Centralized validation utilities for consistent form validation across the application
 */

/**
 * Validation rule types for composable validation
 */
export type ValidationRule = (value: string) => string | undefined;

/**
 * Create a validator function from multiple validation rules
 * @param rules - Array of validation rules to apply
 * @returns A validator function that returns the first error found
 */
export const createValidator = (...rules: ValidationRule[]): ValidationRule => {
  return (value: string) => {
    for (const rule of rules) {
      const error = rule(value);
      if (error) return error;
    }
    return undefined;
  };
};

/**
 * Validation rules for common field types
 */
export const validationRules = {
  /**
   * Required field validation
   */
  required: (fieldName: string = 'This field'): ValidationRule => {
    return (value: string) => {
      if (!value || value.trim() === '') {
        return `${fieldName} is required`;
      }
      return undefined;
    };
  },

  /**
   * Positive number validation
   */
  positiveNumber: (fieldName: string = 'Amount'): ValidationRule => {
    return (value: string) => {
      if (!value) return undefined; // Let required rule handle empty values
      
      const num = parseFloat(value);
      if (isNaN(num)) {
        return `${fieldName} must be a valid number`;
      }
      if (num <= 0) {
        return `${fieldName} must be a positive number`;
      }
      return undefined;
    };
  },

  /**
   * Non-negative number validation
   */
  nonNegativeNumber: (fieldName: string = 'Amount'): ValidationRule => {
    return (value: string) => {
      if (!value) return undefined; // Let required rule handle empty values
      
      const num = parseFloat(value);
      if (isNaN(num)) {
        return `${fieldName} must be a valid number`;
      }
      if (num < 0) {
        return `${fieldName} must be a non-negative number`;
      }
      return undefined;
    };
  },

  /**
   * Percentage rate validation (0-100)
   */
  percentageRate: (fieldName: string = 'Rate'): ValidationRule => {
    return (value: string) => {
      if (!value) return undefined; // Let required rule handle empty values
      
      const rate = parseFloat(value);
      if (isNaN(rate)) {
        return `${fieldName} must be a valid number`;
      }
      if (rate < 0 || rate > 100) {
        return `${fieldName} must be between 0 and 100`;
      }
      return undefined;
    };
  },

  /**
   * Date validation
   */
  validDate: (fieldName: string = 'Date'): ValidationRule => {
    return (value: string) => {
      if (!value) return undefined; // Let required rule handle empty values
      
      const date = new Date(value);
      if (isNaN(date.getTime())) {
        return `${fieldName} must be a valid date`;
      }
      return undefined;
    };
  },

  /**
   * Email validation
   */
  email: (fieldName: string = 'Email'): ValidationRule => {
    return (value: string) => {
      if (!value) return undefined; // Let required rule handle empty values
      
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        return `${fieldName} must be a valid email address`;
      }
      return undefined;
    };
  },

  /**
   * URL validation
   */
  url: (fieldName: string = 'URL'): ValidationRule => {
    return (value: string) => {
      if (!value) return undefined; // Let required rule handle empty values
      
      try {
        new URL(value);
        return undefined;
      } catch {
        return `${fieldName} must be a valid URL`;
      }
    };
  },
};

/**
 * Event-specific validation functions
 */
export const eventValidators = {
  /**
   * Validate event date field
   */
  eventDate: createValidator(
    validationRules.required('Event date'),
    validationRules.validDate('Event date')
  ),

  /**
   * Validate amount field for capital events
   */
  amount: createValidator(
    validationRules.required('Amount'),
    validationRules.positiveNumber('Amount')
  ),

  /**
   * Validate distribution type field
   */
  distributionType: createValidator(
    validationRules.required('Distribution type')
  ),

  /**
   * Validate sub-distribution type field
   */
  subDistributionType: createValidator(
    validationRules.required('Sub-distribution type')
  ),

  /**
   * Validate units purchased field
   */
  unitsPurchased: createValidator(
    validationRules.required('Units purchased'),
    validationRules.positiveNumber('Units purchased')
  ),

  /**
   * Validate units sold field
   */
  unitsSold: createValidator(
    validationRules.required('Units sold'),
    validationRules.positiveNumber('Units sold')
  ),

  /**
   * Validate unit price field
   */
  unitPrice: createValidator(
    validationRules.required('Unit price'),
    validationRules.positiveNumber('Unit price')
  ),

  /**
   * Validate NAV per share field
   */
  navPerShare: createValidator(
    validationRules.required('NAV per share'),
    validationRules.positiveNumber('NAV per share')
  ),

  /**
   * Validate brokerage fee field
   */
  brokerageFee: createValidator(
    validationRules.nonNegativeNumber('Brokerage fee')
  ),

  /**
   * Validate gross amount field
   */
  grossAmount: createValidator(
    validationRules.positiveNumber('Gross amount')
  ),

  /**
   * Validate net amount field
   */
  netAmount: createValidator(
    validationRules.positiveNumber('Net amount')
  ),

  /**
   * Validate withholding tax amount field
   */
  withholdingTaxAmount: createValidator(
    validationRules.nonNegativeNumber('Withholding tax amount')
  ),

  /**
   * Validate withholding tax rate field
   */
  withholdingTaxRate: createValidator(
    validationRules.percentageRate('Withholding tax rate')
  ),

  /**
   * Validate financial year field
   */
  financialYear: createValidator(
    validationRules.required('Financial year')
  ),

  /**
   * Validate statement date field
   */
  statementDate: createValidator(
    validationRules.required('Statement date'),
    validationRules.validDate('Statement date')
  ),

  /**
   * Validate debt interest deduction rate field
   */
  debtInterestDeductionRate: createValidator(
    validationRules.required('Debt interest deduction rate'),
    validationRules.percentageRate('Debt interest deduction rate')
  ),

  /**
   * Validate interest income fields
   */
  interestIncome: createValidator(
    validationRules.nonNegativeNumber('Interest income amount')
  ),

  /**
   * Validate tax rate fields
   */
  taxRate: createValidator(
    validationRules.percentageRate('Tax rate')
  ),
};

/**
 * Fund-specific validation functions
 */
export const fundValidators = {
  /**
   * Validate fund name field
   */
  name: createValidator(
    validationRules.required('Fund name'),
    (value: string) => {
      if (value.trim().length < 2) return 'Fund name must be at least 2 characters';
      if (value.trim().length > 255) return 'Fund name must be less than 255 characters';
      if (!/^[a-zA-Z0-9\s\-_()]+$/.test(value.trim())) {
        return 'Fund name can only contain letters, numbers, spaces, hyphens, underscores, and parentheses';
      }
      return undefined;
    }
  ),

  /**
   * Validate fund type field
   */
  fundType: createValidator(
    validationRules.required('Fund type'),
    (value: string) => {
      if (value.trim().length < 2) return 'Fund type must be at least 2 characters';
      if (value.trim().length > 100) return 'Fund type must be less than 100 characters';
      return undefined;
    }
  ),

  /**
   * Validate commitment amount field
   */
  commitmentAmount: createValidator(
    validationRules.positiveNumber('Commitment amount'),
    (value: string) => {
      if (value) {
        const num = parseFloat(value);
        if (num > 999999999) return 'Commitment amount must be less than 1 billion';
      }
      return undefined;
    }
  ),

  /**
   * Validate expected IRR field
   */
  expectedIrr: createValidator(
    validationRules.percentageRate('Expected IRR')
  ),

  /**
   * Validate expected duration field
   */
  expectedDuration: createValidator(
    (value: string) => {
      if (!value) return undefined; // Let required rule handle empty values
      
      const num = parseInt(value);
      if (isNaN(num)) {
        return 'Expected duration must be a valid number';
      }
      if (num < 1 || num > 1200) {
        return 'Expected duration must be between 1 and 1200 months';
      }
      return undefined;
    }
  ),

  /**
   * Validate description field
   */
  description: createValidator(
    (value: string) => {
      if (value && value.trim().length > 1000) {
        return 'Description must be less than 1000 characters';
      }
      return undefined;
    }
  ),
};

/**
 * Generic field validation function for use in components
 * @param field - Field name to validate
 * @param value - Field value to validate
 * @param eventType - Current event type for conditional validation
 * @param distributionType - Current distribution type for conditional validation
 * @returns Validation error message or undefined if valid
 */
export const validateField = (
  field: string, 
  value: string, 
  eventType?: string, 
  distributionType?: string
): string | undefined => {
  switch (field) {
    case 'event_date':
      return eventValidators.eventDate(value);
      
    case 'amount':
      if (eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION' || eventType === 'RETURN_OF_CAPITAL') {
        return eventValidators.amount(value);
      }
      break;
      
    case 'distribution_type':
      if (eventType === 'DISTRIBUTION' && !distributionType) {
        return eventValidators.distributionType(value);
      }
      break;
      
    case 'sub_distribution_type':
      if ((distributionType === 'DIVIDEND_FRANKED' || distributionType === 'DIVIDEND_UNFRANKED') && !value) {
        return eventValidators.subDistributionType(value);
      }
      break;
      
    case 'units_purchased':
      if (eventType === 'UNIT_PURCHASE') {
        return eventValidators.unitsPurchased(value);
      }
      break;
      
    case 'units_sold':
      if (eventType === 'UNIT_SALE') {
        return eventValidators.unitsSold(value);
      }
      break;
      
    case 'unit_price':
      if (eventType === 'UNIT_PURCHASE' || eventType === 'UNIT_SALE' || eventType === 'NAV_UPDATE') {
        return eventValidators.unitPrice(value);
      }
      break;
      
    case 'nav_per_share':
      if (eventType === 'NAV_UPDATE') {
        return eventValidators.navPerShare(value);
      }
      break;
      
    case 'brokerage_fee':
      return eventValidators.brokerageFee(value);
      
    case 'gross_amount':
    case 'net_amount':
    case 'withholding_tax_amount':
      if (distributionType === 'INTEREST' && eventType === 'DISTRIBUTION') {
        return eventValidators.grossAmount(value);
      }
      break;
      
    case 'withholding_tax_rate':
      if (distributionType === 'INTEREST' && eventType === 'DISTRIBUTION') {
        return eventValidators.withholdingTaxRate(value);
      }
      break;
      
    // Tax Statement validation
    case 'financial_year':
      if (eventType === 'TAX_STATEMENT') {
        return eventValidators.financialYear(value);
      }
      break;
      
    case 'statement_date':
      if (eventType === 'TAX_STATEMENT') {
        return eventValidators.statementDate(value);
      }
      break;
      
    case 'eofy_debt_interest_deduction_rate':
      if (eventType === 'TAX_STATEMENT') {
        return eventValidators.debtInterestDeductionRate(value);
      }
      break;
      
    case 'interest_received_in_cash':
    case 'interest_receivable_this_fy':
    case 'interest_receivable_prev_fy':
    case 'interest_non_resident_withholding_tax_from_statement':
    case 'dividend_franked_income_amount':
    case 'dividend_unfranked_income_amount':
    case 'capital_gain_income_amount':
      if (eventType === 'TAX_STATEMENT' && value) {
        return eventValidators.interestIncome(value);
      }
      break;
      
    case 'interest_income_tax_rate':
    case 'dividend_franked_income_tax_rate':
    case 'dividend_unfranked_income_tax_rate':
    case 'capital_gain_income_tax_rate':
      if (eventType === 'TAX_STATEMENT' && value) {
        return eventValidators.taxRate(value);
      }
      break;
      
    // Fund validation
    case 'name':
      return fundValidators.name(value);
      
    case 'fund_type':
      return fundValidators.fundType(value);
      
    case 'commitment_amount':
      return fundValidators.commitmentAmount(value);
      
    case 'expected_irr':
      return fundValidators.expectedIrr(value);
      
    case 'expected_duration_months':
      return fundValidators.expectedDuration(value);
      
    case 'description':
      return fundValidators.description(value);
      
    default:
      return undefined;
  }
}; 