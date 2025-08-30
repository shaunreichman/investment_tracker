import { useCallback, useEffect, useMemo, useState } from 'react';

/**
 * Validation rule function type
 */
export type ValidationRule = (value: string) => string | undefined;

/**
 * Map of field names to validation rules
 */
export type ValidatorMap<T> = Partial<{
  [K in keyof T]: ValidationRule;
}>;

/**
 * Configuration for the unified form hook
 */
export interface UseUnifiedFormConfig<T> {
  /** Initial form values */
  initialValues: T;
  /** Validation rules for each field */
  validators: ValidatorMap<T>;
  /** Function to call when form is submitted */
  onSubmit: (values: T) => Promise<void>;
  /** Optional callback on successful submission */
  onSuccess?: () => void;
  /** Optional callback on submission error */
  onError?: (error: string) => void;
  /** Whether to validate on field change (default: true) */
  validateOnChange?: boolean;
  /** Whether to validate on blur (default: true) */
  validateOnBlur?: boolean;
}

/**
 * Return type for the unified form hook
 */
export interface UseUnifiedFormReturn<T> {
  // Form state
  values: T;
  errors: Partial<Record<keyof T, string | undefined>>;
  touched: Partial<Record<keyof T, boolean>>;
  isDirty: boolean;
  isValid: boolean;
  isSubmitting: boolean;
  
  // Form actions
  setFieldValue: <K extends keyof T>(field: K, value: T[K]) => void;
  setFieldError: <K extends keyof T>(field: K, error: string | undefined) => void;
  validateField: <K extends keyof T>(field: K) => void;
  validateAll: () => boolean;
  handleSubmit: () => Promise<void>;
  reset: () => void;
  clearErrors: () => void;
  markFieldTouched: <K extends keyof T>(field: K, touched?: boolean) => void;
  markAllTouched: () => void;
}

/**
 * Unified form management hook that provides consistent form state,
 * validation, and submission logic across all forms.
 * 
 * @param config - Configuration object for the form
 * @returns Form state and actions
 */
export function useUnifiedForm<T extends Record<string, any>>(
  config: UseUnifiedFormConfig<T>
): UseUnifiedFormReturn<T> {
  const {
    initialValues,
    validators,
    onSubmit,
    onSuccess,
    onError,
    validateOnChange = true,
    validateOnBlur = true
  } = config;

  // Form state
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string | undefined>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Track initial values for dirty state calculation
  const initialValuesRef = useMemo(() => ({ ...initialValues }), []);

  // Calculate if form is dirty (has changes from initial values)
  const isDirty = useMemo(() => {
    const keys = Object.keys(initialValuesRef) as Array<keyof T>;
    return keys.some(key => values[key] !== initialValuesRef[key]);
  }, [values, initialValuesRef]);

  // Calculate if form is valid (no validation errors)
  const isValid = useMemo(() => {
    return Object.values(errors).every(error => !error);
  }, [errors]);

  // Validate a single field
  const validateField = useCallback(<K extends keyof T>(field: K) => {
    const validator = validators[field];
    if (!validator) return;

    const value = values[field];
    const error = validator(String(value ?? ''));
    
    setErrors(prev => ({
      ...prev,
      [field]: error
    }));
  }, [validators, values]);

  // Validate all fields
  const validateAll = useCallback(() => {
    const newErrors: Partial<Record<keyof T, string | undefined>> = {};
    
    Object.keys(validators).forEach(key => {
      const field = key as keyof T;
      const validator = validators[field];
      if (validator) {
        const value = values[field];
        newErrors[field] = validator(String(value ?? ''));
      }
    });

    setErrors(newErrors);
    return Object.values(newErrors).every(error => !error);
  }, [validators, values]);

  // Set field value and optionally validate
  const setFieldValue = useCallback(<K extends keyof T>(field: K, value: T[K]) => {
    setValues(prev => ({
      ...prev,
      [field]: value
    }));

    // Mark field as touched
    setTouched(prev => ({
      ...prev,
      [field]: true
    }));

    // Validate field if validation on change is enabled
    if (validateOnChange) {
      // Use setTimeout to avoid validation during render
      setTimeout(() => validateField(field), 0);
    }
  }, [validateOnChange, validateField]);

  // Set field error manually
  const setFieldError = useCallback(<K extends keyof T>(field: K, error: string | undefined) => {
    setErrors(prev => ({
      ...prev,
      [field]: error
    }));
  }, []);

  // Mark field as touched
  const markFieldTouched = useCallback(<K extends keyof T>(field: K, touched: boolean = true) => {
    setTouched(prev => ({
      ...prev,
      [field]: touched
    }));

    // Validate field if validation on blur is enabled
    if (touched && validateOnBlur) {
      validateField(field);
    }
  }, [validateOnBlur, validateField]);

  // Mark all fields as touched
  const markAllTouched = useCallback(() => {
    const allTouched: Partial<Record<keyof T, boolean>> = {};
    Object.keys(validators).forEach(key => {
      allTouched[key as keyof T] = true;
    });
    setTouched(allTouched);
  }, [validators]);

  // Clear all validation errors
  const clearErrors = useCallback(() => {
    setErrors({});
  }, []);

  // Reset form to initial values
  const reset = useCallback(() => {
    setValues({ ...initialValues });
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  // Handle form submission
  const handleSubmit = useCallback(async () => {
    // Mark all fields as touched to show validation errors
    markAllTouched();

    // Validate all fields
    if (!validateAll()) {
      return;
    }

    setIsSubmitting(true);
    clearErrors();

    try {
      await onSubmit(values);
      onSuccess?.();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      onError?.(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  }, [values, onSubmit, onSuccess, onError, validateAll, markAllTouched, clearErrors]);

  // Reset form when initial values change
  // REMOVED: This was causing infinite loops and is not needed
  // useEffect(() => {
  //   reset();
  // }, [reset]);

  return {
    // Form state
    values,
    errors,
    touched,
    isDirty,
    isValid,
    isSubmitting,
    
    // Form actions
    setFieldValue,
    setFieldError,
    validateField,
    validateAll,
    handleSubmit,
    reset,
    clearErrors,
    markFieldTouched,
    markAllTouched
  };
}
