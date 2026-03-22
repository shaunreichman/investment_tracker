/**
 * Shared Form Validation - Barrel Export
 * 
 * Central export point for all form validation functionality.
 * Includes validation rules, validators, and field validation utilities.
 * 
 * @module shared/hooks/forms/validation
 */

// Export validation primitives
export { createValidator } from './createValidator';
export { validationRules } from './validationRules';
export type { ValidationRule } from './validationRules';

// Export domain-specific validators
export { eventValidators } from './eventValidators';
export { fundValidators } from './fundValidators';

// Export field validation utility
export { validateField } from './validateField';

