/**
 * Rates Domain Types Barrel Export
 * 
 * Centralized export of all rates domain types.
 * 
 * Usage:
 *   import { RiskFreeRate, FxRate, CreateRiskFreeRateRequest } from '@/rates/types';
 */

// Re-export risk-free rate types
export type {
  // Core model
  RiskFreeRate,
  
  // Request DTOs
  CreateRiskFreeRateRequest,
  
  // Response DTOs
  GetRiskFreeRatesResponse,
  GetRiskFreeRateResponse,
  
  // Query parameters
  GetRiskFreeRatesQueryParams,
  
  // Utility types
  RiskFreeRateSummary,
} from './riskFreeRate';

// Re-export FX rate types
export type {
  // Core model
  FxRate,
  
  // Request DTOs
  CreateFxRateRequest,
  
  // Response DTOs
  GetFxRatesResponse,
  GetFxRateResponse,
  
  // Query parameters
  GetFxRatesQueryParams,
  
  // Utility types
  FxRateSummary,
} from './fxRate';

// Re-export enums from enums.ts
export {
  // FX rate enums
  SortFieldFxRate,
  
  // Risk free rate enums
  RiskFreeRateType,
  SortFieldRiskFreeRate,
} from './ratesEnums';

