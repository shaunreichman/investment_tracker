/**
 * Risk Free Rate Type Definitions
 * 
 * TypeScript interfaces matching backend risk free rate model exactly.
 * Source: src/rates/models/risk_free_rate.py
 * 
 * DO NOT modify these interfaces without updating the corresponding Python model.
 * These must remain in sync with the backend for API communication.
 */

import { Currency } from '@/shared/types';
import { RiskFreeRateType } from './ratesEnums';

// ============================================================================
// RISK FREE RATE MODEL
// ============================================================================

/**
 * RiskFreeRate - Represents risk free rates for different currencies over time.
 * 
 * These rates are used to calculate IRRs for funds.
 * Source: src/rates/models/risk_free_rate.py
 */
export interface RiskFreeRate {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string;
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string;
  
  // Manual fields
  /** ISO-4217 currency code (MANUAL) */
  currency: Currency;
  
  /** Date of the rate (MANUAL) */
  date: string; // ISO 8601 date string (YYYY-MM-DD)
  
  /** Risk-free rate as percentage (e.g., 4.5 for 4.5%) (MANUAL) */
  rate: number;
  
  /** Type of rate (MANUAL) */
  rate_type: RiskFreeRateType;
  
  /** Source of the rate data (MANUAL) */
  source?: string | null;
}

// ============================================================================
// REQUEST DTOs
// ============================================================================

/**
 * Data required to create a new risk-free rate.
 */
export interface CreateRiskFreeRateRequest {
  /** ISO-4217 currency code (required) */
  currency: Currency;
  
  /** Date of the rate (required) */
  date: string; // ISO 8601 date string (YYYY-MM-DD)
  
  /** Risk-free rate as percentage (required) */
  rate: number;
  
  /** Type of rate (optional) */
  rate_type?: RiskFreeRateType;
  
  /** Source of the rate data (optional) */
  source?: string;
}

// Note: UPDATE functionality not yet implemented in backend
// When backend implements PUT /api/risk-free-rates/<id>, add UpdateRiskFreeRateRequest here

// ============================================================================
// RESPONSE DTOs
// ============================================================================

/**
 * Response from GET /api/risk-free-rates
 */
export interface GetRiskFreeRatesResponse {
  /** List of risk-free rates */
  risk_free_rates: RiskFreeRate[];
  
  /** Total count */
  count: number;
}

/**
 * Response from GET /api/risk-free-rates/:id
 */
export interface GetRiskFreeRateResponse {
  /** Risk-free rate details */
  risk_free_rate: RiskFreeRate;
}

// ============================================================================
// QUERY PARAMETERS
// ============================================================================

/**
 * Query parameters for GET /api/risk-free-rates
 */
export interface GetRiskFreeRatesQueryParams {
  /** Filter by single currency */
  currency?: Currency;
  
  /** Filter by multiple currencies (mutually exclusive with currency) */
  currencies?: Currency[];
  
  /** Filter by single rate type */
  rate_type?: RiskFreeRateType;
  
  /** Filter by multiple rate types (mutually exclusive with rate_type) */
  rate_types?: RiskFreeRateType[];
  
  /** Filter by start date */
  start_date?: string; // ISO 8601 date string
  
  /** Filter by end date */
  end_date?: string; // ISO 8601 date string
  
  /** Sort by field */
  sort_by?: string;
  
  /** Sort order */
  sort_order?: 'ASC' | 'DESC';
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Partial risk-free rate for list views (minimal data)
 */
export type RiskFreeRateSummary = Pick<RiskFreeRate, 'id' | 'currency' | 'date' | 'rate' | 'rate_type'>;

