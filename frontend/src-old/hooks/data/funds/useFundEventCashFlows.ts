/**
 * Fund Event Cash Flow Hooks - CRUD operations for fund event cash flows
 * 
 * Maps 1:1 to fund.api.ts cash flow methods and backend cash flow endpoints
 * 
 * @module hooks/data/funds/useFundEventCashFlows
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/hooks/core/api';
import { api } from '@/services/api/index';
import type {
  FundEventCashFlow,
  GetFundEventCashFlowsResponse,
  GetFundEventCashFlowResponse,
  GetFundEventCashFlowsQueryParams,
  CreateFundEventCashFlowRequest,
} from '@/types/models/fund';

// ============================================================================
// CASH FLOW QUERIES
// ============================================================================

/**
 * Get all fund event cash flows with optional filters
 * Maps to: GET /api/fund-event-cash-flows
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with array of cash flows
 * 
 * @example
 * ```typescript
 * // Get cash flows for a specific bank account
 * const { data, loading } = useFundEventCashFlows({ 
 *   bank_account_id: 5 
 * });
 * ```
 */
export function useFundEventCashFlows(
  params?: GetFundEventCashFlowsQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => api.funds.getFundEventCashFlows(params),
    [params]
  );
  
  return useQuery<GetFundEventCashFlowsResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get all cash flows for a specific fund event
 * Maps to: GET /api/funds/:id/fund-events/:id/fund-event-cash-flows
 * 
 * @param fundId - Fund ID
 * @param fundEventId - Fund Event ID
 * @param options - Hook options
 * @returns Query result with array of cash flows
 * 
 * @example
 * ```typescript
 * const { data: cashFlows, loading } = useFundEventCashFlowsByEvent(
 *   fundId, 
 *   eventId
 * );
 * ```
 */
export function useFundEventCashFlowsByEvent(
  fundId: number,
  fundEventId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => api.funds.getFundEventCashFlowsByEvent(fundId, fundEventId),
    [fundId, fundEventId]
  );
  
  return useQuery<GetFundEventCashFlowsResponse>(queryFn, {
    enabled: fundId > 0 && fundEventId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a specific cash flow by ID
 * Maps to: GET /api/funds/:id/fund-events/:id/fund-event-cash-flows/:id
 * 
 * @param fundId - Fund ID
 * @param fundEventId - Fund Event ID
 * @param fundEventCashFlowId - Cash Flow ID
 * @param options - Hook options
 * @returns Query result with cash flow
 * 
 * @example
 * ```typescript
 * const { data: cashFlow, loading } = useFundEventCashFlow(
 *   fundId, 
 *   eventId, 
 *   cashFlowId
 * );
 * ```
 */
export function useFundEventCashFlow(
  fundId: number,
  fundEventId: number,
  fundEventCashFlowId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => api.funds.getFundEventCashFlow(fundId, fundEventId, fundEventCashFlowId),
    [fundId, fundEventId, fundEventCashFlowId]
  );
  
  return useQuery<GetFundEventCashFlowResponse>(queryFn, {
    enabled: fundId > 0 && fundEventId > 0 && fundEventCashFlowId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// CASH FLOW MUTATIONS
// ============================================================================

/**
 * Create a new cash flow for a specific fund event
 * Maps to: POST /api/funds/:id/fund-events/:id/fund-event-cash-flows
 * 
 * @param fundId - Fund ID
 * @param fundEventId - Fund Event ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createCashFlow } = useCreateFundEventCashFlow(fundId, eventId);
 * 
 * createCashFlow({
 *   bank_account_id: 3,
 *   direction: CashFlowDirection.OUTFLOW,
 *   transfer_date: '2024-01-20',
 *   currency: Currency.AUD,
 *   amount: 50000,
 *   reference: 'Bank ref 12345'
 * });
 * ```
 */
export function useCreateFundEventCashFlow(fundId: number, fundEventId: number) {
  return useMutation<FundEventCashFlow, CreateFundEventCashFlowRequest>(
    (data) => api.funds.createFundEventCashFlow(fundId, fundEventId, data)
  );
}

/**
 * Delete a cash flow
 * Maps to: DELETE /api/funds/:id/fund-events/:id/fund-event-cash-flows/:id
 * 
 * @param fundId - Fund ID
 * @param fundEventId - Fund Event ID
 * @param fundEventCashFlowId - Cash Flow ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteCashFlow } = useDeleteFundEventCashFlow(
 *   fundId, 
 *   eventId, 
 *   cashFlowId
 * );
 * 
 * deleteCashFlow(undefined, {
 *   onSuccess: () => refetchCashFlows()
 * });
 * ```
 */
export function useDeleteFundEventCashFlow(
  fundId: number,
  fundEventId: number,
  fundEventCashFlowId: number
) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => api.funds.deleteFundEventCashFlow(fundId, fundEventId, fundEventCashFlowId)
  );
}

