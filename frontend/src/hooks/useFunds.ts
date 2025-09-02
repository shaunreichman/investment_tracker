// Fund-specific Custom Hooks
// This file provides hooks for fund-related API operations

import { useCallback, useMemo } from 'react';
import { apiClient } from '../services/api';
import { useApiCall, useMutation, useApiCallWithDeps, useConditionalApiCall } from './useApiCall';
import {
  Fund,
  DashboardFund,
  CreateFundData,
  CreateFundEventData,
  CreateTaxStatementData,
  TaxStatement,
  FundEvent,
} from '../types/api';

// ============================================================================
// FUNDS HOOKS
// ============================================================================

/**
 * Hook to get all funds
 */
export function useFunds(options?: { refetchOnWindowFocus?: boolean }) {
  const getFunds = useCallback(() => apiClient.getFunds(), []);
  
  return useApiCall<DashboardFund[]>(
    getFunds,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get a single fund by ID
 */
export function useFund(id: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    (fundId: number) => apiClient.getFund(fundId),
    [id],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get fund detail data (fund + events + statistics)
 * This is the main hook used by components
 */
export function useFundDetail(id: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    (fundId: number) => apiClient.getFundDetail(fundId),
    [id],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * NEW: Centralized fund data hook that prevents state pollution
 * This hook ensures that all components get the same data for the same fund ID
 * and properly invalidates when the fund ID changes
 */
export function useCentralizedFundDetail(fundId: number | string | null, options?: { refetchOnWindowFocus?: boolean }) {
  // Convert fundId to number, defaulting to 0 if invalid
  const numericFundId = useMemo(() => {
    if (!fundId) return 0;
    const parsed = Number(fundId);
    return isNaN(parsed) ? 0 : parsed;
  }, [fundId]);

  // Only make API call if we have a valid fund ID
  const shouldFetch = numericFundId > 0;

  // Use useConditionalApiCall but ensure it refetches when fundId changes
  // by creating a new callback function that depends on the fundId
  const getFundDetail = useCallback(() => apiClient.getFundDetail(numericFundId), [numericFundId]);

  return useConditionalApiCall(
    getFundDetail,
    shouldFetch,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to create a new fund
 */
export function useCreateFund() {
  return useMutation<CreateFundData, Fund>(
    (data) => apiClient.createFund(data)
  );
}

// ============================================================================
// FUND EVENTS HOOKS
// ============================================================================

/**
 * Hook to get fund events
 */
export function useFundEvents(fundId: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    (fundId: number) => apiClient.getFundEvents(fundId),
    [fundId],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to create a fund event
 */
export function useCreateFundEvent(fundId: number) {
  return useMutation<CreateFundEventData, FundEvent>(
    (data) => apiClient.createFundEvent(fundId, data)
  );
}



/**
 * Hook to delete a fund event
 */
export function useDeleteFundEvent(fundId: number, eventId: number) {
  return useMutation<void, void>(
    () => apiClient.deleteFundEvent(fundId, eventId)
  );
}

// ============================================================================
// TAX STATEMENTS HOOKS
// ============================================================================

/**
 * Hook to create a tax statement
 */
export function useCreateTaxStatement(fundId: number) {
  return useMutation<CreateTaxStatementData, TaxStatement>(
    (data) => apiClient.createTaxStatement(fundId, data)
  );
}

/**
 * Hook to get fund tax statements
 */
function useFundTaxStatements(fundId: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    (fundId: number) => apiClient.getFundTaxStatements(fundId),
    [fundId],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

// ============================================================================
// UTILITY HOOKS
// ============================================================================

/**
 * Hook to get fund with conditional loading
 */
function useFundConditional(id: number | null, options?: { refetchOnWindowFocus?: boolean }) {
  const getFund = useCallback(() => apiClient.getFund(id!), [id]);
  
  return useConditionalApiCall(
    getFund,
    id !== null,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get fund events with conditional loading
 */
function useFundEventsConditional(fundId: number | null, options?: { refetchOnWindowFocus?: boolean }) {
  const getFundEvents = useCallback(() => apiClient.getFundEvents(fundId!), [fundId]);
  
  return useConditionalApiCall(
    getFundEvents,
    fundId !== null,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
} 