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
  TIMEOUT = 'timeout',          // Request timeouts
  RATE_LIMIT = 'rate_limit',    // Rate limiting (429)
  CONFLICT = 'conflict',        // Resource conflicts (409)
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
 * 
 * Note: The timestamp field uses Date objects for runtime use. If serialization
 * is needed (e.g., for state persistence), convert to ISO string using
 * timestamp.toISOString() before serializing.
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
  details?: unknown;
  
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
export function categorizeError(error: Error | string, statusCode?: number): ErrorType {
  // If we have a status code, use it as the primary categorization method
  if (statusCode !== undefined) {
    if (statusCode === 401) return ErrorType.AUTHENTICATION;
    if (statusCode === 403) return ErrorType.AUTHORIZATION;
    if (statusCode === 404) return ErrorType.NOT_FOUND;
    if (statusCode === 409) return ErrorType.CONFLICT;
    if (statusCode === 422) return ErrorType.VALIDATION;
    if (statusCode === 429) return ErrorType.RATE_LIMIT;
    if (statusCode === 504) return ErrorType.TIMEOUT;
    if (statusCode >= 500) return ErrorType.SERVER;
    if (statusCode >= 400) return ErrorType.VALIDATION;
  }

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
  
  // Timeout errors
  if (lowerMessage.includes('timeout') || 
      lowerMessage.includes('timed out') ||
      lowerMessage.includes('504')) {
    return ErrorType.TIMEOUT;
  }
  
  // Rate limit errors
  if (lowerMessage.includes('rate limit') || 
      lowerMessage.includes('too many requests') ||
      lowerMessage.includes('429')) {
    return ErrorType.RATE_LIMIT;
  }
  
  // Conflict errors
  if (lowerMessage.includes('conflict') || 
      lowerMessage.includes('already exists') ||
      lowerMessage.includes('409')) {
    return ErrorType.CONFLICT;
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
    case ErrorType.TIMEOUT:
      return ErrorSeverity.MEDIUM; // Usually transient
    case ErrorType.RATE_LIMIT:
      return ErrorSeverity.MEDIUM; // User can wait and retry
    case ErrorType.CONFLICT:
      return ErrorSeverity.MEDIUM; // User can resolve conflict
    case ErrorType.UNKNOWN:
      return ErrorSeverity.MEDIUM; // Default to medium for unknown
    default:
      return ErrorSeverity.MEDIUM; // Default fallback
  }
}

/**
 * Determines if an error can be retried
 */
export function isRetryableError(type: ErrorType): boolean {
  return type === ErrorType.NETWORK || 
         type === ErrorType.SERVER || 
         type === ErrorType.TIMEOUT || 
         type === ErrorType.RATE_LIMIT;
}

/**
 * Generates user-friendly error messages based on error type and context
 */
export function getUserFriendlyMessage(type: ErrorType, originalMessage: string, statusCode?: number, context?: string): string {
  // Provide context-specific messages when available
  if (context) {
    switch (context) {
      case 'company_details':
        if (type === ErrorType.SERVER) {
          return 'Unable to load company details due to a system issue. Our team has been notified and is working to resolve this.';
        }
        if (type === ErrorType.NOT_FOUND) {
          return 'The requested company could not be found. It may have been removed or you may have an outdated link.';
        }
        break;
      case 'fund_details':
        if (type === ErrorType.SERVER) {
          return 'Unable to load fund information due to a system issue. Please try again in a few minutes.';
        }
        if (type === ErrorType.NOT_FOUND) {
          return 'The requested fund could not be found. It may have been removed or you may have an outdated link.';
        }
        break;
      case 'api_call':
        if (type === ErrorType.SERVER) {
          return 'The service is temporarily unavailable. Please try again in a few minutes.';
        }
        if (type === ErrorType.NETWORK) {
          return 'Unable to connect to the server. Please check your internet connection and try again.';
        }
        break;
      case 'api_mutation':
        if (type === ErrorType.SERVER) {
          return 'Unable to save your changes due to a system issue. Please try again in a few minutes.';
        }
        if (type === ErrorType.VALIDATION) {
          return 'Please check your input and try again. Some fields may be invalid or required.';
        }
        break;
      case 'dashboard':
        if (type === ErrorType.SERVER) {
          return 'Unable to load dashboard data due to a system issue. Please refresh the page to try again.';
        }
        if (type === ErrorType.NETWORK) {
          return 'Unable to load dashboard information. Please check your connection and try again.';
        }
        break;
      case 'fund_creation':
        if (type === ErrorType.SERVER) {
          return 'Unable to create the fund due to a system issue. Please try again in a few minutes.';
        }
        if (type === ErrorType.VALIDATION) {
          return 'Please check your fund details and try again. Some required information may be missing.';
        }
        break;
      case 'event_creation':
        if (type === ErrorType.SERVER) {
          return 'Unable to create the event due to a system issue. Please try again in a few minutes.';
        }
        if (type === ErrorType.VALIDATION) {
          return 'Please check your event details and try again. Some required information may be missing.';
        }
        break;
      default:
        // Fall through to status code and type-based messages
        break;
    }
  }

  // Status code specific messages
  if (statusCode) {
    switch (statusCode) {
      case 500:
        return 'A server error occurred while processing your request. Our team has been notified and is working to resolve this issue.';
      case 502:
        return 'The service is temporarily unavailable. Please try again in a few minutes.';
      case 503:
        return 'The service is currently under maintenance. Please try again later.';
      case 504:
        return 'The request timed out. Please try again.';
      case 429:
        return 'Too many requests. Please wait a moment before trying again.';
      case 422:
        return 'The request could not be processed. Please check your input and try again.';
      case 409:
        return 'This resource already exists or conflicts with existing data. Please check your information and try again.';
      default:
        // Fall through to type-based messages
        break;
    }
  }

  // Type-based messages
  switch (type) {
    case ErrorType.NETWORK:
      return 'Connection failed. Please check your internet connection and try again.';
    case ErrorType.VALIDATION:
      return 'Please check your input and try again.';
    case ErrorType.AUTHENTICATION:
      return 'Your session has expired. Please refresh the page to continue.';
    case ErrorType.AUTHORIZATION:
      return 'You don\'t have permission to perform this action. Please contact your administrator if you believe this is an error.';
    case ErrorType.NOT_FOUND:
      return 'The requested resource was not found. It may have been moved or removed.';
    case ErrorType.SERVER:
      return 'A server error occurred. Our team has been notified and is working to resolve this issue. Please try again in a few minutes.';
    case ErrorType.TIMEOUT:
      return 'The request timed out. Please try again.';
    case ErrorType.RATE_LIMIT:
      return 'Too many requests. Please wait a moment before trying again.';
    case ErrorType.CONFLICT:
      return 'This resource already exists or conflicts with existing data. Please check your information and try again.';
    case ErrorType.UNKNOWN:
      return 'An unexpected error occurred. Please try again, and if the problem persists, contact support.';
    default:
      return 'An unexpected error occurred. Please try again, and if the problem persists, contact support.';
  }
}

/**
 * Creates a comprehensive ErrorInfo object from an error
 */
export function createErrorInfo(error: Error | string, type?: ErrorType, statusCode?: number): ErrorInfo {
  const errorType = type || categorizeError(error, statusCode);
  const severity = getErrorSeverity(errorType);
  const retryable = isRetryableError(errorType);
  const message = error instanceof Error ? error.message : error;
  
  const errorInfo: ErrorInfo = {
    message,
    type: errorType,
    severity,
    retryable,
    userMessage: getUserFriendlyMessage(errorType, message, statusCode),
    timestamp: new Date(),
    stack: error instanceof Error ? error.stack : undefined,
    id: generateErrorId()
  };
  
  // Only set code if statusCode is provided
  if (statusCode !== undefined) {
    errorInfo.code = statusCode;
  }
  
  return errorInfo;
}

/**
 * Generates a unique error ID for tracking
 */
function generateErrorId(): string {
  return `error_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`;
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
