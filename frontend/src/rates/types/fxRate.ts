/**
 * FX Rate Type Definitions
 * 
 * TypeScript interfaces matching backend FX rate model exactly.
 * Source: src/rates/models/fx_rate.py
 * 
 * DO NOT modify these interfaces without updating the corresponding Python model.
 * These must remain in sync with the backend for API communication.
 */

import { Currency } from '@/shared/types';

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
 * Partial FX rate for list views (minimal data)
 */
export type FxRateSummary = Pick<FxRate, 'id' | 'from_currency' | 'to_currency' | 'date' | 'fx_rate'>;

