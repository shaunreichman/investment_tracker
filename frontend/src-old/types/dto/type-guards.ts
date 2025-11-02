/**
 * Type Guards for Runtime DTO Validation
 * 
 * Type guards to validate API responses at runtime and narrow types safely.
 * These help catch API contract violations and handle edge cases gracefully.
 */

import { 
  ApiResponse, 
  ApiErrorResponse, 
  ControllerResponseDTO,
  ListResponse,
  DeleteResponse,
  HealthCheckResponse
} from './api-response';
import { ApiResponseCode } from './response-codes';

/**
 * Type guard to check if a value is an ApiResponse.
 */
export function isApiResponse<T = any>(value: unknown): value is ApiResponse<T> {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const response = value as any;
  
  return (
    typeof response.success === 'boolean' &&
    typeof response.response_code === 'string' &&
    typeof response.timestamp === 'string' &&
    (response.message === undefined || response.message === null || typeof response.message === 'string') &&
    (response.data === undefined || response.data === null || response.data !== undefined) &&
    (response.details === undefined || response.details === null || typeof response.details === 'string')
  );
}

/**
 * Type guard to check if a value is an ApiErrorResponse.
 */
export function isApiErrorResponse(value: unknown): value is ApiErrorResponse {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const response = value as any;
  
  return (
    response.success === false &&
    typeof response.error === 'object' &&
    response.error !== null &&
    typeof response.error.code === 'string' &&
    typeof response.error.message === 'string'
  );
}

/**
 * Type guard to check if an ApiResponse is successful.
 */
export function isSuccessResponse<T>(response: ApiResponse<T>): response is ApiResponse<T> & { success: true; data: T } {
  return response.success === true && response.data !== undefined && response.data !== null;
}

/**
 * Type guard to check if an ApiResponse is an error.
 */
export function isErrorResponse<T>(response: ApiResponse<T>): response is ApiResponse<T> & { success: false } {
  return response.success === false;
}

/**
 * Type guard to check if a value is a ControllerResponseDTO.
 */
export function isControllerResponseDTO<T = any>(value: unknown): value is ControllerResponseDTO<T> {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const dto = value as any;
  
  return (
    (dto.data !== undefined || dto.error !== undefined) &&
    typeof dto.response_code === 'string' &&
    Object.values(ApiResponseCode).includes(dto.response_code as ApiResponseCode)
  );
}

/**
 * Type guard to check if a ControllerResponseDTO contains an error.
 */
export function isDtoError<T>(dto: ControllerResponseDTO<T>): dto is ControllerResponseDTO<T> & { error: string } {
  return typeof dto.error === 'string' && dto.error.length > 0;
}

/**
 * Type guard to check if a ControllerResponseDTO contains data.
 */
export function isDtoSuccess<T>(dto: ControllerResponseDTO<T>): dto is ControllerResponseDTO<T> & { data: T } {
  return dto.error === undefined || dto.error === null;
}

/**
 * Type guard to check if a value is a ListResponse.
 */
export function isListResponse<T>(value: unknown): value is ListResponse<T> {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const response = value as any;
  
  return (
    Array.isArray(response.items) &&
    typeof response.count === 'number'
  );
}

/**
 * Type guard to check if a value is a DeleteResponse.
 */
export function isDeleteResponse(value: unknown): value is DeleteResponse {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const response = value as any;
  
  return (
    typeof response.message === 'string' &&
    (response.deleted_id === undefined || 
     typeof response.deleted_id === 'number' || 
     typeof response.deleted_id === 'string')
  );
}

/**
 * Type guard to check if a value is a HealthCheckResponse.
 */
export function isHealthCheckResponse(value: unknown): value is HealthCheckResponse {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const response = value as any;
  
  return (
    typeof response.status === 'string' &&
    typeof response.message === 'string'
  );
}

/**
 * Extract data from ApiResponse safely.
 * Returns the data if successful, throws an error if not.
 */
export function extractResponseData<T>(response: ApiResponse<T>): T {
  if (isSuccessResponse(response)) {
    return response.data;
  }
  
  throw new Error(response.message || 'API request failed');
}

/**
 * Extract data from ApiResponse or return null if error.
 * Safer alternative to extractResponseData that doesn't throw.
 */
export function extractResponseDataOrNull<T>(response: ApiResponse<T>): T | null {
  if (isSuccessResponse(response)) {
    return response.data;
  }
  
  return null;
}

/**
 * Validate response code is in expected set.
 */
export function hasResponseCode(response: ApiResponse<any>, ...codes: ApiResponseCode[]): boolean {
  return codes.some(code => response.response_code === code);
}

/**
 * Assert that a response is successful, throwing an error if not.
 * Useful for situations where you expect success and want to fail fast.
 */
export function assertSuccessResponse<T>(response: ApiResponse<T>): asserts response is ApiResponse<T> & { success: true; data: T } {
  if (!isSuccessResponse(response)) {
    const errorMsg = response.message || `API request failed with code: ${response.response_code}`;
    throw new Error(errorMsg);
  }
}

/**
 * Type guard to check if unknown error is an Error object.
 */
export function isError(error: unknown): error is Error {
  return error instanceof Error;
}

/**
 * Type guard to check if unknown value is a string.
 */
export function isString(value: unknown): value is string {
  return typeof value === 'string';
}

/**
 * Type guard to check if unknown value is a number.
 */
export function isNumber(value: unknown): value is number {
  return typeof value === 'number' && !isNaN(value);
}

/**
 * Type guard to check if unknown value is an array.
 */
export function isArray(value: unknown): value is any[] {
  return Array.isArray(value);
}

/**
 * Type guard to check if unknown value is an object (and not null or array).
 */
export function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * Safely parse unknown value as API response.
 * Returns the parsed response or null if invalid.
 */
export function safeParseApiResponse<T = any>(value: unknown): ApiResponse<T> | null {
  if (isApiResponse<T>(value)) {
    return value;
  }
  
  return null;
}

/**
 * Validate that a value has all required properties.
 * Useful for runtime validation of API responses.
 */
export function hasRequiredProperties<T extends object>(
  value: unknown,
  ...properties: (keyof T)[]
): value is T {
  if (!isObject(value)) {
    return false;
  }
  
  return properties.every(prop => prop in value);
}
