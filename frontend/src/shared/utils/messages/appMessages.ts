/**
 * Shared application copy.
 *
 * Consolidates SUCCESS and ERROR messages so domains reuse authoritative text.
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  GENERIC: 'An unexpected error occurred. Please try again.',
} as const;

export const SUCCESS_MESSAGES = {
  FUND_CREATED: 'Fund created successfully.',
  FUND_UPDATED: 'Fund updated successfully.',
  EVENT_CREATED: 'Event created successfully.',
  EVENT_UPDATED: 'Event updated successfully.',
  EVENT_DELETED: 'Event deleted successfully.',
  TAX_STATEMENT_CREATED: 'Tax statement created successfully.',
  TAX_STATEMENT_UPDATED: 'Tax statement updated successfully.',
} as const;

