/**
 * FX Rate Hooks - CRUD operations for foreign exchange rates
 * 
 * Maps 1:1 to rates.api.ts FX rate methods and backend endpoints
 * 
 * @module hooks/data/rates/useFxRates
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/hooks/core/api';
import { api } from '@/services/api/index';
import type {
  FxRate,
  GetFxRatesResponse,
  GetFxRateResponse,
  GetFxRatesQueryParams,
  CreateFxRateRequest,
} from '@/types/models/rates';

// ============================================================================
// FX RATE QUERIES
// ============================================================================

/**
 * Get all FX rates with optional filters
 * Maps to: GET /api/fx-rates
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with FX rates and count
 * 
 * @example
 * ```typescript
 * const { data, loading } = useFxRates({ 
 *   from_currency: Currency.USD,
 *   to_currency: Currency.AUD,
 *   start_rate_date: '2024-01-01'
 * });
 * ```
 */
export function useFxRates(
  params?: GetFxRatesQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(() => api.rates.getFxRates(params), [params]);
  
  return useQuery<GetFxRatesResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a single FX rate by ID
 * Maps to: GET /api/fx-rates/:id
 * 
 * @param fxRateId - FX Rate ID
 * @param options - Hook options
 * @returns Query result with FX rate data
 * 
 * @example
 * ```typescript
 * const { data: rate, loading } = useFxRate(rateId);
 * ```
 */
export function useFxRate(
  fxRateId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => api.rates.getFxRate(fxRateId),
    [fxRateId]
  );
  
  return useQuery<GetFxRateResponse>(queryFn, {
    enabled: fxRateId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// FX RATE MUTATIONS
// ============================================================================

/**
 * Create a new FX rate
 * Maps to: POST /api/fx-rates
 * 
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createFxRate, loading } = useCreateFxRate();
 * 
 * createFxRate({
 *   from_currency: Currency.USD,
 *   to_currency: Currency.AUD,
 *   rate_date: '2024-01-15',
 *   rate_value: 1.52
 * });
 * ```
 */
export function useCreateFxRate() {
  return useMutation<FxRate, CreateFxRateRequest>(
    (data) => api.rates.createFxRate(data)
  );
}

/**
 * Delete an FX rate
 * Maps to: DELETE /api/fx-rates/:id
 * 
 * @param fxRateId - FX Rate ID to delete
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteFxRate, loading } = useDeleteFxRate(rateId);
 * 
 * deleteFxRate(undefined, {
 *   onSuccess: () => refetchRates()
 * });
 * ```
 */
export function useDeleteFxRate(fxRateId: number) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => api.rates.deleteFxRate(fxRateId)
  );
}

