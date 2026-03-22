import type { ValidationRule } from './validationRules';

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

