/**
 * Form Management Hooks - Barrel Export
 * 
 * Central export point for all form management functionality.
 * Includes the useForm hook and form-related types.
 * 
 * @module shared/hooks/forms
 */

// Export form hook
export { useForm, default } from './useForm';

// Export form types
export type {
  FormFieldConfig,
  FormFieldsConfig,
  UseFormOptions,
  UseFormReturn
} from './types';

// Export number input hook
export { useNumberInput } from './useNumberInput';
export type {
  UseNumberInputOptions,
  UseNumberInputReturn
} from './useNumberInput';

// Export validation utilities
export * from './validation';

// Export unified form hook (simple state-based alternative to React Hook Form)
export { useUnifiedForm } from './useUnifiedForm';
export type {
  ValidationRule,
  ValidatorMap,
  UseUnifiedFormConfig,
  UseUnifiedFormReturn
} from './useUnifiedForm';

