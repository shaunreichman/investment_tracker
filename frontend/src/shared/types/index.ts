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

// Export errors
export {
  ErrorType,
  ErrorSeverity,
  type ErrorInfo,
  type ErrorDisplayOptions,
  categorizeError,
  getErrorSeverity,
  isRetryableError,
  getUserFriendlyMessage,
  createErrorInfo,
  isNetworkError,
  isValidationError,
  isServerError,
  formatErrorForLogging,
} from './errors';

// Export DTOs
export * from './dto';

