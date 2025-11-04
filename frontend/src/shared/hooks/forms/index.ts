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

