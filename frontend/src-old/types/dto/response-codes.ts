/**
 * Standardized API Response Codes
 * 
 * TypeScript enum matching backend API response codes exactly.
 * Source: src/api/dto/response_codes.py
 * 
 * DO NOT modify these codes without updating the corresponding Python enum.
 * These must remain in sync with the backend for API communication.
 */

/**
 * Standardized response codes for API responses.
 * 
 * Each response code maps to a specific outcome that can occur in the API,
 * providing consistent response handling across all endpoints.
 */
export enum ApiResponseCode {
  // === SUCCESS CODES (2xx) ===
  /** Operation completed successfully */
  SUCCESS = 'SUCCESS',
  /** Resource created successfully */
  CREATED = 'CREATED',
  /** Resource updated successfully */
  UPDATED = 'UPDATED',
  /** Resource deleted successfully */
  DELETED = 'DELETED',
  /** Operation completed with no content to return */
  NO_CONTENT = 'NO_CONTENT',
  /** Request accepted for processing */
  ACCEPTED = 'ACCEPTED',
  /** Partial content returned successfully */
  PARTIAL_CONTENT = 'PARTIAL_CONTENT',
  
  // === CLIENT ERRORS (4xx) ===
  /** Request validation failed */
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  /** The requested resource was not found */
  RESOURCE_NOT_FOUND = 'RESOURCE_NOT_FOUND',
  /** HTTP method not allowed for this endpoint */
  METHOD_NOT_ALLOWED = 'METHOD_NOT_ALLOWED',
  /** Resource conflict occurred */
  CONFLICT_ERROR = 'CONFLICT_ERROR',
  /** Authentication required */
  UNAUTHORIZED = 'UNAUTHORIZED',
  /** Insufficient permissions */
  FORBIDDEN = 'FORBIDDEN',
  /** Invalid request format or parameters */
  BAD_REQUEST = 'BAD_REQUEST',
  /** Payment required to access this resource */
  PAYMENT_REQUIRED = 'PAYMENT_REQUIRED',
  /** Requested content type not acceptable */
  NOT_ACCEPTABLE = 'NOT_ACCEPTABLE',
  /** Request timed out */
  REQUEST_TIMEOUT = 'REQUEST_TIMEOUT',
  /** Unsupported media type */
  UNSUPPORTED_MEDIA_TYPE = 'UNSUPPORTED_MEDIA_TYPE',
  /** Too many requests, rate limit exceeded */
  TOO_MANY_REQUESTS = 'TOO_MANY_REQUESTS',
  /** Request entity too large */
  REQUEST_ENTITY_TOO_LARGE = 'REQUEST_ENTITY_TOO_LARGE',
  
  // === SERVER ERRORS (5xx) ===
  /** Internal server error occurred */
  INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR',
  /** Service temporarily unavailable */
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  /** Database operation failed */
  DATABASE_ERROR = 'DATABASE_ERROR',
  /** Bad gateway error */
  BAD_GATEWAY = 'BAD_GATEWAY',
  /** Gateway timeout */
  GATEWAY_TIMEOUT = 'GATEWAY_TIMEOUT',
  /** HTTP version not supported */
  HTTP_VERSION_NOT_SUPPORTED = 'HTTP_VERSION_NOT_SUPPORTED',
  /** Feature not implemented */
  NOT_IMPLEMENTED = 'NOT_IMPLEMENTED',
  
  // === BUSINESS LOGIC ERRORS ===
  /** Authentication failed */
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  /** Access denied */
  AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',
  /** Business logic error */
  BUSINESS_LOGIC_ERROR = 'BUSINESS_LOGIC_ERROR',
  /** Business rule violation */
  BUSINESS_RULE_VIOLATION = 'BUSINESS_RULE_VIOLATION',
  /** Insufficient funds for operation */
  INSUFFICIENT_FUNDS = 'INSUFFICIENT_FUNDS',
  /** Duplicate entry detected */
  DUPLICATE_ENTRY = 'DUPLICATE_ENTRY',
  /** Rate limit exceeded */
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  /** System is in maintenance mode */
  MAINTENANCE_MODE = 'MAINTENANCE_MODE',
  /** Feature is not available */
  FEATURE_NOT_AVAILABLE = 'FEATURE_NOT_AVAILABLE'
}

/**
 * Get the appropriate HTTP status code for a response code.
 */
export function getHttpStatusCode(code: ApiResponseCode): number {
  const statusMapping: Record<ApiResponseCode, number> = {
    // Success codes (2xx)
    [ApiResponseCode.SUCCESS]: 200,
    [ApiResponseCode.CREATED]: 201,
    [ApiResponseCode.UPDATED]: 200,
    [ApiResponseCode.DELETED]: 204,
    [ApiResponseCode.NO_CONTENT]: 204,
    [ApiResponseCode.ACCEPTED]: 202,
    [ApiResponseCode.PARTIAL_CONTENT]: 206,
    
    // Client errors (4xx)
    [ApiResponseCode.VALIDATION_ERROR]: 400,
    [ApiResponseCode.BAD_REQUEST]: 400,
    [ApiResponseCode.UNAUTHORIZED]: 401,
    [ApiResponseCode.AUTHENTICATION_ERROR]: 401,
    [ApiResponseCode.PAYMENT_REQUIRED]: 402,
    [ApiResponseCode.FORBIDDEN]: 403,
    [ApiResponseCode.AUTHORIZATION_ERROR]: 403,
    [ApiResponseCode.RESOURCE_NOT_FOUND]: 404,
    [ApiResponseCode.METHOD_NOT_ALLOWED]: 405,
    [ApiResponseCode.NOT_ACCEPTABLE]: 406,
    [ApiResponseCode.CONFLICT_ERROR]: 409,
    [ApiResponseCode.REQUEST_TIMEOUT]: 408,
    [ApiResponseCode.UNSUPPORTED_MEDIA_TYPE]: 415,
    [ApiResponseCode.TOO_MANY_REQUESTS]: 429,
    [ApiResponseCode.REQUEST_ENTITY_TOO_LARGE]: 413,
    
    // Server errors (5xx)
    [ApiResponseCode.INTERNAL_SERVER_ERROR]: 500,
    [ApiResponseCode.DATABASE_ERROR]: 500,
    [ApiResponseCode.NOT_IMPLEMENTED]: 501,
    [ApiResponseCode.BAD_GATEWAY]: 502,
    [ApiResponseCode.SERVICE_UNAVAILABLE]: 503,
    [ApiResponseCode.GATEWAY_TIMEOUT]: 504,
    [ApiResponseCode.HTTP_VERSION_NOT_SUPPORTED]: 505,
    
    // Business logic
    [ApiResponseCode.BUSINESS_RULE_VIOLATION]: 400,
    [ApiResponseCode.BUSINESS_LOGIC_ERROR]: 400,
    [ApiResponseCode.INSUFFICIENT_FUNDS]: 400,
    [ApiResponseCode.DUPLICATE_ENTRY]: 409,
    [ApiResponseCode.RATE_LIMIT_EXCEEDED]: 429,
    [ApiResponseCode.MAINTENANCE_MODE]: 503,
    [ApiResponseCode.FEATURE_NOT_AVAILABLE]: 501,
  };
  
  return statusMapping[code] || 500; // Default to 500 for unknown codes
}

/**
 * Get a human-readable description of the response code.
 */
export function getResponseCodeDescription(code: ApiResponseCode): string {
  const descriptions: Record<ApiResponseCode, string> = {
    // Success codes
    [ApiResponseCode.SUCCESS]: 'Operation completed successfully',
    [ApiResponseCode.CREATED]: 'Resource created successfully',
    [ApiResponseCode.UPDATED]: 'Resource updated successfully',
    [ApiResponseCode.DELETED]: 'Resource deleted successfully',
    [ApiResponseCode.NO_CONTENT]: 'Operation completed with no content to return',
    [ApiResponseCode.ACCEPTED]: 'Request accepted for processing',
    [ApiResponseCode.PARTIAL_CONTENT]: 'Partial content returned successfully',
    
    // Client errors
    [ApiResponseCode.VALIDATION_ERROR]: 'Request validation failed',
    [ApiResponseCode.RESOURCE_NOT_FOUND]: 'The requested resource was not found',
    [ApiResponseCode.METHOD_NOT_ALLOWED]: 'HTTP method not allowed for this endpoint',
    [ApiResponseCode.CONFLICT_ERROR]: 'Resource conflict occurred',
    [ApiResponseCode.UNAUTHORIZED]: 'Authentication required',
    [ApiResponseCode.FORBIDDEN]: 'Insufficient permissions',
    [ApiResponseCode.BAD_REQUEST]: 'Invalid request format or parameters',
    [ApiResponseCode.PAYMENT_REQUIRED]: 'Payment required to access this resource',
    [ApiResponseCode.NOT_ACCEPTABLE]: 'Requested content type not acceptable',
    [ApiResponseCode.REQUEST_TIMEOUT]: 'Request timed out',
    [ApiResponseCode.UNSUPPORTED_MEDIA_TYPE]: 'Unsupported media type',
    [ApiResponseCode.TOO_MANY_REQUESTS]: 'Too many requests, rate limit exceeded',
    [ApiResponseCode.REQUEST_ENTITY_TOO_LARGE]: 'Request entity too large',
    
    // Server errors
    [ApiResponseCode.INTERNAL_SERVER_ERROR]: 'Internal server error occurred',
    [ApiResponseCode.DATABASE_ERROR]: 'Database operation failed',
    [ApiResponseCode.SERVICE_UNAVAILABLE]: 'Service temporarily unavailable',
    [ApiResponseCode.BAD_GATEWAY]: 'Bad gateway error',
    [ApiResponseCode.GATEWAY_TIMEOUT]: 'Gateway timeout',
    [ApiResponseCode.HTTP_VERSION_NOT_SUPPORTED]: 'HTTP version not supported',
    [ApiResponseCode.NOT_IMPLEMENTED]: 'Feature not implemented',
    
    // Business logic
    [ApiResponseCode.AUTHENTICATION_ERROR]: 'Authentication failed',
    [ApiResponseCode.AUTHORIZATION_ERROR]: 'Access denied',
    [ApiResponseCode.BUSINESS_LOGIC_ERROR]: 'Business logic error',
    [ApiResponseCode.BUSINESS_RULE_VIOLATION]: 'Business rule violation',
    [ApiResponseCode.INSUFFICIENT_FUNDS]: 'Insufficient funds for operation',
    [ApiResponseCode.DUPLICATE_ENTRY]: 'Duplicate entry detected',
    [ApiResponseCode.RATE_LIMIT_EXCEEDED]: 'Rate limit exceeded',
    [ApiResponseCode.MAINTENANCE_MODE]: 'System is in maintenance mode',
    [ApiResponseCode.FEATURE_NOT_AVAILABLE]: 'Feature is not available',
  };
  
  return descriptions[code] || 'Unknown response occurred';
}

/**
 * Check if a response code indicates success (2xx).
 */
export function isSuccessResponse(code: ApiResponseCode): boolean {
  return getHttpStatusCode(code) >= 200 && getHttpStatusCode(code) < 300;
}

/**
 * Check if a response code indicates a client error (4xx).
 */
export function isClientError(code: ApiResponseCode): boolean {
  return getHttpStatusCode(code) >= 400 && getHttpStatusCode(code) < 500;
}

/**
 * Check if a response code indicates a server error (5xx).
 */
export function isServerError(code: ApiResponseCode): boolean {
  return getHttpStatusCode(code) >= 500;
}

/**
 * Get user-friendly error message for display.
 * Returns a message appropriate for showing to end users.
 */
export function getUserFriendlyMessage(code: ApiResponseCode, customMessage?: string): string {
  if (customMessage) {
    return customMessage;
  }
  
  // User-friendly messages (less technical than descriptions)
  const userMessages: Partial<Record<ApiResponseCode, string>> = {
    [ApiResponseCode.VALIDATION_ERROR]: 'Please check your input and try again.',
    [ApiResponseCode.RESOURCE_NOT_FOUND]: 'The requested item could not be found.',
    [ApiResponseCode.UNAUTHORIZED]: 'Please log in to continue.',
    [ApiResponseCode.FORBIDDEN]: 'You don\'t have permission to perform this action.',
    [ApiResponseCode.CONFLICT_ERROR]: 'This item already exists or conflicts with existing data.',
    [ApiResponseCode.INTERNAL_SERVER_ERROR]: 'Something went wrong. Please try again later.',
    [ApiResponseCode.SERVICE_UNAVAILABLE]: 'The service is temporarily unavailable. Please try again later.',
    [ApiResponseCode.DATABASE_ERROR]: 'A database error occurred. Please try again.',
    [ApiResponseCode.BUSINESS_RULE_VIOLATION]: 'This action violates business rules.',
    [ApiResponseCode.INSUFFICIENT_FUNDS]: 'Insufficient funds for this operation.',
    [ApiResponseCode.DUPLICATE_ENTRY]: 'This entry already exists.',
    [ApiResponseCode.TOO_MANY_REQUESTS]: 'Too many requests. Please slow down and try again.',
    [ApiResponseCode.MAINTENANCE_MODE]: 'The system is currently under maintenance.',
  };
  
  return userMessages[code] || getResponseCodeDescription(code);
}
