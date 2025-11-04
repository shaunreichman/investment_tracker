/**
 * Rates Data Hooks - Barrel Export
 * 
 * All hooks for rates domain operations:
 * - Risk-Free Rates (CRUD)
 * - FX Rates (CRUD)
 * 
 * @module rates/hooks
 */

// Risk-Free Rate hooks
export {
  useRiskFreeRates,
  useRiskFreeRate,
  useCreateRiskFreeRate,
  useDeleteRiskFreeRate,
} from './useRiskFreeRates';

// FX Rate hooks
export {
  useFxRates,
  useFxRate,
  useCreateFxRate,
  useDeleteFxRate,
} from './useFxRates';

// Rates form validation schemas
export * from './schemas';

// Rates form transformers
export * from './transformers';

