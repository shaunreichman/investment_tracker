/**
 * Form Management Hook
 * 
 * Wrapper around React Hook Form that integrates with Zod validation
 * and provides application-specific patterns for consistent form handling.
 * 
 * @example
 * ```typescript
 * const form = useForm<FundFormData>({
 *   schema: fundSchema,
 *   fieldConfig: fundFieldConfig,
 *   defaultValues: { name: '', managementFee: 0 },
 *   onSubmit: async (data) => {
 *     await createFund(data);
 *   }
 * });
 * ```
 */

import { useForm as useRHF, FieldValues } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { UseFormOptions, UseFormReturn, FormFieldConfig } from './types';

/**
 * Enterprise-grade form hook wrapping React Hook Form with Zod validation
 * 
 * Provides consistent form handling across the application with:
 * - Schema-based validation (Zod)
 * - Type-safe form data (TypeScript inference from schema)
 * - Configurable validation timing (onBlur default)
 * - Field configuration helpers
 * - Integration with existing mutation hooks
 * 
 * @param options - Form configuration including schema, field config, and submit handler
 * @returns Extended React Hook Form instance with helper methods
 */
export function useForm<T extends FieldValues>({
  schema,
  fieldConfig = {},
  onSubmit,
  defaultValues,
  mode = 'onBlur', // Default to onBlur for better UX
  formOptions
}: UseFormOptions<T>) {
  // Initialize React Hook Form with Zod resolver
  // Note: Type assertion needed for Zod schema compatibility with RHF
  const formConfig: any = {
    resolver: zodResolver(schema as any),
    mode,
    ...(defaultValues !== undefined && { defaultValues }),
    ...formOptions
  };
  
  const form = useRHF<T>(formConfig);

  /**
   * Get field configuration for a specific field
   * Returns empty config if field config not provided
   */
  const getFieldConfig = (name: keyof T): FormFieldConfig => {
    return fieldConfig[name] || {
      label: String(name)
    };
  };

  /**
   * Get formatted value for display
   * Uses field config's format function if available, otherwise returns raw value
   */
  const getFormattedValue = (name: keyof T): string => {
    const config = getFieldConfig(name);
    const value = form.getValues(name as any);
    
    if (config.format) {
      return config.format(value);
    }
    
    return value != null ? String(value) : '';
  };

  /**
   * Check if a field is required
   * Note: This is a helper - actual validation is in the Zod schema
   * Returns false by default (fields are optional unless schema says otherwise)
   */
  const isFieldRequired = (name: keyof T): boolean => {
    // This is a best-effort check. The Zod schema is the source of truth.
    // For accurate required checks, the schema should be introspected,
    // but for simplicity we default to false and rely on validation errors.
    return false;
  };

  /**
   * Wrapped submit handler
   * Integrates form validation with submission logic
   */
  const handleSubmit = form.handleSubmit(async (data: T) => {
    try {
      await onSubmit(data);
    } catch (error) {
      // Error handling can be enhanced here
      // (e.g., set form-level errors from API responses)
      console.error('Form submission error:', error);
      throw error;
    }
  });

  // Return extended form instance
  return {
    ...form,
    handleSubmit,
    getFieldConfig,
    getFormattedValue,
    isFieldRequired
  };
}

export default useForm;

