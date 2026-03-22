/**
 * ErrorDisplay Component Types
 * 
 * Type definitions for ErrorDisplay and its sub-components.
 * 
 * @module components/shared/feedback/ErrorDisplay
 */

import type { ErrorInfo, ErrorType, ErrorSeverity } from '@/types/errors';

// ============================================================================
// MAIN ERROR DISPLAY PROPS
// ============================================================================

/**
 * Props for the ErrorDisplay component
 */
export interface ErrorDisplayProps {
  /** Error information to display */
  error: ErrorInfo | null;
  
  /** Whether to show technical error details */
  showDetails?: boolean;
  
  /** Whether the error can be dismissed */
  canDismiss?: boolean;
  
  /** Whether to auto-dismiss the error */
  autoDismiss?: boolean;
  
  /** Delay before auto-dismissing (in milliseconds) */
  dismissDelay?: number;
  
  /** Maximum retry attempts */
  maxRetries?: number;
  
  /** Callback when retry is requested */
  onRetry?: () => void | Promise<void>;
  
  /** Callback when error is dismissed */
  onDismiss?: () => void;
  
  /** Callback when details are toggled */
  onToggleDetails?: (show: boolean) => void;
  
  /** Custom error message override */
  customMessage?: string;
  
  /** Whether to show error ID for debugging */
  showErrorId?: boolean;
  
  /** Custom styling */
  sx?: any;
}

// ============================================================================
// SUB-COMPONENT PROPS
// ============================================================================

/**
 * Props for ErrorHeader component
 */
export interface ErrorHeaderProps {
  /** Error information */
  error: ErrorInfo;
  
  /** Whether technical details are shown */
  showDetails: boolean;
  
  /** Whether error has technical details to show */
  hasTechnicalDetails: boolean;
  
  /** Whether error can be dismissed */
  canDismiss: boolean;
  
  /** Whether to show error ID */
  showErrorId?: boolean;
  
  /** Callback to toggle details visibility */
  onToggleDetails: () => void;
  
  /** Callback to dismiss error (optional) */
  onDismiss?: () => void;
}

/**
 * Props for ErrorMessage component
 */
export interface ErrorMessageProps {
  /** Message to display */
  message: string;
}

/**
 * Props for ErrorDetails component
 */
export interface ErrorDetailsProps {
  /** Error information */
  error: ErrorInfo;
  
  /** Whether to show details */
  show: boolean;
}

/**
 * Props for ErrorMetadata component
 */
export interface ErrorMetadataProps {
  /** Error information */
  error: ErrorInfo;
}

/**
 * Props for ErrorRetry component
 */
export interface ErrorRetryProps {
  /** Whether retry is allowed */
  canRetry: boolean;
  
  /** Whether retry is in progress */
  isRetrying: boolean;
  
  /** Current retry count */
  retryCount: number;
  
  /** Maximum retry attempts */
  maxRetries: number;
  
  /** Callback to execute retry */
  onRetry: () => void;
}

