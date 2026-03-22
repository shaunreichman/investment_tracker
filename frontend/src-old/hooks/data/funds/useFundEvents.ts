/**
 * Fund Event Hooks - CRUD operations for fund events
 * 
 * Maps 1:1 to fund.api.ts event methods and backend fund event endpoints
 * 
 * @module hooks/data/funds/useFundEvents
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/hooks/core/api';
import { api } from '@/services/api/index';
import type {
  FundEvent,
  GetFundEventsResponse,
  GetFundEventResponse,
  GetFundEventsQueryParams,
  CreateCapitalCallRequest,
  CreateReturnOfCapitalRequest,
  CreateUnitPurchaseRequest,
  CreateUnitSaleRequest,
  CreateNavUpdateRequest,
  CreateDistributionRequest,
} from '@/types/models/fund';

// ============================================================================
// FUND EVENT QUERIES
// ============================================================================

/**
 * Get all fund events with optional filters
 * Maps to: GET /api/fund-events
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with array of fund events
 * 
 * @example
 * ```typescript
 * // Get all capital call events
 * const { data, loading } = useFundEvents({ 
 *   event_type: EventType.CAPITAL_CALL 
 * });
 * ```
 */
export function useFundEvents(
  params?: GetFundEventsQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(() => api.funds.getFundEvents(params), [params]);
  
  return useQuery<GetFundEventsResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get all events for a specific fund
 * Maps to: GET /api/funds/:id/fund-events
 * 
 * @param fundId - Fund ID
 * @param params - Query parameters for including relationships
 * @param options - Hook options
 * @returns Query result with array of fund events
 * 
 * @example
 * ```typescript
 * const { data: events, loading } = useFundEventsByFundId(fundId, {
 *   include_fund_event_cash_flows: true
 * });
 * ```
 */
export function useFundEventsByFundId(
  fundId: number,
  params?: { include_fund_event_cash_flows?: boolean },
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => api.funds.getFundEventsByFundId(fundId, params),
    [fundId, params]
  );
  
  return useQuery<GetFundEventsResponse>(queryFn, {
    enabled: fundId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a specific fund event
 * Maps to: GET /api/funds/:id/fund-events/:id
 * 
 * @param fundId - Fund ID
 * @param fundEventId - Fund Event ID
 * @param params - Query parameters for including relationships
 * @param options - Hook options
 * @returns Query result with fund event
 * 
 * @example
 * ```typescript
 * const { data: event, loading } = useFundEvent(fundId, eventId);
 * ```
 */
export function useFundEvent(
  fundId: number,
  fundEventId: number,
  params?: { include_fund_event_cash_flows?: boolean },
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => api.funds.getFundEvent(fundId, fundEventId, params),
    [fundId, fundEventId, params]
  );
  
  return useQuery<GetFundEventResponse>(queryFn, {
    enabled: fundId > 0 && fundEventId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// FUND EVENT MUTATIONS - Specific Event Types
// ============================================================================

/**
 * Create a capital call event
 * Maps to: POST /api/funds/:id/fund-events/capital-call
 * 
 * @param fundId - Fund ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createCapitalCall, loading } = useCreateCapitalCall(fundId);
 * 
 * createCapitalCall({
 *   event_date: '2024-01-15',
 *   amount: 50000,
 *   description: 'Q1 2024 Capital Call'
 * });
 * ```
 */
export function useCreateCapitalCall(fundId: number) {
  return useMutation<FundEvent, CreateCapitalCallRequest>(
    (data) => api.funds.createCapitalCall(fundId, data)
  );
}

/**
 * Create a return of capital event
 * Maps to: POST /api/funds/:id/fund-events/return-of-capital
 * 
 * @param fundId - Fund ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createReturnOfCapital } = useCreateReturnOfCapital(fundId);
 * 
 * createReturnOfCapital({
 *   event_date: '2024-03-15',
 *   amount: 25000
 * });
 * ```
 */
export function useCreateReturnOfCapital(fundId: number) {
  return useMutation<FundEvent, CreateReturnOfCapitalRequest>(
    (data) => api.funds.createReturnOfCapital(fundId, data)
  );
}

/**
 * Create a unit purchase event
 * Maps to: POST /api/funds/:id/fund-events/unit-purchase
 * 
 * @param fundId - Fund ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createUnitPurchase } = useCreateUnitPurchase(fundId);
 * 
 * createUnitPurchase({
 *   event_date: '2024-02-01',
 *   units_purchased: 100,
 *   unit_price: 10.50,
 *   brokerage_fee: 15.00
 * });
 * ```
 */
export function useCreateUnitPurchase(fundId: number) {
  return useMutation<FundEvent, CreateUnitPurchaseRequest>(
    (data) => api.funds.createUnitPurchase(fundId, data)
  );
}

/**
 * Create a unit sale event
 * Maps to: POST /api/funds/:id/fund-events/unit-sale
 * 
 * @param fundId - Fund ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createUnitSale } = useCreateUnitSale(fundId);
 * 
 * createUnitSale({
 *   event_date: '2024-06-15',
 *   units_sold: 50,
 *   unit_price: 12.00
 * });
 * ```
 */
export function useCreateUnitSale(fundId: number) {
  return useMutation<FundEvent, CreateUnitSaleRequest>(
    (data) => api.funds.createUnitSale(fundId, data)
  );
}

/**
 * Create a NAV update event
 * Maps to: POST /api/funds/:id/fund-events/nav-update
 * 
 * @param fundId - Fund ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createNavUpdate } = useCreateNavUpdate(fundId);
 * 
 * createNavUpdate({
 *   event_date: '2024-03-31',
 *   nav_per_share: 11.25
 * });
 * ```
 */
export function useCreateNavUpdate(fundId: number) {
  return useMutation<FundEvent, CreateNavUpdateRequest>(
    (data) => api.funds.createNavUpdate(fundId, data)
  );
}

/**
 * Create a distribution event
 * Maps to: POST /api/funds/:id/fund-events/distribution
 * 
 * Supports both simple distributions and distributions with withholding tax
 * 
 * @param fundId - Fund ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createDistribution } = useCreateDistribution(fundId);
 * 
 * // Simple distribution
 * createDistribution({
 *   event_date: '2024-06-30',
 *   distribution_type: DistributionType.DIVIDEND_FRANKED,
 *   amount: 5000
 * });
 * 
 * // Distribution with withholding tax
 * createDistribution({
 *   event_date: '2024-06-30',
 *   distribution_type: DistributionType.INTEREST,
 *   has_withholding_tax: true,
 *   gross_amount: 5000,
 *   withholding_tax_rate: 10
 * });
 * ```
 */
export function useCreateDistribution(fundId: number) {
  return useMutation<FundEvent, CreateDistributionRequest>(
    (data) => api.funds.createDistribution(fundId, data)
  );
}

/**
 * Delete a fund event
 * Maps to: DELETE /api/funds/:id/fund-events/:id
 * 
 * @param fundId - Fund ID
 * @param fundEventId - Fund Event ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteEvent } = useDeleteFundEvent(fundId, eventId);
 * 
 * deleteEvent(undefined, {
 *   onSuccess: () => refetchEvents()
 * });
 * ```
 */
export function useDeleteFundEvent(fundId: number, fundEventId: number) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => api.funds.deleteFundEvent(fundId, fundEventId)
  );
}
