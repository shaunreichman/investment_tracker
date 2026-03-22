/**
 * Form Management Types
 * 
 * Type definitions for React Hook Form + Zod integration.
 * These types support the field configuration pattern where Zod schemas
 * define validation and these types define UI metadata.
 */

import { FieldValues, UseFormProps } from 'react-hook-form';
import { ZodSchema } from 'zod/v3';

/**
 * Field configuration for UI metadata
 * Separate from validation logic (which lives in Zod schemas)
 */
export interface FormFieldConfig {
  /** Display label for the field */
  label: string;
  
  /** Helper text shown when field has no error or not yet touched */
  helpText?: string;
  
  /** Placeholder text for input field */
  placeholder?: string;
  
  /** Optional formatting function for display (e.g., currency, percentage) */
  format?: (value: any) => string;
  
  /** Optional parsing function to convert display value back to typed value */
  parse?: (value: string) => any;
}

/**
 * Configuration map for all fields in a form
 * Keys match the field names in the form schema
 */
export type FormFieldsConfig<T extends FieldValues> = {
  [K in keyof T]?: FormFieldConfig;
};

/**
 * Options for the useForm wrapper hook
 * Extends React Hook Form's options with Zod schema and field configs
 */
export interface UseFormOptions<T extends FieldValues> {
  /** Zod schema for validation (single source of truth) */
  schema: ZodSchema<T>;
  
  /** Optional UI metadata for form fields */
  fieldConfig?: FormFieldsConfig<T>;
  
  /** Form submission handler */
  onSubmit: (data: T) => Promise<void> | void;
  
  /** Default values for form fields */
  defaultValues?: UseFormProps<T>['defaultValues'];
  
  /** Validation mode (default: 'onBlur' for better UX) */
  mode?: UseFormProps<T>['mode'];
  
  /** Additional React Hook Form options */
  formOptions?: Omit<UseFormProps<T>, 'resolver' | 'defaultValues' | 'mode'>;
}

/**
 * Return type from useForm wrapper
 * Extends React Hook Form's return with helper methods
 */
export interface UseFormReturn<T extends FieldValues> {
  /** Get field configuration for a specific field */
  getFieldConfig: (name: keyof T) => FormFieldConfig;
  
  /** Get formatted value for display */
  getFormattedValue: (name: keyof T) => string;
  
  /** Check if a field is required (not optional in schema) */
  isFieldRequired: (name: keyof T) => boolean;
}

