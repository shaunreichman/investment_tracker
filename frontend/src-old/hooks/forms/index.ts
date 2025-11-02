/**
 * Forms Module Barrel Export
 * 
 * Central export point for form management hooks, types, and schemas.
 * 
 * @example
 * ```typescript
 * import { useForm, positivePercentage, emailAddress } from '@/hooks/forms';
 * ```
 */

// Core hook
export { useForm, default as useFormDefault } from './useForm';

// Types
export type {
  FormFieldConfig,
  FormFieldsConfig,
  UseFormOptions,
  UseFormReturn
} from './types';

// Schemas
export * from './schemas';

// Transformers
export * from './transformers';

// Re-export commonly used React Hook Form types for convenience
export type { FieldValues, FieldErrors, UseFormReturn as RHFUseFormReturn } from 'react-hook-form';
export { Controller, useFieldArray, useWatch } from 'react-hook-form';

