/**
 * Standardized API Response Interfaces
 * 
 * TypeScript interfaces matching backend API response structures exactly.
 * Source: src/api/dto/api_response.py and controller_response_dto.py
 * 
 * DO NOT modify these interfaces without updating the corresponding Python classes.
 * These must remain in sync with the backend for API communication.
 */

import { ApiResponseCode } from './response-codes';

/**
 * Standardized API response wrapper.
 * 
 * This is the final response format sent from routes to the client.
 */
export interface ApiResponse<T = any> {
  /** Whether the operation was successful (auto-determined from HTTP status) */
  success: boolean;
  
  /** Response code enum value */
  response_code: string;
  
  /** Optional message describing the response */
  message?: string | null;
  
  /** The actual response data (if successful) */
  data?: T | null;
  
  /** Additional details about the response (often error details) */
  details?: string | null;
  
  /** ISO 8601 timestamp of when the response was generated */
  timestamp: string;
}

/**
 * Controller Response Data Transfer Object.
 * 
 * Generic DTO for all controller responses between controller and route layers.
 * This is the internal format used before being wrapped in ApiResponse.
 */
export interface ControllerResponseDTO<T = any> {
  /** The response data (if successful) */
  data?: T | null;
  
  /** Error message (if error occurred) */
  error?: string | null;
  
  /** Response code */
  response_code: ApiResponseCode;
  
  /** Optional message */
  message?: string | null;
}

/**
 * Error response structure.
 * 
 * Standardized error response format when success is false.
 */
export interface ApiErrorResponse {
  /** Always false for error responses */
  success: false;
  
  /** Error object containing details */
  error: {
    /** Error code */
    code: string;
    
    /** Error message */
    message: string;
    
    /** Additional error details */
    details?: any;
    
    /** Timestamp of when error occurred */
    timestamp?: string;
  };
  
  /** ISO 8601 timestamp */
  timestamp?: string;
}

/**
 * Union type for all possible API responses.
 * 
 * This represents what we might receive from the API - either:
 * - A structured ApiResponse wrapper
 * - Raw data (for backwards compatibility during transition)
 */
export type ApiResponseWrapper<T> = ApiResponse<T> | T;

/**
 * Common list response format.
 * 
 * Many endpoints return a list of items in this format.
 */
export interface ListResponse<T> {
  /** Array of items */
  items: T[];
  
  /** Total count of items */
  count: number;
}

/**
 * Delete response format.
 */
export interface DeleteResponse {
  /** Success message */
  message: string;
  
  /** ID of deleted resource */
  deleted_id?: number | string;
}

/**
 * Health check response.
 */
export interface HealthCheckResponse {
  /** Status of the service */
  status: string;
  
  /** Health check message */
  message: string;
  
  /** Timestamp of health check */
  timestamp?: string;
  
  /** Additional health details */
  details?: {
    /** Database connection status */
    database?: 'healthy' | 'unhealthy';
    
    /** API version */
    version?: string;
    
    /** Uptime in seconds */
    uptime?: number;
  };
}
