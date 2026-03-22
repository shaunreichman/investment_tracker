/**
 * ErrorDisplay Utilities
 * 
 * Helper functions for error display logic (icons, colors, mappings).
 * 
 * @module components/shared/feedback/ErrorDisplay
 */

import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { ErrorType, ErrorSeverity } from '@/types/errors';

// ============================================================================
// ICON MAPPINGS
// ============================================================================

/**
 * Maps error type to appropriate icon
 */
export const getErrorIcon = (type: ErrorType) => {
  switch (type) {
    case ErrorType.NETWORK:
      return RefreshIcon;
    case ErrorType.VALIDATION:
      return WarningIcon;
    case ErrorType.AUTHENTICATION:
    case ErrorType.AUTHORIZATION:
      return ErrorIcon;
    case ErrorType.NOT_FOUND:
      return InfoIcon;
    case ErrorType.SERVER:
      return ErrorIcon;
    case ErrorType.UNKNOWN:
    default:
      return ErrorIcon;
  }
};

/**
 * Maps error severity to appropriate icon
 */
export const getSeverityIcon = (severity: ErrorSeverity) => {
  switch (severity) {
    case ErrorSeverity.LOW:
      return InfoIcon;
    case ErrorSeverity.MEDIUM:
      return WarningIcon;
    case ErrorSeverity.HIGH:
    case ErrorSeverity.CRITICAL:
      return ErrorIcon;
    default:
      return ErrorIcon;
  }
};

// ============================================================================
// COLOR MAPPINGS
// ============================================================================

/**
 * Maps error type to MUI Alert severity color
 */
export const getErrorColor = (type: ErrorType): 'error' | 'warning' | 'info' => {
  switch (type) {
    case ErrorType.NETWORK:
      return 'warning';
    case ErrorType.VALIDATION:
      return 'warning';
    case ErrorType.AUTHENTICATION:
    case ErrorType.AUTHORIZATION:
      return 'error';
    case ErrorType.NOT_FOUND:
      return 'info';
    case ErrorType.SERVER:
      return 'error';
    case ErrorType.UNKNOWN:
    default:
      return 'error';
  }
};

/**
 * Maps error severity to MUI Alert severity color
 */
export const getSeverityColor = (severity: ErrorSeverity): 'error' | 'warning' | 'info' => {
  switch (severity) {
    case ErrorSeverity.LOW:
      return 'info';
    case ErrorSeverity.MEDIUM:
      return 'warning';
    case ErrorSeverity.HIGH:
    case ErrorSeverity.CRITICAL:
      return 'error';
    default:
      return 'error';
  }
};

