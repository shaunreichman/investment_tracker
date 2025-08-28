import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useFormLifecycle, FormLifecycleEvent } from './useFormLifecycle';

/**
 * Enhanced configuration for the unified form hook with lifecycle management
 */
export interface UseEnhancedUnifiedFormConfig<T> {
  /** Initial form values */
  initialValues: T;
  /** Validation rules for each field */
  validators: Partial<{
    [K in keyof T]: (value: string) => string | undefined;
  }>;
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
  /** Whether to enable lifecycle management (default: true) */
  enableLifecycle?: boolean;
  /** Whether to enable auto-save */
  enableAutoSave?: boolean;
  /** Custom analytics event handler */
  onAnalyticsEvent?: (event: FormLifecycleEvent, data?: any) => void;
}

/**
 * Enhanced return type for the unified form hook with lifecycle management
 */
export interface UseEnhancedUnifiedFormReturn<T> {
  // Form state
  values: T;
  errors: Partial<Record<keyof T, string | undefined>>;
  touched: Partial<Record<keyof T, boolean>>;
  isDirty: boolean;
  isValid: boolean;
  isSubmitting: boolean;
  
  // Enhanced dirty state tracking
  dirtyFields: Partial<Record<keyof T, boolean>>;
  hasUnsavedChanges: boolean;
  lastModified: Date | null;
  
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
  
  // Lifecycle management
  lifecycle: {
    currentState: string;
    progress: number;
    canSubmit: boolean;
    canCancel: boolean;
    isInProgress: boolean;
    startEditing: () => void;
    startValidation: () => void;
    completeValidation: (isValid: boolean) => void;
    startSubmission: () => void;
    completeSubmission: (success: boolean, error?: string) => void;
    cancelForm: () => void;
    resetForm: () => void;
  };
}

/**
 * Enhanced unified form management hook that provides consistent form state,
 * validation, submission logic, and lifecycle management across all forms.
 * 
 * This hook extends the basic useUnifiedForm with:
 * - Enhanced dirty state tracking with field-level granularity
 * - Form lifecycle state machine management
 * - Progress tracking for complex forms
 * - Analytics and user behavior tracking
 * - Auto-save capabilities
 * 
 * @param config - Configuration object for the form
 * @returns Enhanced form state, actions, and lifecycle management
 */
export function useEnhancedUnifiedForm<T extends Record<string, any>>(
  config: UseEnhancedUnifiedFormConfig<T>
): UseEnhancedUnifiedFormReturn<T> {
  const {
    initialValues,
    validators,
    onSubmit,
    onSuccess,
    onError,
    validateOnChange = true,
    validateOnBlur = true,
    enableLifecycle = true,
    enableAutoSave = false,
    onAnalyticsEvent
  } = config;

  // Form state
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string | undefined>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastModified, setLastModified] = useState<Date | null>(null);

  // Track initial values for dirty state calculation
  const initialValuesRef = useRef<T>({ ...initialValues });

  // Lifecycle management
  const lifecycle = useFormLifecycle({
    enableAnalytics: true,
    showProgress: true,
    enableAutoSave,
    autoSaveInterval: 30000,
    ...(onAnalyticsEvent && { onAnalyticsEvent })
  });

  // Enhanced dirty state tracking with field-level granularity
  const dirtyFields = useMemo(() => {
    const fields: Partial<Record<keyof T, boolean>> = {};
    const keys = Object.keys(initialValuesRef.current) as Array<keyof T>;
    
    keys.forEach(key => {
      const initialValue = initialValuesRef.current[key];
      const currentValue = values[key];
      
      // Deep comparison for objects and arrays
      if (typeof initialValue === 'object' && initialValue !== null) {
        fields[key] = JSON.stringify(initialValue) !== JSON.stringify(currentValue);
      } else {
        fields[key] = initialValue !== currentValue;
      }
    });
    
    return fields;
  }, [values]);

  // Calculate if form is dirty (has changes from initial values)
  const isDirty = useMemo(() => {
    return Object.values(dirtyFields).some(isDirty => isDirty);
  }, [dirtyFields]);

  // Enhanced unsaved changes detection
  const hasUnsavedChanges = useMemo(() => {
    return isDirty && (lifecycle.currentState === 'editing' || lifecycle.currentState === 'validating');
  }, [isDirty, lifecycle.currentState]);

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
    if (enableLifecycle) {
      lifecycle.startValidation();
    }

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
    const isValid = Object.values(newErrors).every(error => !error);
    
    if (enableLifecycle) {
      lifecycle.completeValidation(isValid);
    }
    
    return isValid;
  }, [validators, values, enableLifecycle, lifecycle]);

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

    // Update last modified timestamp
    setLastModified(new Date());

    // Start editing lifecycle if not already editing
    if (enableLifecycle && lifecycle.currentState === 'idle') {
      lifecycle.startEditing();
    }

    // Track field change analytics
    if (enableLifecycle) {
      lifecycle.trackEvent('field_changed', { field: String(field), value });
    }

    // Validate field if validation on change is enabled
    if (validateOnChange) {
      // Use setTimeout to avoid validation during render
      setTimeout(() => validateField(field), 0);
    }
  }, [validateOnChange, validateField, enableLifecycle, lifecycle]);

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
    setLastModified(null);
    
    if (enableLifecycle) {
      lifecycle.resetForm();
    }
  }, [initialValues, enableLifecycle, lifecycle]);

  // Handle form submission
  const handleSubmit = useCallback(async () => {
    // Mark all fields as touched to show validation errors
    markAllTouched();

    // Validate all fields
    if (!validateAll()) {
      return;
    }

    if (enableLifecycle) {
      lifecycle.startSubmission();
    }

    setIsSubmitting(true);
    clearErrors();

    try {
      await onSubmit(values);
      
      if (enableLifecycle) {
        lifecycle.completeSubmission(true);
      }
      
      onSuccess?.();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      
      if (enableLifecycle) {
        lifecycle.completeSubmission(false, errorMessage);
      }
      
      onError?.(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  }, [values, onSubmit, onSuccess, onError, validateAll, markAllTouched, clearErrors, enableLifecycle, lifecycle]);

  // Reset form when initial values change
  useEffect(() => {
    reset();
  }, [reset]);

  // Update initial values ref when initialValues change
  useEffect(() => {
    initialValuesRef.current = { ...initialValues };
  }, [initialValues]);

  return {
    // Form state
    values,
    errors,
    touched,
    isDirty,
    isValid,
    isSubmitting,
    
    // Enhanced dirty state tracking
    dirtyFields,
    hasUnsavedChanges,
    lastModified,
    
    // Form actions
    setFieldValue,
    setFieldError,
    validateField,
    validateAll,
    handleSubmit,
    reset,
    clearErrors,
    markFieldTouched,
    markAllTouched,
    
    // Lifecycle management
    lifecycle: {
      currentState: lifecycle.currentState,
      progress: lifecycle.progress,
      canSubmit: lifecycle.canSubmit,
      canCancel: lifecycle.canCancel,
      isInProgress: lifecycle.isInProgress,
      startEditing: lifecycle.startEditing,
      startValidation: lifecycle.startValidation,
      completeValidation: lifecycle.completeValidation,
      startSubmission: lifecycle.startSubmission,
      completeSubmission: lifecycle.completeSubmission,
      cancelForm: lifecycle.cancelForm,
      resetForm: lifecycle.resetForm
    }
  };
}
