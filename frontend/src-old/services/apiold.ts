// ============================================================================
// LEGACY API CLIENT (TRANSITIONING TO DOMAIN-ORGANIZED STRUCTURE)
// ============================================================================
//
// This file is being migrated to a domain-organized structure.
//
// NEW STRUCTURE (use this for new code):
//   import { api } from '@/services/api';
//   const banks = await api.banking.getBanks();
//
// MIGRATION STATUS:
//   ✅ Banking API - Migrated to services/api/banking.api.ts
//   ⏳ Funds API - TODO: Migrate when creating types/models/fund.ts
//   ⏳ Companies API - TODO: Migrate when creating types/models/company.ts
//   ⏳ Entities API - TODO: Migrate when creating types/models/entity.ts
//   ⏳ Rates API - TODO: Migrate when creating types/models/rates.ts
//
// This file will remain for backwards compatibility until all domains are migrated.
// ============================================================================

// Centralized API Client (Legacy)
// This file provides a centralized, type-safe API client for all backend communication

import {
  // Core types
  Fund,
  FundEvent,
  TaxStatement,
  Company,
  Entity,
  PortfolioSummary,
  DashboardData,
  FundDetailData,
  
  // Request/response data types
  CreateFundData,
  CreateFundEventData,
  CreateTaxStatementData,
  CreateCompanyData,
  CreateEntityData,
  
  // API responses (legacy types from api.ts)
  ApiError as ApiErrorType,
  
  // List responses
  FundEventListResponse,
  TaxStatementListResponse,
  CompanyListResponse,
  EntityListResponse,
  CompanyOverviewResponse,
  EnhancedFundsResponse,
  CompanyDetailsResponse,
  DashboardFund
} from '../types/api';

// New standardized DTO types
import {
  ApiResponse,
  ApiResponseWrapper,
  ApiResponseCode,
  ApiErrorResponse,
  isApiResponse,
  isApiErrorResponse,
  isSuccessResponse,
  extractResponseData,
  getUserFriendlyMessage
} from '../types/dto';

import { getApiBaseUrl } from '../config/environment';
import { isNetworkError } from '../types/errors';

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

class ApiError extends Error {
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
    return this.details?.success === false && this.details?.error;
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

class ApiClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseUrl: string, defaultHeaders: Record<string, string> = {}) {
    this.baseUrl = baseUrl;
    this.defaultHeaders = defaultHeaders;
  }

  private async request<T>(
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
        
        // Handle new structured ApiErrorResponse format
        if (isApiErrorResponse(errorData)) {
          const responseCode = Object.values(ApiResponseCode).find(
            code => code === errorData.error.code
          );
          
          throw new ApiError(
            errorData.error.message || 'Unknown error',
            response.status,
            {
              code: errorData.error.code,
              details: errorData.error.details,
              timestamp: errorData.error.timestamp,
              ...errorData
            },
            responseCode
          );
        }
        
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

  // ============================================================================
  // FUNDS API
  // ============================================================================

  async getFunds(): Promise<DashboardFund[]> {
    const response = await this.request<{ funds: DashboardFund[] }>('/api/dashboard/funds');
    return response.funds;
  }

  // Alias to canonical endpoint to avoid divergence. Prefer getFundDetail for typed full response.
  async getFund(id: number): Promise<Fund> {
    const response = await this.request<{ fund: Fund; events: FundEvent[]; tax_statements: TaxStatement[]; statistics: any }>(`/api/funds/${id}`);
    return response.fund;
  }

  async getFundDetail(id: number): Promise<FundDetailData> {
    return this.request<FundDetailData>(`/api/funds/${id}`);
  }

  async createFund(data: CreateFundData): Promise<Fund> {
    return this.request<Fund>('/api/funds', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteFund(fundId: number): Promise<void> {
    return this.request<void>(`/api/funds/${fundId}`, {
      method: 'DELETE',
    });
  }

  // ============================================================================
  // FUND EVENTS API
  // ============================================================================

  async getFundEvents(fundId: number): Promise<FundEventListResponse> {
    return this.request<FundEventListResponse>(`/api/funds/${fundId}/events`);
  }

  async createFundEvent(fundId: number, data: CreateFundEventData): Promise<FundEvent> {
    return this.request<FundEvent>(`/api/funds/${fundId}/events`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }



  async deleteFundEvent(fundId: number, eventId: number): Promise<void> {
    return this.request<void>(`/api/funds/${fundId}/events/${eventId}`, {
      method: 'DELETE',
    });
  }

  // ============================================================================
  // TAX STATEMENTS API
  // ============================================================================

  async createTaxStatement(fundId: number, data: CreateTaxStatementData): Promise<TaxStatement> {
    return this.request<TaxStatement>(`/api/funds/${fundId}/tax-statements`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getFundTaxStatements(fundId: number): Promise<TaxStatementListResponse> {
    return this.request<TaxStatementListResponse>(`/api/funds/${fundId}/tax-statements`);
  }

  // ============================================================================
  // COMPANIES API
  // ============================================================================

  async getCompanies(): Promise<CompanyListResponse> {
    const response = await this.request<{ companies: Company[] }>('/api/companies');
    return response.companies;
  }

  async createCompany(data: CreateCompanyData): Promise<Company> {
    try {
      const response = await this.request<Company>('/api/companies', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      
      return response;
    } catch (error) {
      console.error('❌ API: createCompany failed:', error);
      throw error;
    }
  }

  async deleteCompany(companyId: number): Promise<{ message: string; deleted_company_id: number }> {
    try {
      const response = await this.request<{ message: string; deleted_company_id: number }>(`/api/companies/${companyId}`, {
        method: 'DELETE',
      });
      
      return response;
    } catch (error: any) {
      console.error('❌ API: deleteCompany failed:', error);
      throw error;
    }
  }

  async getCompanyFunds(companyId: number): Promise<{ company: Company; funds: Fund[] }> {
    return this.request<{ company: Company; funds: Fund[] }>(`/api/companies/${companyId}/funds`);
  }

  // ============================================================================
  // COMPANIES UI ENHANCED API
  // ============================================================================

  async getCompanyOverview(companyId: number): Promise<CompanyOverviewResponse> {
    return this.request<CompanyOverviewResponse>(`/api/companies/${companyId}/overview`);
  }

  async getEnhancedFunds(
    companyId: number,
    params: {
      sort_by?: string;
      sort_order?: 'asc' | 'desc';
      status_filter?: 'all' | 'active' | 'completed' | 'suspended';
      search?: string;
      page?: number;
      per_page?: number;
    } = {}
  ): Promise<EnhancedFundsResponse> {
    const searchParams = new URLSearchParams();
    
    if (params.sort_by) searchParams.append('sort_by', params.sort_by);
    if (params.sort_order) searchParams.append('sort_order', params.sort_order);
    if (params.status_filter) searchParams.append('status_filter', params.status_filter);
    if (params.search) searchParams.append('search', params.search);
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.per_page) searchParams.append('per_page', params.per_page.toString());

    const queryString = searchParams.toString();
    const endpoint = `/api/companies/${companyId}/funds/enhanced${queryString ? `?${queryString}` : ''}`;
    
    return this.request<EnhancedFundsResponse>(endpoint);
  }

  async getCompanyDetails(companyId: number): Promise<CompanyDetailsResponse> {
    return this.request<CompanyDetailsResponse>(`/api/companies/${companyId}/details`);
  }

  // ============================================================================
  // ENTITIES API
  // ============================================================================

  async getEntities(): Promise<Entity[]> {
    const response = await this.request<Entity[]>('/api/entities');
    return response;
  }

  async createEntity(data: CreateEntityData): Promise<Entity> {
    return this.request<Entity>('/api/entities', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============================================================================
  // BANKING API - MIGRATED TO services/api/banking.api.ts
  // ============================================================================
  //
  // Banking methods have been moved to the new domain-organized structure.
  // 
  // NEW USAGE:
  //   import { api } from '@/services/api';
  //   const banks = await api.banking.getBanks();
  //   const bank = await api.banking.createBank({ name: 'Test', country: 'US' });
  //
  // The methods below are deprecated and will be removed once all code is migrated.
  // ============================================================================

  // ============================================================================
  // HEALTH CHECK
  // ============================================================================

  async healthCheck(): Promise<{ status: string; message: string }> {
    return this.request<{ status: string; message: string }>('/api/health');
  }

  // ============================================================================
  // DEBUGGING & TESTING UTILITIES
  // ============================================================================

  /**
   * Test endpoint to verify new response format handling
   * This method can be used to test the new DTO response format
   */
  async testResponseFormat(endpoint: string): Promise<{ 
    isNewFormat: boolean; 
    rawResponse: any; 
    extractedData: any 
  }> {
    try {
      const rawResponse = await fetch(`${this.baseUrl}${endpoint}`);
      const responseData = await rawResponse.json();
      
      const isNewFormat = responseData.success === true && responseData.data !== undefined;
      const extractedData = isNewFormat ? responseData.data : responseData;
      
      return {
        isNewFormat,
        rawResponse: responseData,
        extractedData
      };
    } catch (error) {
      return {
        isNewFormat: false,
        rawResponse: null,
        extractedData: null
      };
    }
  }
}

// ============================================================================
// SINGLETON INSTANCE
// ============================================================================

// Create and export a singleton instance
export const apiClient = new ApiClient(API_BASE_URL, DEFAULT_HEADERS);

// ============================================================================
// CONVENIENCE EXPORTS
// ============================================================================

// Export the class for testing or custom instances
export { ApiClient };

// Export types for use in other files
export type { ApiErrorType as ApiError };

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

/*
// Example usage in components:

import { apiClient } from '../services/api';

// Get all funds
const funds = await apiClient.getFunds();

// Create a new fund
const newFund = await apiClient.createFund({
  name: 'My Fund',
  tracking_type: FundTrackingType.COST_BASED,
  company_id: 1,
  entity_id: 1,
});

// Get fund with events
const fund = await apiClient.getFund(1);

// Create a fund event
const event = await apiClient.createFundEvent(1, {
  event_type: EventType.CAPITAL_CALL,
  event_date: '2024-01-01',
  amount: 100000,
});

// Create a tax statement
const taxStatement = await apiClient.createTaxStatement(1, {
  entity_id: 1,
  financial_year: '2024-25',
  statement_date: '2024-08-24',
  eofy_debt_interest_deduction_rate: 32.5,
});
*/ 