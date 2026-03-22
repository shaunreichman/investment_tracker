/**
 * Fund Hooks - CRUD operations for funds
 * 
 * Maps 1:1 to fundApi methods and backend /api/funds endpoints
 * 
 * @module fund/hooks/useFunds
 */

import { useCallback, useMemo, useRef } from 'react';
import { useQuery, useMutation } from '@/shared/hooks/core';
import { fundApi } from '../api';
import type {
  Fund,
  GetFundsResponse,
  GetFundResponse,
  GetFundsQueryParams,
  CreateFundRequest,
} from '../types';

// ============================================================================
// UTILITIES
// ============================================================================

/**
 * Serialize params to a stable string key for comparison
 * Sorts keys to ensure consistent serialization regardless of property order
 */
function serializeParams(params?: GetFundsQueryParams): string {
  if (!params || Object.keys(params).length === 0) {
    return '{}';
  }
  
  // Sort keys for consistent serialization
  const sorted = Object.keys(params)
    .sort()
    .reduce((acc, key) => {
      const value = params[key as keyof GetFundsQueryParams];
      // Handle undefined/null values consistently
      if (value === undefined || value === null) {
        return acc;
      }
      acc[key] = value;
      return acc;
    }, {} as Record<string, any>);
  
  return JSON.stringify(sorted);
}

// ============================================================================
// FUND QUERIES
// ============================================================================

/**
 * Get all funds with optional filters
 * Maps to: GET /api/funds
 * 
 * Uses deep comparison of params to prevent unnecessary query function recreation.
 * Only recreates the query function when params actually change (by value, not reference).
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with array of funds
 * 
 * @example
 * ```typescript
 * // Get all funds
 * const { data, loading } = useFunds();
 * 
 * // Get active funds for a company
 * const { data, loading } = useFunds({ 
 *   company_id: 1, 
 *   fund_status: FundStatus.ACTIVE 
 * });
 * ```
 */
export function useFunds(
  params?: GetFundsQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  // Serialize params to detect actual changes (not just reference changes)
  const paramsKey = useMemo(() => serializeParams(params), [params]);
  const prevParamsKeyRef = useRef<string>(paramsKey);
  
  // Only recreate queryFn when params actually change
  const stableParams = useMemo(() => {
    if (prevParamsKeyRef.current !== paramsKey) {
      prevParamsKeyRef.current = paramsKey;
    }
    return params;
  }, [paramsKey, params]);
  
  const queryFn = useCallback(() => fundApi.getFunds(stableParams), [stableParams]);
  
  return useQuery<GetFundsResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a single fund by ID
 * Maps to: GET /api/funds/:id
 * 
 * @param fundId - Fund ID
 * @param params - Query parameters for including relationships
 * @param options - Hook options
 * @returns Query result with fund data
 * 
 * @example
 * ```typescript
 * // Get fund with events
 * const { data: fund, loading } = useFund(fundId, { 
 *   include_fund_events: true 
 * });
 * ```
 */
export function useFund(
  fundId: number,
  params?: {
    include_fund_events?: boolean;
    include_fund_event_cash_flows?: boolean;
    include_fund_tax_statements?: boolean;
  },
  options?: { refetchOnWindowFocus?: boolean }
) {
  // Serialize params to detect actual changes
  const paramsKey = useMemo(() => {
    if (!params) return '{}';
    return JSON.stringify(params);
  }, [params]);
  
  const stableParams = useMemo(() => params, [paramsKey]);
  
  const queryFn = useCallback(
    () => fundApi.getFund(fundId, stableParams),
    [fundId, stableParams]
  );
  
  return useQuery<GetFundResponse>(queryFn, {
    enabled: fundId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// FUND MUTATIONS
// ============================================================================

/**
 * Create a new fund
 * Maps to: POST /api/funds
 * 
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createFund, loading } = useCreateFund();
 * 
 * createFund({
 *   name: 'New Fund LP',
 *   entity_id: 1,
 *   company_id: 2,
 *   tracking_type: FundTrackingType.NAV_BASED,
 *   tax_jurisdiction: Country.AU,
 *   currency: Currency.AUD
 * });
 * ```
 */
export function useCreateFund() {
  return useMutation<Fund, CreateFundRequest>(
    (data) => fundApi.createFund(data)
  );
}

/**
 * Delete a fund
 * Maps to: DELETE /api/funds/:id
 * 
 * @param fundId - Fund ID to delete
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteFund, loading } = useDeleteFund(fundId);
 * 
 * deleteFund(undefined, {
 *   onSuccess: () => navigate('/funds')
 * });
 * ```
 */
export function useDeleteFund(fundId: number) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => fundApi.deleteFund(fundId)
  );
}

