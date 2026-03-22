import { createValidator } from './createValidator';
import { validationRules } from './validationRules';

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

