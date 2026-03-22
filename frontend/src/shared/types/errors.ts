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
// ERROR UTILITY FUNCTIONS
// ============================================================================
// Note: Utility functions (categorizeError, createErrorInfo, etc.) are exported
// from '@/shared/utils/errors' to avoid circular dependencies.
// Import them directly: import { categorizeError } from '@/shared/utils/errors';
