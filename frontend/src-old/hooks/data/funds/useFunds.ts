/**
 * Fund Hooks - CRUD operations for funds
 * 
 * Maps 1:1 to fund.api.ts methods and backend /api/funds endpoints
 * 
 * @module hooks/data/funds/useFunds
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/hooks/core/api';
import { api } from '@/services/api/index';
import type {
  Fund,
  GetFundsResponse,
  GetFundResponse,
  GetFundsQueryParams,
  CreateFundRequest,
} from '@/types/models/fund';

// ============================================================================
// FUND QUERIES
// ============================================================================

/**
 * Get all funds with optional filters
 * Maps to: GET /api/funds
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
  const queryFn = useCallback(() => api.funds.getFunds(params), [params]);
  
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
  const queryFn = useCallback(
    () => api.funds.getFund(fundId, params),
    [fundId, params]
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
    (data) => api.funds.createFund(data)
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
    () => api.funds.deleteFund(fundId)
  );
}

