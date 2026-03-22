/**
 * Validation rule types for composable validation
 */
export type ValidationRule = (value: string) => string | undefined;

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

