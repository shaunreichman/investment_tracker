/**
 * Risk-Free Rate Hooks - CRUD operations for risk-free rates
 * 
 * Maps 1:1 to rates.api.ts risk-free rate methods and backend endpoints
 * 
 * @module hooks/data/rates/useRiskFreeRates
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/hooks/core/api';
import { api } from '@/services/api/index';
import type {
  RiskFreeRate,
  GetRiskFreeRatesResponse,
  GetRiskFreeRateResponse,
  GetRiskFreeRatesQueryParams,
  CreateRiskFreeRateRequest,
} from '@/types/models/rates';

// ============================================================================
// RISK-FREE RATE QUERIES
// ============================================================================

/**
 * Get all risk-free rates with optional filters
 * Maps to: GET /api/risk-free-rates
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with risk-free rates and count
 * 
 * @example
 * ```typescript
 * const { data, loading } = useRiskFreeRates({ 
 *   country: Country.AU,
 *   rate_type: RateType.ANNUAL
 * });
 * ```
 */
export function useRiskFreeRates(
  params?: GetRiskFreeRatesQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(() => api.rates.getRiskFreeRates(params), [params]);
  
  return useQuery<GetRiskFreeRatesResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a single risk-free rate by ID
 * Maps to: GET /api/risk-free-rates/:id
 * 
 * @param riskFreeRateId - Risk-Free Rate ID
 * @param options - Hook options
 * @returns Query result with risk-free rate data
 * 
 * @example
 * ```typescript
 * const { data: rate, loading } = useRiskFreeRate(rateId);
 * ```
 */
export function useRiskFreeRate(
  riskFreeRateId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => api.rates.getRiskFreeRate(riskFreeRateId),
    [riskFreeRateId]
  );
  
  return useQuery<GetRiskFreeRateResponse>(queryFn, {
    enabled: riskFreeRateId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// RISK-FREE RATE MUTATIONS
// ============================================================================

/**
 * Create a new risk-free rate
 * Maps to: POST /api/risk-free-rates
 * 
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createRate, loading } = useCreateRiskFreeRate();
 * 
 * createRate({
 *   country: Country.AU,
 *   rate_type: RateType.ANNUAL,
 *   rate_date: '2024-01-01',
 *   rate_value: 4.35
 * });
 * ```
 */
export function useCreateRiskFreeRate() {
  return useMutation<RiskFreeRate, CreateRiskFreeRateRequest>(
    (data) => api.rates.createRiskFreeRate(data)
  );
}

/**
 * Delete a risk-free rate
 * Maps to: DELETE /api/risk-free-rates/:id
 * 
 * @param riskFreeRateId - Risk-Free Rate ID to delete
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteRate, loading } = useDeleteRiskFreeRate(rateId);
 * 
 * deleteRate(undefined, {
 *   onSuccess: () => refetchRates()
 * });
 * ```
 */
export function useDeleteRiskFreeRate(riskFreeRateId: number) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => api.rates.deleteRiskFreeRate(riskFreeRateId)
  );
}

