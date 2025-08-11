// Centralized Error Handler Hook
// This hook provides a single source of truth for error state management
// across the entire application, with automatic error categorization and retry mechanisms

import { useState, useCallback, useRef, useEffect } from 'react';
import { ErrorInfo, ErrorType, ErrorSeverity, createErrorInfo, categorizeError, getUserFriendlyMessage } from '../types/errors';

// ============================================================================
// ERROR HANDLER STATE INTERFACE
// ============================================================================

/**
 * State interface for the error handler hook
 */
export interface ErrorHandlerState {
  /** Current error information */
  error: ErrorInfo | null;
  
  /** Whether an error is currently being processed */
  isProcessing: boolean;
  
  /** Retry attempt count */
  retryCount: number;
  
  /** Maximum number of retry attempts */
  maxRetries: number;
  
  /** Whether retry is currently in progress */
  isRetrying: boolean;
  
  /** Error history for debugging */
  errorHistory: ErrorInfo[];
}

// ============================================================================
// ERROR HANDLER OPTIONS
// ============================================================================

/**
 * Configuration options for the error handler hook
 */
export interface ErrorHandlerOptions {
  /** Maximum number of retry attempts (default: 3) */
  maxRetries?: number;
  /** Delay between retry attempts in milliseconds (default: 1000) */
  retryDelay?: number;
  /** Whether to enable exponential backoff (default: true) */
  enableExponentialBackoff?: boolean;
  /** Whether to persist errors across component unmounts (default: false) */
  persistErrors?: boolean;
  /** Whether to log errors to console (default: true) */
  enableLogging?: boolean;
  /** Custom error categorization function */
  categorizeError?: (error: Error | string) => ErrorType;
  /** Custom user-friendly message generator */
  getUserMessage?: (type: ErrorType, message: string, statusCode?: number, context?: string) => string;
}

// ============================================================================
// ERROR HANDLER HOOK
// ============================================================================

/**
 * Centralized error handler hook for consistent error management
 * 
 * @param options Configuration options for error handling
 * @returns Error handler state and methods
 */
export function useErrorHandler(options: ErrorHandlerOptions = {}) {
  // ============================================================================
  // CONFIGURATION
  // ============================================================================
  
  const {
    maxRetries = 3,
    retryDelay = 1000,
    enableExponentialBackoff = true,
    persistErrors = false,
    enableLogging = true,
    categorizeError: customCategorizeError,
    getUserMessage: customGetUserMessage
  } = options;

  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================
  
  const [state, setState] = useState<ErrorHandlerState>({
    error: null,
    isProcessing: false,
    retryCount: 0,
    maxRetries,
    isRetrying: false,
    errorHistory: []
  });

  // Refs for managing retry timeouts and persistence
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastErrorRef = useRef<ErrorInfo | null>(null);

  // ============================================================================
  // ERROR CATEGORIZATION
  // ============================================================================
  
  /**
   * Categorizes an error using custom or default categorization
   */
  const categorizeErrorWithCustom = useCallback((error: Error | string): ErrorType => {
    if (customCategorizeError) {
      return customCategorizeError(error);
    }
    return categorizeError(error);
  }, [customCategorizeError]);

  /**
   * Generates user-friendly error message using custom or default generator
   */
  const getUserMessageWithCustom = useCallback((type: ErrorType, message: string, statusCode?: number, context?: string): string => {
    if (customGetUserMessage) {
      return customGetUserMessage(type, message, statusCode, context);
    }
    return getUserFriendlyMessage(type, message, statusCode, context);
  }, [customGetUserMessage]);

  // ============================================================================
  // ERROR SETTING AND CLEARING
  // ============================================================================
  
  /**
   * Sets an error with automatic categorization and logging
   */
  const setError = useCallback((error: Error | string | ErrorInfo, context?: string) => {
    let errorInfo: ErrorInfo;
    
    if (typeof error === 'string') {
      // String error - create ErrorInfo
      const type = categorizeErrorWithCustom(error);
      errorInfo = createErrorInfo(error, type);
    } else if (error instanceof Error) {
      // Error object - create ErrorInfo
      const type = categorizeErrorWithCustom(error);
      
      // Check if this is an ApiError with status code
      let statusCode: number | undefined;
      if ('status' in error) {
        statusCode = (error as any).status;
      }
      
      errorInfo = createErrorInfo(error, type, statusCode);
    } else {
      // Already ErrorInfo object
      errorInfo = error;
    }

    // Update user message with context if not already set
    if (!errorInfo.userMessage) {
      errorInfo.userMessage = getUserMessageWithCustom(errorInfo.type, errorInfo.message, errorInfo.code, context);
    }

    // Add context to error details for debugging
    if (context && !errorInfo.details) {
      errorInfo.details = { context };
    } else if (context && errorInfo.details) {
      errorInfo.details = { ...errorInfo.details, context };
    }

    // Log error if enabled
    if (enableLogging) {
      console.error(`[ErrorHandler] ${errorInfo.type.toUpperCase()}: ${errorInfo.message}`, {
        error: errorInfo,
        context,
        timestamp: errorInfo.timestamp,
        retryable: errorInfo.retryable
      });
    }

    // Update state
    setState(prev => ({
      ...prev,
      error: errorInfo,
      isProcessing: false,
      isRetrying: false,
      errorHistory: [...prev.errorHistory, errorInfo].slice(-10) // Keep last 10 errors
    }));

    // Store for persistence if enabled
    if (persistErrors) {
      lastErrorRef.current = errorInfo;
    }

    // Clear any existing retry timeout
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
  }, [categorizeErrorWithCustom, getUserMessageWithCustom, enableLogging, persistErrors]);

  /**
   * Clears the current error
   */
  const clearError = useCallback(() => {
    setState(prev => ({
      ...prev,
      error: null,
      retryCount: 0,
      isRetrying: false
    }));

    // Clear retry timeout
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
  }, []);

  // ============================================================================
  // RETRY MECHANISM
  // ============================================================================
  
  /**
   * Calculates retry delay with exponential backoff
   */
  const calculateRetryDelay = useCallback((attempt: number): number => {
    if (!enableExponentialBackoff) {
      return retryDelay;
    }
    
    // Exponential backoff: baseDelay * 2^attempt
    return retryDelay * Math.pow(2, attempt);
  }, [retryDelay, enableExponentialBackoff]);

  /**
   * Retries the last error if it's retryable
   */
  const retry = useCallback(async (retryFunction?: () => Promise<any>) => {
    const currentError = state.error;
    
    if (!currentError || !currentError.retryable || state.retryCount >= maxRetries) {
      return false;
    }

    // Set retrying state
    setState(prev => ({
      ...prev,
      isRetrying: true,
      retryCount: prev.retryCount + 1
    }));

    try {
      // If retry function provided, use it
      if (retryFunction) {
        await retryFunction();
      }
      
      // Clear error on success
      clearError();
      return true;
    } catch (error) {
      // Handle retry failure
      const newError = error instanceof Error ? error : new Error(String(error));
      setError(newError);
      
      // Schedule next retry if attempts remaining
      if (state.retryCount < maxRetries) {
        const delay = calculateRetryDelay(state.retryCount);
        retryTimeoutRef.current = setTimeout(() => {
          retry(retryFunction);
        }, delay);
      }
      
      return false;
    }
  }, [state.error, state.retryCount, maxRetries, clearError, setError, calculateRetryDelay]);

  /**
   * Cancels any pending retry
   */
  const cancelRetry = useCallback(() => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    
    setState(prev => ({
      ...prev,
      isRetrying: false
    }));
  }, []);

  // ============================================================================
  // ERROR PROCESSING
  // ============================================================================
  
  /**
   * Executes an async function with automatic error handling
   */
  const withErrorHandling = useCallback(async <T>(
    asyncFunction: () => Promise<T>, 
    retryable?: boolean,
    context?: string
  ): Promise<T | null> => {
    try {
      if (state.error) {
        clearError();
      }
      
      setState(prev => ({ ...prev, isProcessing: true }));
      
      const result = await asyncFunction();
      
      // Clear any existing error on success
      clearError();
      
      return result;
    } catch (error) {
      // Check if this is an ApiError with status code
      let statusCode: number | undefined;
      if (error && typeof error === 'object' && 'status' in error) {
        statusCode = (error as any).status;
      }
      
      const errorInfo = createErrorInfo(
        error instanceof Error ? error : new Error(String(error)),
        undefined,
        statusCode
      );
      
      // Override retryable flag if specified
      if (retryable !== undefined) {
        errorInfo.retryable = retryable;
      }
      
      setError(errorInfo, context);
      return null;
    } finally {
      setState(prev => ({ ...prev, isProcessing: false }));
    }
  }, [clearError, setError, state.error]);

  // ============================================================================
  // ERROR PERSISTENCE
  // ============================================================================
  
  /**
   * Restores persisted error on component mount
   */
  useEffect(() => {
    if (persistErrors && lastErrorRef.current && !state.error) {
      setState(prev => ({
        ...prev,
        error: lastErrorRef.current
      }));
    }
  }, [persistErrors, state.error]);

  // ============================================================================
  // CLEANUP
  // ============================================================================
  
  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);

  // ============================================================================
  // UTILITY METHODS
  // ============================================================================
  
  /**
   * Checks if current error is of a specific type
   */
  const isErrorType = useCallback((type: ErrorType): boolean => {
    return state.error?.type === type;
  }, [state.error]);

  /**
   * Checks if current error has a specific severity
   */
  const isErrorSeverity = useCallback((severity: ErrorSeverity): boolean => {
    return state.error?.severity === severity;
  }, [state.error]);

  /**
   * Gets error message for display
   */
  const getErrorMessage = useCallback((): string => {
    return state.error?.userMessage || 'An unexpected error occurred';
  }, [state.error]);

  /**
   * Gets technical error details for debugging
   */
  const getErrorDetails = useCallback((): string => {
    return state.error?.message || '';
  }, [state.error]);

  // ============================================================================
  // RETURN VALUE
  // ============================================================================
  
  return {
    // State
    error: state.error,
    isProcessing: state.isProcessing,
    isRetrying: state.isRetrying,
    retryCount: state.retryCount,
    maxRetries: state.maxRetries,
    errorHistory: state.errorHistory,
    
    // Actions
    setError,
    clearError,
    retry,
    cancelRetry,
    withErrorHandling,
    
    // Utilities
    isErrorType,
    isErrorSeverity,
    getErrorMessage,
    getErrorDetails,
    
    // Computed properties
    hasError: !!state.error,
    canRetry: !!(state.error?.retryable && state.retryCount < maxRetries),
    isRetryable: !!state.error?.retryable,
    isCritical: state.error?.severity === ErrorSeverity.CRITICAL
  };
} 