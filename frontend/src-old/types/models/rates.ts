/**
 * Rates Domain Type Definitions
 * 
 * TypeScript interfaces matching backend rates models exactly.
 * Source: src/rates/models/
 * 
 * DO NOT modify these interfaces without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import { Currency } from '../enums/shared.enums';
import { RiskFreeRateType } from '../enums/rates.enums';

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
// FX RATE MODEL
// ============================================================================

/**
 * FxRate - Represents FX rates for different currencies over time.
 * 
 * Used for currency conversion in fund calculations.
 * Source: src/rates/models/fx_rate.py
 */
export interface FxRate {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string;
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string;
  
  // Manual fields
  /** From currency code (MANUAL) */
  from_currency: Currency;
  
  /** To currency code (MANUAL) */
  to_currency: Currency;
  
  /** Date of the rate - must be last day of the month (MANUAL) */
  date: string; // ISO 8601 date string (YYYY-MM-DD)
  
  /** FX rate from from_currency to to_currency (MANUAL) */
  fx_rate: number;
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

/**
 * Data required to create a new FX rate.
 * 
 * Note: Backend does not support optional source field for FX rates
 */
export interface CreateFxRateRequest {
  /** From currency code (required) */
  from_currency: Currency;
  
  /** To currency code (required) */
  to_currency: Currency;
  
  /** Date of the rate - must be last day of the month (required) */
  date: string; // ISO 8601 date string (YYYY-MM-DD)
  
  /** FX rate from from_currency to to_currency (required) */
  fx_rate: number;
}

// Note: UPDATE functionality not yet implemented in backend
// When backend implements PUT /api/fx-rates/<id>, add UpdateFxRateRequest here

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

/**
 * Response from GET /api/fx-rates
 */
export interface GetFxRatesResponse {
  /** List of FX rates */
  fx_rates: FxRate[];
  
  /** Total count */
  count: number;
}

/**
 * Response from GET /api/fx-rates/:id
 */
export interface GetFxRateResponse {
  /** FX rate details */
  fx_rate: FxRate;
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

/**
 * Query parameters for GET /api/fx-rates
 */
export interface GetFxRatesQueryParams {
  /** Filter by from currency */
  from_currency?: Currency;
  
  /** Filter by to currency */
  to_currency?: Currency;
  
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

/**
 * Partial FX rate for list views (minimal data)
 */
export type FxRateSummary = Pick<FxRate, 'id' | 'from_currency' | 'to_currency' | 'date' | 'fx_rate'>;
