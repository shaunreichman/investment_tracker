/**
 * useErrorDetailsToggle Hook
 * 
 * Manages the show/hide state for technical error details.
 * Provides a toggle function with proper memoization.
 * 
 * @module hooks/ui
 */

import { useState, useCallback } from 'react';

/**
 * Return type for useErrorDetailsToggle hook
 */
export interface UseErrorDetailsToggleReturn {
  /** Current visibility state of error details */
  showDetails: boolean;
  
  /** Function to toggle error details visibility */
  toggleDetails: () => void;
  
  /** Function to explicitly set error details visibility */
  setShowDetails: (show: boolean) => void;
}

/**
 * Hook for managing error details visibility state
 * 
 * @param initialShow - Initial visibility state (default: false)
 * @returns Object containing showDetails state and toggle functions
 * 
 * @example
 * ```tsx
 * const { showDetails, toggleDetails } = useErrorDetailsToggle(false);
 * 
 * <Button onClick={toggleDetails}>
 *   {showDetails ? 'Hide' : 'Show'} Details
 * </Button>
 * <Collapse in={showDetails}>
 *   {technicalDetails}
 * </Collapse>
 * ```
 */
export function useErrorDetailsToggle(
  initialShow: boolean = false
): UseErrorDetailsToggleReturn {
  const [showDetails, setShowDetails] = useState<boolean>(initialShow);
  
  const toggleDetails = useCallback(() => {
    setShowDetails(prev => !prev);
  }, []);

  return {
    showDetails,
    toggleDetails,
    setShowDetails
  };
}

