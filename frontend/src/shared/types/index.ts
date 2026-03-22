/**
 * Shared Types Barrel Export
 * 
 * Centralized export of all shared domain types, enums, errors, and DTOs.
 * 
 * Usage:
 *   import { SortOrder, Currency, ErrorInfo } from '@/shared/types';
 */

// Export enums
export {
  SortOrder,
  EventOperation,
  Country,
  Currency,
  DomainObjectType,
  SortFieldDomainUpdateEvent,
  isReverseSortOrder,
  getCurrencyDecimalPlaces,
} from './enums';

// Export error types
export {
  ErrorType,
  ErrorSeverity,
  type ErrorInfo,
  type ErrorDisplayOptions,
} from './errors';

// Re-export error utility functions from utils to maintain backward compatibility
// These are re-exported here for convenience, but the source is @/shared/utils/errors
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
} from '@/shared/utils/errors';

// Export DTOs
export * from './dto';

