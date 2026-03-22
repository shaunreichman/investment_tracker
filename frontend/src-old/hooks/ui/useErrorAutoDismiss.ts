/**
 * useErrorAutoDismiss Hook
 * 
 * Automatically dismisses an error after a specified delay.
 * Useful for temporary error displays like toasts and banners.
 * 
 * @module hooks/ui
 */

import { useEffect } from 'react';

/**
 * Hook for auto-dismissing errors after a delay
 * 
 * @param shouldAutoDismiss - Whether auto-dismiss is enabled
 * @param dismissDelay - Delay in milliseconds before auto-dismiss
 * @param onDismiss - Callback function to execute when dismissing
 * @param error - Error object to track (resets timer when error changes)
 * 
 * @example
 * ```tsx
 * useErrorAutoDismiss(
 *   autoDismiss,
 *   5000,
 *   () => setError(null),
 *   error
 * );
 * ```
 */
export function useErrorAutoDismiss(
  shouldAutoDismiss: boolean,
  dismissDelay: number,
  onDismiss?: () => void,
  error?: unknown
): void {
  useEffect(() => {
    // Don't set timer if auto-dismiss is disabled or no dismiss callback
    if (!shouldAutoDismiss || !onDismiss || !error) {
      return undefined;
    }
    
    // Set timer to auto-dismiss after delay
    const timer = setTimeout(() => {
      onDismiss();
    }, dismissDelay);
    
    // Cleanup: clear timer on unmount or when dependencies change
    return () => {
      clearTimeout(timer);
    };
  }, [shouldAutoDismiss, dismissDelay, onDismiss, error]);
}

