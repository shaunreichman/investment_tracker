// Form Completion Utility Hook
// This hook provides consistent form completion handling across all forms

import { useState, useCallback } from 'react';

export interface FormCompletionOptions {
  /** Duration to show success message before auto-closing (default: 1500ms) */
  successDuration?: number;
  /** Whether to auto-close the modal after success (default: true) */
  autoClose?: boolean;
  /** Whether to reset form data after success (default: true) */
  resetForm?: boolean;
  /** Custom success message to display */
  successMessage?: string;
}

export interface FormCompletionHandlers {
  /** Call this when form submission succeeds */
  handleSuccess: (data?: any) => void;
  /** Call this when form submission fails */
  handleError: (error: any) => void;
  /** Call this to manually reset the form */
  resetForm: () => void;
  /** Current success state */
  success: boolean;
  /** Current loading state */
  loading: boolean;
}

/**
 * Hook for consistent form completion handling across all forms
 * 
 * @param options Configuration options for form completion behavior
 * @param callbacks Object containing callback functions
 * @returns Form completion handlers and state
 */
export function useFormCompletion(
  options: FormCompletionOptions = {},
  callbacks: {
    onSuccess?: (data?: any) => void;
    onClose?: () => void;
    onReset?: () => void;
    setLoading?: (loading: boolean) => void;
  } = {}
): FormCompletionHandlers {
  const {
    successDuration = 1500,
    autoClose = true,
    resetForm: shouldResetForm = true
  } = options;

  const { onSuccess, onClose, onReset, setLoading } = callbacks;

  const [success, setSuccess] = useState(false);

  const handleSuccess = useCallback((data?: any) => {
    // Show success state
    setSuccess(true);
    
    // Call custom success callback if provided
    if (onSuccess) {
      onSuccess(data);
    }
    
    // Auto-close after delay if enabled
    if (autoClose) {
      setTimeout(() => {
        setSuccess(false);
        if (onClose) {
          onClose();
        }
      }, successDuration);
    }
    
    // Reset form if enabled
    if (shouldResetForm && onReset) {
      setTimeout(() => {
        onReset();
      }, successDuration);
    }
  }, [successDuration, autoClose, shouldResetForm, onSuccess, onClose, onReset]);

  const handleError = useCallback((error: any) => {
    // Hide success state
    setSuccess(false);
    
    // Set loading to false if callback provided
    if (setLoading) {
      setLoading(false);
    }
    
    // Error handling is typically done by the calling component
    // This hook just ensures consistent state management
  }, [setLoading]);

  const resetForm = useCallback(() => {
    setSuccess(false);
    if (onReset) {
      onReset();
    }
  }, [onReset]);

  return {
    handleSuccess,
    handleError,
    resetForm,
    success,
    loading: false // This would be managed by the calling component
  };
}

/**
 * Standard form completion pattern for modals
 * 
 * Usage:
 * ```typescript
 * const { handleSuccess, handleError, success } = useFormCompletion(
 *   { successDuration: 2000, autoClose: true },
 *   { onSuccess: handleDataUpdate, onClose: handleClose, onReset: resetForm }
 * );
 * 
 * // In your submit handler:
 * try {
 *   const result = await submitForm();
 *   handleSuccess(result);
 * } catch (error) {
 *   handleError(error);
 * }
 * ```
 */
