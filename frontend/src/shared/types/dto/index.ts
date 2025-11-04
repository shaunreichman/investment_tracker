/**
 * DTO (Data Transfer Objects) Barrel Export
 * 
 * Centralized export of all DTO types, response codes, and type guards.
 * 
 * Usage:
 *   import { ApiResponse, ApiResponseCode, isSuccessResponse } from '@/shared/types/dto';
 */

// Response codes
export {
  ApiResponseCode,
  getHttpStatusCode,
  getResponseCodeDescription,
  isSuccessResponse as isSuccessResponseCode,
  isClientError,
  isServerError,
  getUserFriendlyMessage
} from './response-codes';

// API response interfaces
export type {
  ApiResponse,
  ControllerResponseDTO,
  ApiResponseWrapper,
  ListResponse,
  DeleteResponse,
  HealthCheckResponse
} from './api-response';

// Type guards
export {
  isApiResponse,
  isSuccessResponse,
  isErrorResponse,
  isControllerResponseDTO,
  isDtoError,
  isDtoSuccess,
  isListResponse,
  isDeleteResponse,
  isHealthCheckResponse,
  extractResponseData,
  extractResponseDataOrNull,
  hasResponseCode,
  assertSuccessResponse,
  isError,
  isString,
  isNumber,
  isArray,
  isObject,
  safeParseApiResponse,
  hasRequiredProperties
} from './type-guards';

