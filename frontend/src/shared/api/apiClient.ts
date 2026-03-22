/**
 * Base API Client
 * 
 * Provides core HTTP request functionality with:
 * - Standardized error handling
 * - DTO response parsing
 * - Type-safe request/response handling
 * - Network error detection
 */

import {
  ApiResponse,
  ApiResponseWrapper,
  ApiResponseCode,
  isApiResponse,
  isSuccessResponse,
  getUserFriendlyMessage
} from '@/shared/types/dto';
import { getApiBaseUrl } from '@/config/environment';
import { isNetworkError } from '@/shared/utils/errors';

// ============================================================================
// CONFIGURATION
// ============================================================================

const API_BASE_URL = getApiBaseUrl();

const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

// ============================================================================
// ERROR HANDLING
// ============================================================================

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any,
    public responseCode?: ApiResponseCode
  ) {
    super(message);
    this.name = 'ApiError';
  }

  // Get error code from structured error response
  get errorCode(): string | undefined {
    return this.responseCode || this.details?.code || this.details?.response_code;
  }

  // Get additional error details
  get errorDetails(): any {
    return this.details?.details;
  }

  // Check if this is a structured error response
  get isStructuredError(): boolean {
    return this.details?.success === false && this.details?.response_code;
  }

  // Get user-friendly error message
  get userFriendlyMessage(): string {
    if (this.responseCode) {
      return getUserFriendlyMessage(this.responseCode, this.message);
    }
    return this.message;
  }

  // Check if error is a client error (4xx)
  get isClientError(): boolean {
    return this.status >= 400 && this.status < 500;
  }

  // Check if error is a server error (5xx)
  get isServerError(): boolean {
    return this.status >= 500;
  }
}

// ============================================================================
// BASE API CLIENT
// ============================================================================

export class ApiClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseUrl: string = API_BASE_URL, defaultHeaders: Record<string, string> = DEFAULT_HEADERS) {
    this.baseUrl = baseUrl;
    this.defaultHeaders = defaultHeaders;
  }

  /**
   * Core request method handling all HTTP communication.
   * 
   * Features:
   * - Automatic DTO parsing
   * - Structured error handling
   * - Type-safe responses
   * - Backwards compatible with legacy format
   */
  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      ...this.defaultHeaders,
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        method: 'GET', // Default method for GET requests
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({})) as any;
        
        // Handle ApiResponse with error (success: false)
        if (isApiResponse(errorData) && !errorData.success) {
          const responseCode = Object.values(ApiResponseCode).find(
            code => code === errorData.response_code
          );
          
          throw new ApiError(
            errorData.message || 'Request failed',
            response.status,
            errorData,
            responseCode
          );
        }
        
        // Fallback to old error format for compatibility during transition
        const errorMessage = errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`;
        throw new ApiError(
          typeof errorMessage === 'string' ? errorMessage : 'Unknown error',
          response.status,
          errorData
        );
      }

      // Handle empty responses (e.g., DELETE requests with 204 No Content)
      if (response.status === 204) {
        return {} as T;
      }

      const responseData = await response.json() as ApiResponseWrapper<T>;
      
      // Handle new ApiResponse format using type guard
      if (isApiResponse<T>(responseData)) {
        if (isSuccessResponse(responseData)) {
          // New format: extract data from DTO wrapper
          return responseData.data;
        } else {
          // ApiResponse with success: false (should have been caught above, but handle defensively)
          const responseCode = Object.values(ApiResponseCode).find(
            code => code === responseData.response_code
          );
          
          throw new ApiError(
            responseData.message || 'Request failed',
            response.status,
            responseData,
            responseCode
          );
        }
      }
      
      // Handle legacy response format for backward compatibility during transition
      // This ensures existing functionality works while backend migrates
      return responseData as T;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Handle network and other errors
      if (isNetworkError(error as any)) {
        throw new ApiError('Network error', 0, undefined, ApiResponseCode.SERVICE_UNAVAILABLE);
      }
      
      throw new ApiError('Unknown error', 0, undefined, ApiResponseCode.INTERNAL_SERVER_ERROR);
    }
  }

  /**
   * Helper method for GET requests with query parameters.
   */
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const searchParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => searchParams.append(key, String(v)));
          } else {
            searchParams.append(key, String(value));
          }
        }
      });
    }

    const queryString = searchParams.toString();
    const fullEndpoint = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request<T>(fullEndpoint);
  }

  /**
   * Helper method for POST requests.
   */
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Helper method for PUT requests.
   */
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * Helper method for DELETE requests.
   */
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }
}

// ============================================================================
// SINGLETON INSTANCE
// ============================================================================

/**
 * Singleton API client instance for use throughout the application.
 */
export const apiClient = new ApiClient();
