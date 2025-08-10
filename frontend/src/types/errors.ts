// Error Types and Interfaces
// This file provides the foundation for standardized error handling across the application

// ============================================================================
// ERROR CLASSIFICATION SYSTEM
// ============================================================================

/**
 * Error types for categorizing different kinds of errors
 * This helps provide appropriate user messages and handling strategies
 */
export enum ErrorType {
  NETWORK = 'network',           // Connection issues, timeouts, fetch failures
  VALIDATION = 'validation',     // Form validation errors, user input issues
  AUTHENTICATION = 'authentication', // Login failures, expired sessions
  AUTHORIZATION = 'authorization',   // Permission issues, access denied
  NOT_FOUND = 'not_found',      // Resource not found (404)
  SERVER = 'server',            // Backend errors (500+)
  UNKNOWN = 'unknown'           // Unknown or unclassified errors
}

/**
 * Error severity levels for determining UI treatment and user impact
 */
export enum ErrorSeverity {
  LOW = 'low',        // Info messages, warnings, non-critical issues
  MEDIUM = 'medium',  // User action required, but not blocking
  HIGH = 'high',      // Critical errors, user cannot proceed
  CRITICAL = 'critical' // System failures, requires immediate attention
}

// ============================================================================
// ERROR INFORMATION INTERFACE
// ============================================================================

/**
 * Comprehensive error information for standardized error handling
 */
export interface ErrorInfo {
  /** The original error message */
  message: string;
  
  /** Categorized error type */
  type: ErrorType;
  
  /** Error severity level */
  severity: ErrorSeverity;
  
  /** HTTP status code (if applicable) */
  code?: number;
  
  /** Additional error details for debugging */
  details?: any;
  
  /** When the error occurred */
  timestamp: Date;
  
  /** Whether this error can be retried */
  retryable: boolean;
  
  /** User-friendly error message */
  userMessage: string;
  
  /** Original error stack trace (for debugging) */
  stack?: string | undefined;
  
  /** Error ID for tracking and analytics */
  id?: string;
}

// ============================================================================
// ERROR DISPLAY OPTIONS
// ============================================================================

/**
 * Options for configuring error display behavior
 */
export interface ErrorDisplayOptions {
  /** Whether to show technical error details */
  showDetails?: boolean;
  
  /** Whether retry functionality should be available */
  canRetry?: boolean;
  
  /** Whether the error can be dismissed */
  canDismiss?: boolean;
  
  /** Whether to auto-dismiss the error */
  autoDismiss?: boolean;
  
  /** Delay before auto-dismissing (in milliseconds) */
  dismissDelay?: number;
  
  /** Custom error display variant */
  variant?: 'inline' | 'modal' | 'toast' | 'banner';
}

// ============================================================================
// ERROR CATEGORIZATION FUNCTIONS
// ============================================================================

/**
 * Categorizes an error based on its message and properties
 */
export function categorizeError(error: Error | string): ErrorType {
  const message = error instanceof Error ? error.message : error;
  const lowerMessage = message.toLowerCase();
  
  // Network errors
  if (lowerMessage.includes('network') || 
      lowerMessage.includes('fetch') || 
      lowerMessage.includes('connection') ||
      lowerMessage.includes('timeout') ||
      lowerMessage.includes('failed to fetch')) {
    return ErrorType.NETWORK;
  }
  
  // Validation errors
  if (lowerMessage.includes('validation') || 
      lowerMessage.includes('required') ||
      lowerMessage.includes('invalid') ||
      lowerMessage.includes('format')) {
    return ErrorType.VALIDATION;
  }
  
  // Authentication errors
  if (lowerMessage.includes('unauthorized') || 
      lowerMessage.includes('401') ||
      lowerMessage.includes('authentication') ||
      lowerMessage.includes('login')) {
    return ErrorType.AUTHENTICATION;
  }
  
  // Authorization errors
  if (lowerMessage.includes('forbidden') || 
      lowerMessage.includes('403') ||
      lowerMessage.includes('permission') ||
      lowerMessage.includes('access denied')) {
    return ErrorType.AUTHORIZATION;
  }
  
  // Not found errors
  if (lowerMessage.includes('not found') || 
      lowerMessage.includes('404') ||
      lowerMessage.includes('does not exist')) {
    return ErrorType.NOT_FOUND;
  }
  
  // Server errors
  if (lowerMessage.includes('server') || 
      lowerMessage.includes('500') ||
      lowerMessage.includes('internal error')) {
    return ErrorType.SERVER;
  }
  
  return ErrorType.UNKNOWN;
}

/**
 * Determines error severity based on error type
 */
export function getErrorSeverity(type: ErrorType): ErrorSeverity {
  switch (type) {
    case ErrorType.NETWORK:
      return ErrorSeverity.MEDIUM; // Usually transient, can be retried
    case ErrorType.VALIDATION:
      return ErrorSeverity.LOW; // User can fix, not critical
    case ErrorType.AUTHENTICATION:
      return ErrorSeverity.HIGH; // Blocks user access
    case ErrorType.AUTHORIZATION:
      return ErrorSeverity.HIGH; // Blocks user action
    case ErrorType.NOT_FOUND:
      return ErrorSeverity.MEDIUM; // Resource missing, but not critical
    case ErrorType.SERVER:
      return ErrorSeverity.CRITICAL; // System failure
    case ErrorType.UNKNOWN:
      return ErrorSeverity.MEDIUM; // Default to medium for unknown
  }
}

/**
 * Determines if an error can be retried
 */
export function isRetryableError(type: ErrorType): boolean {
  return type === ErrorType.NETWORK || type === ErrorType.SERVER;
}

/**
 * Generates user-friendly error messages based on error type
 */
export function getUserFriendlyMessage(type: ErrorType, originalMessage: string): string {
  switch (type) {
    case ErrorType.NETWORK:
      return 'Connection failed. Please check your internet connection and try again.';
    case ErrorType.VALIDATION:
      return 'Please check your input and try again.';
    case ErrorType.AUTHENTICATION:
      return 'Please log in again to continue.';
    case ErrorType.AUTHORIZATION:
      return 'You don\'t have permission to perform this action.';
    case ErrorType.NOT_FOUND:
      return 'The requested resource was not found.';
    case ErrorType.SERVER:
      return 'A server error occurred. Please try again later.';
    case ErrorType.UNKNOWN:
      return 'An unexpected error occurred. Please try again.';
  }
}

/**
 * Creates a comprehensive ErrorInfo object from an error
 */
export function createErrorInfo(error: Error | string, type?: ErrorType): ErrorInfo {
  const errorType = type || categorizeError(error);
  const severity = getErrorSeverity(errorType);
  const retryable = isRetryableError(errorType);
  const message = error instanceof Error ? error.message : error;
  
  return {
    message,
    type: errorType,
    severity,
    retryable,
    userMessage: getUserFriendlyMessage(errorType, message),
    timestamp: new Date(),
    stack: error instanceof Error ? error.stack : undefined,
    id: generateErrorId()
  };
}

/**
 * Generates a unique error ID for tracking
 */
function generateErrorId(): string {
  return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// ============================================================================
// ERROR UTILITY FUNCTIONS
// ============================================================================

/**
 * Checks if an error is a network error
 */
export function isNetworkError(error: Error | string): boolean {
  return categorizeError(error) === ErrorType.NETWORK;
}

/**
 * Checks if an error is a validation error
 */
export function isValidationError(error: Error | string): boolean {
  return categorizeError(error) === ErrorType.VALIDATION;
}

/**
 * Checks if an error is a server error
 */
export function isServerError(error: Error | string): boolean {
  return categorizeError(error) === ErrorType.SERVER;
}

/**
 * Formats an error for logging
 */
export function formatErrorForLogging(errorInfo: ErrorInfo): string {
  return `[${errorInfo.type.toUpperCase()}] ${errorInfo.message} (${errorInfo.timestamp.toISOString()})`;
} 