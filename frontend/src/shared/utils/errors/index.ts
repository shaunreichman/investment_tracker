/**
 * Error Utilities Barrel Export
 * 
 * Centralized export of all error normalization utilities and logging.
 * 
 * Usage:
 *   import { createErrorInfo, errorLogger, categorizeError } from '@/shared/utils/errors';
 */

// Export error normalization utilities
export {
  categorizeError,
  getErrorSeverity,
  isRetryableError,
  getUserFriendlyMessage,
  createErrorInfo,
  isNetworkError,
  isValidationError,
  isServerError,
  formatErrorForLogging,
} from './errorNormalization';

// Export error logger
export {
  errorLogger,
  type ErrorContext,
  type ErrorLoggerConfig,
} from './errorLogger';

