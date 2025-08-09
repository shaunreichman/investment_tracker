// Centralized API Client
// This file provides a centralized, type-safe API client for all backend communication

import {
  // Core types
  Fund,
  FundEvent,
  TaxStatement,
  InvestmentCompany,
  Entity,
  PortfolioSummary,
  DashboardData,
  FundDetailData,
  
  // Request/response data types
  CreateFundData,
  CreateFundEventData,
  CreateTaxStatementData,
  CreateInvestmentCompanyData,
  CreateEntityData,
  
  // API responses
  ApiError as ApiErrorType,
  
  // List responses
  FundListResponse,
  FundEventListResponse,
  TaxStatementListResponse,
  InvestmentCompanyListResponse,
  EntityListResponse
} from '../types/api';

import { getApiBaseUrl } from '../config/environment';
import { ErrorType, createErrorInfo } from '../types/errors';

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
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Maps HTTP status codes to error types
 */
function mapStatusToErrorType(status: number): ErrorType {
  switch (status) {
    case 400:
      return ErrorType.VALIDATION;
    case 401:
      return ErrorType.AUTHENTICATION;
    case 403:
      return ErrorType.AUTHORIZATION;
    case 404:
      return ErrorType.NOT_FOUND;
    case 500:
    case 502:
    case 503:
    case 504:
      return ErrorType.SERVER;
    default:
      return ErrorType.UNKNOWN;
  }
}

/**
 * Determines if an error is a network error
 */
function isNetworkError(error: any): boolean {
  return (
    error instanceof TypeError ||
    error.message?.includes('fetch') ||
    error.message?.includes('network') ||
    error.message?.includes('connection') ||
    error.message?.includes('timeout')
  );
}

/**
 * Creates a comprehensive error info object from API errors
 */
function createApiErrorInfo(error: any, status?: number): any {
  let errorType: ErrorType;
  
  if (isNetworkError(error)) {
    errorType = ErrorType.NETWORK;
  } else if (error instanceof ApiError) {
    errorType = mapStatusToErrorType(error.status);
  } else {
    errorType = ErrorType.UNKNOWN;
  }
  
  return createErrorInfo(error, errorType);
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
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const apiError = new ApiError(
          errorData.error || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        );
        
        // Create comprehensive error info
        const errorInfo = createApiErrorInfo(apiError, response.status);
        throw errorInfo;
      }

      // Handle empty responses (e.g., DELETE requests)
      if (response.status === 204) {
        return {} as T;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        // Create comprehensive error info
        const errorInfo = createApiErrorInfo(error, error.status);
        throw errorInfo;
      }
      
      // Handle network and other errors
      const errorInfo = createApiErrorInfo(error);
      throw errorInfo;
    }
  }

  // ============================================================================
  // FUNDS API
  // ============================================================================

  async getFunds(): Promise<FundListResponse> {
    const response = await this.request<{ funds: Fund[] }>('/api/dashboard/funds');
    return response.funds;
  }

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
  // INVESTMENT COMPANIES API
  // ============================================================================

  async getInvestmentCompanies(): Promise<InvestmentCompanyListResponse> {
    const response = await this.request<{ companies: InvestmentCompany[] }>('/api/investment-companies');
    return response.companies;
  }

  async createInvestmentCompany(data: CreateInvestmentCompanyData): Promise<InvestmentCompany> {
    return this.request<InvestmentCompany>('/api/investment-companies', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCompanyFunds(companyId: number): Promise<{ company: InvestmentCompany; funds: Fund[] }> {
    return this.request<{ company: InvestmentCompany; funds: Fund[] }>(`/api/companies/${companyId}/funds`);
  }

  // ============================================================================
  // ENTITIES API
  // ============================================================================

  async getEntities(): Promise<EntityListResponse> {
    const response = await this.request<{ entities: Entity[] }>('/api/entities');
    return response.entities;
  }

  async createEntity(data: CreateEntityData): Promise<Entity> {
    return this.request<Entity>('/api/entities', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============================================================================
  // DASHBOARD API
  // ============================================================================

  async getPortfolioSummary(): Promise<PortfolioSummary> {
    return this.request<PortfolioSummary>('/api/dashboard/portfolio-summary');
  }

  async getRecentEvents(): Promise<FundEventListResponse> {
    return this.request<FundEventListResponse>('/api/dashboard/recent-events');
  }

  async getDashboardPerformance(): Promise<any> {
    return this.request<any>('/api/dashboard/performance');
  }

  async getDashboardData(): Promise<DashboardData> {
    // Fetch all dashboard data in parallel
    const [portfolioSummary, funds, recentEvents, performance] = await Promise.all([
      this.getPortfolioSummary(),
      this.getFunds(),
      this.getRecentEvents(),
      this.getDashboardPerformance(),
    ]);

    return {
      portfolio_summary: portfolioSummary,
      funds,
      recent_events: recentEvents,
      performance,
    };
  }

  // ============================================================================
  // HEALTH CHECK
  // ============================================================================

  async healthCheck(): Promise<{ status: string; message: string }> {
    return this.request<{ status: string; message: string }>('/api/health');
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
  tracking_type: FundType.COST_BASED,
  investment_company_id: 1,
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